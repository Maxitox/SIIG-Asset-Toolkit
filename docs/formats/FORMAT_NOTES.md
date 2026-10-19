# 3D stage, wall, ANM, and shader update

The formerly unresolved Bmap/Xmap, wall/Xwall, stage generator, standalone ANM, and Xbox 360 shader-container layouts are now structurally decoded. See `docs/formats/STAGE3D_NOTES.md`, `docs/formats/ANM_NOTES.md`, and `docs/formats/XENOS_SHADER_NOTES.md`. Xenos instruction disassembly, five auxiliary-vector role names, and complete runtime playback remain unresolved.

# MAP renderer correction and atlas resolution

The June 10 XEX confirms that MAP cells are 2D tile/sprite data: `0` is empty, the lower six bits are one-based tile IDs `1..49`, `0x40` flips X, and `0x80` flips Y. The files do not place 3D wall GMX resources. Runtime resource IDs 6, 7, 8, and 9 now resolve to `fence1_512`, `fence2_512`, `fence6_512a`, and `fence3_512`, using the verified 7×7 atlas layout. Exact player-facing layer labels remain unresolved; SCROLL_01/02/03 runtime trajectories are reconstructed in Stage Explorer v8 proof-of-concept preview, while exact gameplay viewport/camera composition remains bounded. See `docs/formats/MAP_RENDERER_NOTES.md`.

# Reverse-engineered format notes

These notes distinguish fields confirmed by the game executable and corpus-wide validation from portions that remain incomplete.

## BBX container — confirmed

All multibyte fields are big-endian.

```text
0x00  4   magic: 01 42 42 58
0x04  4   resource count
0x08  4   archive mode
0x0C  4   filename-hash seed
0x10 16   reserved / runtime-related header fields
0x20 ...  resource records, 0x10 bytes each
```

Each resource record is:

```text
+0x00  u32  payload offset, relative to BBX base
+0x04  u32  payload size
+0x08  u32  null-terminated filename offset, or zero when unnamed
+0x0C  u32  game-specific filename identifier/hash
```

For archive modes 0 and 1, the record table is followed by a sorted array of `{hash, resource_index}` pairs, each 8 bytes. The executable can use this table for name lookup.

The toolkit reimplements the exact PowerPC hash routine found at `0x824739D0` and supports the seed at header offset `0x0C`.

### Runtime resource table — confirmed

After loading an archive, the game registers resources in 0x88-byte records:

```c
struct ResourceEntry {
    char     name[0x80];
    void*    data;       // +0x80
    uint32_t size;       // +0x84
};
```

The executable enumerates every BBX resource as `(name, data, size)` and copies it into this table.

## GMX model/scene format — geometry, hierarchy, materials and animation fields confirmed

GMX is a sequential big-endian chunk stream. Every chunk begins with:

```text
+0x00  char[4]  tag
+0x04  u32      total chunk size, including the 8-byte header
```

Common tags include:

```text
GMX  SHAD  MTRL  PARE  BONE  MESH  ARRY  ANIM
```

### ARRY chunk

```text
+0x08  u16  array index
+0x0A  u16  flags
+0x10  char[16] semantic, such as IN.position / IN.normal / IN.texuv / IN.color
+0x20  u32  attribute slot
+0x24  u32  components per element
+0x28  u32  OpenGL-style scalar type
+0x2C  u32  element count
+0x30  ...  big-endian array data
```

Observed scalar types:

```text
0x1406  float32
0x1403  uint16
```

### MESH chunk

```text
+0x08  u16  mesh index
+0x0A  u16  flags
+0x10  u32  primitive mode
+0x14  u32  not yet named
+0x18  u32  index count
+0x1C  u16  skin index
+0x1E  u16  ARRY-reference count
+0x20  u16[] referenced ARRY indices
```

Observed primitive modes:

```text
0x0001  lines
0x0004  triangles
```

The OBJ converter writes positions, normals, UVs, indexed faces and indexed lines. Colors are recognized and reported in JSON but Wavefront OBJ has no universally supported vertex-color representation. The glTF exporter preserves vertex colors directly.

### TXIF and SHAD chunks

Both are fixed 0x30-byte records:

```text
+0x08  u16       record index
+0x0A  u16       flags
+0x10  char[32]  texture filename (TXIF) or shader name (SHAD)
```

The textured corpus references `ptn_001.dds`; observed shader names are `no_texture` and `texture`.

### MTRL chunk

```text
+0x08  u16       material index
+0x0A  u16       flags
+0x10  char[32]  material name
+0x30  u32       SHAD index
+0x34  u32       parameter count
+0x38  ...       variable parameter records
```

Each parameter begins with a 48-byte name, followed by a type and count/reference field. Type 0 stores float scalars/vectors, type 1 stores 4×4 matrices, and type 2 stores a TXIF index. Observed parameter names are `mWVP`, `DiffuseSampler`, `DiffuseColor`, `DiffuseAlpha`, and `EmissiveColor`.

