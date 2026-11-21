# 🔊 40. Audio

**Audio is half of how a game feels, and it must never stall a frame or leak hidden information.** The mixer runs on its own real-time path. Gameplay sends compact commands, and every sound has a priority, a budget and a reason to exist.

Planned design as of 2026-11. Numbers are starting points, not measurements. Unlinked details are recalled and unverified. All modules are replaceable through the `audio` port ([rule 8](01-thesis.md#design-rules)). Short trick lists: [thirty years of tricks](20-tricks-30-years.md#-audio). Library licenses: [next-gen techniques](17-next-gen-techniques.md#build-vs-wrap).

## Rules

| Rule | Why |
|---|---|
| **The audio callback never blocks** | No locks, allocation, file I/O or logging, or the output crackles |
| **Gameplay talks to audio through a lock-free command queue** | Simulation and mixer stay independent |
| **Schedule on the audio clock** | Sample-accurate timing regardless of frame rate |
| **Every sound belongs to a bus and priority** | The mix stays controlled |
| **A headless server loads no audio module** | Gameplay can never depend on playback |
| **Audio events pass the visibility filter** | Sound cannot reveal hidden enemies |

## Architecture

```text
gameplay events -> sound events -> voice manager -> decoders -> spatializer -> buses -> master -> device
                                       ^                                       |
                              priority + budgets                      ducking, effects, limiter
```

| Layer | Job | Verify |
|---|---|---|
| Sound event | Data asset: clips, randomisation, routing, limits | Schema validation at cook time |
| Voice manager | Starts, steals, virtualises voices | Voice cap is never exceeded |
| Decoder | Streams or decodes on worker jobs | No file I/O on the audio thread |
| Mixer | DSP graph in fixed blocks | Callback worst case stays under budget |
| Output | Device adapter per platform | Device loss and route change recover |

**Starting adapters:** [miniaudio](17-next-gen-techniques.md#build-vs-wrap) for simple mixing and device output, [Steam Audio](https://valvesoftware.github.io/steam-audio/) (Apache-2.0) for spatial simulation, [Oboe](https://github.com/google/oboe) (Apache-2.0) for low-latency Android output. Vendor middleware fits as an external adapter.

## Mix and buses

```text
master
├── music
├── sfx
│   ├── player
│   ├── weapons
│   ├── world
│   └── ambience
├── voice
└── ui
```

| Practice | Use | Verify |
|---|---|---|
| Player sliders per major bus | Music, SFX, voice, UI | Each reaches silence |
| **Ducking** | Lower music and ambience under dialogue | Dialogue stays above target level |
| Snapshots | Menu, underwater, low health, cutscene | Transitions make no clicks |
| HDR-style priority mixing | Loudest important events duck smaller sounds | Critical cue audible in stress scene |
| Master limiter | Safety only, not the mix | Output never clips |
| Dynamic range options | Home, headphones, night, mobile | Measured for each preset |
| Mono compatibility | Important cues survive downmix | Downmix test keeps cue energy |

## Voice limiting and priority

| Control | Starting point |
|---|---|
| Real voices | 32 mobile, 64–128 desktop, tune per game |
| Per-event instance limit | 2–8 for repeated sounds |
| Cooldown between repeats | 30–100 ms for rapid events |
| Steal order | Lowest priority, then quietest, then oldest |
| Inaudible voices | Virtual: track time, consume no DSP |
| Never stolen | Dialogue, critical gameplay cues |

**Check:** a 1,000-event stress scene stays within the voice cap, DSP budget and with no missing critical cue.

## Load, stream, compress

Follows the [resource lifecycle](34-resource-lifecycle.md).

| Sound | Store | Codec default |
|---|---|---|
| Very short, frequent | In memory, decoded or ADPCM | PCM or ADPCM |
| Short to medium SFX | In memory, compressed | Vorbis or Opus, measure decode cost |
| Music and ambience | Streamed | Opus or Vorbis |
| Dialogue | Streamed, with a preloaded start | Opus |
| Voice chat | Network | [Opus](https://datatracker.ietf.org/doc/html/rfc6716) |
| Critical latency cues | Preloaded | PCM or ADPCM |

Rules: keep source WAVs in open formats, cook per platform, loop at sample-accurate points, and preload the first block of streamed sounds. **Check:** starvation test on slow storage produces no dropouts in critical buses.

## Variation

Repetition is the fastest way to make a game feel cheap.

- Several takes per event, with no immediate repeat.
- Small random pitch and volume ranges.
- Layered sounds: transient, body, tail.
- Surface-based footsteps and impacts, driven by physics material data.
- Velocity-scaled impacts with a minimum threshold.

Cosmetic randomness uses a presentation RNG, **never** the deterministic simulation RNG. **Check:** enabling audio does not change the World checksum.

## 3D audio

| Feature | Default | Upgrade | Verify |
|---|---|---|---|
| Attenuation | Authored curves per category | | Level matches curve at test distances |
| Panning | Equal-power | HRTF on headphones | Left/right test scene |
| Doppler | Off or subtle | Vehicle-specific | No pitch spikes on teleport |
| Listener | Between camera and player, per genre | | Off-screen cues stay readable |
| Occlusion | Ray casts, smoothed and amortised | Geometry-aware simulation | Wall lowers level and highs |
| Propagation | Room and portal graph | [Steam Audio](https://valvesoftware.github.io/steam-audio/) | Sound arrives through the door route |
| Reverb | Authored zones with blended sends | Baked or simulated reflections | Zone crossing has no click |
| Large sources | Rivers, crowds as areas or emitters | Instanced beds | Voice count stays bounded |

AI hearing uses the **simulation's stimulus system**, not audio playback, so results stay deterministic and work on servers.

## Music

| Technique | Use | Verify |
|---|---|---|
| Vertical layers | Add stems by intensity | Stems stay sample-aligned |
| Horizontal sections | Move between segments on bar lines | Transition lands on the planned beat |
| Stingers | Musical accent on an event | Scheduled to next valid grid point |
| Parameter-driven mix | Danger, speed, health | Changes are smoothed |
| Silence | Intentional rests | Director can request it |

## Timing and rhythm games

Under `loop.audio`, the audio clock is the game's master clock ([kernel](04-kernel.md#time-and-simulation-models)).

| Practice | Why |
|---|---|
| Convert device sample position to song time | Frame time drifts |
| Filter clock readings | Some devices report in bursts |
| Separate audio and visual offsets | Displays and headphones differ |
| Built-in tap calibration | Bluetooth latency varies widely |
| Judge input by timestamp where available | Frame timing should not decide accuracy |
| Store a per-device calibration profile | Players switch outputs |

**Check:** a loopback or simulated-clock test keeps scheduled events inside a stated sample tolerance over a long session.

## Dialogue and localisation

- Every line has a stable ID, speaker, context, emotion and max duration.
- Audio and subtitles resolve through `l10n`.
- Missing language falls back to subtitles, never silence with no text.
- Lip-sync data is generated and stored per language.
- Ducking and priority are per line.
- Subtitles support speaker names, size and background options ([coverage](11-scripting-modding-tools.md#coverage-checklist-every-area-a-shipped-game-touches)).
- AI-generated voice needs provenance and rights recorded per asset ([companions](19-companion-tools.md)).

**Check:** a localisation test confirms every line has audio or subtitles, and no subtitle overruns.

## Loudness

Measure integrated loudness with [ITU-R BS.1770](https://www.itu.int/dms_pubrec/itu-r/rec/bs/R-REC-BS.1770-5-202311-I!!MSW-E.docx) on a representative play session.

| Platform | Starting target | Peak | Evidence |
|---|---|---|---|
| Console, PC | −24 LUFS ±2 LU | −1 dBTP | [ITU report](https://www.itu.int/dms_pub/itu-r/opb/rep/R-REP-BS.2434-2018-PDF-E.pdf), [Audiokinetic](https://audiokinetic.com/en/mastering-a-game-with-wwise-part1) |
| Portable | −18 LUFS ±2 LU | −1 dBTP | Same sources |
| Mobile | −18 or −16 LUFS | −1 dBTP | **Sources disagree:** [GANG reference](https://www.audiogang.org/wp-content/uploads/2015/04/IESD-Mix-Ref-Levels-v03.02.pdf) gives −16 |

Check current platform-holder documentation before certification. `ag audio loudness` should report integrated level, range and true peak from a bot-driven capture.

## Platform constraints

Full platform rules: [platforms](30-platforms.md).

| Platform | Practice |
|---|---|
| Windows, Linux, macOS | Handle device switching and sample-rate changes |
| Android | Low-latency path through Oboe, device-specific calibration |
| iOS | Correct audio session, interruptions from calls and Siri |
| Mobile | Fewer voices, cheaper codecs, respect silent mode and battery |
| Browser | [Context starts suspended until a user gesture](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API/Best_practices), so show an audio-unlock path and [check its state](https://developer.chrome.com/blog/web-audio-autoplay) |
| Browser | Run mixing in an AudioWorklet where available, and keep a small first download |
| Consoles | Follow private platform requirements |
| All | Pause or duck when unfocused, as a setting |

## Online and fog-of-war safety

| Rule | Shape |
|---|---|
| Replicate gameplay events, not audio | The client maps an event to sound |
| **Filter sound events by visibility** | No event for an entity the player may not perceive |
| Coarsen information when hearing is allowed | Direction or region rather than exact position |
| Do not leak through timing | Hidden actions send no early packets |
| Local player sound is immediate | Predicted cosmetic feedback |
| Correct mispredicted cues | Fade or cancel without a jarring cut |
| Voice chat is a separate module | Opus, moderation and reporting |

Audited by the [packet audit](35-client-server-models.md#proof).

## Budgets

| Resource | Starting budget, per platform tier |
|---|---|
| DSP | Mobile 1–2 ms equivalent, desktop 2–4 ms |
| Audio memory | Set by tag: SFX, music buffers, voice |
| Streams | 2–4 mobile, 8+ desktop |
| Callback | Worst case well below its buffer duration |
| Device latency | Lowest stable buffer, measured per device |

## Proof

| Automated test | Passes when |
|---|---|
| Offline render | Same scripted run produces a stable reference mix within tolerance |
| Silence and clipping | No unexpected silence, no clipped samples |
| Real-time safety | Callback has zero locks, allocations and I/O in instrumented builds |
| Voice stress | Critical cues survive at the voice cap |
| Determinism | Audio on or off gives the same World checksum |
| Device change | Unplugging output recovers |
| Fog audit | No hidden-enemy sound event reaches a client |
| Loudness | Capture is inside the target range |
| Missing asset | Coded error and silence, no crash |
| Soak | No voice or memory leak over a long session |
