# 🤝 Contributing

AnyGame is at the design stage and is not maintained until it is ready, so issues and pull requests may go unanswered. The most useful contributions today are corrections, sourced evidence, and answers to [open questions](docs/build/open-questions.md).

## 🧼 Clean-room policy

This applies to every contributor, human or AI.

- **Never contribute anything derived from leaked source code or decompiled binaries.** If you have read such material for an engine, do not contribute to the matching AnyGame subsystem, and tell the maintainers.
- **Private-server emulators count as off limits** when they derive from reverse-engineered or leaked game code.
- **Allowed sources:** published talks and papers, frame-capture studies, public modding documentation of file formats, and open-source engines under compatible licenses.
- **Credit what you reuse.** Keep license notices, and name the source in your pull request.
- **No copied game content.** Samples and kits use original names, characters, art, music and levels.

## 🔀 Pull requests

- Branch from `main`, with one concern per pull request.
- Use conventional commits, such as `docs(build): add phase 0 exit check`.
- Run `bin/check` before opening a pull request. CI runs the same command.
- Follow the doc rules in [CLAUDE.md](CLAUDE.md).
- Date load-bearing claims, and link a source for claims about other engines.
- AI-assisted contributions are welcome. You are responsible for checking them.
