# Phase 0.04: Reflection and schema

> Phase: [Phase 0](phase-0-kernel.md). Depends on: [0.01](phase-0-01-build-ci-platform.md), [0.02](phase-0-02-memory.md).

## Goal

Annotated C++ becomes one versioned schema that drives serialisation and migrations, and old data loads with nothing dropped.

## Design source

- [Kernel: Reflection and schema](../idea/04-kernel.md).
- [Primitives](../idea/23-primitives.md): one declaration, every side.
- [Client and server models](../idea/35-client-server-models.md): field visibility classes.
- [Future-ready](../idea/22-future-ready.md): version everything that persists.
- [C++23 craft](../idea/16-cpp23-craft.md): component rules, padding and hashing.

## Files to create or change

- `tools/reflect/`: clang-based generator, a separate tool outside the kernel budget.
- `kernel/include/ag/reflect/{attributes,schema,serialize,migrate}.h`.
- `kernel/src/reflect/{schema,serialize,migrate}.cpp`.
- `cmake/AgReflect.cmake`: generates code for a target.
- `kernel/tests/reflect/*_test.cpp`, `kernel/tests/reflect/fixtures/`: stored old-version data.

## Public interface sketch

| Name | Responsibility |
|---|---|
| `[[ag::component]]`, `[[ag::event]]` | Mark reflected types |
| `[[ag::replicated(...)]]`, `[[ag::predicted]]` | Network metadata, stored only in this slice |
| `[[ag::team]]`, `[[ag::owner_only]]`, `[[ag::server]]` | Field visibility metadata |
| `[[ag::quantise(x)]]` | Wire precision metadata |
| `ag::TypeSchema`, `ag::FieldSchema` | Name, stable ID, version, type, offset, attributes |
| `ag::SchemaRegistry` | Finds schemas by name or ID |
| `ag::serialize`, `ag::deserialize` | Field-by-field, never raw struct bytes |
| `ag::register_migration` | From version, to version, transform |
| `ag::schema_to_json` | Machine-readable output for `ag describe` |

## Steps

1. Build `tools/reflect` on libclang. It reads annotated headers and writes generated C++ plus JSON. verify: a fixture header produces the expected golden JSON.
2. Make output deterministic. verify: two runs produce byte-identical files.
3. Assign stable field IDs. Renames need an explicit annotation. verify: reordering fields leaves IDs unchanged, and an unannotated rename produces a structured error.
4. Enforce the `Component` concept in generated code. verify: a component containing `std::string` fails to compile with a message naming the field.
5. Implement serialise and deserialise through the schema in little-endian form. verify: round-trip tests cover every primitive type, and padding differences do not change output.
6. Preserve unknown fields when reading newer or foreign data. verify: read then write of a fixture with an extra field keeps its bytes.
7. Implement a migration chain from any stored version to current. verify: a stored v1 fixture migrates through v2 to v3, with values asserted for every field.
8. Fail visibly on a missing migration. verify: loading a version with no path returns `AG_SCHEMA_NO_MIGRATION` and writes nothing.
9. Fuzz `deserialize`. verify: a libFuzzer target runs 60 s under ASan and UBSan with no crash.

## Must not happen

- No field silently dropped.
- No `memcpy` or `memcmp` of a whole struct for persistence or hashing.
- No runtime dependency on libclang.
- No hand-written schema for a reflected type.
- No use of C++26 reflection yet.

## Done when

- **Owns exit check:** "Loading old data runs its migration and drops no fields."
- `schema_to_json` output is stable and tested, ready for [0.08](phase-0-08-ag-cli.md).
