# Optional tools

- `ghidra/ApplySIIGFunctionNames.java` applies confirmed labels during Ghidra research.

- `systemfont_derived_font.py` is an optional Pillow + fontTools experiment that converts the recovered 32 px systemfont bitmap atlas into local-use TTF/OTF/WOFF/WOFF2 bitmap-outline derivatives. It does **not** recover original font outlines, and generated fonts are never bundled because they embed game glyph artwork.

Normal extraction and conversion do not require this folder.
