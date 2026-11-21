# 🧭 42. UX, accessibility and localisation

**Every player should be able to understand, control and enjoy the game.** These are cheapest when designed in from the first screen, and expensive to retrofit. The engine's UI, input and text blocks should make the good path the default.

Guidance as of 2026-11-21. Linked claims were checked from search extracts. Unlinked numbers are recalled starting points and unverified. Guidelines help but do not replace testing with disabled players and native speakers. Defaults can be overridden ([rule 8](01-thesis.md#design-rules)).

Related: [UI modding](11-scripting-modding-tools.md), [tricks](20-tricks-30-years.md), [idea to distribution](25-idea-to-distribution.md), [quality bar](32-quality-bar.md), [game design](41-game-and-level-design.md).

## UI hierarchy

Show what the player needs now, in order of urgency.

| Level | Content | Treatment |
|---|---|---|
| Critical | Death risk, incoming attack, objective failure | Immediate, multi-sensory |
| Active | Health, ammo, cooldowns, current goal | Always readable |
| Contextual | Interaction prompts, nearby items | Appears when relevant |
| Reference | Map, inventory, stats | On request |
| Ambient | Flavour and world detail | Never competes with play |

## HUD rules

| Rule | Why |
|---|---|
| Keep critical data near the player's focus | Fewer eye movements |
| Prefer in-world cues when clear | Less clutter |
| Do not rely on colour alone | Accessibility |
| Support safe zones and all aspect ratios | TVs, ultrawide, notched phones |
| Scale UI independently of render resolution | Readable on every display |
| Let players move, resize or hide elements | Personal comfort |
| Animate state changes briefly | Change is noticed without delay |

## Menus and navigation

| Rule | Shape |
|---|---|
| Every screen has a clear back action | Same input everywhere |
| Works fully on each supported input | No mouse-only menu in a controller game |
| Focus is always visible | Controller and keyboard users |
| Focus is restored on return | Do not lose the player's place |
| Destructive actions confirm | Delete save, quit unsaved, spend money |
| Settings apply with preview | No restart unless truly required |
| Fast paths | Continue is the first option for returning players |

## First-time experience

1. Boot quickly to something interactive.
2. Ask only what is essential: language, then comfort and accessibility.
3. Detect sensible graphics and input defaults.
4. Start playing, and teach in context ([onboarding](41-game-and-level-design.md#onboarding-teach-through-play)).
5. Never require an account unless the game truly needs one.

## Settings every game should have

| Category | Settings |
|---|---|
| Display | Resolution, window mode, refresh, frame cap, VSync, HDR, brightness |
| Graphics | Presets, individual options, upscaler, render scale |
| Audio | Master, music, effects, voice, UI, mono, mute on background |
| Controls | Full remapping, sensitivity, invert axes, dead zones, vibration, hold or toggle |
| Interface | UI scale, text size, subtitles, HUD options, language |
| Accessibility | See below, reachable from the first launch |
| Gameplay | Difficulty, assists, camera options |
| Online | Voice, chat filters, block and report, privacy, crossplay |
| Data | Telemetry consent, cloud saves, export, delete |

Settings persist per device or profile, survive updates, and have a reset to defaults.

## Input

| Device | Requirements |
|---|---|
| All | Action-based input. Game code never reads a raw key |
| Keyboard and mouse | Full rebinding, raw mouse input, multiple bindings |
| Controller | Dead zones, glyphs per device, hot-swap, disconnect pauses safely |
| Touch | Large targets, reachable thumb zones, custom layout, no hover-dependent UI |
| Mixed | Prompts follow the last used device |
| Remapping | [In game, for all controls](https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/107), with presets and conflict handling |

## States players should never have to guess

| State | What to show |
|---|---|
| Loading | Progress or activity, with a useful tip |
| Saving | Indicator, and when it is safe to quit |
| Offline | What still works, and retry |
| Server down | Plain explanation, status link, next step |
| Update required | Size, reason and progress |
| Purchase pending | Status, never a second charge |
| Empty list | What it means and what to do |
| Error | What happened, what to do, and a support code |

Never show raw exception text to players. Coded errors map to localised messages.

## Saves

| Rule | Why |
|---|---|
| Autosave often, with visible feedback | Lost progress is the worst bug |
| Write atomically, and keep backups | Crash or power loss cannot destroy a save |
| Show playtime, location, date and thumbnail | Easy to identify |
| Warn before overwrite | Prevent accidents |
| Old saves load after updates | [No regrets](31-no-regrets.md) |
| Handle cloud conflicts clearly | Show both versions and let the player choose |
| Save on suspend on mobile and in the browser | The OS may kill the game |

## Multiplayer UX

| Moment | Requirements |
|---|---|
| Matchmaking | Estimated wait, cancel, party status |
| Connection | Ping, packet-loss indicator, region choice |
| Disconnect | Automatic reconnect, clear countdown |
| Teammate leaves | Explain what happens next |
| Communication | Pings and quick chat for players without voice |
| Safety | Mute, block, report, chat filter, privacy defaults |
| End of match | Clear result, why, rewards, requeue |
| Fair-play status | Visible and appealable ([online](09-online.md)) |

## Accessibility

Use the [Game Accessibility Guidelines](https://gameaccessibilityguidelines.com/full-list/), organised into [Basic, Intermediate and Advanced](https://gameaccessibilityguidelines.com/basic/), and the [Xbox Accessibility Guidelines](https://learn.microsoft.com/en-us/xbox/accessibility/guidelines). The basic tier names remapping, text size, colour-blindness and subtitle presentation as the most commonly raised issues.

**AnyGame default:** new kits should satisfy the GAG Basic tier out of the box, wherever it applies.

### Baseline targets

| Area | Target | Source |
|---|---|---|
| Text contrast | 4.5:1 standard, 3:1 large, 7:1 high contrast mode | [XAG 102](https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/102) |
| Subtitles | All important speech, with speaker identification available | [GAG](https://gameaccessibilityguidelines.com/provide-subtitles-for-all-important-speech/), [XAG overview](https://learn.microsoft.com/en-us/xbox/accessibility/guidelines) |
| Subtitle layout | At least 46 px at 1080p, background, up to 40 characters per line | [GAG](https://gameaccessibilityguidelines.com/if-any-subtitles-captions-are-used-present-them-in-a-clear-easy-to-read-way/) |
| Remapping | Presets plus full custom remapping, in game | [GAG](https://gameaccessibilityguidelines.com/allow-controls-to-be-remapped-reconfigured/) |
| Audio cues | Important cues replicated in text or visuals | [GAG](https://gameaccessibilityguidelines.com/ensure-that-all-important-supplementary-information-eg-the-direction-you-are-being-shot-from-conveyed-by-audio-is-replicated-in-text-visuals/) |
| Screen narration | On-screen information available aurally, cancel and repeat | [XAG 106](https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/106) |

### Design by need

| Need | Provide |
|---|---|
| **Vision** | Text scale, high contrast, colour-blind-safe cues, icons plus colour, narration, audio navigation |
| **Hearing** | Subtitles, captions for sound effects, visual direction indicators, mono audio |
| **Motor** | Remapping, hold or toggle, no required rapid tapping, one-handed presets, aim assist, adjustable timing |
| **Cognitive** | Clear goals, objective reminder, adjustable speed, simple language, skip and replay of tutorials |
| **Photosensitivity** | Avoid flashing patterns, offer effect reduction, test before release |
| **Motion comfort** | Camera shake toggle, motion blur off, FOV, reduced head bob, static reference points |
| **Mental wellbeing** | Content warnings, ability to skip distressing scenes, no manipulative pressure |

### Difficulty assists

Independent toggles rather than one easy mode:

| Assist | Example |
|---|---|
| Timing | Slower game speed, longer input windows |
| Combat | Damage scale, aim assist, auto-dodge option |
| Navigation | Objective marker, path hint |
| Puzzle | Hints, skip after repeated failure |
| Progression | Skip a section |

Do not shame players for using assists. Competitive modes may restrict those that affect fairness, and state why.

### Screen reader path

- UI widgets expose role, label, value and state from the schema.
- Focus changes are announced.
- Menus are fully navigable without vision.
- Use platform text-to-speech through an adapter.
- Gameplay narration needs game-specific design and testing with blind players.

## Localisation

### String pipeline

```text
source string + context + screenshot -> extract -> translation provider
      -> import -> validate placeholders, length, glyphs -> cook per locale -> screenshot test
```

| Rule | Why |
|---|---|
| **No user-facing text in code** | String IDs from day one |
| **Never concatenate sentences** | Word order differs |
| **Named placeholders** | Translators can reorder them |
| **Context for each string** | "Close" the door or "close" the menu |
| **Stable IDs, version on meaning change** | Translations stay valid |
| **Dates, numbers and currency by locale** | Formatting differs |
| **Text in images is avoided** | Costly to localise |
| **Voice and subtitles share IDs** | Stay aligned |

### Plurals and gender

Use [ICU MessageFormat](https://unicode-org.github.io/icu/userguide/format_parse/messages/) with [CLDR plural rules](https://unicode.org/reports/tr35/tr35-numbers.html). Languages can use the categories zero, one, two, few, many and other, so English singular/plural logic is wrong in general.

```text
{count, plural, one {# enemy remains} other {# enemies remain}}
{target_gender, select, female {She wins} male {He wins} other {They win}}
```

Prefer gender-neutral phrasing where possible, and let translators add the forms each language needs.

### Layout and text

| Area | Rule |
|---|---|
| Text expansion | Layouts flex. Plan for strings much longer than English, especially short labels |
| Right-to-left | Mirror layout, use bidirectional text shaping, and keep media controls and numbers correct |
| Shaping | Use a shaping engine for Arabic, Indic and other complex scripts |
| CJK | Large glyph sets, on-demand font atlases, line-breaking rules |
| Fonts | Fallback chain, per-locale font, licence covers embedding |
| Size | Ship or download only the player's languages and voice packs |
| Input | Support IME for names and chat |
| Sorting and search | Use locale-aware collation |

### Pseudo-locale

Run every build through a generated locale that accents characters, lengthens strings, and wraps them in markers. It exposes hard-coded text, clipping, broken placeholders and missing glyphs before any translator is paid.

### Culture checks

Review symbols, gestures, colours, maps, borders, historical references, humour, age ratings and legal requirements per market. **A native human reviewer signs off on any shipped language.** Machine translation is acceptable for drafts and pseudo-review, and should be disclosed if shipped unreviewed.

## Automated checks

`ag check ux`, `ag check accessibility` and `ag check l10n` are planned. They report findings as advice by default, and a game can make them release gates.

| Check | Finds |
|---|---|
| Contrast scan on UI captures | Text below target |
| Text-size check at reference resolutions | Text too small |
| Safe-zone and aspect-ratio screenshots | Clipped or off-screen UI |
| Focus traversal bot | Unreachable or trapped controls |
| Input-device sweep | A menu impossible on one device |
| Rebinding test | Conflicts, or actions that cannot be remapped |
| Colour-vision simulation | Information carried by colour alone |
| Flash and luminance scan on capture | Potentially unsafe flashes, as a warning needing specialist review |
| Subtitle coverage | Voice lines without subtitles |
| Audio-cue coverage | Gameplay cues without a visual equivalent |
| Hard-coded string lint | User-facing text outside the string table |
| Placeholder and ICU validation | Broken translations |
| Pseudo-locale screenshot diff | Overflow, clipping, missing glyphs |
| Right-to-left capture | Unmirrored layout |
| Error-state tests | Offline, server down, failed purchase, corrupt save |
| Save interruption test | Crash during save loses nothing |

## What still needs people

| Decision | Who |
|---|---|
| Whether an accessibility feature truly works | Disabled players |
| Whether a translation is natural and respectful | Native speakers |
| Whether the UI feels clear under pressure | Human playtesters |
| Photosensitivity sign-off where required | Qualified review |
| Legal and ratings compliance | The responsible person |
