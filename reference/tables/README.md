# Reference tables

- `CENTIPEDE_RUNTIME_TOPOLOGY_DEV14.csv` — initial 32-link roles/transforms plus executable-backed split, endpoint-promotion, reform and ≤5-survivor final-phase topology metadata.
CSV tables used by the toolkit and retained for independent review. Runtime-required files include `STAGE_PAIRING.csv`, `STAGE_TILE_SETS.csv`, and `TILE_SET_TEXTURES.csv`.

Executable-derived research tables through 2.8.0-dev5:

- `ENTITY_RUNTIME_REGISTRY.csv` — five-build 0x2C runtime entity/primitive records with decoded fields and raw words.
- `ENTITY_RUNTIME_REGISTRY_BUILD_DIFF.csv` — exact-index differences between May, June, retail Xbox, and retail PS3 registries.
- `ENTITY_RUNTIME_REGISTRY_SUMMARY.json` — counts and normalized equality checks.
- `ROUTE_ANIMATION_DESCRIPTORS.csv` — two retail route-model descriptors with unresolved flag retained raw.
- `CAMERA_PRESETS_RAW.csv` — all 32 × 30 retail PS3 camera-preset words with hex/int/float views; field semantics intentionally unnamed.

- `CAMERA_PRESETS_RUNTIME.csv` — all 32 camera presets after the executable's 160 runtime initializer writes, with conservative structural field names.
- `CAMERA_PRESETS_RUNTIME_SEMANTIC.csv` — the same 32 runtime presets with dev5 evidence-backed camera/fog names and the unresolved shared material scalar retained explicitly.
- `CAMERA_PRESET_SCHEMA.csv` — per-word structural schema, consumer addresses, transition behavior, confidence, and unresolved semantic notes.

- `PA_ROUTE_BUILD_GATES.csv` — PS3 retail/Xbox retail/June 10/May 11/May 9 PA-route activation-gate comparison.
- `PA_ROUTE_FUNCTIONS.csv` — cross-build `Route::SetPaRoute`, activation-wrapper, and setup function correspondences.
- `PA_ROUTE_CAMERA_SELECTIONS.csv` — cam01/cam02 selection support and retail-activation evidence.
- `PA_ROUTE_BOSS_MAPPING.csv` — conservative Water Strider/Ultimate UFO to field-descriptor/Bmap correlations with confidence labels.
- `PA_ROUTE_BOSS_FUNCTIONS.csv` — cross-build Ultimate UFO / Water Strider executable function map.
- `WATER_STRIDER_ROUTE_SEGMENTS.csv` — retail/June/PS3 17-segment 0..1440 Water Strider course table.
- `ULTIMATE_UFO_ROUTE_PHASES.csv` — retail/June/PS3 and May prototype Ultimate UFO phase tables.

- `ULTIMATE_UFO_LATE_OBJECTS.csv` — cross-build executable identity of the late Ultimate UFO owned model used by phases 11/final-disable.

Dev12 Ultimate UFO tables:

- `ULTIMATE_UFO_PART_STATUS_OBJECTS.csv` — May 9 HUD objects and executable col/dis fields, with human role observations kept separate.
- `ULTIMATE_UFO_DEBUG_HUD.csv` — Mframe/Sframe/state offsets and debug input behavior.
- `ULTIMATE_UFO_STAGE_PROFILES.csv` — normal 5-3 vs Bonus 5-6 authored context and fast-destroy policy.
- `ULTIMATE_UFO_MFRAME_ROUTE_CHAIN.csv` — direct five-build Mframe -> fld015 route-frame setters.
- `PA_CAMERA_LIFECYCLE.csv` — retail PS3 animated cam01 -> procedural PA camera path.
- `ULTIMATE_UFO_LATE_CAMERA_GEOMETRY.csv` — real late fld015 samples evaluated with preset-4 base eye/target geometry.
- `CAMERA_PRESET_DIRECT_CALLERS_PS3.csv` — exhaustive direct callsites to retail PS3 camera preset setter `0x0015B524`; no Ultimate UFO direct caller.

Dev13 Ultimate UFO camera tables:

- `GMX_RUNTIME_MATRIX_CONVENTION.csv` — serialized GMX affine versus SgModel/runtime row-vector representation and evidence boundary.
- `ULTIMATE_UFO_CAMERA_TRANSITION_GATE.csv` — retail timed-transition gate semantics, UFO reset clear, and static direct-writer audit.
- `ULTIMATE_UFO_FINAL_VANISH_EVOLUTION.csv` — May prototype direct Vanish endpoint versus June/retail 6030/6200 split.


Dev15 mobile tables:

- `MOBILE_PACKAGE_PROVENANCE.csv` — supplied IPA/APK identifiers, declared versions, wrapper assessment, hashes, and resource-integrity boundaries.
- `MOBILE_FORMAT_LINEAGE.csv` — iOS/Android/console DAT, MAP, TZIP and generator-format comparison.
- `MOBILE_CORPUS_VALIDATION.csv` — real supplied mobile DAT/MAP corpus counts and parse results.
- `MOBILE_LEVEL9_SPLIT.csv` — six isolated Android Level-9 replacements and their terminal V2 boss opcodes.
- `MOBILE_LEVEL9_OPCODE_HANDLERS.csv` — iOS ARMv7 `analyzeScript` jump-table proof for opcodes 0x4C..0x51 and their named `set*V2` handlers.
- `MOBILE_IOS_SYMBOL_ANCHORS.csv` — retained ARMv7 mobile engine / Survival / generator symbol values.
Dev16 mobile-exclusives tables:

