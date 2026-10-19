# Third-party notices

This source-only package does not bundle FFmpeg, OpenSSL, vgmstream, Ghidra, XEXLoaderWV, TrueAncestor, Xenia, DirectXTK, or any other external binary/library. It contains no game assets.

## Adapted source logic

### Xenia

The function `xg_address_2d_tiled_offset` in `siig_toolkit.py` is an independent Python translation/adaptation of Xenos tiled-texture addressing logic published by the Xenia project. It was reduced to SIIG's texture cases, renamed, and validated against the supplied texture corpus.

Upstream: https://github.com/xenia-project/xenia  
License: BSD 3-Clause  
Notice: `LICENSES/XENIA-BSD-3-CLAUSE.txt`

The exact historical upstream commit/file consulted was not preserved. This limitation is recorded in `docs/project/SOURCE_AUDIT.md` and `reference/provenance/PROVENANCE.json`.

## Normative documentation and algorithm references

### NIST FIPS 197

The locally written AES-128 implementation is validated with the published FIPS-197 known-answer vector. No NIST implementation code is included.

Reference: https://csrc.nist.gov/pubs/fips/197/final

### Microsoft DirectXTK Wave Formats

The XMA2 RIFF wrapper field layout follows the public `XMA2WAVEFORMATEX` documentation. No DirectXTK source code is included.

Reference: https://github.com/microsoft/DirectXTK/wiki/Wave-Formats  

### Microsoft DirectXTK XWBTool / XACT Wave Bank Structures

WIP187 consults the public DirectXTK XWBTool documentation and legacy Microsoft XACT wave-bank structure documentation to validate the standard entry layout, duration/format/play/loop metadata, channel/rate fields, PCM/XMA2 content support, and the Xbox big-endian 16-bit PCM byte-order caveat. The Mod Workspace XWB reconstruction code is locally authored; no Microsoft source code, SDK binary, XMA encoder, or proprietary implementation is included.

References: https://github.com/microsoft/DirectXTK/wiki/XWBTool and https://learn.microsoft.com/en-us/previous-versions/bb206347(v=vs.85)
License of the referenced project: MIT


### Microsoft Learn XAudio2 Volume Meter API

The public `XAUDIO2FX_VOLUMEMETER_LEVELS` documentation was consulted to identify the first pointer in the 12-byte structure observed in the June 10 executable as `pPeakLevels`. No Microsoft implementation code is included, copied, or adapted.

Reference: https://learn.microsoft.com/en-us/windows/win32/api/xaudio2fx/ns-xaudio2fx-xaudio2fx_volumemeter_levels

### Microsoft Learn XAudio2 Audio Graph

The public XAudio2 Audio Graph documentation was consulted to establish that Xbox 360 processes the graph in 5 1/3 ms quanta. At SIIG's 48 kHz BGM rate this is exactly 256 samples and bounds the Visualizer volume-meter processing window. No Microsoft implementation code is included, copied, or adapted.

Reference: https://learn.microsoft.com/en-us/windows/win32/xaudio2/xaudio2-audio-graph

### Khronos glTF 2.0

Generated `.gltf` files target the Khronos glTF 2.0 specification. No Khronos implementation library is bundled.

Reference: https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html

### Portable Network Graphics

The limited PNG reader/writer used for texture and MAP rendering is locally written against the PNG format specification. No third-party PNG library is bundled.

Reference: https://www.w3.org/TR/png/

### Python standard library

The toolkit uses Python standard-library modules, including `zipfile`, `hashlib`, `zlib`, `json`, `csv`, and `struct`. The interpreter is not bundled.

Reference: https://www.python.org/  
License: PSF License

## External tools

### Ghidra

Used for reverse engineering and by the optional Java label script. Not distributed with this toolkit.

Upstream: https://github.com/NationalSecurityAgency/ghidra  
License: Apache-2.0

### XEXLoaderWV

Used by the project owner to load Xbox 360 XEX files into Ghidra. No code is bundled or copied.

Upstream: https://github.com/zeroKilo/XEXLoaderWV  
Original author credit in the repository: Warranty Voider

### FFmpeg

Invoked as a separate process when installed by the user. It is not linked, modified, or redistributed by this package.

Upstream: https://ffmpeg.org/  
License: LGPL-2.1-or-later by default; GPL terms may apply to particular builds.

### OpenSSL

When an `openssl` executable is available, the finalized PS3 PKG reader may invoke it as a separate process for AES-128-CTR acceleration. The toolkit does not link to or redistribute OpenSSL and retains its locally written Python AES fallback.

Upstream: https://openssl-library.org/  
License: Apache-2.0 for OpenSSL 3.0 and later; older releases use their historical OpenSSL/SSLeay terms.

### vgmstream

The Sony BNK parser (`src/meta/bnk_sony.c`) and PS-ADPCM decoder (`src/coding/psx_decoder.c`) were explicitly consulted as behavioral/field-layout cross-checks while implementing SIIG's narrow independent Python reader/decoder. No vgmstream source is copied or vendored. vgmstream also remains a recommended external fallback for unsupported game-audio variants.

Upstream: https://github.com/vgmstream/vgmstream  
Sony BNK reference: https://github.com/vgmstream/vgmstream/blob/master/src/meta/bnk_sony.c  
PS-ADPCM reference: https://github.com/vgmstream/vgmstream/blob/master/src/coding/psx_decoder.c  
License: ISC-style terms in upstream `COPYING`  
Consulted snapshot: `master`, 2026-09-05; exact commit hash was not captured by this project.

### TrueAncestor EDAT Rebuilder

Historically used externally to obtain decrypted PS3 SDAT payloads before internal SIIG SDAT support was completed. It remains a fallback reference only. No TrueAncestor code or files are included. Because an explicit redistribution/source license was not identified in this audit, it remains strictly a user-supplied external tool.

Reference: https://www.psx-place.com/resources/trueancestor-edat-rebuilder-by-jjkkyu.34/  
Author: JjKkYu

## Locally authored container support

The STFS and PS3 PKG readers are clean-room project implementations. They do not incorporate code from a third-party container reader. See `docs/project/SOURCE_AUDIT.md` and `docs/guides/CONTAINER_INPUT_NOTES.md` for evidence and test boundaries.


## Blender

Blender is an optional external host for `addons/SIIG_Blender_Addon_v0.4.0.zip`. Blender is not bundled. The add-on is locally authored, imports `bpy` at runtime, and invokes Blender's built-in glTF importer after the toolkit creates a temporary glTF file. No Blender source code is copied into the toolkit.

WIP187 also consults public psx-spx SPU documentation to cross-check Sony ADPCM loop-start/repeat/end control-bit meanings. No psx-spx implementation code is copied or bundled.
