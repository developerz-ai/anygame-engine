# 🛠️ 11. Scripting, modding, tools and everything else a game needs

Modding is not a feature added later: a mod is a package, loaded by the same mechanism as the game's own content, with fewer permissions.

## Scripting tiers

| Tier | Language | Runs | For |
|---|---|---|---|
| Native | C++23 engine modules (plugins) | Full speed, hot-reloadable | Engine modules, performance-critical gameplay |
| Script | Lua (Luau-style typed dialect) by default; the VM is a plugin, so C#, Wren, AngelScript or WASM can be added | Sandboxed VM with CPU and memory quotas | Gameplay logic, UI, mods, map scripts |
| Visual | Not in the core. Graphs (abilities, AI, quests) are text assets with schemas | Same VM | Agents write the text directly; a node UI can exist as a community package |
| Data | Text assets with schemas | No code | Balancing, items, units, dialogue |

Bindings for all tiers are generated from the reflection schema, so a new C++ component is scriptable the moment it compiles.

## Modding, the Warcraft III lesson

Warcraft III shipped its own World Editor: terrain, unit data editor, a trigger system (event, condition, action) that compiled to script, and maps as single shareable files that downloaded automatically when joining a lobby. Tower defence and the MOBA genre came out of it. AnyGame copies the whole recipe:

- **The shipped game can include the editor tooling:** the same CLI and text formats its developers use. A game may also ship its own in-game map tool as a package.
- **Triggers.** Event-condition-action authoring that compiles to Lua; advanced modders drop into Lua directly.
- **Data overrides.** Every unit, item and ability is a data asset; a mod layers changes on top without replacing files, so two mods touching different fields do not conflict.
- **Maps and modes as packages** that sync automatically in multiplayer, with content hashes so all peers run identical logic (required for lockstep).
- **Capability sandbox.** A mod declares what it needs (`ui`, `gameplay.read`, `gameplay.write`, `net`, `files`). Scripts cannot touch the OS. Server decides which capabilities are allowed in ranked play.
- **Total conversions** use the same package system the base game uses, so there is no ceiling.
- **Workshop service:** publish, version, depend, rate, moderate; in `liveops`.

## HUD and UI modding, the WoW lesson

WoW's interface is Lua plus markup running against a restricted API, and Blizzard's default UI is written with the same API addons use. AnyGame's HUD works the same way:

- HUD is declarative markup + stylesheet + script, data-bound to ECS queries ("health of my target").
- The default HUD of each kit is itself a replaceable package.
- A "protected action" model: UI scripts can display anything but can only trigger gameplay actions through hardware-initiated input, which blocks botting through addons.
- Layout editor in game: drag, scale, anchor, save profiles; safe-zone, aspect-ratio and controller/touch variants built in.

## Asset pipeline

- Source assets stay in open formats (glTF, USD, PNG/EXR, WAV, FBX import); a content-addressed cache holds cooked results, shared across the team and CI.
- Deterministic, incremental cooking as a dependency graph: change one texture, re-cook only what depends on it.
- All engine-authored assets are text (diffable, mergeable, AI-readable) with binary only for bulk data.
- Hot reload of every asset type on every platform, including a phone connected over the network.
- Patching by content-addressed chunks: small updates, and mobile downloads on demand.

## Code-first: there is no GUI editor

AnyGame is built for coding agents, so the primary authoring surface is code and text, not a visual builder. The core ships no scene editor, no node-graph UI and no drag-and-drop tooling.

- Scenes, prefabs, UI, materials, animation graphs, behaviour trees and quests are text files or code. Each has a schema, a formatter, a linter and a validator that returns structured errors.
- Spatial content comes from code, procedural generation and existing tools. Import from Blender, Tiled, LDtk, Houdini and USD; AnyGame does not rebuild those.
- **A live viewer, not an editor.** One small tool attaches to a running game to look, inspect entities, scrub time and take captures. It changes nothing that is not also a command.
- **Everything is a command.** `ag` covers create, build, run, query, test, profile, cook, deploy. The same commands are exposed over MCP.
- **Feedback an agent can read.** Screenshots, depth and ID buffers, scene dumps as text, frame timings and test results come back from every run.
- GUI tools are welcome as community packages built on the public command protocol. The core team does not maintain them, and no engine feature may depend on one.

```cpp
// A level is code. Readable, diffable, generatable, testable.
void build_arena(ag::World& w) {
    auto ground = w.spawn(Transform{}, Mesh{"meshes/arena.glb"}, StaticCollider{});
    for (int i = 0; i < 8; ++i)
        w.spawn(prefab("enemies/grunt"), Transform{ring_position(i, 8, 12.0f)});
    w.spawn(prefab("player"), Transform{{0, 1, 0}}, LocalPlayer{0});
    w.insert_resource(MatchRules{.time_limit = 180s, .win_score = 20});
}

AG_TEST(arena_is_winnable) {
    auto w = ag::test::world(build_arena);
    ag::test::bot(w, "aggressive").play_for(180s);
    AG_EXPECT(w.resource<Score>().player >= 1);
}
```

## Coverage checklist: every area a shipped game touches

| Area | Module | Area | Module |
|---|---|---|---|
| Input, rebinding, touch, gyro, haptics | `input` | Camera rigs, shake, collision | `camera` |
| Save games, cloud saves, versioning | `persist.save` | Cinematics and sequencer | `sequencer` |
| Localisation, fonts, right-to-left | `l10n` | Subtitles, colour-blind modes, remapping, screen reader | `accessibility` |
| Replays, spectating, photo mode | `replay` | Achievements, platform services | `platform.services` |
| Store, DLC, entitlements | `commerce` | Voice and text chat, reporting | `social.comms` |
| Tutorials, hints, onboarding | `gameplay.guidance` | Difficulty and dynamic tuning | `gameplay.tuning` |
| Loading, boot flow, patcher | `boot` | Crash reporting, bug capture with replay | `telemetry` |
| Weather, time of day, seasons | `world.environment` | Destruction, fire, fluids | `physics.fx` |
| Performance scaling, dynamic resolution | `render.scaling` | Automated tests, bots, soak tests | `testing` |
| Console certification checks | `platform.cert` | Age rating, privacy, parental controls | `compliance` |
