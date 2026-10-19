# MANDALA runtime assembly — 2.10.0-dev8

## Result

Dev8 adds the evidence-backed `mandala_initial_combat` assembly for MANDALA at the exact **state-7 activation instant before the first rotational update**. The preset contains **40 visible GMX instances**:

- 20 × `bos_005a.gmx` / runtime `0xB7`;
- 2 × each `bos_005b/c/d/e.gmx` / runtime `0xB8/0xB9/0xBA/0xBB`;
- 12 × `bos_005.gmx` / runtime `0x4A` structural instances.

The later 32 × `0xBC` / `bos_005f.gmx` inner-phase members are deliberately excluded because they have not yet been activated at this boundary.

## Five-build evidence

The MANDALA formation math was compared across May 9 Xbox, May 11 Xbox, June 10 Xbox, retail Xbox and retail PS3. The same formation geometry survives throughout development. Retail Xbox's main mover is `0x82240190`; June's is `0x82267660`.

June makes the trig convention explicit: `0x82204468` reads the native 256-entry signed 8.8 sine table directly and `0x82204480` reads the same table shifted by `0x40`, i.e. cosine. The table begins `0, 6, 12, 18, 25...` and reaches `+256` at phase `0x40`. Therefore boss-local placement is `X=cos(phase)*radius`, `Y=0`, `Z=sin(phase)*radius`.

## Runtime slot membership

Retail's model selector resolves the constructor slots without inference:

- slots `0..19` → `0xB7`;
- slots `20..27` → `(slot & 3) + 0xB8`, yielding B8/B9/BA/BB twice each;
- slots `28..59` → `0xBC`;
- slots `60..71` → `0x4A`.

That means the eight radius-69 moving pieces are opposite pairs: B8 at slots 20/24, B9 at 21/25, BA at 22/26 and BB at 23/27.

## Exact transform construction

The constructor creates the first 20 moving pieces on radius 109 using `floor(i*256/20)-0x40`. Slots 20..27 use radius 69 at 32-phase increments. The 12 structural `0x4A` runtime scale targets are **40, 56, 82, 109, 29, 29, 29, 29, 20, 20, 20, 20**. The first four sit at the boss origin, the four scale-29 copies occupy the radius-69 cardinal positions, and the four scale-20 copies occupy radius-20 cardinal positions.

No MANDALA-specific radial-facing callback was found. Accordingly, the assembly does **not** rotate the octagonal pieces outward merely to make them look radial.

The exact 40-row transform table is `reference/tables/MANDALA_INITIAL_COMBAT_TRANSFORMS_2.10.0-dev8.csv`.

## Freeze boundary

Retail state 6 transitions to state 7, enables/copies the first 28 moving records, and returns immediately. The mover's rotating-position update happens only on the following call. This makes state-7 activation with constructor phase zero an exact deterministic snapshot rather than an arbitrary frame sample.

## Animation policy

B7–BB retain their native GMX animation tracks. No `pose_sample` is baked for them because the executable proves outer runtime placement/state at the selected boundary but does not prove that one internal GMX key should be frozen for every moving piece.

## External retail validation retained from development

The preset was previously exercised against the actual retail Xbox MANDALA GMXs and produced **40 instances, 104 meshes, 240 nodes, 38 preserved native animations**, with scene bounds approximately `X/Z = -117.437 .. +117.437`. Those proprietary GMXs are validation inputs only and are not bundled.
