# SIIG Asset Toolkit 2.8.0-dev14 release notes

Dev14 closes the static-analysis phase of the June/retail Ultimate UFO ending after Mframe 6200. It separates proven reset mechanics from what the ordinary Normal 5-3 ending is actually proven to execute.

- Proved the retail Mframe-6030 phase invokes part 0 with state 1, so it is not the camera-gate clear.
- Proved the Mframe-6200 phase only disables the owned `bos_015k` object and has no part-state or vtable `+0x48` dispatch.
- Located the exact Xbox camera-gate clear at instruction `0x8212DD20` inside `0x8212DCB0`; it requires part 0/state 0 outside the Extra/Bonus 5-6 exception.
- Traced generic vtable `+0x48` at `0x820FBEE8` into that part-0/state-0 clear mechanism.
- Confirmed camera-controller construction (`0x820ECFD8`) and accepted preset changes (`0x820ECDF0`) set the gate to 1 rather than clearing it.
- Excluded Normal 5-3 DAT cleanup and destructor-only manager removal as ordinary sources of the gate clear.
- Classified the 25,200-timer-unit generic lifetime path as a watchdog, not an established normal route-end trigger.
- Added `ULTIMATE_UFO_FINAL_RESET_AUDIT.csv` and a dedicated regression check, raising the dependency-free suite to 46 checks.
- Bracketed the June 10 prototype's visible Ultimate UFO debug-registration removal to ~427.367–427.400 s in Normal seg6, at the Stage 5-3 completion white-out, and recorded it separately as gameplay observation.

**Final dev14 static conclusion:** there is no proven ordinary Normal 5-3 post-6200 `+0x48` caller. The part-0/state-0 handler proves the camera-gate clear *mechanism if invoked*; it does not prove that the ordinary retail ending invokes that mechanism. Static evidence leaves a runtime-only branch between a higher-level reset before teardown and destructor-only manager removal. Dev14 deliberately does not invent an exact gate-clear frame or claim that the clear definitely executes.
