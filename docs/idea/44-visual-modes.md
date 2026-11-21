# 🎭 44. Visual modes: one game, many looks

**The same simulation can wear several complete looks, and each player chooses their own.** Because AnyGame already separates simulation from presentation, a game can offer classic, remastered and next-gen graphics, switch between them live, and let players using different looks play in the same match.

Planned design as of 2026-11. Games named here are references for the technique only.

## Who proved it

| Game | What it shows | Evidence |
|---|---|---|
| Warcraft III: Reforged | [Patch 3.0 added a Definitive Edition mode beside Classic, with cross-graphics play](https://news.blizzard.com/en-us/warcraft3/24302500). [Reforged remains the HD look](https://www.dtgre.com/2026/09/warcraft-3-reforged-3-0-graphics-modes-classic-reforged-definitive.html?m=1) | Official post, plus a third-party guide |
| Halo: Combat Evolved Anniversary | [Original engine ran gameplay while a second engine rendered the new look](https://gamedeveloper.com/business/making-i-halo-anniversary-i-work), with [a live toggle](https://pcgamer.com/halo-ce-switch-graphics) | Press and developer accounts |
| Age of Empires II: Definitive Edition | [Higher-resolution art as a separate optional pack](https://www.xbox.com/en-AU/games/store/enhanced-graphics-pack/9N2522ZB038Z) | Store page |

Halo needed two engines because the original was never built for this, and [running both cost performance](https://www.videogamer.com/news/halo-2-anniversarys-campaign-currently-runs-at-30fps-but-343-promises-itll-be-60fps-at-launch). AnyGame gets the benefit from its architecture, and pays only for the look in use.

## How it works

```text
                        ┌── look: classic  (low-poly, pixel filter, original audio)
SIMULATION -> EXTRACT ──┼── look: remaster (HD assets, desktop tier)
 (unchanged)            └── look: nextgen  (ray-traced GI, virtual geometry)
```

A **look** is a package. Gameplay refers to stable visual IDs, and the active look decides what each ID becomes.

```toml
# content/looks/classic/anygame.toml: illustrative
[look]
id = "classic"
render_preset = "forward-retro"
provides = ["visuals", "vfx", "ui-skin", "audio"]
fallback = "remaster"
```

| A look may change | A look must never change |
|---|---|
| Meshes, sprites, textures, materials | Hitboxes and collision |
| Animation clips, if timing events match | Gameplay timing and frame data |
| Lighting and render graph preset | Stats, abilities and rules |
| VFX, UI skin, fonts | What information a player can see |
| Music, sound and voice | Replay, save and network data |

## Rules

| Rule | Why |
|---|---|
| **Gameplay never reads a mesh, texture or clip** | Otherwise a look changes the game |
| **Collision and hit volumes are gameplay data** | Every look plays identically |
| **Animation events come from a shared timeline** | A new clip cannot move a hit window |
| **A look is local to each player** | Cross-look multiplayer needs no extra netcode |
| **Looks are not in the content hash for match rules** | Different looks can share a match |
| **Each look loads on demand** | Players store and download only what they use |
| **Each has a fallback** | A missing asset shows the fallback look, never a hole |
| **Switch through the [resource lifecycle](34-resource-lifecycle.md)** | Show the old look until the new one is ready |
| **Look packages can be mods** | The community can add a whole art style |

## 👾 Old-school graphics are first-class

**Pixel art and retro looks are a real art direction, not a low setting.** A game can be retro from its first commit, with no modern look at all, and it ships with none of the high-end renderer.

| Style | Render preset | Key techniques |
|---|---|---|
| 8-bit | `retro.8bit` | Small fixed palette, tile and sprite limits as an optional rule, integer scaling |
| 16-bit | `retro.16bit` | Palette swaps, parallax layers, scanline effects, Mode 7-style floors |
| Modern pixel art | `pixel.hd` | Low-res world, high-res lighting and UI, sub-pixel camera smoothing |
| PS1-style 3D | `retro.psx` | Low-res target, vertex snapping, affine textures, dithering, no filtering, short draw distance |
| N64-style 3D | `retro.n64` | Three-point filtering, fog, low-res textures, soft output |
| Early PC 3D | `retro.lowpoly` | Flat or vertex lighting, lightmaps, low-res textures |
| Raycast or sector look | `retro.raycast` | Billboards, grid or sector worlds |
| Voxel | `voxel` | Chunked meshing, ambient occlusion per voxel |
| Isometric | `iso2d` | Depth-sorted sprites, tile layers |
| Vector | `vector` | SDF lines and glow |
| Terminal and ASCII | `ascii` | Glyph grid as the framebuffer |
| Toon and hand-drawn | `toon` | Outlines, ramp shading, animation on twos |

Every preset is a render-graph preset, so a game can mix them or write its own.

| Building block | What it does |
|---|---|
| Low-res target + integer scale | Crisp pixels at any display size, with letterbox or a clean fractional option |
| Palette and LUT pass | Limit colours, swap palettes, day/night by palette |
| Ordered dithering | Authentic gradients and transparency |
| Nearest sampling, no mips | Sharp texels |
| Vertex snapping, affine mapping | The wobble of early 3D |
| Stepped animation | 8, 12 or 15 fps animation on a smooth game loop |
| CRT, scanline, composite, phosphor passes | Optional display emulation, always with an off switch |
| Retro audio | Chip-style synth, bitcrush, low sample rates |
| Authentic limits, optional | Sprites per line or colours per tile, as a lint a game can opt into |

Rules for a good retro game:

- **Keep the simulation modern.** High tick rate, low latency and clean input, even when the art is old.
- **Pixels stay consistent.** One pixel density across world, characters and UI unless the style chooses otherwise.
- **UI stays readable,** with options for larger text and for turning off CRT, flicker and wobble effects.
- **Enjoy the savings.** Retro games should hit the smallest binaries and run on the weakest devices ([small and fast](21-small-and-fast.md)).

## Competitive fairness

A look must never become a cheat, or the best-looking option a disadvantage.

| Risk | Rule |
|---|---|
| A look hides foliage or smoke | Ranked play defines what must stay visible |
| Tiny or dark units are harder to read | Readability checks for silhouette, team colour and contrast |
| Effects obscure a telegraph | Critical gameplay signals stay equally clear |
| Audio cues differ | Important sounds exist in every look at comparable loudness |
| Custom look reveals hidden data | Looks only receive what [visibility filtering](35-client-server-models.md#every-field-has-a-visibility-class) sent |
| Modded look changes a silhouette | Ranked may allow signed looks only |

## Why this is powerful

- **Remaster without touching the game.** Ship a new look years later, and old saves and replays still work.
- **One game, every device.** A phone can use a light look, a high-end PC a next-gen one.
- **Nostalgia stays available.** Players can keep the look they love.
- **Before and after live toggle** makes a strong trailer and press moment.
- **Art direction becomes a setting**: pixel art, toon, realistic, horror.
- **Agents can generate a look as a package** with tools such as [ts23d or Kubeez](19-companion-tools.md), and replace it without risk to gameplay.
- **Accessibility looks:** high contrast or reduced motion can be a full look.

## Proof

| Check | Passes when |
|---|---|
| **Look invariance** | One replay run under every look gives an identical simulation checksum |
| Hit data | Every look uses the same collision and event timeline |
| Coverage | Every visual ID resolves in every look or its declared fallback |
| Live switch | Switching mid-game causes no crash, no simulation change and no frame over budget |
| Cross-look match | Bots using different looks finish a match with no desync |
| Pay for what you use | A build with one look contains no assets from the others |
| Readability | Automated contrast and silhouette checks pass in each look |
| Pixel-perfect | At each integer scale, a golden capture has no shimmer or uneven pixels |
| Retro footprint | A retro-only build contains no high-end renderer code |
