# iOS → console original-boss state-machine lineage — dev20

Dev20 moves the iOS→console ancestry result from constructor/pool structure into the **actual gameplay movers** for the six original Stage-3 bosses. The evidence is source-only: addresses, normalized instruction fingerprints, constants, equations and semantic observations are retained; raw executable bytes and decompiled proprietary code are not bundled.

The raw evidence used for this checkpoint is the re-supplied May 9, May 11, June 10 and retail Xbox 360 Ghidra exports, retail PS3 Ghidra export, and the project-owner iOS 4.1.0 ARMv7 research copy. The modified iOS distribution copy has a malformed/nonstandard final Mach-O load command; analysis used a bounded local metadata repair for disassembly while leaving the source binary untouched.

## 1. The console dispatcher keeps the original mobile IDs exactly

The strongest first-order marker is numeric. The original mobile bosses are entity types **70..75**. The console gameplay dispatcher routes **0x46..0x4B**, which are exactly decimal 70..75, to six dedicated mover functions in every recovered Xbox build. Retail PS3 independently has the same six numeric cases.

| Boss | ID | iOS mover | May 9 | May 11 | June 10 | Xbox retail | PS3 retail |
|---|---:|---|---|---|---|---|---|
| THE MOON | 0x46 / 70 | `moveTheMoon` | `0x82254920` | `0x82256570` | `0x822611D8` | `0x82239D08` | `0x0011459C` |
| THE SUN | 0x47 / 71 | `moveTheSun` | `0x82255CC8` | `0x82257918` | `0x82262390` | `0x8223AEC0` | `0x001121A4` |
| GIGANTIC UFO | 0x48 / 72 | `moveGiganticUfo` | `0x822574A8` | `0x822590F8` | `0x82263910` | `0x8223C440` | `0x0010DB14` |
| LADYBUG | 0x49 / 73 | `moveLadybug` | `0x82259520` | `0x8225B170` | `0x82265970` | `0x8223E4A0` | `0x00109DB8` |
| MANDALA | 0x4A / 74 | `moveMandala` | `0x8225B390` | `0x8225D000` | `0x82267660` | `0x82240190` | `0x001084CC` |
| UNKNOWN | 0x4B / 75 | `moveUnknown` | `0x8225C0C8` | `0x8225DD38` | `0x822682A0` | `0x82240DD0` | `0x001039EC` |

Dispatcher anchors are May 9 `0x8225E9D0`, May 11 `0x82260668`, June 10 `0x8226A988`, Xbox retail `0x822434B8`, and PS3 retail `0x0012FB70`.

## 2. Exact constructor fingerprints recovered

Dev19 had to retain only the established ~86–93% May11→June10 range because the raw exports were unavailable at its sealing boundary. The re-supplied exports recover the exact values:

| Boss | May9→May11 | May11→June10 | June10→retail |
|---|---:|---:|---:|
| THE MOON | 100% | 87.947883% | 100% |
| THE SUN | 100% | 86.072423% | 100% |
| GIGANTIC UFO | 100% | 87.995050% | 100% |
| LADYBUG | 100% | 89.208633% | 100% |
| MANDALA | 100% | 92.691316% | 100% |
| UNKNOWN | 100% | 92.075472% | 100% |

This confirms the previous conclusion: the large common construction/layout refactor is concentrated between May 11 and June 10.

## 3. Mover evolution across Xbox builds

Raw mnemonic fingerprints are useful for locating refactor windows, but **they are not themselves semantic equivalence tests**. GIGANTIC UFO and UNKNOWN, for example, have tiny June→retail mnemonic differences that reduce to `subi`/`addi` changes in relocated global-address materialization. After normalizing that relocation effect, no gameplay change is established there.

