# SIIG historical archive import pack

Extract this ZIP into the root of your local `SIIG-Asset-Toolkit` repository checkout, preserving paths. Then review the added `archives/` directory in GitHub Desktop and commit it on `public-release/dev25`. Do not merge to `main` or change repository visibility yet.

Contains 142 historical toolkit ZIP packages (about 181 MiB before outer compression), grouped by release/development era. SHA-256 values are in `archives/SHA256SUMS.txt`; file sizes, paths, and hashes are in `archives/ARCHIVE_MANIFEST.json`.

The package ZIPs were checked for ZIP integrity and screened for obvious proprietary game payload extensions (XEX/STFS/PKG/EDAT/SDAT, GMX/TEX/MAP/BBX, game audio/video) and common secret patterns. No such payloads/secrets were found. A few old package source files include example paths (for example `/home/example` or `C:\Users\Example`), not personal paths. Some archives include nested ZIPs for the toolkit's own Blender add-on and old `.pyc` bytecode; these are preserved to keep the historical package intact. This is a preliminary technical screen, not a legal opinion or a substitute for provenance review.

Sealed vs development: `v2.10.0-dev23` is the latest sealed checkpoint. `v2.10.0-dev25` is unsealed. Candidate and WIP checkpoints retain their historical labels.
