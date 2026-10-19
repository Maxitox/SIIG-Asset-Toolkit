# SIIG localization formats

## Recommended editable text.bin sheet (WIP197)

`text2csv` now writes both legacy CSV and **tab-separated UTF-8** exports. For ordinary editing use `text_strings.tsv` (or `text_strings_raw.tsv` when source escapes must stay literal). Mod Workspace tracks `text_strings.tsv` as the canonical editable `text.bin` file. Tabs avoid the regional CSV-delimiter problem where comma-delimited UTF-8 can open as one long value in column A. `text-build` accepts TSV, legacy CSV, and JSON. Per-language `.txt` files remain convenient read-only/reference views.


## `text.bin`

`text.bin` is a mode-3 BBX archive with seven anonymous payloads. Every payload has exactly 542 CRLF-delimited lines:

```text
entry 0  identifiers / lookup keys
entry 1  Japanese UTF-8
entry 2  English UTF-8
entry 3  French UTF-8
entry 4  Italian UTF-8
entry 5  German UTF-8
entry 6  Spanish UTF-8
```

The executable loads entry 0 and the selected-language entry, splits both at CRLF boundaries, and pairs their lines in order. Thus line `N` of entry 0 is the key for line `N` of each translation payload. Some values contain the literal source sequence `\n`; the readable exports expand that sequence into a real line break, while `text_strings_raw.tsv` (and legacy `text_strings_raw.csv`) preserve the source spelling.

The first and last recovered records are:

```text
EVOL_TEXT1      Bonus Stage 1-1 is now available.
RICH_PRESENCE9  Title Screen
```

## `message.bin`

`message.bin` is a mode-3 BBX archive with six anonymous Shift-JIS payloads. The payloads are Squirrel-style source files consisting of assignments such as:

```text
STR_WARNING <- [
"WARNING",
"A FORMIDABLE ENEMY",
"HAS ENTERED THE BATTLE.",
]
```

Language order:

```text
entry 0  Japanese locale / region-default block (the UI strings are intentionally English)
entry 1  English
entry 2  French
entry 3  Italian
entry 4  German
entry 5  Spanish
```

Each payload contains the same 284 array names and 1,295 string values. The source uses language-specific ASCII glyph codes for accented capital letters. For example, French `ESPqCES`, Italian `PIm`, German `ZURkCK`, and Spanish `ATENCIhN` render as `ESPÈCES`, `PIÙ`, `ZURÜCK`, and `ATENCIÓN`. The toolkit preserves the original scripts as `*_raw.nut` and writes Unicode-corrected scripts as `*_readable.nut`.

Confirmed substitutions include:

```text
universal names  p=É, t=Í, k=Ü
French           q=È, v=Î, r=Ê, e=À, y=Œ
Italian          q=È, e=À, m=Ù, u=Ì
German           c=Ä, k=Ü, g=Ö
Spanish          h=Ó, b=Ñ, l=Ú, d=Á, p=É, t=Í, z=¡
```

The `%d` printf sequence is explicitly preserved rather than changing its `d` to `Á` in Spanish.

## Toolkit command

Decode one archive:

```bat
python siig_toolkit.py text2csv "C:\path\to\text.bin" -o localization
python siig_toolkit.py text2csv "C:\path\to\message.bin" -o localization
```

Decode both by pointing at their directory:

```bat
python siig_toolkit.py text2csv "C:\path\to\media" -o localization
```

Important outputs:

```text
localization\text\text_strings.tsv
localization\text\text_strings_raw.tsv
localization\text\text_strings.csv          (legacy compatibility)
localization\text\text_strings_raw.csv      (legacy compatibility)
localization\text\text_strings.json
localization\message\message_strings.tsv
localization\message\message_groups.tsv
localization\message\message_strings.csv    (legacy compatibility)
localization\message\message_strings.json
localization\message\message_*_readable.nut
```


## Native rebuild (dev22)

`text-build` compiles the recommended `text_strings_raw.tsv` / `text_strings.tsv`, legacy CSV, or `text_strings.json` back into a native seven-payload mode-3 BBX using the original `text.bin` as a structural template:

```bat
python siig_toolkit.py text-build localization\text\text_strings.tsv --template text.bin -o text_mod.bin
```

It preserves the BBX header/seed/identifiers/payload order plus the template newline and trailing-newline convention. Readable fields are converted back from real newlines/tabs to the source escape spelling.

`message-build` compiles the six Unicode-readable Squirrel scripts back into native Shift-JIS payloads:

```bat
python siig_toolkit.py message-build localization\message --template message.bin -o message_mod.bin
```

The builder reverses the language-specific accent substitutions documented above before Shift-JIS encoding and validates matching group/order/count across all six languages. `--raw` consumes the source-exact `_raw.nut` scripts instead.

Dev22's byte-identity rebuild gates use canonical synthetic localization fixtures; runtime acceptance of arbitrary edited strings is not claimed.
