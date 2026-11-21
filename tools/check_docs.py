#!/usr/bin/env python3
"""Docs gate: links, anchors, indexes, tables, code fences and secrets."""

import json
import re
import subprocess
import sys
from pathlib import Path

SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{40,}\b"),
    re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bsk_live_[A-Za-z0-9]{16,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
)
FENCE = re.compile(r"^\s*(```+|~~~+)")
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*#*$")
HTML_ANCHOR = re.compile(r'<a\s+name="([^"]+)"')
LINK = re.compile(r"(?<!\\)\]\(([^()\s]+)\)")
INLINE_CODE = re.compile(r"(`+).+?\1")
TABLE_DIVIDER = re.compile(r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$")
UNESCAPED_PIPE = re.compile(r"(?<!\\)\|")
EXTERNAL = re.compile(r"^[a-z][a-z0-9+.-]*:", re.IGNORECASE)


def project_files(root):
    """Tracked and new files, honouring .gitignore."""
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=root, capture_output=True, text=True, check=True,
    )
    paths = (root / line for line in result.stdout.splitlines())
    return sorted(p for p in paths if p.is_file() and not p.is_symlink())


def prose_lines(text):
    """Yield (line number, line) outside fenced code, plus any unclosed fence."""
    lines, fence, opened_at = [], None, 0
    for number, line in enumerate(text.splitlines(), 1):
        match = FENCE.match(line)
        if match:
            marker = match.group(1)
            if fence is None:
                fence, opened_at = marker, number
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
            continue
        if fence is None:
            lines.append((number, line))
    return lines, opened_at if fence else None


def github_slug(heading):
    heading = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading)
    heading = re.sub(r"[`*]", "", heading).strip().lower()
    heading = re.sub(r"[^\w\- ]", "", heading)
    return heading.replace(" ", "-")


def anchors(text):
    lines, _ = prose_lines(text)
    seen, result = {}, set()
    for _, line in lines:
        result.update(HTML_ANCHOR.findall(line))
        match = HEADING.match(line)
        if match:
            slug = github_slug(match.group(1))
            count = seen.get(slug, 0)
            seen[slug] = count + 1
            result.add(f"{slug}-{count}" if count else slug)
    return result


def check_links(path, lines, root):
    errors = []
    for number, line in lines:
        for target in LINK.findall(INLINE_CODE.sub("", line)):
            if EXTERNAL.match(target):
                continue
            file_part, _, fragment = target.partition("#")
            resolved = (path.parent / file_part).resolve() if file_part else path
            if not resolved.is_relative_to(root.resolve()) or not resolved.exists():
                errors.append((path, number, "broken-link", f"{target} does not exist"))
            elif fragment and resolved.suffix == ".md":
                if fragment not in anchors(resolved.read_text(encoding="utf-8")):
                    errors.append((path, number, "broken-anchor", f"{target} has no such heading"))
    return errors


def check_tables(path, lines):
    errors = []
    by_number = dict(lines)
    for number, line in lines:
        header = by_number.get(number - 1)
        if header is None or "|" not in header or not TABLE_DIVIDER.match(line):
            continue
        expected = len(UNESCAPED_PIPE.findall(header.strip().strip("|")))
        row_number = number + 1
        while "|" in by_number.get(row_number, ""):
            row = by_number[row_number].strip().strip("|")
            if len(UNESCAPED_PIPE.findall(row)) != expected:
                errors.append((path, row_number, "table-columns", f"expected {expected + 1} cells"))
            row_number += 1
    return errors


def check_indexes(root):
    errors = []
    for folder in ("docs/idea", "docs/build"):
        directory = root / folder
        index = directory / "README.md"
        if not index.exists():
            if directory.exists():
                errors.append((directory, 1, "missing-index", "folder has no README.md"))
            continue
        text = index.read_text(encoding="utf-8")
        for doc in sorted(directory.glob("*.md")):
            if doc.name != "README.md" and f"({doc.name}" not in text:
                errors.append((doc, 1, "unindexed-doc", f"add {doc.name} to {folder}/README.md"))
    return errors


def check_secrets(path, text):
    errors = []
    for number, line in enumerate(text.splitlines(), 1):
        if any(pattern.search(line) for pattern in SECRET_PATTERNS):
            errors.append((path, number, "secret", "possible credential, value not shown"))
    return errors


def check(root):
    root = root.resolve()
    errors = check_indexes(root)
    for path in project_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        errors += check_secrets(path, text)
        if path.suffix != ".md":
            continue
        lines, unclosed = prose_lines(text)
        if unclosed:
            errors.append((path, unclosed, "unclosed-fence", "code fence never closes"))
        errors += check_links(path, lines, root)
        errors += check_tables(path, lines)
    return [
        {"file": str(p.relative_to(root)), "line": n, "code": code, "message": message}
        for p, n, code, message in errors
    ]


def main(argv):
    root = Path(__file__).resolve().parent.parent
    errors = check(root)
    if "--json" in argv:
        print(json.dumps({"ok": not errors, "errors": errors}, indent=2))
    else:
        for e in errors:
            print(f"{e['file']}:{e['line']}: {e['code']}: {e['message']}")
        print("docs: ok" if not errors else f"docs: {len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
