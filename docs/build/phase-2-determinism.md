# Phase 2: Determinism

**Proves:** the snapshot and determinism design. **Depends on:** Phases 0 and 1, [decision 012](../decisions/012-determinism-guarantee-tiers.md). **Read:** [kernel](../idea/04-kernel.md), [online](../idea/09-online.md), [kits](../idea/10-kits.md), [replays and rejoin](../idea/47-layers-rejoin-replay-spectate.md), [mechanics](../idea/37-gameplay-mechanics.md).

## Build order

1. `loop.deterministic` with the chosen maths mode and ordered jobs.
2. Input log, `replay`, and nightly checksum test.
3. `net.rollback`.
4. `kit.fighting` with a small complete game.
5. `net.lockstep`, flow fields, fog of war.
6. `kit.rts` with a small complete game.

## Exit checks

- A recorded match replays to an identical final checksum on every platform the guarantee covers.
- Rollback re-simulation fits inside the frame budget at the kit's maximum rollback window.
- A lockstep desync is detected and reports the first divergent tick.
- A server re-simulates an input log and rejects a tampered result.
- Both kit games are playable online between two machines.
