# SIIG Asset Toolkit 2.10.0-dev10

Dev10 resolves the remaining HORNET presentation gap with an executable-backed **exposed-core state** and validates it against the project owner's re-uploaded original retail Xbox game package.

## HORNET exposed core

- Added catalog `hornet_exposed_core`.
- It represents the deterministic high-level **state-3 entry**: one A1 / `bos_008.gmx`, native motion 0 at sample 0, identity boss-local transform.
- The common reset puts all 125 subordinate records in state `-1`, so neither the BF armor pool nor the C0 prism pool is selected at this boundary.
- The meshless C1 formation rig remains runtime control data and is not emitted as visible geometry.
- Retail Xbox, June 10 Xbox and retail PS3 independently preserve the same state/reset structure.

## Real retail validation

The newly re-uploaded retail Xbox STFS package was extracted directly. HORNET GMX and `enemy.anm` hashes exactly match the previously recorded dev5 corpus. A real `hornet_exposed_core` export produced one instance, two meshes, four nodes and bounds of approximately ±13.8054.

No proprietary game files or generated retail glTF are bundled in the source release.

## GUI

GUI `0.21.0-dev10` now separates HORNET into:

- full armor;
- exposed core;
- prism wall variants;
- spreading/state-6 propagation family.

The exposed-core option is available in Simple mode and as manifest/assembly actions in Advanced mode.
