# Historical toolkit archives

This directory is the planned home for versioned toolkit ZIPs and their integrity records. The aim is to let researchers reproduce older behavior and compare regressions without mistaking an experimental checkpoint for a stable release.

## Archive policy

- Preserve each source ZIP as an unmodified artifact whenever possible.
- Use the original version/checkpoint in the filename; do not rename WIP checkpoint snapshots to look like sealed releases.
- Include a SHA-256 sidecar or a generated archive manifest with the original filename, byte size, hash, and provenance.
- Label stable/sealed releases separately from development builds, candidates, and WIP checkpoints.
- Avoid duplicate copies of the same ZIP unless they differ in bytes; if hashes differ, retain both and explain the difference.
- Do not publish any archive until its contents have been inspected for proprietary game files, extracted game dumps, secrets, private paths, and third-party material that cannot be redistributed.

## Inventory discovered so far

The project Library currently contains historical toolkit ZIPs from the early `v1.x` line through `v2.10.0-dev25`. The inventory includes:

- Early and numbered releases: `v1.1`–`v1.9.1`, `v2.0`–`v2.5.1` (with gaps where no package was found).
- `v2.8.0-dev` checkpoints, including dev1, dev2, dev4–dev28, plus a dev14 duplicate-suffix copy and a dev24 candidate.
- `v2.9.0-dev1`–`dev7`.
- `v2.10.0-dev1`–`dev25`, including historical dev24 WIP snapshots (WIP125–WIP200, with gaps), a dev15 candidate, a dev22 WIP package, and dev23 WIP snapshots.

This is a discovery inventory, not a claim that every file has already been imported or approved for redistribution. The Library also contains duplicate copies of some artifacts. Only one byte-identical copy should be archived unless distinct hashes or provenance justify keeping variants.

See [INVENTORY.md](INVENTORY.md) for the filename-and-size list of the 142 distinct ZIP filenames discovered in the Library. That list is not yet a list of audited or committed archives.

## Current staging status

**Pending:** binary archives have not yet been committed to this directory. The current GitHub file-editing workflow can update text files but cannot upload ZIP bytes directly. The archive ZIPs must be added through a local repository checkout / GitHub Desktop (or as GitHub Release assets), after the content and checksum audit.

The first archive candidate should be the latest sealed `v2.10.0-dev23` package and then the historical development packages, ending with the current `v2.10.0-dev25` package. Keep dev25 marked **unsealed**. Do not substitute candidate/WIP packages for a canonical release.

## Suggested layout

```text
archives/
  releases/
    v1/
    v2/
  development/
    v2.8.0/
    v2.9.0/
    v2.10.0/
  SHA256SUMS.txt
```

For many downloadable binaries, GitHub Releases are generally more practical than placing every ZIP in the source tree. The repository should still keep a machine-readable index and checksums so that every archived file is identifiable.
