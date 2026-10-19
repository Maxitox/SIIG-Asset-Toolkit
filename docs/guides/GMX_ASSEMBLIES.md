# Multi-GMX assemblies (2.10.0-dev18)

Some SIIG runtime objects are assembled from several separate GMX resources. `gmx-assemble` combines explicit GMX instances into one glTF scene without claiming that the game stores those instances as one native GMX.

## Built-in evidence-backed catalogs

### MANDALA initial combat — `mandala_initial_combat`

Dev8 reconstructs MANDALA at the exact state-7 activation instant before the first rotational update. The visible composition is **20×B7 + 2×B8 + 2×B9 + 2×BA + 2×BB + 12×4A = 40 instances**. The later 32×BC inner phase is intentionally excluded.

The transform math is cross-checked across May 9 Xbox, May 11 Xbox, June 10 Xbox, retail Xbox and retail PS3. Native GMX animations are preserved and no speculative radial-facing rotation is added. See `docs/research/MANDALA_RUNTIME_ASSEMBLY_2.10.0-dev8.md`.

### PROGRESSIVE UFO — `progressive_ufo`

The executable-backed five-object formation remains:

| model | runtime | local translation | outer local rotation |
|---|---|---|---|
| `bos_009.gmx` | `0xA2` | `(0,0,0)` | `(0,0,0)` |
| `bos_009a.gmx` | `0xC2` | `(-90,0,-10)` | `(0,0,0)` |
| `bos_009a.gmx` | `0xC2` | `(90,0,-10)` | `(0,0,0)` |
| `bos_009b.gmx` | `0xC3` | `(-160,0,-50)` | `(0,0,0)` |
| `bos_009b.gmx` | `0xC3` | `(160,0,-50)` | `(0,0,0)` |

The slight visible tilt of both barrier machines is authored **inside `bos_009b.gmx`** (about 190.794° Z on both barrier mesh bones), not an assembly-matrix error. See `docs/research/PROGRESSIVE_UFO_BARRIER_ORIENTATION_2.10.0-dev5.md`.

```bat
python siig_toolkit.py gmx-assemble-catalog progressive_ufo --root extracted_gmx -o progressive_ufo.gltf
```

### PROGRESSIVE UFO classic formation — `progressive_ufo_classic`

Dev16 adds the separately named recurring pose used by retail major states 5 and 8. The original `progressive_ufo` catalog above is unchanged. The classic preset keeps the same A2+C2+C2+C3+C3 membership but uses the executable's second pose table, including exact outer rotations:

| model | local translation | runtime Euler XYZ (radians) |
|---|---|---|
| `bos_009.gmx` | `(0,0,0)` | `(π,0,0)` |
| `bos_009a.gmx` | `(-78.5,0,5)` | `(0.0610865,0,1.4049901)` |
| `bos_009a.gmx` | `(78.5,0,5)` | `(0.0610865,0,-1.3962635)` |
| `bos_009b.gmx` | `(115,0,3)` | `(0,0,1.7453293)` |
| `bos_009b.gmx` | `(-115,0,3)` | `(0,0,-1.7453293)` |

```bat
python siig_toolkit.py gmx-assemble-catalog progressive_ufo_classic --root extracted_gmx -o progressive_ufo_classic.gltf
```

See `docs/research/PROGRESSIVE_UFO_CLASSIC_FORMATION_2.10.0-dev16.md`.

### CRAB — `crab`

The default CRAB catalog now represents the deterministic **landed/combat-ready** state. It contains `A7 + CD + CC + 2×CE + 4×CF`.

A7 is baked at native sample **1**, the first sample of its looping landed combat segment. CD is baked at sample 0. Child placement comes from the runtime named-locator path. This avoids the hundreds-of-units-high first-visible intro snapshot while preserving native coordinates; nothing is manually recentered.

The old dev4 state remains available as `crab_first_visible`: A7 sample 167 while the boss is still airborne during its entrance.

