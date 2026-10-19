# SIIG Asset Toolkit documentation

This folder keeps the toolkit root focused on commands and launchers. No documentation or research data was removed in v2.5.1.

## Start here

- [Full-game extraction](guides/FULL_GAME_RIP.md)
- [Native asset round-trip editing](guides/NATIVE_ASSET_ROUNDTRIP.md)
- [Atlas Inspector / safe sprite editing](guides/ATLAS_EDITING.md)
- [Mod workspace / patch building](guides/MOD_WORKSPACE.md)
- [Shareable `.siigmod` packages](guides/MOD_PACKAGES.md)
- [Container inputs](guides/CONTAINER_INPUT_NOTES.md)
- [Testing](guides/TESTING.md)
- [Security](guides/SECURITY_NOTES.md)
- [Asset Viewer](guides/ASSET_VIEWER_NOTES.md)
- [BBX repacking](guides/BBX_REPACK_NOTES.md)
- [Blender add-on](guides/BLENDER_ADDON_NOTES.md)

## Format research

- [`research/AXON_RUNTIME_ASSEMBLY_2.10.0-dev18.md`](research/AXON_RUNTIME_ASSEMBLY_2.10.0-dev18.md) — exact A5 standalone body plus CA core/16-CB two-ring expanded runtime assembly and fresh-retail validation.
- [`research/SQUID_RUNTIME_ASSEMBLY_2.10.0-dev17.md`](research/SQUID_RUNTIME_ASSEMBLY_2.10.0-dev17.md) — exact A9 body + eight DA locator-attached legs, retail state-8 leg disable transition, and fresh retail export validation.
- [`research/PROGRESSIVE_UFO_CLASSIC_FORMATION_2.10.0-dev16.md`](research/PROGRESSIVE_UFO_CLASSIC_FORMATION_2.10.0-dev16.md) — executable-backed recurring state-5/state-8 classic formation, cross-checked on June 10 and retail PS3.

The [`formats/`](formats/) folder contains BBX/GMX/TEX/audio/localization/DAT/MAP/ANM/stage/shader findings.

## Project and provenance

The [`project/`](project/) folder contains credits, attribution policy, AI disclosure, source audit, exclusions, notices, and license status. Machine-readable source records are in [`../reference/provenance/`](../reference/provenance/).

## Releases and validation

- Historical release notes: [`releases/`](releases/)
- Validation reports: [`../validation/`](../validation/)
- Reference tables: [`../reference/tables/`](../reference/tables/)
- System-font support data: [`../reference/systemfont/`](../reference/systemfont/)
- Ghidra helper: [`../tools/ghidra/`](../tools/ghidra/)
- Blender add-on: [`../addons/`](../addons/)


### 2.8.0-dev9 / dev8 / dev7 / dev6 / dev5 / dev4 / dev3 route-camera, animation, and PA-route research additions

- `formats/STAGE3D_NOTES.md` — fixed-spacing and DAT-coupled executable-backed route-runtime behavior and limitations.
- `research/RUNTIME_ENTITY_CAMERA_ROUTE_RESEARCH.md` — exact non-loop route sampling and runtime camera-preset structure.
- `research/SPECIAL_STAGE_RELOAD_CHAIN_DEV10.md` — direct WARNING[12]/[14] script-to-reload mapping for Water Strider and Ultimate UFO.
- `research/ULTIMATE_UFO_DEATH_TRANSITION_DEV10.md` — HP-zero dispatch, prototype Vanish lineage, and retail late destruction phases.
- `../reference/tables/CAMERA_PRESETS_RUNTIME_SEMANTIC.csv` — executable-backed semantic camera preset table.
- `releases/RELEASE_NOTES_2.8.0-dev9.md`
- `releases/RELEASE_NOTES_2.8.0-dev8.md`
- `releases/RELEASE_NOTES_2.8.0-dev7.md`
- `releases/RELEASE_NOTES_2.8.0-dev6.md`
- `releases/RELEASE_NOTES_2.8.0-dev5.md`
- `releases/RELEASE_NOTES_2.8.0-dev4.md`
- `releases/RELEASE_NOTES_2.8.0-dev3.md`
- `../reference/tables/CAMERA_PRESETS_RUNTIME.csv`
- `../reference/tables/CAMERA_PRESET_SCHEMA.csv`

### 2.8.0-dev2 research additions

