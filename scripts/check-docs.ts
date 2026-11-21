#!/usr/bin/env bun
/** Docs gate: links, anchors, indexes, tables, code fences and secrets. */
import { existsSync, lstatSync, readdirSync, readFileSync } from 'node:fs';
import { dirname, extname, isAbsolute, join, relative, resolve } from 'node:path';

export type DocError = { file: string; line: number; code: string; message: string };
type Line = { number: number; text: string };

const SECRET_PATTERNS = [
  /-----BEGIN [A-Z ]*PRIVATE KEY-----/,
  /\bgh[pousr]_[A-Za-z0-9]{36,}\b/,
  /\bgithub_pat_[A-Za-z0-9_]{40,}\b/,
  /\bsk-ant-[A-Za-z0-9_-]{20,}\b/,
  /\bsk_live_[A-Za-z0-9]{16,}\b/,
  /\bAKIA[0-9A-Z]{16}\b/,
];
const FENCE = /^\s*(```+|~~~+)/;
const HEADING = /^#{1,6}\s+(.+?)\s*#*$/;
const HTML_ANCHOR = /<a\s+name="([^"]+)"/g;
const LINK = /(?<!\\)\]\(([^()\s]+)\)/g;
const INLINE_CODE = /(`+).+?\1/g;
const TABLE_DIVIDER = /^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$/;
const UNESCAPED_PIPE = /(?<!\\)\|/g;
const EXTERNAL = /^[a-z][a-z0-9+.-]*:/i;
const INDEXED_FOLDERS = ['docs/idea', 'docs/build'];

/** Tracked and new files, honouring .gitignore. Symlinks are skipped. */
function projectFiles(root: string): string[] {
  const result = Bun.spawnSync(['git', 'ls-files', '--cached', '--others', '--exclude-standard'], {
    cwd: root,
  });
  if (result.exitCode !== 0) throw new Error(`git ls-files failed: ${result.stderr.toString()}`);
  return result.stdout
    .toString()
    .split('\n')
    .filter(Boolean)
    .map((file) => join(root, file))
    .filter((file) => existsSync(file) && lstatSync(file).isFile())
    .sort();
}

/** Lines outside fenced code, plus the line of a fence that never closes. */
function proseLines(text: string): { lines: Line[]; unclosedAt: number | null } {
  const lines: Line[] = [];
  let fence: string | null = null;
  let openedAt = 0;
  text.split(/\r?\n/).forEach((line, index) => {
    const number = index + 1;
    const marker = FENCE.exec(line)?.[1];
    if (!marker) {
      if (fence === null) lines.push({ number, text: line });
    } else if (fence === null) {
      fence = marker;
      openedAt = number;
    } else if (marker[0] === fence[0] && marker.length >= fence.length) {
      fence = null;
    }
  });
  return { lines, unclosedAt: fence === null ? null : openedAt };
}

