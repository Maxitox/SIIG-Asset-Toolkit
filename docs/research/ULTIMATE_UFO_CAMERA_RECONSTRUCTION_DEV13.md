# Ultimate UFO procedural camera reconstruction — dev13

Dev13 converts the dev12 late-camera chain into a reusable frame-by-frame reconstruction instead of relying on a few hand-evaluated matrices.

## GMX matrix representation

Real GMX ANIM samples are serialized as conventional row-major matrices for column-vector use: translation occupies flat indices 3/7/11. SIIG's retail PS3 runtime camera math consumes row-vector matrices whose translation occupies the final row.

The runtime evidence is:

- `0x0036A154` builds/updates row-vector translation matrices.
- `0x00369BE4` performs the ordinary `C = A × B` matrix multiply used by that path.
- `0x00157A10` consumes runtime camera/node matrices using the row-vector layout.
- `0x00159D58` obtains the SgModel field-node matrix and copies it into the route controller.
- real `cam01_op1.gmx` serializes visible animated-camera translations at indices 3/7/11, so the SgModel path necessarily bridges the serialized and runtime representations before `0x00157A10` consumes them.

The toolkit therefore models the representation bridge as a 4×4 transpose. It does not claim to have recovered the internal implementation address/body of the SgModel virtual node-matrix getter itself.

## `field-camera`

New command:

```text
python siig_toolkit.py field-camera fld015.gmx --preset 4 \
  --start-frame 5897 --end-frame 6300 -o ufo_late.csv
```

Optional `--runtime-x` and `--runtime-y` values apply the executable-backed dynamic horizontal response. If they are omitted, the toolkit deliberately leaves that response out rather than inventing player coordinates.

For each emitted frame the CSV records:

- FieldPos;
- reconstructed procedural eye and target;
- route tangent;
- eye displacement projected onto the route tangent;
- rear-follow distance;
- world-Z eye/target separation;
- runtime row-vector orientation matrix;
- a conservative follow classification.

This command models the procedural camera after PA animated-camera mode. `cam01_op1.gmx` / `cam02_op1.gmx` remain handled by `camera-animation`.

## Real normal-5-3 late-route result

The supplied retail `fld015.gmx` was evaluated at every logical Mframe from **5897 through 6300**, using preset 4. There are 404 inclusive samples.

Result:

- **404/404 frames classify as `rear_follow`.**
- rear distance projected along the instantaneous route tangent: **59.8589619 .. 72.1110210** units;
- mean rear distance: **63.6650162** units.

Selected endpoints:

| Mframe | Eye | Target | Eye along route |
|---:|---|---|---:|
| 5897 | `(0, 37.2534, 72.0348)` | `(0, 97.2534, 32.0348)` | `-69.3146` |
| 6300 | `(0, 890.8080, 21.2456)` | `(0, 950.8080, -18.7544)` | `-60.2929` |

Negative `eye_along_route` means the eye lies behind the local direction of route travel. This turns dev12's six-frame rear-follow sample into a complete late-window result.

## Dynamic-response stress

Preset 4's executable-backed runtime response can shift the camera laterally as runtime X/Y changes. Two deliberately extreme constant-X evaluations were run over all 404 late frames (`runtime_y=233`, `runtime_x=0` and `426`). Both still classify **404/404 frames as rear-follow**, with the same rear-distance min/max/mean as the base reconstruction.

This is expected from the late route geometry: its tangent has no material X component in this interval, so a dynamic local-X displacement changes lateral framing without changing the eye's projection behind the route.

Actual player X/Y through the recorded May prototype fight was not recovered from the available project files during dev13; therefore dev13 does not claim a pixel-identical replay of the rendered shot.

## Camera transition gate

Retail adds another late-camera behavior that June 10 did not expose in the same UFO path.

Retail PS3 preset setter `0x0015B524` shows controller `+0x11C` is a **timed-transition acceptance gate**:

- duration 0 preset changes are accepted regardless of the gate and re-enable it;
- positive-duration changes require the gate to be nonzero.

Ultimate UFO part-0/state-0 reset clears that gate in both retail Xbox (`0x8212DCB0`) and retail PS3 (`0x001D3380`), except the special Extra/Bonus 5-6 fast-destruction branch. This is a transition-lock behavior, not a geometric camera parameter.

## Final Vanish evolution

The May prototypes make the old route endpoint explicit:

- May 9 `MoveMain 0x82142008`, state/phase 12 at Mframe 6200, invokes vtable `+0x48(part 0)`; prototype debug strings identify the corresponding operation as `UltimateUfo::Vanish` at `0x821410A8`.
- May 11 `MoveMain 0x821431D0` does the same; `UltimateUfo::Vanish` is at `0x821423B8`.

This is consistent with the project-owner footage observation that the May boss disappears just after frame 6200. Later June/retail builds split the ending into the 6030 part-0 destruction/explosion action and 6200 `bos_015k` shutdown, and their MoveMain no longer directly performs that final part-0 `+0x48` call. The later engine-owned final-reset caller remains unresolved.

The retail `DEL_LV5_BOSS` opcode can reach the generic vanish/reset machinery, but neither retail 5-3 nor Bonus 5-6 contains an authored `DEL_LV5_BOSS` record, so it is not assigned as the ending trigger for these fights.

## Evidence boundary

Dev13 upgrades the normal 5-3 conclusion to **full-window rear-follow procedural geometry**: every real `fld015` frame from core hold through route end places preset 4 behind the direction of travel, and the known dynamic horizontal response does not break that relationship.

The remaining boundaries are narrower:

- a dynamically computed/unresolved external preset mutation is not mathematically impossible, though no static/direct Ultimate UFO preset writer was found;
- actual player runtime X/Y is needed for an exact dynamic-X replay;
- the later-build caller that performs the eventual final part-0 reset after the 6030/6200 split remains unidentified;
- a retail activation callsite selecting PA camera index 1 / `cam02_op1.gmx` remains unproven.
