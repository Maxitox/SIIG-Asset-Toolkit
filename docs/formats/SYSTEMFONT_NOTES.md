# SIIG system font findings

`systemfont.crp` is not a standalone font-container format. It is the game's ordinary Xbox 360 TEX format with every byte XORed by `0xF1`.

The supplied `default.xex` confirms the exact flow in function `0x8215B010`:

```text
/systemfont.bin.gz → systemfont.crp → XOR 0xF1 → texture loader
```

The decoded atlas is 2048×3392 pixels and consists of 32×32 cells. The glyph map and variable-width metrics are stored in the executable rather than in the CRP itself.

Included files:

- `reference/systemfont/systemfont_glyphs.csv`: 6,732 glyph records with Unicode, atlas rectangle, width, left inset and aliases.
- `reference/systemfont/systemfont.fnt`: AngelCode BMFont text descriptor for 6,730 native Unicode entries.
- `reference/systemfont/systemfont_metadata.json`: table and atlas summary.

The two glyph records with no native Unicode value appear to be special/blank entries. Recovered aliases are listed in the CSV. Retail `Function_8215ACB0` proves the exact alias-scale split: every recovered ASCII alias (letters, digits, space and punctuation) uses 0.5 scale, while the 85-entry halfwidth-katakana alias path retains the default 1.0 scale. The `.fnt` descriptor intentionally contains native mappings only and does not emulate per-alias scaling.
