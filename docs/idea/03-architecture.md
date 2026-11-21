# 🏛️ 3. Architecture

AnyGame is a full-stack framework: client runtime, server runtime, persistence and tooling share one kernel, one data schema and one module system.

Each layer depends only on layers below it. Tooling (CLI, live viewer, asset pipeline, agent interface) sits beside the stack and talks to every layer through the same public APIs as game code.

## The Rails idea, applied

Rails won by making the common path one command and the uncommon path possible. AnyGame copies four habits:

- **Convention over configuration.** A default project layout (`game/`, `client/`, `content/`, `server/`, `schema/`, `tests/`; see [project organisation](24-project-organization.md)). Put a component in `game/components/` and it is reflected, serialised, replicated and visible in the editor with no registration code.
- **Generators.** `ag new mygame --kit mmo`, `ag generate ability Fireball`, `ag generate service matchmaking` create working, tested code that follows house style.
- **Full stack in the box.** Client, dedicated server, database migrations, background jobs and deployment descriptors come from the same project and run locally with `ag dev`.
- **Escape hatches everywhere.** Each convention is a default module that can be replaced ([section 5](05-extending.md)).

## Platforms

| Target | Graphics backend | Notes |
|---|---|---|
| Windows | D3D12 primary, Vulkan optional | Full feature set including ray tracing |
| Linux, Steam Deck | Vulkan | Also the dedicated-server and CI platform (headless, no graphics) |
| macOS | Metal | Apple Silicon first |
| iOS | Metal | Static linking only; scripts run interpreted or ahead-of-time compiled, since iOS forbids JIT |
| Android | Vulkan | Thermal and battery governor; optional compatibility renderer for old devices |
| Consoles | Vendor APIs | Shipped as private packages under NDA; proves the platform layer is a plugin |
| Web | WebGPU + WASM | Optional package, 2D and light 3D. The kernel compiles to `wasm32` from Phase 0 ([platforms](30-platforms.md)) |

One shader source language (Slang or HLSL) cross-compiles to DXIL, SPIR-V and Metal. Three renderer tiers (mobile forward, desktop clustered, high-end virtual geometry with ray tracing) share the same materials and scene data, so one project scales from a phone to a high-end PC.
