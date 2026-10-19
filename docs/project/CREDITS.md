# Credits

## Project work

- **Project owner and data curator:** supplied the original retail Xbox 360 LIVE package, original retail PS3 PKG/RAP, extracted retail files, prototype builds, Ghidra exports, and hardware/emulator observations. Public credit remains intentionally unspecified until the project owner chooses a name.
- **OpenAI ChatGPT:** assisted with reverse-engineering hypotheses, clean-room parser/converter implementation, MAP atlas reconstruction, package-input support, BBX repacking, Blender/HTML tooling, automated validation, security hardening, documentation, and release packaging.

## Clean-room game-format research

Unless an explicit source is listed below, BBX, GMX, game-specific TEX wrappers, PS3 TEX wrappers, system-font metadata, localization, COL, ANM, DAT, MAP, stage tables, MAP atlas mapping, STFS, and PS3 PKG work was reconstructed from user-supplied files, Ghidra evidence, synthetic fixtures, and cross-build/cross-platform validation. Original game source code was not available and is not included.

## Explicit third-party sources and tools

- **Xenia — Xbox 360 Emulator Research Project:** algorithmic reference for Xenos 2D tiled-texture addressing. The local Python routine is a project-specific adaptation. BSD 3-Clause notice included.
- **NIST FIPS 197:** AES-128 algorithm/known-answer reference used to validate locally written package cryptography.
- **Microsoft DirectXTK documentation:** structural reference for `XMA2WAVEFORMATEX`; no DirectXTK source bundled.
- **Microsoft DirectXTK XWBTool / legacy XACT wave-bank documentation:** public reference for standard 24-byte XWB entries, PCM/XMA2 content support, and Xbox big-endian 16-bit PCM byte-order handling used by the WIP187 flexible Mod Workspace audio builder; no Microsoft source or SDK tools bundled.
- **Microsoft Learn XAudio2 Volume Meter API:** public `XAUDIO2FX_VOLUMEMETER_LEVELS` field semantics used to identify the Visualizer BGM peak-meter structure; no Microsoft implementation code bundled or copied.
- **Microsoft Learn XAudio2 Audio Graph:** public Xbox 360 processing-quantum documentation used to establish the Visualizer BGM meter window duration (5 1/3 ms = 256 samples at 48 kHz); no Microsoft implementation code bundled or copied.
- **Khronos glTF 2.0 Specification:** normative reference for generated glTF files.
- **PNG specification:** normative reference for the locally written limited PNG codec.
- **Ghidra:** PowerPC/XEX analysis and optional Java label API; not bundled.
- **XEXLoaderWV by Warranty Voider / maintained fork:** external Ghidra XEX loader used by the project owner; not bundled.
- **FFmpeg:** optional external XMA2-to-PCM decoder; not bundled.
- **vgmstream:** public Sony BNK (`src/meta/bnk_sony.c`) and PS-ADPCM (`src/coding/psx_decoder.c`) implementations were used as behavioral/field-layout cross-checks for the locally written narrow PS3 audio decoder; no vgmstream code is bundled or copied. Upstream license is recorded in the notices.
- **OpenSSL:** optional external executable used only to accelerate finalized PS3 PKG AES-CTR extraction; Python fallback remains built in. OpenSSL is not bundled.
- **TrueAncestor EDAT Rebuilder by JjKkYu:** historical external fallback used earlier in the project; not bundled and no longer required for the supplied retail SIIG SDATs.
- **Python standard library:** runtime/API platform; interpreter not bundled.
- **Blender:** optional external host for the bundled GMX import add-on; Blender and its Python modules are not bundled. The add-on source is locally authored and uses Blender's built-in glTF importer.

TCRF/The Cutting Room Floor was not used and is explicitly excluded; see `docs/project/SOURCE_EXCLUSIONS.md`.

See `reference/provenance/SOURCES.csv`, `reference/provenance/PROVENANCE.json`, `docs/project/SOURCE_AUDIT.md`, and `docs/project/THIRD_PARTY_NOTICES.md` for detailed records.

- **psx-spx / consoledev SPU documentation:** public behavioral reference for Sony/PlayStation ADPCM loop-start, repeat, and end flag semantics used to cross-check WIP187 PS3 control-byte regeneration; no code copied or bundled.
