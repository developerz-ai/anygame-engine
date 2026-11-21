# ❓ Open questions

What is still undecided. Settled questions move to [decisions](../decisions/README.md).

## Still open

| # | Blocks | Question | Next step |
|---|---|---|---|
| 9 | Phase 3 | Slang or HLSL as the shader source? | Spike both across D3D12, Vulkan, Metal and WebGPU before the render graph |
| 13 | Each kit | What is each kit's original flagship game? | Name each sample game when its kit is planned |
| 18 | Slice 0.08 | Is the `ag` CLI written in C++23 or Bun? | Recommended: C++23, so it ships as one binary with no runtime. Slice 0.08 assumes this |
| 19 | Slice 0.01 | How does CI get the GCC 16 baseline? | Hosted runners may not include it. Slice 0.01 must pin a container or lower the baseline with evidence |

## Resolved

| # | Question | Answer |
|---|---|---|
| 1 | What are the kernel's parts? | [Decision 011](../decisions/011-kernel-scope-and-budget.md) |
| 2 | What does the 30k-line budget cover? | [Decision 011](../decisions/011-kernel-scope-and-budget.md) |
| 3 | Headers or C++ modules? | [Decision 003](../decisions/003-headers-default-modules-optin.md) |
| 4 | How strong is the determinism promise? | [Decision 012](../decisions/012-determinism-guarantee-tiers.md) |
| 5 | Is there an editor? | [Decisions 006](../decisions/006-no-gui-editor-in-core.md) and [013](../decisions/013-tooling-ships-separately.md) |
| 6 | Can a shipped game include tooling? | [Decision 013](../decisions/013-tooling-ships-separately.md) |
| 7 | Does a simple 2D solver break "no new solver"? | [Decision 014](../decisions/014-wrap-solvers-and-languages.md) |
| 8 | Does narrative need a new language? | [Decision 014](../decisions/014-wrap-solvers-and-languages.md) |
| 10 | When do the other kits land? | [Decision 015](../decisions/015-kit-and-platform-schedule.md) |
| 11 | Where do XR, web and consoles land? | [Decision 015](../decisions/015-kit-and-platform-schedule.md) |
| 12 | Is MIT final? | [Decision 007](../decisions/007-mit-no-required-services.md) |
| 14 | Do sources need links? | Added in [sources](../idea/sources.md) |
| 15 | When do quests, workshop and commerce land? | [Decision 015](../decisions/015-kit-and-platform-schedule.md) |
| 16 | How does the kernel run on WebAssembly? | [Decision 009](../decisions/009-kernel-targets-wasm32.md) |
| 17 | Should `kit.moba` join the kits? | Yes, [decision 015](../decisions/015-kit-and-platform-schedule.md) |
