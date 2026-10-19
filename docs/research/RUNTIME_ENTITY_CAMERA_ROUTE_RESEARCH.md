# Runtime entity, route, and camera research

This note records executable-backed findings integrated through SIIG Asset Toolkit 2.8.0-dev5. It is intentionally conservative: fields are named only when their use is demonstrated by the Xbox 360/PS3 executables or by the supplied game corpus.

## Runtime entity registry

The game keeps a fixed-stride runtime resource/primitive registry. In PS3 retail, `0x00175D08(runtime_type)` returns `0x004B5C40 + runtime_type * 0x2C`; `0x00175D2C` reports 0xF0 entries. Retail Xbox 360 and June 10 use the same 240-entry logical table; May 9 and May 11 use 241 entries.

Each 0x2C-byte record contains eleven big-endian 32-bit words. The PS3 constructor at `0x00175FB0` and helper `0x00166488` establish this interpretation:

| word | interpreted field | evidence |
|---:|---|---|
| 0 | GMX/model-name pointer | looked up as a resident GMX resource when nonzero |
| 1 | primitive geometry mode | values 0/1 select two primitive construction paths; `-1` for model-backed entries |
| 2 | texture resource ID | nonnegative values are looked up through the texture/resource manager; `-1` means no primitive texture |
| 3 | primitive state flag | low byte is forwarded to the primitive render-state helper |
| 4 | primitive width | used as width/half-extent input |
| 5 | primitive height | used as height/half-extent input |
| 6 | atlas X | divided by texture width for U coordinates |
| 7 | atlas Y | divided by texture height for V coordinates |
| 8 | atlas width | added to X and normalized for the opposite U edge |
| 9 | atlas height | added to Y and normalized for the opposite V edge |
| 10 | render-group selector | mapped through four renderer groups |

The four selector values resolve to literal engine group names:

0. `Offset Opacity`
1. `Offset Translucent`
2. `Offset Terminate`
3. `Non Opacity`

The supplied retail registry only uses groups 0 and 3. Group 3 is concentrated in the `bos_015` model family.

### Cross-build shape

Normalized for relocated pointers:

- May 9 and May 11 are identical: 241 entries, 131 model-backed, 22 primitive-backed, 88 unconfigured.
- June 10, retail Xbox 360, and retail PS3 are identical: 240 entries, 129 model-backed, 22 primitive-backed, 89 unconfigured.
- June introduces an unused registry slot at runtime type `0xB4`, shifting following entries by +1.
- The May registry entries for `bos_015e.gmx` and `bos_015f.gmx` are absent from the later registry. After those two omissions, the remaining tail has a net -1 shift relative to May.

This describes **registry membership only**. It does not, by itself, prove that a corresponding GMX file was deleted from a build.

See `reference/tables/ENTITY_RUNTIME_REGISTRY.csv`, `ENTITY_RUNTIME_REGISTRY_BUILD_DIFF.csv`, and `ENTITY_RUNTIME_REGISTRY_SUMMARY.json`.

## Bmap/Xmap route source

Each active 0x118-byte Bmap/Xmap record has five optional vectors at `+0xDC`. PS3 retail function `0x0015E5D8` scans slots 0 through 4, appending every nonzero vector. `0x0015E7D0` performs this for every active record in record order. If record 0 contributes no route point, the runtime appends an origin vector before continuing.

Across the supplied 47 same-layout files:

- active records: 19,563
- nonzero route-point vectors: 19,562
- populated slot: slot 2 only
- records using more than one slot: 0
- origin fallback: exactly once, for `Bmap16.bin`

The toolkit now exports this exact source sequence as `.route_source.csv` and `.route_source.obj`. These are **control/source points, not the engine-resampled spline**. The existing `primary_route_point`/initial `FieldPos` semantics remain separate: record 0 slot 2 is used when present, otherwise placement slot 0 position is used for initial `FieldPos`.

## Retail route resampling

The source points above are consumed by a second executable-backed sampling layer. Dev3 reproduces the non-loop, constant-spacing form in `siig_route.py` through `route-resample`; dev4 adds the runtime position/source-index state machine and DAT-coupled `route-playback`.