export function githubSlug(heading: string): string {
  return heading
    .replace(/\[([^\]]*)\]\([^)]*\)/g, '$1')
    .replace(/[`*]/g, '')
    .trim()
    .toLowerCase()
    .replace(/[^\p{L}\p{N}_\- ]/gu, '')
    .replaceAll(' ', '-');
}

function anchors(text: string): Set<string> {
  const seen = new Map<string, number>();
  const result = new Set<string>();
  for (const { text: line } of proseLines(text).lines) {
    for (const match of line.matchAll(HTML_ANCHOR)) result.add(match[1] as string);
    const heading = HEADING.exec(line)?.[1];
    if (!heading) continue;
    const slug = githubSlug(heading);
    const count = seen.get(slug) ?? 0;
    seen.set(slug, count + 1);
    result.add(count ? `${slug}-${count}` : slug);
  }
  return result;
}

function isInside(root: string, path: string): boolean {
  const fromRoot = relative(root, path);
  return !fromRoot.startsWith('..') && !isAbsolute(fromRoot);
}

function checkLinks(root: string, path: string, lines: Line[]): DocError[] {
  const errors: DocError[] = [];
  const file = relative(root, path);
  for (const { number, text } of lines) {
    for (const match of text.replace(INLINE_CODE, '').matchAll(LINK)) {
      const target = match[1] as string;
      if (EXTERNAL.test(target)) continue;
      const [filePart = '', fragment] = target.split('#', 2);
      const resolved = filePart ? resolve(dirname(path), filePart) : path;
      if (!isInside(root, resolved) || !existsSync(resolved)) {
        errors.push({
          file,
          line: number,
          code: 'broken-link',
          message: `${target} does not exist`,
        });
      } else if (fragment && extname(resolved) === '.md') {
        if (!anchors(readFileSync(resolved, 'utf8')).has(fragment)) {
          errors.push({
            file,
            line: number,
            code: 'broken-anchor',
            message: `${target} has no such heading`,
          });
        }
      }
    }
  }
  return errors;
}

const pipes = (row: string) =>
  row.trim().replace(/^\|/, '').replace(/\|$/, '').match(UNESCAPED_PIPE)?.length ?? 0;

function checkTables(file: string, lines: Line[]): DocError[] {
  const errors: DocError[] = [];
  const byNumber = new Map(lines.map(({ number, text }) => [number, text]));
  for (const { number, text } of lines) {
    const header = byNumber.get(number - 1);
    if (!header?.includes('|') || !TABLE_DIVIDER.test(text)) continue;
    const expected = pipes(header);
    for (let row = number + 1; byNumber.get(row)?.includes('|'); row++) {
      if (pipes(byNumber.get(row) as string) !== expected) {
        errors.push({
          file,
          line: row,
          code: 'table-columns',
          message: `expected ${expected + 1} cells`,
        });
      }
    }
  }
  return errors;
}

function checkIndexes(root: string): DocError[] {
  const errors: DocError[] = [];
  for (const folder of INDEXED_FOLDERS) {
    const directory = join(root, folder);
    if (!existsSync(directory)) continue;
    const index = join(directory, 'README.md');
    if (!existsSync(index)) {
      errors.push({
        file: folder,
        line: 1,
        code: 'missing-index',
        message: 'folder has no README.md',
      });
      continue;
    }
    const text = readFileSync(index, 'utf8');
    for (const name of readdirSync(directory).sort()) {
      if (name.endsWith('.md') && name !== 'README.md' && !text.includes(`(${name}`)) {
        errors.push({
          file: `${folder}/${name}`,
          line: 1,
          code: 'unindexed-doc',
          message: `add ${name} to ${folder}/README.md`,
        });
      }
    }
  }
  return errors;
}

function checkSecrets(file: string, text: string): DocError[] {
  const errors: DocError[] = [];
  text.split(/\r?\n/).forEach((line, index) => {
    if (SECRET_PATTERNS.some((pattern) => pattern.test(line))) {
      errors.push({
        file,
        line: index + 1,
        code: 'secret',
        message: 'possible credential, value not shown',
      });
    }
  });
  return errors;
}

export function checkDocs(rootPath: string): DocError[] {
  const root = resolve(rootPath);
  const errors = checkIndexes(root);
  const utf8 = new TextDecoder('utf-8', { fatal: true });
  for (const path of projectFiles(root)) {
    let text: string;
    try {
      text = utf8.decode(readFileSync(path));
    } catch (error) {
      if (error instanceof TypeError) continue; // binary file: nothing to scan as text
      throw error;
    }
    const file = relative(root, path);
    errors.push(...checkSecrets(file, text));
    if (extname(path) !== '.md') continue;
    const { lines, unclosedAt } = proseLines(text);
    if (unclosedAt !== null) {
      errors.push({
        file,
        line: unclosedAt,
        code: 'unclosed-fence',
        message: 'code fence never closes',
      });
    }
    errors.push(...checkLinks(root, path, lines), ...checkTables(file, lines));
  }
  return errors;
}

if (import.meta.main) {
  const errors = checkDocs(join(import.meta.dir, '..'));
  if (process.argv.includes('--json')) {
    console.log(JSON.stringify({ ok: errors.length === 0, errors }, null, 2));
  } else {
    for (const e of errors) console.log(`${e.file}:${e.line}: ${e.code}: ${e.message}`);
    console.log(errors.length ? `docs: ${errors.length} problem(s)` : 'docs: ok');
  }
  process.exit(errors.length ? 1 : 0);
}
