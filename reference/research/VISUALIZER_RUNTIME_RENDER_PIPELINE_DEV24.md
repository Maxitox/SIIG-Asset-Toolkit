# Visualizer runtime render pipeline — dev24

## Scope

This note records the executable-backed render behavior used by the dev24
Visualizer Simulator fidelity pass.  The primary visual reference remains the
June 10 Visualizer Check Mode footage, while the render pipeline below is
recovered from the May 11 Xbox 360 prototype because that build retains the
same VisualizerMain / VisualizationBase implementation with useful symbols and
source strings.

No proprietary executable, SHAPE texture, ParameterSet row, or SequenceSet row
is bundled in the source-only toolkit.  Function/address references below are
research provenance only.

## Render-target and source dimensions

`Function_8216B168` constructs VisualizerMain with width `0x500` and height
`0x2D0`, therefore the internal feedback target is exactly **1280 x 720**.

`Function_8216EAF0` creates ten source-image objects by calling
`Function_8216E238(..., 0x80, 0x80, ...)`, therefore each SHAPE source has an
exact **128 x 128** runtime footprint.  The ten-resource ordering remains:

1. WhiteCircle
2. line
3. 3line
4. square
5. triangle
6. WhiteCircle2
7. line2
8. 3line2
9. square2
10. triangle2

The source-only simulator still has procedural stand-ins for these ten
proprietary source textures, but a user-generated simulator can embed the exact
converted PNGs from a local rip. The serialized retail TEX headers now also
prove the SHAPE fetch itself is point-filtered with repeat addressing and
anisotropy disabled. Exact proprietary pixels remain user-supplied only.

## Parameter split: SHAPE versus feedback

`Function_8216B4F8` applies the current SHAPE/source parameters:

- interpolated RGBA;
- interpolated source scale X/Y;
- source position;
- source rotation parameters.

`Function_8216B660` separately applies feedback/magnify parameters:

- free or fixed feedback/source anchor position;
- SHAPE clear color;
- interpolated magnify alpha;
- interpolated magnify scale X/Y.

This separation is important: magnify scale/alpha belongs to the previous
framebuffer, while rotation belongs to the current SHAPE source.

## Rotation

The selected SHAPE implementation stores the per-render rotation increment at
source-image `+0x0C`.  Raw PPC at `0x8216E228` computes it as:

`rotation_base + add_rotation * interpolation_factor`

The interpolation factor is the current Visualizer parameter factor (the
Check Mode volume-driven factor in the simulator).

`Function_8216E380` then applies rotation as follows:

- `fix_rotation == 0`: accumulate the per-render increment and use the running
  angle;
- `fix_rotation != 0`: use `fix_rotation` directly, converted from degrees to
  radians.

The feedback framebuffer itself is **not rotated** by this path.  This corrects
the old dev23 simulator, which incorrectly applied the SHAPE rotation to the
whole previous framebuffer.

## Exact Position Fix runtime table

The fixed-position setter indexes a writable float2 table by raw Position Fix
value.  WIP170 initially read only the table's **pre-startup** image and therefore
misclassified the three rows as aliases.  June 10 startup initializer
`0x82564470` patches the missing Y rows before normal use: it loads `-308.0`,
writes `+308.0` into raw 1..3, and `-308.0` into raw 7..9.  Retail and May 11
show the same six-store initializer pattern.

The final runtime table is:

| Index | X | Y | Runtime meaning |
|---:|---:|---:|---|
| 0 | 0 | 0 | Free X/Y path |
| 1 | -448 | +308 | Upper left |
| 2 | 0 | +308 | Upper center |
| 3 | +448 | +308 | Upper right |
| 4 | -448 | 0 | Middle left |
| 5 | 0 | 0 | Fixed center |
| 6 | +448 | 0 | Middle right |
| 7 | -448 | -308 | Lower left |
| 8 | 0 | -308 | Lower center |
| 9 | +448 | -308 | Lower right |

Index 0 remains the free-position path in VisualizerMain; Check Mode exposes
free X/Y bounds of X `[-560, 560]`, Y `[-360, 360]`.  Therefore raw 0 can look
like raw 5 when free X/Y is `(0,0)`, but raw 0 follows the free coordinates
whereas raw 5 is fixed at center.  Dataset v16 preserves all ten raw values and
exposes all nine fixed grid points instead of collapsing them.

The Visualizer coordinate system is centered with **+X right and +Y up**. Canvas uses +Y downward, so the host bridge in current builds is:

`canvas_x = 640 + visualizer_x`

`canvas_y = 360 - visualizer_y`

WIP191 temporarily inferred an extra 1.5× scale from capture fitting. WIP195 superseded that hypothesis after retail stage 4-5 `SEQUENCE_12 / PARAM_7` proved it could move the complete 128×128 source off-target and collapse the recurrence into a background-color gradient. WIP197 closes the global scale directly in the June 10 executable: `Function_82177DF0` sends `x * 0.0015625` (= X/640) and `y * 0.0027777778` (= Y/360) into the 1280×720 render path. No extra 1.5 factor is present there.

The fixed grid therefore maps to X `192/640/1088` and Y `52/360/668`. Free `(10,+360)` maps to `(650,0)`, placing its source center on the top edge. The simulator exposes a research-only anchor/source-bounds overlay so any remaining hardware mismatch can be measured as a pivot/composite/presentation issue instead of being hidden behind another global-coordinate guess.

## Ping-pong render order

The feedback class owns two render targets and swaps them with
`Function_8216D628` after each pass.  `Function_8216D830` performs the render
sequence in this order:

