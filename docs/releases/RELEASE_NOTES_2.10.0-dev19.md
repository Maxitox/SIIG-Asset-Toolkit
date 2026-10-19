# SIIG Asset Toolkit 2.10.0-dev19

Dev19 adds evidence-bounded THE SUN assembly support.

- `the_sun_native_body` preserves the six native `bos_002.gmx` arm tracks.
- `the_sun_extended_arms` bakes exact native logical sample 40 for a deterministic extended-arm inspection pose.
- `the_sun_long_wave` exports the exact maximum 48-instance `bos_002b.gmx` field: four groups of twelve at X `69/165/261/357`, Z `176..198` step 2.
- Corrected ownership documentation: runtime `0x47` drives the body internally; `0xB2/0xB3` allocation lives in neighboring `0x48` controller setup.
- The extended-arm body and maximum B3 wave remain separate presets because their exact temporal synchronization is not proven.
- GUI 0.30.0-dev19 adds a three-form THE SUN selector in Simple and Advanced GMX Workbench modes.
- Fresh retail validation confirms `bos_002.gmx` and `bos_002b.gmx` hashes and successful 1/1/48-instance exports.
- Dependency-free regression suite: **101/101**.
