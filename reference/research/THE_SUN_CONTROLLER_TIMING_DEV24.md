# THE SUN controller timing / synchronization — dev24

This dev24 trace supersedes the earlier dev19 synchronization boundary. Dev19 correctly recovered THE SUN's native 41-sample body animation and the separate 48-slot `0xB3` / `bos_002b.gmx` protection-barrier field, but it deliberately did not assert that body sample 40 and the full barrier field occurred at the same time. Retail controller tracing now proves that they do **not**.

## Runtime ownership

- Root runtime type: `0x47` / `bos_002.gmx`.
- Runtime+1 visual factory case: `0x48`.
- Controller constructor: `Function_8212BA68`.
- Auxiliary setup: `Function_8212BB58`.
- B3 visual update: `Function_8212BBF0`.
- Body visual update: `Function_8212BE00`.
- Root mover/state machine: `Function_8223AEC0`.

## Opening state 0 — barrier ramp and body frame

During root state 0, the mover grows the barrier-length field from `0` to `0x1800` while decreasing the first-barrier position from `0xC800` by the same fixed-point step:

`barrier_step = 0x3C00 / (frame_multiplier * 0x1E)`

At the authored base `frame_multiplier = 1`, integer division gives `0x0200` (512) per update. `Function_8212BBF0` derives the visible count per group as `length >> 9`, capped by the twelve authored slots. Therefore the four groups grow by one segment each update and reach all **48 segments after 12 updates**.

At the same time, `Function_8212BE00` explicitly forces native body clip 0 to **frame 0** for every root state except 9, 10 and 11. The exact synchronized end-of-opening snapshot is therefore:

- body: `bos_002.gmx`, native clip 0 / frame 0;
- barriers: 4 groups × 12 `bos_002b.gmx` = 48 placements;
- group X centers: `69, 165, 261, 357`;
- full-ramp Z values: `176..198` in steps of 2.

This is exposed as `the_sun_opening_full_barriers`.

## States 9–11 — native body extension/hold/retraction

Only root states 9, 10 and 11 enter the native body-frame interpolation path. The controller reads the shared progress scalar and computes:

`body_frame = trunc((progress / 0x16900) * clip0_end_frame)`

Retail `bos_002.gmx` clip 0 ends at frame 40.

### State 9 — extend

- progress starts at `0`;
- `+0x600` per update;
- clamps at `0x16900`;
- requires **61 updates** to reach the clamp;
- the penultimate authored step `0x16800` evaluates to frame 39;
- the clamp evaluates to frame 40;
- reaching the clamp transitions to state 10.

### State 10 — hold

The body remains at progress `0x16900` / frame 40. The state timer is:

`(frame_multiplier * 0x708) / 0x1E`

At the authored base multiplier this is **60 updates**.

### State 11 — retract

- progress starts at `0x16900`;
- `-0x600` per update;
- clamps at `0`;
- requires **61 updates** to reach zero;
- the same interpolation law runs in reverse.

This is why the static `the_sun_extended_arms` sample 40 belongs to the later state-9/10 controller phase, not to the opening full-barrier state.

## June 10 cross-build check

The June 10 prototype independently preserves the same controller law:

- body visual update: `Function_82146E38`;
- B3 auxiliary update: `Function_82146C28`;
- mover/state-machine path: `0x82262390`;
- same `0x16900` progress maximum;
- same `0x600` state-9/state-11 step;
- same states 9/10/11 body-frame interpolation rule;
- same four-group B3 barrier geometry formula.

This cross-build agreement is strong evidence that the retail behavior is intentional rather than a decompiler artifact.

## Tooling exposure

`python siig_toolkit.py the-sun-controller --frame-multiplier 1`

returns the exact state-0 ramp, representative state-9/11 body frames, state-10 hold timing, and the evidence boundary.

The GMX Workbench exposes four THE SUN inspection forms:

1. `the_sun_opening_full_barriers` — exact synchronized state-0 end snapshot;
2. `the_sun_native_body` — native body with animation retained;
3. `the_sun_extended_arms` — native sample 40 static inspection pose;
4. `the_sun_protection_barriers` — the complete 48-slot B3 placement field by itself.

The legacy alias `the_sun_long_wave` still resolves to the barrier-field catalog for compatibility, but `bos_002b.gmx` is documented as the destructible **player-protection barrier** field, not a wave beam.

## Boundary

The geometry/timing law and the opening body/barrier synchronization are exact. The barriers are destructible during live gameplay; this static sampler does not reconstruct which individual B3 members survive damage in later states. No later survival pattern is inferred.