- `MOBILE_DELETION_V2_MAPPING.csv` — Extra 23..28 to Level-8 DELETION scripts, original Stage-3 bosses, V2 opcodes/types, and script-argument comparison.
- `MOBILE_V2_ENTITY_POOLS.csv` — exact iOS `ES_Init2(type, capacity)` pools for each original/V2 boss pair.
- `MOBILE_SURVIVAL_GRAPH.csv` — complete 36-node Survival branch graph with terminal ending mapping.
- `MOBILE_SURVIVAL_ENDINGS.csv` — terminal nodes 28..35 to ending names and achievement indices 52..59.
- `MOBILE_SURVIVAL_CONVERSION.csv` — six conditional `_checkSurvivalStage` substitutions with the status-byte meaning kept unresolved.
- `MOBILE_CHIMERA_MAPPING.csv` — six iOS Level-9 Chimera resources, mission names, crossover packs, boss opcodes, map metrics, and Android stubs.
- `MOBILE_CHIMERA_BOSS_HANDLERS.csv` — crossover constructor/entity/helper/FPS60/attack-symbol anchors.
- `MOBILE_LEVEL9_SPLIT.csv` — corrected current view of iOS Chimera content versus Android V2-based replacement stubs.
- `MOBILE_LEVEL9_OPCODE_HANDLERS.csv` — iOS `analyzeScript` dispatch proof for V2 0x4C..0x51 plus Chimera 0x52..0x54.



Dev18 iOS→console lineage tables:

- `IOS_CONSOLE_FUNCTION_LINEAGE_DEV18.csv` — iOS symbols/addresses to recovered Xbox subsystem functions, preserved behavior, changes, and confidence.
- `IOS_CONSOLE_OPCODE_FRONTIER_DEV18.csv` — mobile/June-console active opcode overlap and upper-range expansion families.
- `IOS_CONSOLE_GENERATOR_LINEAGE_DEV18.csv` — mobile/console generator corpus and 24-block architecture comparison.
- `IOS_CONSOLE_STAGE_DELTA_DEV18.csv` — decoded normal-stage 1-1..3-6 command counts, opcode-sequence similarity, record identity, and timing comparison.


Dev19 direct gameplay-code lineage tables:

- `IOS_CONSOLE_BOSS_POOL_LINEAGE_DEV19.csv` — all 30 Stage-3 subordinate pool slots and the single THE SUN 36→60 console change.
- `XBOX_BOSS_CONSTRUCTOR_EVOLUTION_DEV19.csv` — four-build constructor mnemonic-fingerprint evolution and retained May11→June10 similarity band.
- `XBOX_ENEMY_HANDLER_LINEAGE_DEV19.csv` — `0x96..0xAB` slot/name status, deliberate `0x9F` null, and known pool retunes.
- `WORLD5_BOSS_INTEGRATION_DEV19.csv` — May 9 / May 11 / June 10 / retail campaign-integration chronology for 0xA6..0xAB.
Dev20 original-boss state-machine lineage tables:

- `IOS_CONSOLE_BOSS_MOVER_LINEAGE_DEV20.csv` — direct iOS mover symbols/addresses to May 9 / May 11 / June 10 / retail Xbox / retail PS3 movers, fingerprints, and semantic anchors.
- `XBOX_BOSS_CONSTRUCTOR_EVOLUTION_DEV20.csv` — recovered exact constructor addresses, mnemonic lengths, and per-boss May11→June10 similarity values.


- `HORNET_PRISM_WALL_2.10.0-dev6.csv` — the 13 exact runtime-valid HORNET prism-wall root slots and resulting 1×A1 + 44×C0 settled formations.


Dev10 HORNET exposed-core table:

- `HORNET_EXPOSED_CORE_2.10.0-dev10.csv` — retail Xbox / June 10 Xbox / retail PS3 state-3 transition/reset anchors and the A1-only state-entry result.

Dev7 HORNET propagation table:

- `HORNET_PROPAGATION_2.10.0-dev7.csv` — every runtime-valid seed/wave, expansion type, selected indices/count and completion wave for the state-6 C0 propagation family.

Dev12 UNKNOWN tables:

- `UNKNOWN_INTERNAL_FORMS_DEV12.csv` — all 14 named `ukXX` branches, per-form real-export counts, duplicate metadata, normal-cycle reachability, and canonical visual signatures.
- `UNKNOWN_RUNTIME_CYCLE_DEV12.csv` — exact normal twelve-tick selector sequence with the `uk08` -> `uk01` visual duplicate relationship.
Dev15 GIGANTIC UFO tables:

- `GIGANTIC_UFO_RUNTIME_ATTACHMENT_MAP_DEV15.csv` — one root plus all 36 B5 child-to-`lt_001..lt_036` mappings.
- `GIGANTIC_UFO_ASSET_ROLES_DEV15.csv` — 0x9E root, three non-model 0xB4 helper slots, and 36 0xB5 weapon modules.
Dev17 SQUID tables:

- `SQUID_RUNTIME_ATTACHMENT_MAP_DEV17.csv` — all fourteen runtime records, exact modeled membership, and the retail `lt_000..lt_007` attachment pointer mapping.
- `SQUID_PHASE_TRANSITION_DEV17.csv` — retail state-8 and June 10 eight-leg disable-loop evidence.



Dev19 THE SUN tables:

- `THE_SUN_RUNTIME_ASSEMBLY_DEV19.csv` — the three evidence-bounded body/extended/wave catalogs and runtime identities.
- `THE_SUN_LONG_WAVE_LAYOUT_DEV19.csv` — exact four-group fixed-point/full-ramp B3 placement constants.
- `ALL_BOSS_RECONSTRUCTION_MATRIX_DEV20.csv` — all 18 console boss families, runtime/root model mapping, canonical catalogs, evidence grade, and fresh-retail root GMX statistics/hashes.