```bat
python siig_toolkit.py gmx-assemble-catalog crab --root extracted_gmx -o crab.gltf
python siig_toolkit.py gmx-assemble-catalog crab_first_visible --root extracted_gmx -o crab_first_visible.gltf
```

See `docs/research/CRAB_RUNTIME_ASSEMBLY_2.10.0-dev5.md` and the preserved dev4 report.

### HORNET full armor — `hornet_full_armor`

HORNET uses one A1 core plus a runtime pool of **125 BF armor cubes**, **125 C0 prism objects**, and one meshless **C1 formation rig**. C1 sample 0 provides an exact 5×5×5 locator lattice at axis levels ±31.68, ±15.84 and 0.

The beginner preset exports the deterministic fully revealed armor state as **126 visible instances: A1 + 125 BF**. C1 has no mesh and therefore is not added as a useless visible root. The C0 pool is real but dormant in this state. Dev6 separately reconstructs its 45-cell prism-wall attack as a 13-variant runtime family.

```bat
python siig_toolkit.py gmx-assemble-catalog hornet_full_armor --root extracted_gmx -o hornet_full_armor.gltf
```

See `docs/research/HORNET_RUNTIME_ASSEMBLY_2.10.0-dev5.md`.

### HORNET exposed core — `hornet_exposed_core`

Dev10 proves a real A1-only **high-level state-3 entry**. On transition, the common reset restores `bos_008.gmx` at native motion 0/sample 0 and writes all 125 subordinate placement records to state `-1`; the normal selection logic therefore chooses neither BF armor nor C0 prisms at this exact boundary. C1 is a meshless control rig and is not emitted as visible geometry.

```bat
python siig_toolkit.py gmx-assemble-catalog hornet_exposed_core --root extracted_gmx -o hornet_exposed_core.gltf
```

The state/reset structure is independently present in retail Xbox, June 10 Xbox and retail PS3. Fresh real-retail validation from the re-uploaded Xbox package produced 1 instance, 2 meshes, 4 glTF nodes and native bounds about ±13.8054. The preset is intentionally the deterministic state-entry snapshot; it does not claim A1 remains frozen at sample 0 during the whole attack. See `docs/research/HORNET_EXPOSED_CORE_2.10.0-dev10.md`.

### HORNET prism wall — `hornet_prism_wall_XX`

The C0 prism-wall state uses an exact 5×9 grid with 46-unit spacing. The game randomly places A1 into one of exactly 13 valid cells and suppresses that cell's C0 child. Therefore each settled visible variant is **A1 + 44×C0**, not A1 + 45×C0.

Valid suffixes are: `00`, `02`, `06`, `08`, `18`, `20`, `22`, `24`, `26`, `36`, `38`, `42`, `44`. There is deliberately no unqualified `hornet_prism_wall` preset because choosing one random retail result as canonical would be arbitrary.

```bat
python siig_toolkit.py gmx-assemble-catalog hornet_prism_wall_22 --root extracted_gmx -o hornet_prism_wall_22.gltf
```

A1's native animation remains live in this assembly because the runtime still loops its own `0→20` clip while occupying the wall cell. The 44 C0 outer transforms are static identity-rotation/unit-scale grid placements. Advanced GUI exposes the same 13-slot selector; Simple mode intentionally keeps the deterministic full-armor preset instead.

See `docs/research/HORNET_PRISM_WALL_2.10.0-dev6.md`. Dev7 resolves the following state-6 propagation separately; it is not folded into the settled wall.

### HORNET propagation — `hornet_propagation_SS_wave_WW`

State 6 inherits one of the same 13 prism-wall seeds, hides A1, and reveals C0 prisms in deterministic waves over the 5×9 grid. Wave 0 is the inherited seed only; wave 1 expands orthogonally; wave 2 diagonally; later waves alternate until all 45 cells are visible.

```bat
python siig_toolkit.py gmx-assemble-catalog hornet_propagation_22_wave_03 --root extracted_gmx -o hornet_propagation_22_wave_03.gltf
```