| Boss | May9→May11 | May11→June10 | June10→retail raw | Interpretation |
|---|---:|---:|---:|---|
| THE MOON | 100% | 89.251359% | 100% | common layout/timing refactor |
| THE SUN | 100% | 72.906404% | 100% | largest original-six refactor in this window |
| GIGANTIC UFO | 100% | 92.745240% | 99.758571% | retail raw delta is relocation-only |
| LADYBUG | 99.564438% | 82.869154% | 100% | May9→May11 includes one real behavior guard |
| MANDALA | 100% | 89.570552% | 100% | common layout/timing refactor |
| UNKNOWN | 100% | 91.432617% | 99.853372% | retail raw delta is relocation-only |

The May11→June10 movers exhibit the same entity-layout migration already seen in constructors: old `0x10C`-era fields move into the `0x120` layout, including X/Y arrays, state/timer and speed-related fields, while repeated runtime-rate queries are replaced by centralized frame-multiplier mathematics.

## 4. Direct state-machine correspondences

### THE MOON

Mobile state 0 reaches a paired event sequence at counters **122 / 132**: the first event includes sound `0x80` and vibration `100`, and the second initializes the next subordinate object. The console keeps the same ordered pair and **10-unit separation**, but retimes the base thresholds to **262 / 272**. June/retail express those thresholds through the newer frame-multiplier representation. Because the console counter also steps differently, this should be described as a retimed threshold scheme, not a simplistic “+140 frames” shift.

### THE SUN

The original mobile type-71 path contains a four-pair ramp toward **6144 (`0x1800`)**, changing the pair by **−512 / +512**. The V2 type-101 path bypasses this original-only branch. Console Xbox and PS3 retain the same `0x1800` target and four-pair propagation. The step is represented as `15360 / timing_denominator`, which is **512** at the base 30-Hz authored rate. This is direct algebraic preservation of gameplay logic through the console timing refactor.

### GIGANTIC UFO

The shared mobile mover branches between original type 72 and V2 type 102. One original placement path adds **4096 (`0x1000`)** while the V2 side uses **18432 (`0x4800`)**. Console Xbox and PS3 use the `0x1000` path and do not contain the V2 `0x4800` alternative in the corresponding logic. The console boss therefore descends from the original mobile behavior, not the V2 variant.

### LADYBUG

The inherited state-`0x14` path grows three values by **1.1× per update**, saturating at `0x7FFF`. May 9 performs that path without the later guard. May 11 adds a check that a central global state is **not `0x10`** before the growth/clear behavior; the guard persists into June and retail. The exact semantic name of that global state remains unresolved, so dev20 records the condition without guessing a gameplay label.

### MANDALA

The mobile mover builds its opening geometry with two distinctive trigonometric coefficients: **109** for a 20-element ring and **69** for the next 8-element group, with alternating direction. Retail console retains explicit `0x6D` (109) and `0x45` (69) coefficients, the same 20/8 grouping and alternating direction. The adaptation replaces the mobile fixed center with console runtime root/base placement rather than redesigning the geometry.

### UNKNOWN

The original mobile type-75 path uses **±2560 (`0xA00`)** motion values at helper slots corresponding to `+0x14` and `+0x28`. V2 type 105 doubles those values in several phases and has a V2-specific `setVer2Destroy` defeat path. Console uses the original `0xA00` motion and lacks both the V2 doubling and the V2 defeat branch. Again, the console lineage is specifically the original mobile variant.

## 5. What dev20 establishes

Together with dev19's 29/30 pool-slot preservation, dev20 moves the ancestry claim to the state-machine level:

- the six dispatcher IDs are the original mobile type IDs unchanged;
- each ID maps to a dedicated console mover in May 9, May 11, June 10, retail Xbox and retail PS3;
- distinctive mobile constants, loop sizes, event ordering and geometry survive in the corresponding console movers;
- the May11→June10 engine refactor changes layout/timing representation while preserving recognizable gameplay mathematics;
- GIGANTIC UFO and UNKNOWN select the **original** mobile branches rather than V2 behavior;
- LADYBUG contains a genuine prototype-era gameplay edit between May 9 and May 11.

The remaining state-machine work is finer-grained: label more individual states/attacks inside the six movers and then apply the same method to the console-only World 4/5 families to identify where the inherited mobile framework gives way to newly authored 3D combat logic.
