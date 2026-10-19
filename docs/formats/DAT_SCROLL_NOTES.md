# DAT scroll semantics (PS3 EBOOT-verified)

The retail PS3 EBOOT proves that all three scroll commands have two signed 8.8 fixed-point arguments:

- `SCROLL_01` (`0x006E`) sets X/Y velocity for 2D MAP layer 0. Its Y word also drives the 3D wall/background system.
- `SCROLL_02` (`0x006F`) sets X/Y velocity for 2D MAP layer 1. Its Y word also drives the 3D route/camera/field system.
- `SCROLL_03` (`0x0070`) sets X/Y velocity for 2D MAP layer 2. Only its separate 3D dispatcher branch is diagnostic-only.

The scripts are authored in a 30 Hz logical timebase. Gameplay scene 2 sets the runtime frame multiplier to 2, so durations are doubled and per-update velocities are divided by 2 for 60 updates per second. This preserves displacement and real-time duration.
