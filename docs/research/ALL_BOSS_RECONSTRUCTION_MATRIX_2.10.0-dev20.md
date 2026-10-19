# All-boss reconstruction matrix — 2.10.0-dev20

## Scope

dev20 treats the console boss roster as one audited system instead of a sequence of isolated releases. The matrix has **18 boss families**. A family is marked **deep runtime reconstruction** only when the toolkit has executable-backed multipart, phase, form, locator, or runtime-transform evidence beyond a root model. A family marked **native inspection only** has a directly proven runtime-type → root-GMX mapping and a lossless native-body inspection catalog, but no invented gameplay assembly.

## Coverage

| Boss | Runtime type | Root GMX | Canonical catalog | Coverage | Fresh retail root |
|---|---|---|---|---|---:|
| THE MOON | `0x46` | `bos_001.gmx` | `the_moon_native_body` | native inspection only | 27,504 bytes / 2 meshes / 3 bones / 0 tracks |
| THE SUN | `0x47` | `bos_002.gmx` | `the_sun_native_body` | deep runtime reconstruction | 78,016 bytes / 8 meshes / 9 bones / 6 tracks |
| GIGANTIC UFO | `0x48 / 0x9E` | `bos_003.gmx` | `gigantic_ufo_complete` | deep runtime reconstruction | 414,192 bytes / 2 meshes / 40 bones / 0 tracks |
| LADYBUG | `0x49` | `bos_004.gmx` | `ladybug_native_body` | native inspection only | 40,528 bytes / 8 meshes / 13 bones / 8 tracks |
| MANDALA | `0x4A` | `bos_005.gmx` | `mandala_initial_combat` | deep runtime reconstruction | 3,584 bytes / 1 meshes / 2 bones / 0 tracks |
| UNKNOWN | `0x4B` | `bos_006.gmx` | `unknown_all_forms` | deep runtime reconstruction | 661,760 bytes / 33 meshes / 48 bones / 0 tracks |
| CENTIPEDE | `0xA0` | `bos_007.gmx` | `centipede_initial_combat_ring` | deep runtime reconstruction | 25,264 bytes / 2 meshes / 3 bones / 0 tracks |
| HORNET | `0xA1` | `bos_008.gmx` | `hornet_full_armor` | deep runtime reconstruction | 28,736 bytes / 2 meshes / 3 bones / 2 tracks |
| PROGRESSIVE UFO | `0xA2` | `bos_009.gmx` | `progressive_ufo` | deep runtime reconstruction | 146,480 bytes / 2 meshes / 3 bones / 2 tracks |
| OCTOPUS | `0xA3` | `bos_010.gmx` | `octopus_native_body` | native inspection only | 282,400 bytes / 22 meshes / 49 bones / 12 tracks |
| BUTTERFLY | `0xA4` | `bos_011.gmx` | `butterfly_phase_1` | deep runtime reconstruction | 22,448 bytes / 2 meshes / 3 bones / 0 tracks |
| AXON | `0xA5` | `bos_012.gmx` | `axon_native_body` | deep runtime reconstruction | 172,256 bytes / 42 meshes / 75 bones / 32 tracks |
| WATER STRIDER | `0xA6` | `bos_014.gmx` | `water_strider_native_body` | native inspection only | 202,576 bytes / 16 meshes / 30 bones / 10 tracks |
| CRAB | `0xA7` | `bos_013.gmx` | `crab` | deep runtime reconstruction | 360,720 bytes / 26 meshes / 55 bones / 14 tracks |
| ULTIMATE UFO | `0xA8` | `bos_015.gmx` | `ultimate_ufo_complete` | deep runtime reconstruction | 2,268,720 bytes / 4 meshes / 40 bones / 0 tracks |
| SQUID | `0xA9` | `bos_016.gmx` | `squid_phase1_legs` | deep runtime reconstruction | 44,544 bytes / 2 meshes / 11 bones / 8 tracks |
| VERTEBRATE | `0xAA` | `bos_017.gmx` | `vertebrate_phase1_tower` | deep runtime reconstruction | 33,392 bytes / 2 meshes / 3 bones / 0 tracks |
| NO_NAME | `0xAB` | `bos_018a.gmx` | `no_name_native_body` | native inspection only | 45,728 bytes / 1 meshes / 2 bones / 1 tracks |

## dev20 additions

The five prior coverage gaps now have conservative native-body catalogs:

- `the_moon_native_body` — `0x46` / `bos_001.gmx`.
- `ladybug_native_body` — `0x49` / `bos_004.gmx`.
- `octopus_native_body` — `0xA3` / `bos_010.gmx`.
- `water_strider_native_body` — `0xA6` / `bos_014.gmx`.
- `no_name_native_body` — `0xAB` / `bos_018a.gmx`.

Each uses an identity **outer inspection transform**. This means the toolkit preserves the native GMX local coordinate system; it does **not** claim that the boss is positioned at world origin in gameplay. Native animations remain live in glTF. Fresh retail exports preserve 0/8/12/10/1 animation tracks respectively for THE MOON/LADYBUG/OCTOPUS/WATER STRIDER/NO_NAME.

## Cross-boss invariants

- Every boss family has exactly one canonical catalog key.
- All 18 canonical catalogs resolve through `gmx_assembly_template`.
- Deep reconstruction count is 13; native-inspection-only count is 5.
- `boss-matrix --root <extracted GMX folder>` validates all canonical root GMXs from fresh bytes and reports size, SHA-256, mesh count, bone count, and animation-track count.
- Complex families keep their evidence boundaries: allocation snapshots are not mislabeled as simultaneous visibility; dynamic/random families are not collapsed into fake canonical outcomes; THE SUN extended-arm and full-wave presets remain separate; UNKNOWN internal forms remain native subtrees rather than duplicated GMXs.

## Remaining research frontier

The next deep-runtime targets are the five native-inspection-only families. Their root models are now normalized and regression-tested, so future executable tracing can add state/auxiliary assemblies without changing the 18-family registry contract.

## Validation

Fresh Xbox 360 retail extraction supplied all 18 root GMXs. The five new native catalogs exported successfully with one root instance each. No proprietary GMX or generated retail glTF is bundled in the release; only derived metadata, hashes, catalog definitions, and tests are retained.
