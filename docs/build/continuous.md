# Continuous work

**Proves:** AI-first and no-fork. Runs alongside every phase. **Read:** [extending](../idea/05-extending.md), [scripting and tools](../idea/11-scripting-modding-tools.md), [AI-first](../idea/12-ai-first.md).

| Track | Standing rule |
|---|---|
| CLI | Every new capability is an `ag` command with JSON output |
| MCP | Exposes the same commands as the CLI, with no separate logic |
| Live viewer | Changes nothing that is not also a command |
| Modding and workshop | Mods use the same package mechanism as game content, with fewer permissions |
| Lifecycle | Each phase adds its part of [idea to distribution](../idea/25-idea-to-distribution.md): planning primitives from Phase 0, `distribute` adapters from Phase 1 |
| One-prompt eval | Each kit adds a genre playbook and a [one-prompt](../idea/26-one-prompt-to-game.md) eval scored by a bot |
| Docs | Markdown with runnable examples that CI executes |
| Conformance | Every interface ships a suite any replacement must pass |
| Budgets | Each module declares CPU, GPU and memory budgets. CI fails on regression |
| Clean-room | Every contribution follows [CONTRIBUTING.md](../../CONTRIBUTING.md) |
