# Phase 7: MMO

**Proves:** persistent scale. **Depends on:** Phases 3 to 5. **Read:** [online](../idea/09-online.md), [kits](../idea/10-kits.md), [client and server models](../idea/35-client-server-models.md), [distributed servers](../idea/46-distributed-servers.md), [layers and world copies](../idea/47-layers-rejoin-replay-spectate.md).

## Build order

1. Replication layer holding entity state outside simulation servers.
2. Simulation servers as subscribers with entity authority.
3. Area-of-interest grids and static zones.
4. Entity hand-off between servers.
5. Persistence as a subscriber.
6. `economy`, `social`, instancing and phasing.
7. `kit.mmo` with a small complete game.
8. Dynamic zone splitting.

## Exit checks

- Killing a simulation server mid-session disconnects no player, and a replacement takes over.
- An entity crossing a server boundary is neither lost nor duplicated.
- Merging two world copies and thousands of layer hops lose and duplicate nothing.
- A soak test of bot clients finds no item duplication in the economy audit.
- Restarting the whole stack restores persisted world state.