- `research/RUNTIME_ENTITY_CAMERA_ROUTE_RESEARCH.md`
- `releases/RELEASE_NOTES_2.8.0-dev2.md`
- `../reference/tables/ENTITY_RUNTIME_REGISTRY.csv`
- `../reference/tables/CAMERA_PRESETS_RAW.csv`

- `research/ULTIMATE_UFO_LATE_OBJECT_DEV11.md` — executable identity and cross-build evolution of the late Ultimate UFO owned model.

## Latest development research

- [`research/ULTIMATE_UFO_FINAL_RESET_DEV14.md`](research/ULTIMATE_UFO_FINAL_RESET_DEV14.md) — post-6200 caller audit, exact retail `+0x11C` clear condition, and excluded false leads.

- [`research/ULTIMATE_UFO_DEBUG_STATE_DEV12.md`](research/ULTIMATE_UFO_DEBUG_STATE_DEV12.md)
- [`research/ULTIMATE_UFO_STAGE_VARIANTS_CAMERA_DEV12.md`](research/ULTIMATE_UFO_STAGE_VARIANTS_CAMERA_DEV12.md)

- [`research/ULTIMATE_UFO_CAMERA_RECONSTRUCTION_DEV13.md`](research/ULTIMATE_UFO_CAMERA_RECONSTRUCTION_DEV13.md) — frame-by-frame field-camera reconstruction and late Ultimate UFO camera/vanish research.

## Mobile lineage (dev15)

- [`research/MOBILE_LINEAGE_DEV15.md`](research/MOBILE_LINEAGE_DEV15.md) — iOS/Android package provenance, TZIP/DAT/MAP lineage, generator continuity, Level-9 split, and iOS symbol anchors.
- [`releases/RELEASE_NOTES_2.8.0-dev15.md`](releases/RELEASE_NOTES_2.8.0-dev15.md)
## Mobile exclusives (dev16)

- [`research/MOBILE_V2_SURVIVAL_CHIMERA_DEV16.md`](research/MOBILE_V2_SURVIVAL_CHIMERA_DEV16.md) — DELETION/V2 boss mappings, 36-node Survival graph and eight endings, and the resolved six-stage Chimera Level-9 branch.
- [`releases/RELEASE_NOTES_2.8.0-dev16.md`](releases/RELEASE_NOTES_2.8.0-dev16.md)
## Mobile behavior (dev17)

- [`research/MOBILE_SURVIVAL_V2_BEHAVIOR_DEV17.md`](research/MOBILE_SURVIVAL_V2_BEHAVIOR_DEV17.md) — Evolution Tree-gated Survival Chimera substitutions, exact fallbacks/unlocks, original↔V2 attack-pool changes, explicit V2 mover branches, and Chimera A/B boss-argument differences.
- [`releases/RELEASE_NOTES_2.8.0-dev17.md`](releases/RELEASE_NOTES_2.8.0-dev17.md)

## 2.10.0-dev3 multipart boss assembly

- [`guides/GMX_ASSEMBLIES.md`](guides/GMX_ASSEMBLIES.md) — multi-GMX assembly workflow and direct PROGRESSIVE UFO export.
- [`research/PROGRESSIVE_UFO_RUNTIME_ASSEMBLY_2.10.0-dev3.md`](research/PROGRESSIVE_UFO_RUNTIME_ASSEMBLY_2.10.0-dev3.md) — June Xbox / retail Xbox / retail PS3 evidence for the five-part runtime formation.
- [`releases/RELEASE_NOTES_2.10.0-dev3.md`](releases/RELEASE_NOTES_2.10.0-dev3.md)
- [`../reference/tables/PROGRESSIVE_UFO_RUNTIME_ASSEMBLY_2.10.0-dev3.csv`](../reference/tables/PROGRESSIVE_UFO_RUNTIME_ASSEMBLY_2.10.0-dev3.csv) — machine-readable instance transforms and evidence anchors.

- `research/THE_SUN_RUNTIME_ASSEMBLY_2.10.0-dev19.md` — THE SUN internal arm animation, corrected 0x47/0x48 ownership, and exact 48-segment B3 long-wave reconstruction.
- `research/ALL_BOSS_RECONSTRUCTION_MATRIX_2.10.0-dev20.md` — unified 18-family boss registry and reconstruction evidence grades.