Key PS3 retail functions:

- `0x00158790` — equal-distance linear subdivision. It advances by `delta / count` **before** writing each output, omits P0, and explicitly overwrites the final output with P1.
- `0x00158A28` — cubic Hermite evaluator. Curves include P0 and P1 and require at least two samples.
- `0x00158D38` — curve setup and six-state tangent-axis selection. The six signed direction states select duplicate 1.5-magnitude X/Y/Z axis vectors; sign comes from the segment delta.
- `0x00159298` — straight/curve classifier. It computes three component-plane angles, truncates degrees to integers, and chooses linear only when all are multiples of 90 degrees.
- `0x0015A338` — initialization. Direction starts at `-Z`; if initial FieldPos exactly equals source point 0, source indexes start at 1/2/3, otherwise 0/1/2.
- `0x00159560` — runtime advancement. In non-loop mode another source segment is built only while the current source index is `< source_count - 2`, leaving the final source point as look-ahead context.

For a curved segment, the tangent vectors are component-wise products of adjacent source deltas and the old/new axis selector vectors. Curve sample count is the linear distance/spacing base count scaled by approximately 1.3.

The supplied 47-file corpus contains one route-empty file (`Xmap4_1.bin`). At a deterministic **100-unit analysis spacing**, the other 46 files produce 19,471 traversed segments and 155,690 samples; 62 segments take the Hermite path. This spacing is only a regression/inspection value. Dev4 separately models mutable SCROLL_02 spacing and loop wrapping in `route-playback`; the fixed-spacing corpus figures remain useful as deterministic regression values.


### Dynamic runtime behavior (dev4)

Retail `0x00159560` consumes at most one generated route sample per runtime update. If a linear segment is still active and `+0x6C` spacing differs from previous linear spacing `+0x70`, the engine discards the remaining samples and rebuilds from the current `FieldPos` to the same endpoint. Curved/Hermite segments skip this spacing-change rebuild branch. In loop mode, endpoint and look-ahead counters are reduced modulo the route-source count while the underlying counters continue increasing; non-loop mode retains the `< source_count - 2` tail rule.

Retail `0x0014E408` converts signed SCROLL_02 Y to per-update route spacing as signed integer truncation-toward-zero of `script_y / frame_multiplier`, narrowed to signed 16-bit and multiplied by `1/256`. DAT authored frame `F` corresponds to runtime update `F × frame_multiplier`. `route-playback` applies that schedule. WIP160 deterministically derives `levelW_stageS.dat` from normal `XmapW_S.bin` and `map4_/map5_` names and cross-checks that stage/script number against the executable-backed registry. The caller still supplies an assumed route initialization frame, and `Bmap` boss/special ownership is not inferred.

The real 47-file route corpus contains 46 resampleable files and one route-empty `Xmap4_1.bin`. All 46 pass non-loop spacing-change and loop-wrap smoke stepping. The normal-stage naming rule now makes the corresponding `XmapW_S` / `map4_/map5_` DAT filename deterministic (`levelW_stageS.dat`): for example, `Xmap2_1.bin + level2_stage1.dat` reaches route completion after 100,000 runtime updates with initial spacing 1.0, while `Xmap3_1.bin + level3_stage1.dat` reaches route completion after 265,020 updates and applies seven SCROLL_02 spacing events/rebuilds before termination. This does not assign one owning DAT to state-dependent `Bmap` boss/special routes.

## Route animation models

The separate `/3ddata/route.bin.gz` BBX contains `fld015.gmx` and `fld014.gmx`. The 0x1C-byte executable descriptors at PS3 retail `0x00532814` are now decoded as `{name[16], start_frame, end_frame, loop_flag}`:

- `fld015`: start 0, end 6300, loop false; the GMX contains 6,301 matrix samples, so frame 6300 selects the final sample.
- `fld014`: start 0, end 1440, loop true; the GMX contains 1,440 matrix samples, so descriptor frame 1440 modulo-wraps to sample 0.