The snapshot is the wave activation instant: reached C0s only, zero extra Y rotation, no A1 and no laser/effect geometry. Valid wave ranges depend on the seed. There is deliberately no unqualified default. Advanced GUI exposes explicit seed/wave controls. See `docs/research/HORNET_PROPAGATION_2.10.0-dev7.md`.

## VERTEBRATE structural phases

VERTEBRATE's persistent body is separate from its transient attack rigs. Dev13 exposes two exact structural presets:

- `vertebrate_phase1_tower` — 2× `bos_017.gmx` endcaps + 30× `bos_017a.gmx` pillars. Pillars use `Y=-630+70*i` for `i=0..29`; the lower cap is at `Y=-608`, Z=180°, and the upper cap at `Y=1448`.
- `vertebrate_phase2_endcaps` — after the 120-frame collapse, all pillars are gone and the two endcaps are co-located at the boss-local origin with effective Z rotations 90° and 270°.

```bat
python siig_toolkit.py gmx-assemble-catalog vertebrate_phase1_tower --root extracted_gmx -o vertebrate_phase1_tower.gltf
python siig_toolkit.py gmx-assemble-catalog vertebrate_phase2_endcaps --root extracted_gmx -o vertebrate_phase2_endcaps.gltf
```

`bos_017b..j.gmx` are deliberately excluded from these body presets: runtime behavior treats them as separate attack auxiliaries, and fresh retail inspection shows `bos_017c..j` carry 22–25 native animation tracks each. See `docs/research/VERTEBRATE_RUNTIME_ASSEMBLY_2.10.0-dev13.md`.

## SQUID structural phases

SQUID has two exact modeled states. `squid_phase1_legs` contains one animated `bos_016.gmx` A9 body and eight static `bos_016a.gmx` DA legs parented to native body locators `lt_000..lt_007`. `squid_phase2_body` represents retail state 8 and later after the runtime disables leg records 1–8; the A9 body remains active.

```bat
python siig_toolkit.py gmx-assemble-catalog squid_phase1_legs --root extracted_gmx -o squid_phase1_legs.gltf
python siig_toolkit.py gmx-assemble-catalog squid_phase2_body --root extracted_gmx -o squid_phase2_body.gltf
```

The phase-1 legs use identity local matrices under their exact named locators, so all eight native body animation clips remain live. Non-GMX runtime records 9–13 are intentionally excluded. See `docs/research/SQUID_RUNTIME_ASSEMBLY_2.10.0-dev17.md`.

## THE SUN runtime forms

Dev24 exposes four evidence-bounded THE SUN inspection/export presets and an exact controller sampler:

- `the_sun_opening_full_barriers` — the exact synchronized end-of-opening state: `bos_002.gmx` at native clip 0/frame **0** plus all **48** `0xB3` / `bos_002b.gmx` player-protection barriers.
- `the_sun_native_body` — retail `0x47` / `bos_002.gmx` at identity outer transform with its six native arm tracks preserved.
- `the_sun_extended_arms` — the same body with exact native logical sample **40** baked. Retail proves this frame belongs to the later state-9/state-10 extension/hold path, not to the opening barrier ramp.
- `the_sun_protection_barriers` — the exact 48-slot B3 field by itself: four groups of twelve at X `69,165,261,357` and Z `176..198` in steps of 2. Legacy alias `the_sun_long_wave` remains accepted for compatibility.

```bat
python siig_toolkit.py gmx-assemble-catalog the_sun_opening_full_barriers --root extracted_gmx -o the_sun_opening.gltf
python siig_toolkit.py gmx-assemble-catalog the_sun_native_body --root extracted_gmx -o the_sun_native.gltf
python siig_toolkit.py gmx-assemble-catalog the_sun_extended_arms --root extracted_gmx -o the_sun_extended.gltf
python siig_toolkit.py gmx-assemble-catalog the_sun_protection_barriers --root extracted_gmx -o the_sun_barriers.gltf
python siig_toolkit.py the-sun-controller --frame-multiplier 1
```

