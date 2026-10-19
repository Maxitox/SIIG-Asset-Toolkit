# SIIG systemfont alias scale — dev24 closure

## Result

Retail Xbox `Function_8215ACB0` closes the remaining scale ambiguity for every alias represented in `reference/systemfont/systemfont_glyphs.csv`.

The runtime starts each glyph lookup with scale `1.0` and then follows one of three relevant alias paths:

1. ASCII digits `0..9`, uppercase `A..Z`, and lowercase `a..z` map arithmetically to the corresponding fullwidth glyph indices and set scale to `0.5`.
2. When a glyph is not native, the 73-entry table at `DAT_820221F8` is searched. Its nonzero entries are the recovered ASCII space/punctuation aliases at the same target-glyph indexes. A hit explicitly writes scale `0.5`.
3. Remaining aliases are searched in the 85-entry table at `DAT_820220A0`. That table contains the halfwidth-katakana UTF-8 keys. Hits map into the native katakana range beginning at glyph index `0xEB` (with the documented dakuten/handakuten pair handling) and **do not alter the default scale `1.0`**.

The later `glyph_index > 0x1A13 && glyph_index != 0xD09` half-scale guard does not apply to these halfwidth aliases because their mapped target indices are in the low katakana range.

## Recovered alias corpus

The current CSV contains 152 alias entries before duplicate-cmap suppression:

- 94 ASCII aliases -> exact runtime scale `0.5`.
- 58 halfwidth-katakana aliases -> exact runtime scale `1.0`.
- 0 aliases remain with unresolved scale.

Three halfwidth aliases repeat an already-mapped codepoint (`ｲ`, `ｴ`, `ﾜ`) for alternate native characters, so the convenience-font cmap keeps the first mapping exactly as before. The generated font therefore exposes 149 unique aliases.

## Derived-font consequence

`tools/systemfont_derived_font.py` now applies the executable-backed split instead of treating punctuation and halfwidth katakana as approximate. A real-retail local build produced:

- 6,730 native Unicode glyphs;
- 149 unique alias glyphs;
- 6,879 cmap entries total;
- 94 half-scale aliases;
- 55 unique native-scale aliases after duplicate suppression;
- 0 approximate aliases.

The generator still produces bitmap-to-outline convenience fonts only. This does not recover the original authoring TTF/OTF, and generated fonts continue to embed copyrighted game glyph artwork and are not bundled with the public/source toolkit.

## Evidence boundary

This result proves alias scale/mapping behavior. It does not change the already documented 32 px atlas, baseline, threshold-to-rectangle outline approximation, or redistribution boundary.