### PARE and BONE hierarchy

`PARE` records describe a parent and all of its children:

```text
+0x10  u32    child count
+0x14  s32    parent BONE index (-1 for a root)
+0x18  u32[]  child BONE indices
```

`BONE` is a fixed 0x80-byte record:

```text
+0x08  u16       bone/node index
+0x0A  u16       flags
+0x10  char[32]  node name
+0x30  float[16] local 4×4 transform (big-endian, row-vector storage)
+0x70  u32       attachment count
+0x74  u32[]     encoded attachments
```

Attachment type 2 references a MTRL and type 3 references a MESH; the low 16 bits are the record index. All 1,938 mesh-bearing nodes in the supplied corpus have one material and one mesh attachment.

### MOTN and ANIM chunks

`MOTN` is a fixed 0x20-byte motion descriptor containing the motion index in the upper 16 bits of the field at +0x08 and a float duration at +0x14.

`ANIM` stores one transform track:

```text
+0x08  u32       encoded motion index
+0x10  u32       target BONE index
+0x14  u32       channel type (12 observed)
+0x18  u32       key count
+0x1C  u32       values per key (16 observed)
+0x20  float[]   key times
        float[]   key_count × 16 transform matrices
```

The animation matrices use conventional row-major transform storage and are decomposed into glTF translation, quaternion rotation and scale channels. See `docs/formats/GMX_GLTF_NOTES.md`.

## TEX texture format — confirmed for all supplied textures

A `.tex` file consists of:

```text
0x00  0x1C bytes  serialized Xbox 360 D3D resource fields
0x1C  0x18 bytes  six-dword Xenos texture-fetch constant
0x34  ...         tiled GPU pixel data
```

All 54 supplied textures use:

```text
Xenos format       6 (8_8_8_8)
Endian mode        2 (8-in-32)
Tiled              yes
Channel swizzle    Z, Y, X, W
```

The logical width and height are encoded in fetch dword 2 as 13-bit minus-one fields. The physical row pitch is encoded in 32-pixel units in fetch dword 0. Pixel data uses the Xbox 360 32×32 tiled address layout. The 2D pipe selector is `((x >> 3) & 3) XOR (((y >> 3) & 1) << 1)`; omitting the Y[3] XOR produces repeating 8-row jitter. The corrected converter applies this bank/pipe mapping, then the endian transform and channel swizzle. It was validated against the controller icons, yielding the expected green A, red B, blue X and yellow Y, and against larger UI/atlas textures.

As of 2.9.0-dev3 this confirmed uniform layout is also used for donor-free Xbox TEX synthesis. The builder aligns physical pitch to 32 pixels, aligns the tiled allocation height to 32 rows, emits the canonical fetch fields above, and then uses the same addressing/endian/swizzle inverse path to encode RGBA pixels. This supports new logical dimensions while keeping the synthesized format inside the observed SIIG Xbox texture family.

## Sound archive and XACT banks — confirmed

`sound.bin` contains four nested BBX archives with XACT3 sound-bank/wave-bank pairs:

```text
se/SE.xsb                         83 cues
se/SE.xwb                         83 waves
bgm/BGM_007.xsb                   1 cue
bgm/BGM_007.xwb                   1 wave
bgm/BGM_008.xsb                   1 cue
bgm/BGM_008.xwb                   1 wave
bgm/BGM_XACT_SE33.xsb             1 cue
bgm/BGM_XACT_SE33.xwb             1 wave
```

All four XWB files are big-endian Xbox 360 XACT3 version 46 (`DNBW`, version `0x2E`) standard wave banks. Their entries are 24 bytes each and use XMA2. The bank data is aligned to `0x800` bytes. The mini-wave-format bit fields decode as:

```text
bits  0..1    codec tag (1 = XMA2)
bits  2..4    channel count
bits  5..22   sample rate
bits 23..30   block-align field
bit  31       bit-depth flag
```

The standard entry layout is:

```text
+0x00  u32  low 4 bits flags; upper 28 bits decoded sample count
+0x04  u32  packed mini-wave-format
+0x08  u32  relative wave-data offset
+0x0C  u32  compressed data size
+0x10  u32  loop start in samples
+0x14  u32  loop length in samples
```

The XSB files provide cue names. In this title each cue maps sequentially to one XWB wave, yielding 86 named streams total. The toolkit wraps each raw Xbox 360 XMA2 stream in a standard RIFF/XMA2 header, then calls FFmpeg when available to produce PCM WAV.


## Localization databases — confirmed

`text.bin` is a mode-3 BBX containing seven anonymous, line-aligned UTF-8 payloads: one 542-line identifier list followed by Japanese, English, French, Italian, German and Spanish values. The executable pairs the identifier and selected-language lines by index.

