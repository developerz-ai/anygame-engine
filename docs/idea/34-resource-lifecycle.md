# ♻️ 34. Load on demand, cache, unload

**Nothing is in memory unless the player is about to need it.** Every resource (mesh, texture, sound, animation, script, level cell, even a module where the platform allows it) goes through one lifecycle, one budget system and one handle type.

Planned design as of 2026-11. Budgets are targets until CI measures them. The `resource` port is replaceable like any other.

## One lifecycle

```text
unloaded -> queued -> reading -> decoding -> uploading -> ready <-> cached -> evicting -> unloaded
              |          |           |            |
              +----------+-----------+------------+--> failed (fallback shown, retry policy applies)
```

| State | Meaning | Costs |
|---|---|---|
| `unloaded` | Only the handle and metadata exist | A few bytes |
| `queued` | Requested, ordered by priority | Can still be cancelled |
| `reading` | Async I/O from disk or network | Bandwidth |
| `decoding` | Decompress on worker jobs | CPU, never the main thread |
| `uploading` | Sent to GPU within a per-frame budget | Upload bandwidth |
| `ready` | In use this frame | RAM or VRAM |
| `cached` | Unused, kept because it may return | Reclaimable at any moment |
| `evicting` | Waits until the GPU has finished with it | Frames in flight |
| `failed` | Shows a fallback and reports a coded error | Never a crash |

## Rules

| Rule | Why |
|---|---|
| **Gameplay holds handles, never pointers** | A resource can move or be evicted safely |
| **A request never blocks a frame** | No load hitches |
| **Every resource type has a fallback** | Low mip, low LOD, placeholder, silence |
| **Load progressively** | Lowest mip and LOD first, then refine |
| **One request per content hash** | Duplicate requests share one load |
| **Cancel what is no longer needed** | A player who turned around should not pay for it |
| **Budgets are in MB and ms** | Per tag and per platform tier |
| **Pin only for the current frame** | Long-lived pins defeat eviction |
| **Free GPU memory after its last frame in flight** | Prevents use-after-free on the GPU |
| **Hysteresis on load and unload radii** | Stops thrashing at a boundary |

## What to load next

Priority combines visible screen size, distance, predicted camera path, importance and how long it has waited.

| Signal | Example |
|---|---|
| On screen now | Visible mesh at required LOD |
| About to be visible | Along vehicle velocity, or the next door |
| Gameplay critical | Player weapon, collision, active quest |
| Known ahead | Level manifest, recorded route from bots |
| Audio | Starts of sounds in memory, the rest streamed |
| Background | Fill the idle budget with likely content |

**Learn from play:** bot runs record which assets each area uses, and that manifest pre-orders loads and disc or package layout.

## What to unload first

Default eviction is **cost-aware LRU**: least recently used, weighted by size and by how expensive it is to bring back.

| Evict first | Keep longest |
|---|---|
| Highest mips of distant textures | Fallback mips and low LODs |
| Decoded data with a compressed copy in cache | Player, UI and critical gameplay assets |
| Assets from areas far behind the player | Whatever bots predict returns soon |
| Cheap-to-rebuild data | Expensive-to-rebuild data |

Under memory pressure, respond in order: drop `cached` → lower quality → shrink pools → reduce streaming radius → save and warn. Mobile and browser limits make this essential ([platforms](30-platforms.md)).

## Cache tiers

| Tier | Holds | Evicted by |
|---|---|---|
| VRAM | Ready GPU resources | Frame budget |
| RAM | Decoded and compressed assets | Tag budget |
| Local disk | Downloaded chunks, pipeline cache | Size limit, version |
| Package | Shipped content | Never |
| CDN | On-demand content | Release retention |
| Team and CI | Cooked artefacts | Content hash |

All tiers are **content-addressed**: same bytes, same key, so a stale entry cannot be served and patches stay small.

## Lazy code and modules

| Target | Approach |
|---|---|
| Linux, Windows, macOS, Android | Load optional shared modules on first use |
| iOS | Static link, lazy initialisation |
| Browser | Split WebAssembly and fetch on demand where supported |
| All | A system with no matching entities does not run, and optional systems initialise on first use |

## Proving it works

| Test | Passes when |
|---|---|
| **Eviction chaos mode** | Evicting everything unpinned each frame causes no crash or stale handle |
| Traversal route | No frame exceeds budget because of streaming |
| Soak | Memory returns to baseline after repeated area changes |
| Thrash | Walking a boundary does not reload continuously |
| Slow storage and network | Fallbacks show, and the game stays responsive |
| Corrupt or missing asset | Fallback plus coded error, no crash |
| Low-memory signal | The game sheds memory and survives |

`ag profile --resources` reports budgets, hit rates, load latency, evictions, reload churn and which assets were loaded but never seen.