1. bind/clear the destination target with the configured clear RGBA;
2. invoke the current SHAPE/source draw (`Function_8216D938`);
3. invoke the effect path (`Function_8216D4A8` -> subclass
   `Function_8216DC18`) that samples the previous target using magnify scale
   and alpha;
4. unbind the destination target;
5. swap the two feedback targets.

Therefore the executable order is **SHAPE first, previous feedback second**.
The dev23 simulator used the reverse order.

`Function_8216DC18` builds a transform around the same free/fixed anchor used by
the source image, applies only magnify X/Y scale, samples the previous render
target, and supplies magnify alpha to the EffectBlur shader path.  No SHAPE
rotation term is fed into that feedback transform.

This recursive, scale-only feedback is what makes an off-centre source produce
successive transparent/magnified copies and makes centred shapes expand through
the frame instead of turning the whole history into a rotating smear.

## dev24 simulator model

The browser implementation now mirrors the recovered high-level pipeline:

`clear destination -> SHAPE stamp -> magnified/alpha previous target -> swap`

It uses:

- 1280 x 720 internal canvases;
- 128 x 128 procedural source footprint;
- exact Position Fix coordinates;
- source-only accumulated/fixed rotation;
- feedback magnify X/Y and alpha around the same anchor;
- the recovered 49 ParameterSet / 57 SequenceSet / 29-value contract and
  10-resource SHAPE ordering.

Remaining approximation boundaries are deliberately explicit:

- the Xbox 360 BGM meter window is now recovered as one 5 1/3 ms XAudio2 processing quantum, exactly 256 samples at the simulator's 48 kHz preview rate; the browser mirrors the window size but does not claim sample-phase alignment with native XAudio2 scheduling;
- exact proprietary SHAPE pixels are consumed from a user rip when available; both the recursive feedback sampler and the independently serialized SHAPE sampler are now proven point-filtered/repeat;
- the ordinary SHAPE `ScreenSpritePS` path is now closed: sampled texture RGBA is multiplied by runtime float4 tint RGBA and blended SrcAlpha/OneMinusSrcAlpha; the browser preserves real PNG RGBA and uses source-over;
- EffectBlur pixel-shader sample/color math is closed: sampled feedback RGB is preserved while source alpha is replaced by the uniform feedback alpha; exact Canvas/Xenos render-target alpha-channel storage equivalence remains bounded;

## Regression boundary

The dev24 self-test protects the dimensions, Position Fix table, SHAPE-first
ordering, absence of framebuffer rotation, source-only rotation, and runtime
function provenance.  This prevents a future refactor from silently restoring
the old dev23 feedback model.

## BGM meter semantics

June 10 audio tracing resolves the former BGM-meter value uncertainty. `Function_82495500` averages exactly two floats from the first pointer field of the 12-byte XAudio2 volume-meter structure; Microsoft's public API definition identifies that field as `pPeakLevels`. `FUN_824956C0` latches the result and `FUN_82495360` returns it unchanged. Dedicated Check Mode `Function_82183B20` passes that raw peak mean directly into the Visualizer when VolumeSet is BGM. WIP167 additionally recovers the normal scripted-stage path: `Function_82177648` writes the same raw value into an adaptive window, `Function_821773F0` derives MIN/MAX and normalized VOL SCALE, and parameter interpolation consumes VOL SCALE. `VL_VOLUME_SCALE`/opcode `0xCE` calls `Function_82177300` to set the adaptive window length (constructor default 300; stages 4-2/4-4/4-5 author 180). Browser upstream XAudio2 analysis-window timing remains approximate; see `VISUALIZER_GAMEPLAY_BGM_NORMALIZER_DEV24.md`.
## Xenos feedback sampler (dev24 WIP151)

The previous-feedback texture itself is now recoverable down to its Xenos fetch constant. `Function_821AA630` creates the feedback texture with `Function_8226F240(width, height, 1, 1, 0, 0x28280106, 0, 3)`. The resource allocation is zero-initialized before `Function_8226EA98` constructs the six-dword fetch descriptor, and `Function_8226F5C0` later copies those six dwords from object offsets `+0x1C..+0x30` into texture stage 0 for `Function_8216DC18`.

For this constructor call, fetch dword 3 resolves to `0x00001414`. Cross-checking the field layout against Xenia's public `xe_gpu_texture_fetch_t` definition gives:

- magnification filter: **point**;
- minification filter: **point**;
- mip filter: **point** (the feedback target has no authored mip chain);
- anisotropic filtering: **disabled**.

The fetch-constant clamp fields resolve to zero, and Xenia's public `ClampMode` enum identifies zero as **repeat**. No later feedback-target path observed here rewrites the fetch descriptor before it is bound.

The browser now mirrors both independently recovered point-filtered paths. It disables Canvas2D image smoothing around the recursive previous-feedback draw and restores the prior state immediately afterward. When a real user-rip SHAPE image is present, the transformed SHAPE draw independently does the same; the procedural fallback remains an approximation rather than a claimed TEX sampler emulation.

The EffectBlur fixed-function blend is independently decoded as Add(SrcAlpha, One) for RGB/alpha, while the source `ScreenSpritePS` pass is Add(SrcAlpha, OneMinusSrcAlpha). Together with the two pixel-shader decodes, the remaining browser renderer boundary is no longer an unknown blend/shader equation; it is limited to exact Xenos render-target alpha storage/compositing details that Canvas does not expose bit-for-bit. Xenia is used only as a public documentation/reference source for fetch/shader field layouts and enums; no additional Xenia implementation code is copied.