`message.bin` is a mode-3 BBX containing six Shift-JIS Squirrel source payloads in Japanese-locale/default-English, English, French, Italian, German and Spanish order. Every payload defines the same 284 arrays and 1,295 strings. Several accented uppercase glyphs use language-specific ASCII placeholders; the toolkit exports both source-exact and Unicode-corrected forms.

See `docs/formats/LOCALIZATION_NOTES.md` for field/order and substitution details.

## DAT command streams — binary structure confirmed

All generator and stage-script `.dat` resources use the same big-endian variable-record layout:

```text
+0x00  u8      format version (1)
+0x01  u16 BE  command count
+0x03  ...     command records

record:
+0x00  u8      number of following 16-bit words
+0x01  s16 BE  delta frame from the previous command
+0x03  u16 BE  opcode ID
+0x05  s16 BE[] opcode-specific parameters
```

The runtime loader flattens the records into a 16-bit word array, replaces each first word with the accumulated absolute frame, and stores an index to each command. The executor compares that frame against the current script frame and dispatches on word 1. The June 10 executable contains a 207-slot opcode-name table (`0x00` through `0xCE`); 113 opcodes occur in the supplied data.

The exact meaning of many opcode-specific parameter positions remains only partially identified, so exports preserve signed values and hexadecimal words without speculative labels.

## MAP byte grids — binary structure confirmed

```text
+0x00  char[4]  `MAP\0`
+0x04  u32 BE   layer count (3 in every supplied file)
+0x08  ...      repeated layer records

layer:
+0x00  u32 BE   width
+0x04  u32 BE   height
+0x08  u8[]     width * height row-major cells
```

Zero-sized layers contain only their 8-byte dimension record. The stage-generator loader copies each layer byte-for-byte into independent buffers and appends each block by `width * height`. Cell decoding is confirmed: zero is empty, the lower six bits are one-based tile IDs 1–49, bit 0x40 reflects X, and bit 0x80 reflects Y. Exact player-facing layer labels remain unresolved; the SCROLL_01/02/03 runtime trajectories are available in the Stage Explorer v8 proof-of-concept preview, while exact gameplay viewport/camera composition remains bounded.

## Remaining semantic work

The major container layouts are decoded. Remaining work is chiefly semantic rather than structural:

- label the remaining opcode-specific DAT parameters and unnamed opcode IDs
- identify trustworthy player-facing names/roles for the three 2D MAP layers and any remaining gameplay-specific viewport composition rules
- assign proven names to the five auxiliary vectors in each 3D stage-path record
- disassemble or translate platform-specific compiled shader instructions beyond bounded raw-microcode extraction
- reconstruct complete frame-accurate 2D/3D stage playback

## System font CRP — confirmed

The font path is handled by `default.xex` function `0x8215B010`. It constructs `/systemfont.bin.gz` and `systemfont.crp`, retrieves the CRP payload from BBX, XORs every 32-bit word with `0xF1F1F1F1` (and remaining bytes with `0xF1`), then sends the decrypted buffer to the normal texture constructor.

Therefore:

```text
systemfont.crp byte N XOR 0xF1 = decrypted TEX byte N
```

The decrypted texture uses the same 0x34-byte TEX header and Xenos texture layout as other game textures:

```text
logical dimensions   2048 × 3392
physical pitch       2048
format                6 (8_8_8_8)
endian                 2 (8-in-32)
swizzle               Z,Y,X,W
tiled                  yes
payload size           27,787,264 bytes
```

The atlas is divided into 32×32 cells, yielding 64 columns and 106 rows. The executable's glyph table begins at `0x8200E508`, contains `0x1A4C` (6,732) records, and has a 12-byte stride:

```text
+0x00  byte[4]  packed UTF-8 sequence, zero-padded
+0x04  u32 BE   visible glyph width
+0x08  u32 BE   left crop/inset inside the 32-pixel cell
```

For glyph index `i`:

```text
cell_x  = (i % 64) * 32
cell_y  = (i / 64) * 32
glyph_x = cell_x + left_inset
glyph_y = cell_y
```

The game computes UVs with divisors 2048 and 3392. Retail `Function_8215ACB0` proves the alias-scale paths: ASCII digits/letters map directly at 0.5 scale; the 73-entry ASCII space/punctuation alias table also sets 0.5; and the 85-entry halfwidth-katakana table maps into the native katakana glyph range while retaining scale 1.0.

## COL collision masks

COL is a 16-byte big-endian header followed by `width * height` one-bit pixels packed LSB-first. Observed headers are `(512, 256, 1, 0)` and `(512, 1024, 4, 0)`.

## Standalone ANM tables

ANM is a sequence of 28-byte records: `char name[16]`, big-endian `float start_frame`, big-endian `float end_frame`, and big-endian `uint32 loop_flag`. The executable-backed standalone animation player consumes those fields as an authored frame range plus loop control; this supersedes the older provisional `char[20] + unknown float/uint32` description.
