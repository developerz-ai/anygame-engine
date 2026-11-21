# Phase 4: Backend

**Proves:** the Rails promise. **Depends on:** Phase 3. **Read:** [online](../idea/09-online.md), [architecture](../idea/03-architecture.md), [client and server models](../idea/35-client-server-models.md), [idea to distribution](../idea/25-idea-to-distribution.md), [distributed servers](../idea/46-distributed-servers.md), [design](../idea/41-game-and-level-design.md).

## Build order

1. `services` generated from schema.
2. `persist` with `ag db migrate`, on PostgreSQL and SQLite.
3. `jobs` on a Postgres-backed queue, plus `events` and `cache`.
4. `identity` and `matchmaking`, with trust score as an input.
5. `fleet`: local process manager, then Kubernetes/Agones.
6. `telemetry`.
7. `ag dev` runs the whole stack with hot reload.

## Exit checks

- `ag new` then `ag dev` runs client, simulation server, database and job runner on a laptop in one command.
- A schema change migrates saved data with no field dropped.
- A retried job with the same idempotency key has no second effect.
- Economy writes are ACID transactions and never travel through replicated state.
- Matchmaking starts and drains a real dedicated server.
- With every backend service down, an offline-capable game keeps playing and syncs later.
- A load test runs headless bot clients from the same game code.
