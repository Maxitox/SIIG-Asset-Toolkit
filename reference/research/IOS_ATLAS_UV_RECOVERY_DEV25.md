# iOS atlas / sprite-UV recovery research — dev25

Status: active research for unsealed `2.10.0-dev25`. Sealed `2.10.0-dev23` remains immutable.

## New evidence

The supplied iOS 4.1.0 application contains `texture.tzip`, a zlib-compressed binary property list. Decompressing and parsing that plist exposes the original texture filenames and image payloads directly. Its `common512.png` payload is **512×1024 RGBA**, which is a useful cross-platform reference but is not the Xbox retail atlas dimensions observed elsewhere in the project. Therefore iOS coordinates must not be copied blindly into the Xbox atlas editor.

The armv7 executable also retains a substantial local C++ symbol table. Relevant recovered symbols include:

- `__ZL10mapUVTable` at `0x002E79AC`, size `0x188` bytes before `imagefont`.
- `__ZL15endingTextureId` at `0x002F23DC`, size `0x20` bytes before `endingTextureUV`.
- `__ZL15endingTextureUV` at `0x002F23FC`, size `0x40` bytes before `survivalRouteTableR`.
- `__ZL17stageTextureTable` at `0x00345D40`.
- `__ZL11tImageTable` at `0x00346370`.
- `__ZL11drawTexture` at `0x0035E484`.

The `mapUVTable` data is especially clear: it is 392 bytes = 98 uint32 values = 49 `(U,V)` pairs. Values run from `0x00` through `0x180` in `0x40` increments, forming a 7×7 grid of 64-pixel map-tile origins. This is **not** the general `common512` sprite table; it is evidence for a separate map/tile UV table.

`endingTextureUV` is a 64-byte table containing repeated `0x000` / `0x100` coordinates, paired with eight `endingTextureId` entries. It demonstrates another native UV-table pattern but is specific to ending textures.

## Sprite renderer evidence

The iOS executable exposes these renderer entry points:

- `addCommandSprite`
- `addCommandSpriteN`
- `addCommandSpriteN2`
- `addCommandSpriteR`
- `addCommandSpriteIN`
- `addCommandSpriteIN2`
- corresponding `...Quads` and texture-sprite variants

Their signatures explicitly carry `textureU0`, `textureV0`, `textureU1`, `textureV1`, followed by position, width, height, rotation and draw flags. The shared `_addCommandSpriteCore` stores these four UV arguments directly in the sprite command structure; it does not itself derive the rectangle from alpha pixels.

Static call sites in the executable load concrete numeric U/V values before calling the sprite commands. This is strong evidence that the native sprite allocation is represented by **game-authored UV rectangles/coordinates at the draw-resource layer**, rather than being recoverable solely from transparent-pixel bounds.

## Naming / duplicate implications

The native renderer does not require the image content itself to be unique. Two different draw records can reference the same atlas rectangle or two different rectangles containing byte-identical pixels. Therefore the Atlas Inspector will continue to use stable technical slot IDs and will not merge duplicate-looking regions.

Semantic names should be assigned only when an executable/data reference or project-owner evidence identifies the slot. Automatic labels based on visual similarity remain prohibited.

## Next research target

The next step is to trace the callers that set `textureU0..textureV1` while establishing the active texture ID, especially the draw routines associated with `common512.png` and the other common 2D atlases. The goal is to recover records of the form:

`texture resource -> sprite/draw identity -> U0,V0,U1,V1 -> draw width/height -> semantic caller`

That should let the Atlas Inspector replace its current conservative alpha/content regions with authoritative native allocation rectangles.

The current `atlas-inspect` implementation therefore remains intentionally conservative. It must not promote `mapUVTable`, `endingTextureUV`, or iOS-only atlas dimensions into Xbox `common512` sprite metadata without caller-level proof.
