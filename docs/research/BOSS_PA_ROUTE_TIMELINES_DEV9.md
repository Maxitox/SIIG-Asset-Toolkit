# Boss PA-route timelines — dev9

Dev9 continues the executable-only PA-route work without changing the frozen dev8 checkpoint. The new conclusions below are backed by literal data tables and their executable consumers. Human-facing camera-angle names are intentionally not assigned where the camera consumer has not yet been proven.

## Water Strider

The retail Xbox 360 table at `0x8200B338`, the PS3 retail table at `0x004BBCDC`, and the June 10 table at `0x820128E8` are byte-for-byte identical. They contain 17 inclusive course intervals spanning frame 0 through 1440. Retail Xbox `0x82136810`, PS3 `0x001E04D0`, and June 10 `0x82151D98` advance the external field/course clock and reset it to zero when it exceeds 1440. This proves a 1441-frame indefinitely repeating route clock while the boss logic remains active.

May 9 and May 11 already contain the same 17 interval boundaries, but their record layout and several opaque per-segment flags differ from the later compact table. Their surrounding driver also differs enough that dev9 does not claim the later retail wrapper address for those prototypes.

## Ultimate UFO

Retail Xbox `0x8212EC50`, PS3 retail `0x001D2988`, and June 10 `0x82149DF8` consume an identical 13-record phase table. Trigger frames are `0, 1750, 2250, 3123, 4231, 4450, 5100, 5300, 5897, 5898, 5902, 6030, 6200`; phase 5 carries a 200-frame delay field. The controller is finite: unlike Water Strider, there is no 1440-style modulo/reset on the 0..6300 field timeline.

The executable state machine also contains explicit stop/resume behavior around phase 9: on entry it clears the route-advance flag, waits on an owned object/event, then restores advancement and clears the delay counter when that object/event reports completion. This is a direct executable-backed hold/resume checkpoint. Additional phase-entry actions occur at phases 4–13 (part visibility toggles, effects, object state changes and final cleanup), but dev9 keeps those actions structurally named unless their exact gameplay/camera meaning is proven.

May 9 and May 11 use the same earlier 12-record table: phase 2 at 1800, phase 3 at 2300, phase 6 at 4600, phase 9 with a 2000-frame delay field, and phase 12 at 6200. By June 10 the route had moved to the retail timings, phase 9's table delay became zero, phase 12 moved to 6030, and a new phase 13 was added at 6200.

## Camera evidence boundary

The known special-route setup still directly selects `cam01_op1.gmx` (PA camera index 0). `Route::SetPaRoute(1)` can load `cam02_op1.gmx`, but dev9 still has no proven retail activation callsite choosing index 1. The boss phase tables contain visibility/action bytes, not self-describing camera-angle labels. Therefore gameplay descriptions such as vertical traversal, airlock escape, and the final rear shot are useful human guidance for matching future camera consumers, but they are not emitted as executable-proven labels yet.

## Cross-build function map

See `reference/tables/PA_ROUTE_BOSS_FUNCTIONS.csv`, `WATER_STRIDER_ROUTE_SEGMENTS.csv`, and `ULTIMATE_UFO_ROUTE_PHASES.csv`.
