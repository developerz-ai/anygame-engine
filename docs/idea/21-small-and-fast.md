# 🪶 21. Small and fast

**Hardware got far faster. Games mostly spent the gain.** Old games were small and fast because they had no choice. AnyGame keeps that discipline by default, so better hardware buys a better game, not a heavier one.

Scale of what is possible, recalled and not re-checked: the original Super Mario Bros. cartridge held about 40 KB, and the 2004 demoscene shooter .kkrieger fits in 96 KB by generating its content at startup.

Numbers here are proposed targets until CI measures them. Like every default, a game can override them ([rule 8](01-thesis.md#design-rules)).

## The rule

**Every byte and millisecond must reach the player as something they can see, hear or feel.** If it does not, stop computing it, stop storing it, or stop shipping it.

## What to measure

| Resource | Why players care | Report per module and asset |
|---|---|---|
| Install size | Storage, first download | Bytes, largest assets, duplicates |
| Patch size | Every update they download | Changed bytes per release |
| RAM and VRAM | Which machines can run it | Peak and idle, by tag |
| CPU and GPU time | Frame rate | ms against budget, p99 |
| Load time | Waiting | Time to first frame and to gameplay |
| Energy | Battery, heat, fan noise | Average power on a reference device |
| Bandwidth | Mobile data, server bills | Bytes per player per second |
| Server cost | Whether a game can stay online | Players per core, MB per player |

`ag profile --budget` shows them together. A build diff states what each change cost.

## How old games stayed small

| Trick | Then | Now |
|---|---|---|
| **Generate, do not store** | Procedural textures and levels | Seeded PCG, recipes as source, cook on install when it saves download |
| **Reuse everything** | Tile sets, palette swaps, mirrored sprites | Trim sheets, instancing, material variants, shared skeletons |
| **Store only the difference** | Delta-encoded animation and maps | Delta patches, content-addressed chunks, no duplicate data |
| **Fit data to its use** | Fixed-point, packed bits | Quantised transforms, octahedral normals, 16-bit where enough |
| **Do not draw what is hidden** | BSP, PVS, portals | GPU culling, occlusion, Hi-Z |
| **Do not update what is idle** | Only simulate near the screen | Sleeping entities, simulation LOD, change detection |
| **Spread work over frames** | Update a few enemies per tick | Time-sliced AI, amortised GI and shadows |
| **Compute once** | Lookup tables, baked lighting | Bake static worlds, cache pipelines, keep dynamic only where it shows |
| **Lower resolution where unseen** | Half-res effects | Half-res particles, variable-rate shading, upscaling |
| **Design around the limit** | Fog, corridors, sprite limits as style | Art direction that looks good cheaply beats brute force |

More in [thirty years of tricks](20-tricks-30-years.md).

## Engine defaults

| Default | Effect |
|---|---|
| Nothing unloaded costs anything | No symbols, memory or ticks for absent modules |
| Empty systems do not run | Idle game does near-zero CPU work |
| **Menus and pauses throttle** | No uncapped GPU on a static screen |
| **Unchanged frames are not redrawn** when the game opts in | Turn-based, UI and narrative games save battery |
| Frame cap follows the display | No frames rendered that nobody sees |
| GPU-compressed textures, compressed meshes | Less VRAM and disk with no runtime decode cost |
| Per-platform cooks | A phone never downloads desktop 4K assets |
| Duplicate-asset report at cook time | Size waste is visible before release |
| Install on demand | Optional content downloads when needed |

## Small by default, unlimited by choice

Lean defaults are a floor, never a ceiling. A game can load anything it wants: DLSS, FSR, XeSS, MetalFX, frame generation, ray tracing, path tracing, neural denoisers, vendor SDKs, or its own technique.

| Rule | Shape |
|---|---|
| **Everything is a plugin** | Each upscaler or vendor feature implements a public interface, such as a render-graph pass |
| **Use several at once** | A game can ship DLSS, FSR and XeSS and select by GPU or player setting |
| **Absent means zero cost** | A game that does not load a vendor SDK ships none of its code |
| **No favourites** | First-party plugins get no private API, so a community or in-house one is equal |
| **Licences stay with the game** | Proprietary SDKs are external packages under their vendor's terms ([build vs wrap](17-next-gen-techniques.md)) |
| **Upscaling is a tool, not an excuse** | Use it to spend saved GPU time on the game. Keep the frame budget honest at native input resolution |

## For coding agents

Agents add code cheaply, so bloat grows quietly unless it is visible.

- Prefer the smallest module set that achieves the game.
- Reuse an asset or system before adding one.
- Run `ag profile --budget` after a feature and report what it cost.
- Report a size or frame-time regression even when it is allowed.
- Spend budget where the player notices. A beautiful hero asset can be worth it. An invisible 4K texture is not.

The developer decides the trade. A game that wants to spend everything on visuals can. The engine makes the price visible and never blocks it.
