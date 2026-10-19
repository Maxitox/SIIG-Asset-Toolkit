# Shareable `.siigmod` packages

`2.8.0-dev24` adds an **optional sharing layer** above the mod workspace. A `.siigmod` is designed to transfer a modification between SIIG Asset Toolkit users **without redistributing the user's original SIIG resources**. It is not a game container, is not meant to be inserted into an STFS package, and is not required for the normal Xbox package-editor deployment workflow.

For direct Xbox deployment, run **Build replacement files**, verify the build, and use the complete containers under `build/xbox360_replacements/` with a compatible Xbox 360 package editor.

## Package model

A package contains:

- `manifest.json` — mod name/version/author/description, target platform, archive/resource keys, and required SHA-256 baselines;
- `patches/*.bin` — only the target bytes needed by the package's binary deltas;
- copy/sparse instructions in the manifest that reconstruct unchanged regions from the recipient's own verified rip.

The package does **not** carry the clean source BBX archives or complete clean source resources. The recipient must have a matching `rip-game` output. Baseline SHA-256 mismatches are rejected before a patch is applied.

Equal-size edits use sparse replacement ranges, which means the payload contains only bytes that differ at those offsets. Length-changing resources use copy/data delta instructions. Length-changing whole-archive overrides above the conservative delta limit are rejected rather than silently embedding a giant replacement; stage the changed inner resource instead when possible.

## Create a package (only when you want to share the mod)

Build/edit a normal workspace first, then:

```text
python siig_toolkit.py mod-pack My_SIIG_Mod -o My_Mod.siigmod \
  --author "Author name" --mod-version "1.0" --description "Description"
```

`mod-pack` materializes tracked editable files through their native builders before packaging, so it works with the same GMX/TEX/DAT/MAP/ANM/COL/stage/localization workflow as `mod-build`.

Inspect a package without applying it:

```text
python siig_toolkit.py mod-package-info My_Mod.siigmod
```

The report shows package SHA-256, platform, affected archive/resource keys, patch counts, and the distribution policy.

## Apply a package

Given a clean `rip-game` output:

```text
python siig_toolkit.py mod-apply My_Mod.siigmod SIIG_Ripped My_Applied_Mod
```

This creates a normal dev23-style workspace and stages the reconstructed native replacements only after all relevant archive/resource baselines match.

To build immediately:

```text
python siig_toolkit.py mod-apply My_Mod.siigmod SIIG_Ripped My_Applied_Mod --build
python siig_toolkit.py mod-verify My_Applied_Mod
```

`--force` may overwrite an already-staged conflicting replacement in the target workspace. It does **not** bypass source-baseline hashes. V1 deliberately treats two packages that modify the same resource as a conflict rather than attempting an unsafe automatic merge.

## Determinism and validation

Package ZIPs use fixed timestamps, stable member order, fixed permissions, and deterministic DEFLATE settings. The built-in tests require package bytes to be reproducible regardless of input mapping order.

Dev24 also exercised the package layer against the externally supplied retail Xbox `text.bin`: one readable localization character was changed, the native archive was rebuilt, packed into `.siigmod`, applied to a fresh workspace, rebuilt again, and verified byte-for-byte against the source workspace result. The resulting package was 1,184 bytes and its binary-delta payload contained exactly **one changed byte**. No retail source bytes are included in the toolkit; only the derived validation result is retained.

## Security / distribution boundaries

- A `.siigmod` is baseline-dependent by design. It is not a stand-alone copy of the modified game.
- ZIP member paths and sizes are validated before package use; duplicate/colliding paths and traversal are rejected.
- Patch payload, source baseline, and reconstructed target hashes are verified.
- Package application never modifies the clean rip in place; it writes into a mod workspace.
- PS3 NPDRM/SDAT re-encryption remains unsupported. A package can reconstruct the inner native BBX, but `mod-build` still cannot generate a signed/encrypted SDAT replacement.
- A native build passing structural/hash verification does not by itself prove every arbitrary edit is accepted by retail runtime code.