The synchronization is now executable-backed. Root state 0 grows the B3 field from 0 to 48 members over 12 authored base updates while `Function_8212BE00` forces the body to clip 0/frame 0. Body interpolation occurs only in states 9/10/11: progress advances by `0x600` to a `0x16900` clamp over 61 updates, holds at native frame 40 for 60 base updates, then retracts over 61 updates. June 10 independently retains the same law.

Individual barrier survival after gameplay damage remains live state and is not frozen into the static opening preset. See `reference/research/THE_SUN_CONTROLLER_TIMING_DEV24.md`; the older `docs/research/THE_SUN_RUNTIME_ASSEMBLY_2.10.0-dev19.md` remains historical evidence for the earlier conservative boundary.

## AXON runtime forms

AXON has two executable-level visual representations that must not be stacked together. Retail `Function_8210D808` creates one standalone A5 / `bos_012.gmx` whole-body model, and separately creates a 17-record subordinate pool containing one CA / `bos_012a.gmx` core plus sixteen CB / `bos_012b.gmx` petals.

Dev18 exposes three inspection/export presets:

- `axon_native_body` — the standalone animated A5 whole-body representation.
- `axon_expanded_petals` — CA core + all sixteen CB petals at the stable expanded target, frozen at runtime phase angle 0.
- `axon_exposed_core` — the CA weak-spot/core model alone for exposed-core inspection.

The expanded form is fully executable-derived. The sixteen CB records form two rings of eight. Ring 1 uses table angles `0,45,...,315`, radius 75 and Y offset -3.0. Ring 2 is staggered by 22.5 degrees, uses radius 220 and Y offset -5.5. Retail stores each runtime angle as the negative of the table angle; at phase 0 the visual update computes `X = radius*sin(runtime_angle)`, `Z = radius*cos(runtime_angle)`, and Y rotation `-90-runtime_angle`.

```bat
python siig_toolkit.py gmx-assemble-catalog axon_native_body --root extracted_gmx -o axon_native.gltf
python siig_toolkit.py gmx-assemble-catalog axon_expanded_petals --root extracted_gmx -o axon_expanded.gltf
python siig_toolkit.py gmx-assemble-catalog axon_exposed_core --root extracted_gmx -o axon_core.gltf
```

Fresh retail validation produces 1/17/1 instances, 42/34/2 meshes, 76/84/20 nodes and 32/0/0 native animations respectively. See `docs/research/AXON_RUNTIME_ASSEMBLY_2.10.0-dev18.md`.

## ULTIMATE UFO complete hierarchy + activity subsets

ULTIMATE UFO is a locator-driven hierarchy rather than a flat set of hard-coded XYZ offsets. `ultimate_ufo_complete` exports all **126 model instances allocated by the retail constructor** at the constructor baseline. That catalog is deliberately an allocation/hierarchy view, not a claim that every phase-gated member is simultaneously rendered. Eight `ultimate_ufo_state_XX` catalogs (`02`, `03`, `06`, `07`, `08`, `09`, `11`, `12`) are controller-activity subsets derived from the retail col/dis phase table.

The runtime hierarchy is resolved from exact named GMX nodes: D5 under A8 `lt_002..003`, D4 under A8 `lt_004..024`, D6 under the D0/D1 FAN parents at `lt_226..257`, and D7 under the D2/D3 RING parents at `lt_258..321`. The assembly exporter reparents child containers to those source-GMX locator nodes so parent animation remains live. Missing or ambiguous locators are errors.

```bat
python siig_toolkit.py gmx-assemble-catalog ultimate_ufo_complete --root extracted_gmx -o ultimate_ufo_complete.gltf
python siig_toolkit.py gmx-assemble-catalog ultimate_ufo_state_06 --root extracted_gmx -o ultimate_ufo_state_06.gltf
```

State 9 uses D9 / `bos_015l.gmx` for the core/weak-spot assembly. States 11 and 12 use D8 / `bos_015k.gmx` for the late airlock object. The retail/June ID mapping must not be confused with older May prototype IDs. See `docs/research/ULTIMATE_UFO_RUNTIME_ASSEMBLY_2.10.0-dev9.md`.

