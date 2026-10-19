#!/usr/bin/env python3
"""Build local-use desktop/web fonts from SIIG's decoded systemfont atlas.

This is an optional experiment, intentionally kept outside the dependency-free core
SIIG toolkit.  It DOES NOT recover the original authoring font or vector outlines.
Instead it thresholds the game's 32 px alpha glyphs and converts contiguous bitmap
runs into block-outline contours while preserving the recovered Unicode mapping,
advance widths, 32 px line height and 28 px baseline.

Required: Pillow, fontTools.  WOFF2 additionally needs brotli (fontTools will report
an error when unavailable).

Do not redistribute generated fonts unless you have the rights to the source game
font artwork.  The script itself contains no game glyph data.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Iterable

try:
    from PIL import Image
    from fontTools.fontBuilder import FontBuilder
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    from fontTools.pens.t2CharStringPen import T2CharStringPen
except ImportError as exc:  # pragma: no cover - optional local experiment
    raise SystemExit("systemfont derived-font experiment requires Pillow and fontTools") from exc

UNITS_PER_EM = 1024
PX_SCALE = 32  # 32 source pixels -> 1024 em units
SOURCE_LINE_HEIGHT = 32
SOURCE_BASELINE = 28
ASCENT = SOURCE_BASELINE * PX_SCALE
DESCENT = -(SOURCE_LINE_HEIGHT - SOURCE_BASELINE) * PX_SCALE


def _glyph_name(codepoint: int) -> str:
    return f"uni{codepoint:04X}" if codepoint <= 0xFFFF else f"u{codepoint:06X}"


def _parse_codepoint(value: str) -> int:
    text = value.strip().upper()
    if not text.startswith("U+"):
        raise ValueError(f"bad Unicode field {value!r}")
    return int(text[2:], 16)


def load_rows(csv_path: Path) -> list[dict]:
    rows: list[dict] = []
    with csv_path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            u = (row.get("unicode") or "").strip()
            if not u:
                continue
            try:
                cp = _parse_codepoint(u)
                width = int(row["glyph_width"])
                height = int(row["glyph_height"])
                x = int(row["glyph_x"])
                y = int(row["glyph_y"])
                adv = int(row.get("xadvance") or width)
            except (KeyError, ValueError) as exc:
                raise ValueError(f"invalid glyph row {row!r}") from exc
            if cp < 0 or cp > 0x10FFFF or 0xD800 <= cp <= 0xDFFF:
                continue
            rows.append({
                "codepoint": cp, "x": x, "y": y, "width": width, "height": height, "advance": adv,
                "aliases": list(row.get("aliases") or ""),
            })
    # The executable table has unique native mappings; keep the first defensively.
    dedup: dict[int, dict] = {}
    for row in rows:
        dedup.setdefault(row["codepoint"], row)
    return [dedup[cp] for cp in sorted(dedup)]


def _row_runs(alpha, y: int, width: int, threshold: int) -> list[tuple[int, int]]:
    runs: list[tuple[int, int]] = []
    x = 0
    while x < width:
        while x < width and alpha[x, y] < threshold:
            x += 1
        if x >= width:
            break
        start = x
        while x < width and alpha[x, y] >= threshold:
            x += 1
        runs.append((start, x))
    return runs


def bitmap_rectangles(alpha_image: Image.Image, threshold: int) -> list[tuple[int, int, int, int]]:
    """Merge equal horizontal alpha runs vertically into pixel rectangles."""
    alpha = alpha_image.load()
    width, height = alpha_image.size
    active: dict[tuple[int, int], list[int]] = {}
    out: list[tuple[int, int, int, int]] = []
    for y in range(height):
        current = set(_row_runs(alpha, y, width, threshold))
        for key in list(active):
            if key not in current:
                x0, x1 = key
                y0, y1 = active.pop(key)
                out.append((x0, y0, x1, y1))
        for key in current:
            if key in active:
                active[key][1] = y + 1
            else:
                active[key] = [y, y + 1]
    for (x0, x1), (y0, y1) in active.items():
        out.append((x0, y0, x1, y1))
    return out


def _draw_rects(pen, rects: Iterable[tuple[int, int, int, int]]) -> None:
    for x0, y0, x1, y1 in rects:
        # Source Y points down; font Y points up around baseline pixel 28.
        left = x0 * PX_SCALE
        right = x1 * PX_SCALE
        top = (SOURCE_BASELINE - y0) * PX_SCALE
        bottom = (SOURCE_BASELINE - y1) * PX_SCALE
        pen.moveTo((left, bottom))
        pen.lineTo((right, bottom))
        pen.lineTo((right, top))
        pen.lineTo((left, top))
        pen.closePath()


def _scale_rects(rects: Iterable[tuple[int, int, int, int]], sx: float, sy: float) -> list[tuple[float, float, float, float]]:
    return [(x0 * sx, y0 * sy, x1 * sx, y1 * sy) for x0, y0, x1, y1 in rects]


def _alias_scale(alias: str) -> tuple[float, float, str]:
    """Return the executable-backed runtime scale for a recovered alias.

    Retail Xbox Function_8215ACB0 uses three alias paths:

    * ASCII digits/letters map directly to fullwidth glyphs and set scale 0.5.
    * The 73-entry DAT_820221F8 ASCII alias table (space/punctuation included)
      also sets scale 0.5 when it matches.
    * The 85-entry DAT_820220A0 halfwidth-katakana table maps into the native
      katakana glyph range without changing the default scale 1.0.

    The current recovered alias corpus contains only those two classes. Keep an
    explicit unresolved fallback so future aliases cannot silently inherit a
    guessed scale.
    """
    if len(alias) == 1 and alias.isascii():
        return 0.5, 0.5, "recovered_uniform_half_scale"
    if len(alias) == 1 and 0xFF61 <= ord(alias) <= 0xFF9F:
        return 1.0, 1.0, "recovered_uniform_native_scale"
    return 1.0, 1.0, "alias_mapping_recovered_scale_unresolved"


def _common_builder(is_ttf: bool, glyph_order: list[str], cmap: dict[int, str], metrics: dict[str, tuple[int, int]]) -> FontBuilder:
    fb = FontBuilder(UNITS_PER_EM, isTTF=is_ttf)
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap(cmap)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=ASCENT, descent=DESCENT, lineGap=0)
    fb.setupNameTable({
        "familyName": "SIIG System Font Derived",
        "styleName": "Bitmap Outline",
        "uniqueFontIdentifier": "SIIG-System-Font-Derived-BitmapOutline-v1",
        "fullName": "SIIG System Font Derived Bitmap Outline",
        "psName": "SIIGSystemFontDerived-BitmapOutline",
        "version": "Version 0.1; derived experiment; not original vector font",
        "copyright": "Derived locally from user-supplied game bitmap data; redistribution rights are not granted by this tool.",
        "description": "Experimental bitmap-to-outline derivative of the SIIG systemfont atlas. Not the original authoring font.",
    })
    fb.setupOS2(
        sTypoAscender=ASCENT,
        sTypoDescender=DESCENT,
        sTypoLineGap=0,
        usWinAscent=ASCENT,
        usWinDescent=-DESCENT,
        sxHeight=16 * PX_SCALE,
        sCapHeight=24 * PX_SCALE,
    )
    fb.setupPost()
    return fb


def build_fonts(atlas_path: Path, csv_path: Path, output_dir: Path, threshold: int, formats: list[str]) -> dict:
    atlas = Image.open(atlas_path).convert("RGBA")
    rows = load_rows(csv_path)
    native_names = {_glyph_name(row["codepoint"]) for row in rows}
    glyph_order = [".notdef"] + [_glyph_name(row["codepoint"]) for row in rows]
    cmap = {row["codepoint"]: _glyph_name(row["codepoint"]) for row in rows}
    metrics = {".notdef": (16 * PX_SCALE, 0)}
    rects_by_name: dict[str, list[tuple[float, float, float, float]]] = {".notdef": []}
    total_rects = 0
    alias_records: list[dict] = []
    for row in rows:
        name = _glyph_name(row["codepoint"])
        width = max(0, row["width"])
        height = max(0, row["height"])
        crop = atlas.crop((row["x"], row["y"], row["x"] + width, row["y"] + height)).getchannel("A")
        rects = bitmap_rectangles(crop, threshold) if width and height else []
        rects_by_name[name] = rects
        total_rects += len(rects)
        metrics[name] = (max(1, row["advance"]) * PX_SCALE, 0)
        for alias in row.get("aliases", []):
            if not alias or len(alias) != 1:
                continue
            cp = ord(alias)
            if cp in cmap or 0xD800 <= cp <= 0xDFFF:
                continue
            sx, sy, status = _alias_scale(alias)
            alias_name = f"alias{cp:04X}" if cp <= 0xFFFF else f"alias{cp:06X}"
            # Avoid a pathological name collision while preserving one cmap target per alias.
            if alias_name in native_names or alias_name in rects_by_name:
                alias_name = f"alias_{cp:X}_{row['codepoint']:X}"
            alias_rects = _scale_rects(rects, sx, sy)
            rects_by_name[alias_name] = alias_rects
            metrics[alias_name] = (max(1, round(row["advance"] * sx)) * PX_SCALE, 0)
            glyph_order.append(alias_name)
            cmap[cp] = alias_name
            total_rects += len(alias_rects)
            alias_records.append({
                "alias": alias, "codepoint": f"U+{cp:04X}", "source": f"U+{row['codepoint']:04X}",
                "scale_x": sx, "scale_y": sy, "status": status,
            })

    output_dir.mkdir(parents=True, exist_ok=True)
    generated: list[dict] = []

    ttf_font = None
    if any(fmt in {"ttf", "woff", "woff2"} for fmt in formats):
        fb = _common_builder(True, glyph_order, cmap, metrics)
        glyphs = {}
        for name in glyph_order:
            pen = TTGlyphPen(None)
            _draw_rects(pen, rects_by_name[name])
            glyphs[name] = pen.glyph()
        fb.setupGlyf(glyphs)
        fb.setupMaxp()
        ttf_font = fb.font

    for fmt in formats:
        if fmt == "ttf":
            font = ttf_font
            path = output_dir / "SIIG_System_Font_Derived_BitmapOutline.ttf"
            font.flavor = None
        elif fmt in {"woff", "woff2"}:
            font = ttf_font
            path = output_dir / f"SIIG_System_Font_Derived_BitmapOutline.{fmt}"
            font.flavor = fmt
        elif fmt == "otf":
            fb = _common_builder(False, glyph_order, cmap, metrics)
            charstrings = {}
            for name in glyph_order:
                pen = T2CharStringPen(metrics[name][0], None)
                _draw_rects(pen, rects_by_name[name])
                charstrings[name] = pen.getCharString(private=None, globalSubrs=None)
            fb.setupCFF(
                "SIIGSystemFontDerived-BitmapOutline",
                {"FullName": "SIIG System Font Derived Bitmap Outline", "FamilyName": "SIIG System Font Derived", "Weight": "Regular"},
                charstrings,
                {},
            )
            font = fb.font
            path = output_dir / "SIIG_System_Font_Derived_BitmapOutline.otf"
        else:  # argparse guards this
            raise ValueError(fmt)
        font.save(path)
        data = path.read_bytes()
        generated.append({"format": fmt, "file": path.name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
        if fmt in {"woff", "woff2"}:
            font.flavor = None

    report = {
        "format": "SIIG_SYSTEMFONT_DERIVED_FONT_EXPERIMENT",
        "schema": 1,
        "source_atlas": atlas_path.name,
        "source_glyph_table": csv_path.name,
        "native_glyph_count": len(rows),
        "cmap_glyph_count": len(cmap),
        "alias_count": len(alias_records),
        "recovered_half_scale_alias_count": sum(1 for item in alias_records if item["status"] == "recovered_uniform_half_scale"),
        "recovered_native_scale_alias_count": sum(1 for item in alias_records if item["status"] == "recovered_uniform_native_scale"),
        "approximate_alias_count": sum(1 for item in alias_records if item["status"] == "alias_mapping_recovered_scale_unresolved"),
        "alpha_threshold": threshold,
        "units_per_em": UNITS_PER_EM,
        "source_line_height_px": SOURCE_LINE_HEIGHT,
        "source_baseline_px": SOURCE_BASELINE,
        "outline_method": "alpha-threshold bitmap runs merged vertically into rectangular vector contours",
        "rectangle_contours": total_rects,
        "status": "derived convenience font; not original vector outlines",
        "alias_policy": "all recovered aliases now use executable-backed scale: ASCII aliases 0.5; halfwidth-katakana aliases 1.0",
        "redistribution_note": "Generated font embeds source game glyph artwork. Do not redistribute unless you have the necessary rights.",
        "outputs": generated,
    }
    (output_dir / "SIIG_System_Font_Derived_REPORT.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (output_dir / "README.txt").write_text(
        "SIIG System Font derived-font experiment\n\n"
        "These files are bitmap-to-outline derivatives generated from the decoded game atlas.\n"
        "They are NOT a recovery of the original TTF/OTF authoring font. The 32 px atlas is\n"
        "thresholded and represented as rectangular contours, so curves remain pixel-shaped.\n"
        "Recovered Unicode mappings, advances, line height (32 px) and baseline (28 px) are used.\n"
        "ASCII letters/digits (and space for practical layout) use the recovered 0.5 alias scale.\n"
        "Other recovered punctuation/halfwidth aliases are included at native scale and remain approximate.\n\n"
        "Generated fonts embed source game glyph artwork. Keep them local unless you have rights\n"
        "to redistribute that artwork. The SIIG toolkit should ship only the generator code, not\n"
        "these generated font files.\n",
        encoding="utf-8",
    )
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description="Build derived TTF/OTF/WOFF fonts from SIIG systemfont atlas + glyph table")
    ap.add_argument("--atlas", required=True, help="decoded systemfont_atlas.png")
    ap.add_argument("--glyphs", required=True, help="systemfont_glyphs.csv")
    ap.add_argument("--output", required=True, help="output directory")
    ap.add_argument("--threshold", type=int, default=96, choices=range(1, 256), metavar="1..255")
    ap.add_argument("--formats", default="ttf,otf,woff,woff2", help="comma list: ttf,otf,woff,woff2")
    args = ap.parse_args()
    formats = [x.strip().lower() for x in args.formats.split(",") if x.strip()]
    allowed = {"ttf", "otf", "woff", "woff2"}
    bad = [x for x in formats if x not in allowed]
    if bad or not formats:
        ap.error(f"unsupported/empty formats: {bad or formats}; choose from {sorted(allowed)}")
    report = build_fonts(Path(args.atlas), Path(args.glyphs), Path(args.output), args.threshold, formats)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