Dev7 corrects an earlier timing interpretation. Channel-type-12 GMX matrix tracks contain a float table before their matrix array, and those floats look like approximately 24 Hz authoring timestamps (`fld015` ends at raw 262.5; `fld014` at raw ~59.9583). Retail runtime functions `_00380998`/`_003809C0`, `_003804A4`, and `_00380A60` show that this matrix path does **not** interpolate or index by those floats. It computes `logical_frame % frame_count` and directly returns the corresponding 0x40-byte matrix record. The engine's model clock is the logical 30 Hz clock.

Accordingly, `gmxtrack` now exports both `runtime_seconds_30hz = sample_index / 30` and `raw_authoring_time`. glTF matrix-animation input keys likewise use sample-index/30 so exported playback matches the retail runtime; the raw float table is retained only as authoring metadata.

## Camera animation models and preset table

The camera subsystem loads `/3ddata/camera.bin.gz` and selects `cam01_op1.gmx` or `cam02_op1.gmx`. Both contain animation tracks for literal nodes `cam1` and `int1`. The camera controller registers one non-loop descriptor named `cam` with start 0 and end 200 for **both** models. Its frame accumulator advances by `1 / frame_multiplier`, is truncated to an integer logical frame, and animated mode exits when the accumulator reaches 200. Therefore:

- `cam01_op1.gmx`: two 200-sample tracks; runtime uses frames 0..199 (~6.667 logical seconds at 30 Hz).
- `cam02_op1.gmx`: two 300-sample tracks, but this camera-controller path still uses only frames 0..199; samples 200..299 are not reached here.
- At frame multiplier 2, logical frames are sampled `0,0,1,1,...,199,199` across 400 runtime updates. At multiplier 1, frames 0..199 are sampled once each.
- `cam1` translation supplies camera eye and `int1` translation supplies camera target; current `FieldPos` is added to both. The normal procedural word-8/9/10 response is bypassed while animated-camera mode is active.

The raw ANIM float timestamps (~24 Hz-looking authoring values) are not the runtime matrix clock for this path; see the route-animation timing correction above.

PS3 retail function `0x0015B4C0` exposes a 32-entry table at `0x0053284C`, with 30 32-bit words (0x78 bytes) per preset. `0x0015B524` consumes those records. The untouched executable words remain preserved in `reference/tables/CAMERA_PRESETS_RAW.csv`; the 160 initializer writes traced at `0x0015C7F0` are preserved separately in `CAMERA_PRESETS_RUNTIME.csv`. Dev5 adds `CAMERA_PRESETS_RUNTIME_SEMANTIC.csv`, whose names are limited to roles proven by downstream consumers.

### Evidence-backed preset fields (dev5)

| words | semantic role | evidence |
|---|---|---|
| 0 | perspective FOV in degrees | `0x00155300` converts degrees to radians and passes the value to the projection-matrix builder |
| 1 | uniform scene/view scale | `0x00155300` composes uniform XYZ scale and reciprocal inverse scale |
| 2–4 | camera-eye offset vec3 | `0x00157A10` transforms the vector through the active route/stage orientation; the result is added to current `FieldPos` and reaches the look-at builder as camera eye |
| 5–7 | scene/view translation vec3 | copied at `0x00154B10` and used in scene/view transform composition |
| 8 | dynamic horizontal-response gain | `0x00157540`; divided by uniform scale and clamped at zero |
| 9 | dynamic target local-X scale | `0x00157540`; scales the local-X response added to camera target |
| 10 | dynamic eye local-X scale | `0x00157540`; scales the corresponding local-X response added to camera eye |
| 11 | **face bias** | PS3 interpolation/forwarding `0x0015B910` → `0x0020D69C` / `0x0020E984`; Xbox `Function_8214E120` virtual `+0x18` → `0x82475590` stores wrapper `+0x60`; `Function_824745F0` uploads it for `collada_face1`; embedded shader `0x8208D408` declares `faceBias : c9` and applies `pos - Normal * faceBias.x` |
| 12–17 | fog profile 0 `{start,end,RGBA}` | scenegraph consumer ultimately writes `fogRange` and `vFogColor` |
| 18–23 | fog profile 1 `{start,end,RGBA}` | same renderer path |
| 24–29 | fog profile 2 `{start,end,RGBA}` | same renderer path |

