# SIIG Asset Toolkit 2.8.0-dev2 development notes

This checkpoint turns the next executable-backed 3D/runtime research into reproducible toolkit outputs.

## Runtime entity registry

- Added a five-build runtime entity/primitive registry table.
- Decoded the 0x2C-byte record fields used for GMX lookup, primitive texture/size/atlas setup, and render-group selection.
- Resolved the four render-group selectors to the engine's own names.
- Documented the May-to-June registry shift without conflating registry removal with asset-file removal.

## Route and camera

- `stage3dmap` now exports the exact runtime route-source control-point sequence as `.route_source.csv` and `.route_source.obj`.
- Added origin-fallback behavior for a record-0 map with no route points.
- Added `gmxtrack` to export GMX matrix animation tracks as decomposed CSV plus translation-path OBJ.
- Added raw camera preset and route-animation descriptor tables from the retail PS3 executable.
- Real-corpus validation covers 47 stage-3D maps and the four retail field/camera GMXs.

## Regression status

- Built-in suite expanded from 23 to 24 checks.
- The new checks cover corrected Bmap/Xmap transforms and route-source ordering/fallback plus synthetic GMX animation-track export.

This remains a development checkpoint. Camera preset field names, exact Hermite/resampling reproduction, and shader ISA translation remain open research.