## All-boss registry and matrix

The console boss roster is one 18-family registry, and dev24 reports three evidence grades: **14 deep runtime reconstructions**, **3 gameplay-pose reconstructions**, and **1 native-inspection-only** family.

OCTOPUS (`octopus_retail_spawn`) and WATER STRIDER (`water_strider_retail_spawn`) use exact authored retail root placement `(213,0,100)`. NO_NAME uses `no_name_retail_main_spawn` at `(213,0,120)` and also exposes `no_name_extra2_stage8_approach`, an exact controller-backed Extra 2-8 move from `(213,0,-100)` to `(213,0,80)`. These three are intentionally classified as gameplay-pose rather than deep multipart reconstruction: native articulation remains live, but no unowned auxiliary GMX is invented. WATER STRIDER's separate `fld014` PA-route also remains a separate stage-field system.

THE MOON (`the_moon_native_body`) is the sole native-inspection-only family. Its identity outer matrix preserves GMX-local inspection space and does **not** assert gameplay world placement because the authored command contains no root X/Z and the traced visual state is controller-internal. Historical native-body catalogs for the promoted families remain available as conservative inspection fallbacks.

Generate the matrix without game data:

```bat
python siig_toolkit.py boss-matrix -o boss_matrix.json
```

Validate canonical roots against an extracted GMX tree:

```bat
python siig_toolkit.py boss-matrix --root extracted_gmx -o boss_matrix.csv
```

A root-backed matrix records presence, byte size, SHA-256, mesh count, bone count, and native animation-track count for all 18 bosses. See `docs/research/ALL_BOSS_RECONSTRUCTION_MATRIX_2.10.0-dev20.md`.

## Writing or editing manifests

Every catalog can be written as editable JSON first:

```bat
python siig_toolkit.py gmx-assembly-template progressive_ufo -o progressive_ufo.assembly.json
python siig_toolkit.py gmx-assembly-template crab -o crab.assembly.json
python siig_toolkit.py gmx-assembly-template hornet_full_armor -o hornet.assembly.json
python siig_toolkit.py gmx-assembly-template hornet_exposed_core -o hornet_exposed.assembly.json
python siig_toolkit.py gmx-assembly-template hornet_prism_wall_22 -o hornet_prism_wall_22.assembly.json
python siig_toolkit.py gmx-assembly-template ultimate_ufo_state_06 -o ultimate_ufo_state_06.assembly.json
python siig_toolkit.py gmx-assembly-template vertebrate_phase1_tower -o vertebrate_phase1_tower.assembly.json
python siig_toolkit.py gmx-assemble hornet.assembly.json --root extracted_gmx -o hornet.gltf
```

Each instance uses a standard 16-value glTF column-major local-to-assembly matrix. Native GMX POSITION XYZ values and units are preserved; the exporter does not silently rescale bosses or reinterpret SIIG units as meters.

### Blender viewing note

SIIG boss models can be very large in their **native game units**. That is intentional. If a model is outside the current Blender view, use **Home / Frame All**, or select the boss root and use **Numpad `.` / Frame Selected**. Do not scale the authoritative assembly just to make navigation convenient unless you intentionally want a display-only copy.

## `pose_sample`

An assembly instance may include optional non-negative `pose_sample`. The exporter bakes that native GMX logical animation sample into the instance node hierarchy and deliberately omits that instance's animation channels from the combined static snapshot. An out-of-range sample is a hard error.

This is used when a multipart state depends on animated attachment nodes, such as CRAB and HORNET's A1 core sample.

## Evidence boundary

Unknown transforms remain hard errors. Built-in catalogs represent specific documented runtime states only; they do not claim that SIIG stores merged boss GMXs, nor that dynamic later phases are equivalent to those snapshots. Native scale is preserved by default. No proprietary validation GMX, executable, Ghidra export, ANM or footage is bundled.
