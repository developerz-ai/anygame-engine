# ⚠️ 14. Risks

The phase order lives in [docs/build/](../build/README.md).

## Risks, stated plainly

- **Scope.** Unreal represents decades of work by a very large team. A credible plan reuses proven open-source parts behind interfaces (a Jolt-class physics library, an existing shader compiler, an audio mixer, a navmesh builder) and spends original effort on the kernel, the extension model and the kits.
- **Abstraction cost.** Interfaces at every boundary can cost performance. Mitigation: batch-oriented APIs (operate on arrays, not single objects), static linking with link-time optimisation for shipping, and budgets in CI.
- **The "generic engine" trap.** Engines without a flagship game drift into untested features. Each kit needs a real game shipped on it.
- **Determinism across compilers and CPUs** is hard for floating-point physics. Mitigation: fixed-point or software-float maths in deterministic kits, accepted performance cost.
- **Stable ABI versus evolution.** Append-only interfaces accumulate cruft. Mitigation: scheduled major versions with automated migration tools.
- **Console access** requires business agreements and cannot be open-sourced.
- **Ecosystem.** A framework wins on packages, docs and examples more than on technology. The package registry and conformance tests are as important as the renderer.

## What not to build

A new programming language, a new version-control system, a new physics solver from scratch, a new DCC tool, or a second object model beside the ECS.
