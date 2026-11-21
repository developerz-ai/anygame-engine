# 🎯 1. Thesis

**Our objective: we provide the building blocks that help developers and their agents build their game. We never stand between them and it.** More blocks will come, and adding them must not change the architecture ([future-ready](22-future-ready.md)). When a design choice trades the developer's control for the engine's convenience, the developer's control wins.

AnyGame is not one engine. It is a 30k-line kernel plus a catalogue of replaceable modules, and a game is a manifest that picks which modules to load.

Thirty years of engines show why. Every monolithic engine bakes in one answer to four questions, and each answer rules out whole genres:

| Question | Typical baked-in answer | Genre it breaks |
|---|---|---|
| Who owns time? | Variable-step frame loop | Fighting games, RTS lockstep, replays |
| Who owns state? | Object graph with virtual `Tick()` | 10,000-unit RTS, MMO server density |
| Who owns authority? | One dedicated server per match | MMOs, peer-to-peer rollback |
| Who owns the frame? | Fixed deferred 3D renderer | Pixel-art 2D, stylised, mobile |

AnyGame bakes in none of them. The kernel knows about memory, jobs, data, reflection and plugins. Time, simulation model, authority and rendering are all modules behind versioned interfaces.

## Design rules

1. **Everything above the kernel is a plugin.** First-party modules get no private API. If the built-in renderer needs a hook, that hook is public.
2. **Data is the contract.** Modules talk through reflected, schema-described data (components, events, assets), not through class inheritance. Data can be versioned, diffed, replicated, serialised and read by an AI agent; a vtable cannot.
3. **Three tiers per domain:** interface, reference implementation, AAA implementation. Physics has an interface, a simple 2D solver, and a full 3D solver. A Pong clone never pays for the third.
4. **Determinism is opt-in per world, but designed in from day one.** Retrofitting it is close to impossible; removing it is free.
5. **Extend by composition, override by registration, never by editing.** Nobody should need to fork. Forking is treated as an engine bug: file the missing extension point.
6. **Headless and scriptable first.** The core has no GUI editor; every operation is a command or a text file. This single rule is what makes the engine usable by AI agents, CI, and dedicated servers.
7. **Pay only for what you load.** A 2D game's shipped binary contains no virtual-geometry code, no navmesh, no netcode.
8. **Help, then get out of the way.** The engine serves the developer and their game, and never stands in front of them. Kits, conventions, gates, budgets and recommendations are defaults a game can override, replace or ignore. Strict rules bind the engine's own code and the safety of its contracts, not a game's design, stack or content choices.
9. **Small and fast by default.** Faster hardware should buy a better game, not a heavier one. Every byte and millisecond must reach the player, and the engine makes each one's price visible ([small and fast](21-small-and-fast.md)).
10. **Ready for the future.** Bet on nothing permanently. New hardware, APIs and models arrive as adapters, and old games and saves keep working ([future-ready](22-future-ready.md)).
11. **No regrets.** No fees, lock-in, forced upgrades, hidden telemetry or overclaiming. A developer can always leave with everything ([no regrets](31-no-regrets.md)).
12. **Fast and correct.** Agents supply development speed, so the engine spends its design on performance and quality. SOLID at the boundaries, data-oriented in hot paths ([quality bar](32-quality-bar.md)).

## What "any game" honestly means

The engine can make it possible to build GTA-scale games. It cannot make them cheap: that scale is mostly content, tooling and thousands of person-years. The realistic promise is that a team never hits an architectural wall and never has to fork to get past one.
