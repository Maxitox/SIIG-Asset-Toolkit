# Space Invaders Infinity Gene Asset Toolkit

The **SIIG Asset Toolkit** is a research and modding toolkit for studying the Xbox 360 version of *Space Invaders Infinity Gene*, with related support and research for the PlayStation 3 version. It focuses on documenting formats and workflows so that researchers can inspect, validate, convert, and experiment with game data from files they supply themselves.

This repository contains toolkit source code, format research, documentation, and development history. It is **not** a copy of the game and does not provide proprietary game assets or executables.

## What it can do

- **Read game containers:** work with Xbox 360 STFS packages and PlayStation 3 PKG inputs.
- **Inspect and extract assets:** examine supported BBX, GMX, TEX, DAT, MAP, animation, localization, and related data.
- **Support modding workflows:** build replacement files and validate outputs for use with compatible package tools.
- **Explore models and stages:** use the GMX Workbench, Asset Viewer, Stage Explorer, and Visualizer Simulator.
- **Support research:** consult format notes, provenance records, validation fixtures, and documented reverse-engineering findings.

Coverage varies by format and platform. Some tools are experimental, and not every asset or game behavior is fully understood.

## Current version status

- **Current development checkpoint:** `v2.10.0-dev25` — unsealed and intended for testing/research.
- **Latest sealed checkpoint:** `v2.10.0-dev23` — immutable.
- The `public-release/dev25` branch is a staging branch for public review. It is not the default `main` branch.

See [CHANGELOG.md](CHANGELOG.md) for release and development history, and [VERSION.txt](VERSION.txt) for the version represented by this source tree.

## Getting started

1. Read the [Quick Start guide](docs/guides/QUICK_START.md).
2. Review the [Desktop GUI guide](docs/guides/DESKTOP_GUI.md) if you want to use the graphical interface.
3. Read the relevant format or workflow notes before changing assets.
4. Supply your own legally obtained game package or extracted files when testing. Keep proprietary game files, dumps, and personal data out of public issues and pull requests.

The toolkit uses Python and, for some optional workflows, external tools such as FFmpeg or OpenSSL. These tools are not bundled; see the relevant guides for requirements and setup.

## Historical versions and regression testing

Historical packages are being organized under the repository's archive plan so researchers can compare behavior across versions. See [the archive index](docs/archives/README.md) for the version inventory and archive status.

Prefer a sealed release for stable use. Development checkpoints may contain regressions or incomplete features; consult the changelog and checksum records before testing an older build. Historical packages must be audited for proprietary content and provenance before they are redistributed.

## Project status and limitations

This is an ongoing reverse-engineering research project, not a complete reimplementation of the game. Format support and behavior may be incomplete, and experimental tools can change between checkpoints. Please report reproducible findings with the platform/build, file path, steps, evidence, hashes where practical, and confidence level.

## Licensing and game files

Original project-authored material is dedicated under [The Unlicense](UNLICENSE) only to the extent the project maintainer has the legal right to dedicate those rights. Third-party components retain their own licenses; see [project licensing](LICENSES/PROJECT-LICENSING.md), [third-party notices](docs/project/THIRD_PARTY_NOTICES.md), and [provenance records](reference/provenance/SOURCES.csv).

The toolkit license does **not** grant rights to *Space Invaders Infinity Gene* or its proprietary assets, executable files, audio, video, or extracted dumps. Do not redistribute those materials without permission.

## Contributing

Research contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) and include evidence and provenance. Do not submit game dumps, proprietary executables/assets, credentials, or private personal data.