The fog identification is not based merely on value patterns. The nested render object's setter stores the first two profile floats as the fog range and the vec4 as fog color; its draw path sends them to renderer/shader uniforms `fogRange` (`0x003756E8` string reference) and `vFogColor` (`0x003756AC`).

Retail `0x00157540` computes the dynamic local-X response from normalized runtime coordinates. In single-precision terms, the toolkit reproduces:

```text
nx = (runtime_x - 213) / 213
ny = (runtime_y - 5) / 228
gain_scaled = max(0, word8 / word1)
common = nx * gain_scaled * ny
target_local_x = common * word9
eye_local_x    = common * word10
```

These are executable-backed runtime roles; the toolkit intentionally does **not** rename them to a speculative gameplay concept such as aim sway.

Word 11 is `0.2` in all 32 supplied retail presets and is now identified as **face bias**. The former ambiguity was closed by the Xbox retail material/shader path: `Function_8214E120` calls virtual slot `+0x18`; raw PPC at `0x82475590` stores the float at material-wrapper `+0x60`; `Function_824745F0` uploads that field for material type 1 (`collada_face1`); and the embedded vertex shader at `0x8208D408` declares `float4 faceBias : register(c9)` and offsets object position by `-Normal * faceBias.x`.

`camera-preset <index>` exposes the semantic preset in JSON. Supplying both `--runtime-x` and `--runtime-y` also evaluates the proven dynamic local-X response. `CAMERA_PRESET_SCHEMA.csv` records all 30 word roles, addresses, transition behavior, confidence, and unresolved notes.


## Procedural route orientation and camera world state (dev6)

Dev6 connects the procedural route position sampler to the camera-eye/target semantics established in dev5. The route object initializes pitch/yaw/roll and additive angle offsets to zero, its orientation matrix to identity, and previous position to initial `FieldPos`.

For moving samples produced by a Hermite segment, retail updates orientation **before** any same-update next-segment preparation. A Hermite `t=0` sample repeats the current position and does not update orientation. When movement occurs:

```text
if delta_x != 0:
    yaw = atan2(-delta_z, delta_x) - pi/2
if delta_z != 0 and pitch_lock == false:
    pitch = atan2(delta_y, -delta_z)
M = Rz(roll + offset_z) * Rx(pitch + offset_x) * Ry(yaw + offset_y)
```

The executable uses row-vector transforms. Straight/linear samples leave the procedural angles unchanged while still advancing the previous runtime position.

For the normal procedural camera path:

```text
base_eye    = FieldPos + transform(camera_eye_offset, M)
base_target = FieldPos
eye          = base_eye    + transform((eye_local_x    * uniform_scale, 0, 0), M)
target       = base_target + transform((target_local_x * uniform_scale, 0, 0), M)
```

`eye_local_x` and `target_local_x` are the proven dev5 word-8/9/10 dynamic response. Animated camera mode is separate: `cam1`/`int1` node translations replace procedural eye/target, and the normal dynamic response is not applied there. Likewise, active `fld014`/`fld015` field-animation mode can supply orientation directly rather than using the procedural route matrix; dev6 does not yet merge those animated modes.

`route-camera-playback` shares the same normal-stage DAT filename inference as `route-playback`; `Bmap` ownership remains explicit. It still requires an explicit start frame, camera preset, and runtime X/Y coordinates. It is an executable-backed reconstruction of the **procedural** path, not an automatic claim about stage activation.

## Remaining boundaries

- Resolve authoritative `Bmap` boss/special route ownership and route-object instantiation timing; normal `XmapW_S` / `map4_/map5_` DAT filename selection is already deterministic.
- Resolve the exact virtual-setter meaning of camera preset word 11; keep it explicitly unresolved until then.
- Couple the route spline, field animation, camera preset state, and `cam1`/`int1` tracks into a single playback model.
- Continue instruction-level RSX/Xenos shader analysis.
