# `est_020` / `est_021` shared bomb lifecycle — dev24 WIP182

## Identification

Project-owner gameplay investigation identifies the two late `est_*` models as one shared OCTOPUS / GLUTTONY bomb lifecycle:

- `est_020.gmx` — **bomb before detonation**; the live/drop projectile model.
- `est_021.gmx` — **bomb detonation / explosion**; the resulting explosion model.

This is a friendly semantic identification from direct gameplay/model comparison. It is not claimed to be an original internal source-code name.

## Independent executable corroboration

The retained Xbox executable strings independently establish that GLUTTONY has a dedicated `Gluttony::DischargeBomb` routine and that the object returned through that path is expected to satisfy `pEShot->GetType() == EShotManager::eENEMY_SHOT_TYPE_ID_SG_BOMB`. The same binary family also retains the `EShotSg` 3D enemy-shot state machinery (`SetGravity`, `MoveGravity`, `ChangeState`, `CheckState`, `GetDischargeTime`).

This executable evidence corroborates the *bomb-shot subsystem and lifecycle context*. It does **not** by itself prove the `est_020` or `est_021` filename assignment, because neither model is present in the top-level runtime model registry and a direct filename/resource call path has not yet been isolated. OCTOPUS retains an executable `Octopus::dischargeShot` path, but WIP182 does not relabel that routine as `SG_BOMB` without a direct type trace.

## Geometry cross-check

The existing WIP180 geometry audit is consistent with the identification:

- `est_020.gmx`: 7,568-byte native GMX; 4,620-byte converted geometry payload; visually catalogued as an octahedron with wireframe octahedron.
- `est_021.gmx`: 62,256-byte native GMX; 31,644-byte converted geometry payload; visually catalogued as a larger dodecahedron-like form with wireframe shell.

The approximately eightfold native-size increase and substantially larger converted geometry in `est_021` are consistent with a compact projectile transitioning to a much richer explosion volume. This is supporting geometry evidence, not the primary identity source.

## Provenance / confidence

- OCTOPUS + GLUTTONY shared usage: **project-owner confirmed gameplay observation**.
- `est_020` = pre-detonation bomb: **project-owner confirmed effect identity**.
- `est_021` = resulting explosion: **project-owner confirmed effect identity**.
- GLUTTONY uses `SG_BOMB`: **executable-backed**.
- Direct `SG_BOMB -> est_020 -> est_021` filename/resource binding: **still open**.
- Exact OCTOPUS shot-type trace: **still open**.

No proprietary GMX, executable, screenshot, or gameplay capture is bundled with the source-only toolkit.
