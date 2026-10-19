# All-boss reconstruction + visual-controller matrix — 2.10.0-dev21

## Scope

dev21 keeps the dev20 18-family evidence grading and adds the corrected retail visual-controller dispatch for every boss. Retail `Function_821489F8` executes `switch(runtime_type + 1)`; caller `Function_820E7AE8` passes that same runtime type to the model-resource resolver, so the factory case is intentionally one greater than the model/runtime type.

## Matrix

| Boss | Runtime | Factory case | Controller | Size | Root GMX | Coverage | Fresh retail root |
|---|---:|---:|---|---:|---|---|---|
| THE MOON | `0x46` | `0x47` | `Function_8212B638` | `0x74` | `bos_001.gmx` | native inspection only | 27,504 B / 2 meshes / 3 bones / 0 tracks |
| THE SUN | `0x47` | `0x48` | `Function_8212BA68` | `0x138` | `bos_002.gmx` | deep runtime reconstruction | 78,016 B / 8 meshes / 9 bones / 6 tracks |
| GIGANTIC UFO | `0x9E` | `0x9F` | `Function_8211B560` | `0x228` | `bos_003.gmx` | deep runtime reconstruction | 414,192 B / 2 meshes / 40 bones / 0 tracks |
| LADYBUG | `0x49` | `0x4A` | `Function_8211EA18` | `0x80` | `bos_004.gmx` | native inspection only | 40,528 B / 8 meshes / 13 bones / 8 tracks |
| MANDALA | `0x4A` | `0x4B` | `Function_8211ED60` | `0x70` | `bos_005.gmx` | deep runtime reconstruction | 3,584 B / 1 meshes / 2 bones / 0 tracks |
| UNKNOWN | `0x4B` | `0x4C` | `Function_821300A8` | `0x254` | `bos_006.gmx` | deep runtime reconstruction | 661,760 B / 33 meshes / 48 bones / 0 tracks |
| CENTIPEDE | `0xA0` | `0xA1` | `Function_82116478` | `0x210` | `bos_007.gmx` | deep runtime reconstruction | 25,264 B / 2 meshes / 3 bones / 0 tracks |
| HORNET | `0xA1` | `0xA2` | `Function_8211E1C0` | `0x290` | `bos_008.gmx` | deep runtime reconstruction | 28,736 B / 2 meshes / 3 bones / 2 tracks |
| PROGRESSIVE UFO | `0xA2` | `0xA3` | `Function_821276D0` | `0x224` | `bos_009.gmx` | deep runtime reconstruction | 146,480 B / 2 meshes / 3 bones / 2 tracks |
| OCTOPUS | `0xA3` | `0xA4` | `Function_82123E18` | `0x28C` | `bos_010.gmx` | native inspection only | 282,400 B / 22 meshes / 49 bones / 12 tracks |
| BUTTERFLY | `0xA4` | `0xA5` | `Function_82111D28` | `0x23C` | `bos_011.gmx` | deep runtime reconstruction | 22,448 B / 2 meshes / 3 bones / 0 tracks |
| AXON | `0xA5` | `0xA6` | `Function_82110378` | `0x234` | `bos_012.gmx` | deep runtime reconstruction | 172,256 B / 42 meshes / 75 bones / 32 tracks |
| WATER STRIDER | `0xA6` | `0xA7` | `Function_821368E8` | `0x2F0` | `bos_014.gmx` | native inspection only | 202,576 B / 16 meshes / 30 bones / 10 tracks |
| CRAB | `0xA7` | `0xA8` | `Function_82119550` | `0x738` | `bos_013.gmx` | deep runtime reconstruction | 360,720 B / 26 meshes / 55 bones / 14 tracks |
| ULTIMATE UFO | `0xA8` | `0xA9` | `Function_8212DEC8` | `0x2EC` | `bos_015.gmx` | deep runtime reconstruction | 2,268,720 B / 4 meshes / 40 bones / 0 tracks |
| SQUID | `0xA9` | `0xAA` | `Function_8212A778` | `0x53C` | `bos_016.gmx` | deep runtime reconstruction | 44,544 B / 2 meshes / 11 bones / 8 tracks |
| VERTEBRATE | `0xAA` | `0xAB` | `Function_821346A0` | `0x298` | `bos_017.gmx` | deep runtime reconstruction | 33,392 B / 2 meshes / 3 bones / 0 tracks |
| NO_NAME | `0xAB` | `0xAC` | `Function_82120B50` | `0x240` | `bos_018a.gmx` | native inspection only | 45,728 B / 1 meshes / 2 bones / 1 tracks |

## Corrected THE MOON / THE SUN boundary

- THE MOON runtime `0x46` owns factory case `0x47` / `Function_8212B638`. Its setup/update pair `Function_8212B6F8` / `Function_8212B760` controls the three-node `bos_001.gmx` representation.
- THE SUN runtime `0x47` owns factory case `0x48` / `Function_8212BA68`. Its setup `Function_8212BB58` allocates the B2/B3 pools and its update path reaches `Function_8212BBF0`, so THE SUN directly owns the segmented long-wave visual.
- The six native `bos_002.gmx` tracks remain the proof for THE SUN arm extension. The correction changes the executable-controller attribution, not the recovered native animation samples or the exact 48-tile long-wave transforms.

## Five native-only targets after the parallel audit

- **THE MOON:** controller class/resource-switch behavior is traced. **Dev24 erratum:** the old “dynamic scaling” description was incorrect; retail writes material alpha (fourth component) for `collada_edge1`/`collada_face1`/`collada_face2` and applies a separate 36-degree-step Z rotation to slot 0. No outer gameplay pose is promoted.
- **LADYBUG:** setup resolves exactly four `0xB6` / `bos_004a.gmx` auxiliaries; exact attachment/visibility sequencing remains under trace.
- **OCTOPUS:** 0x28C-byte controller and `lt_000` locator use are traced; the native 22-mesh/49-bone/12-track root remains the conservative canonical representation.
- **WATER STRIDER:** corrected controller vtable directly contains the recovered 1441-frame route updater `Function_82136810`; a timed route is not collapsed into one fake static pose.
- **NO_NAME:** controller creates the `0xAB` root and large helper pools; no persistent ownership of registry `0xE5` / `bos_018.gmx` is claimed without a direct path.

## Invariants

- All 18 controller rows satisfy `factory_case = runtime_type + 1`.
- All 18 canonical root GMXs are present in the fresh retail extraction.
- Coverage remains 13 deep runtime reconstructions + 5 native-inspection-only families. Knowing a controller class is not enough to promote a boss unless membership, transforms/attachments, and state timing are recovered.
- Sealed dev19 and dev20 remain unchanged; dev21 carries the explicit erratum and corrected current metadata.
