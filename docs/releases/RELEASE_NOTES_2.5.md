# SIIG Asset Toolkit 2.5.0 release notes

Version 2.5.0 is a focused Asset Viewer performance and thumbnail-coverage release.

## Asset Viewer 2.0

The viewer is no longer a monolithic self-contained HTML file. It now uses a small HTML shell plus local inventory, thumbnail, and deferred-preview files. This removes base64 inflation and prevents model/text payloads from being parsed before they are needed.

Changes include:

- linked images and browser-compatible audio instead of base64 embedding;
- a compact external `viewer_data.js` inventory;
- a maximum of 32 deferred text/model payload shards;
- paginated card rendering and intersection-based image loading;
- automatic exclusion of the viewer output directory during rebuilds;
- stable payload keys when a GMX or OBJ borrows a related glTF preview;
- expanded size and thumbnail metrics in `ASSET_VIEWER_REPORT.json`.

The deprecated `--max-embed-mib` and `--max-single-preview-mib` options remain accepted for command-line compatibility but no longer embed media.

## Thumbnail coverage

New native thumbnail paths cover:

- direct GMX and OBJ wireframes without requiring a pre-existing glTF;
- Xbox 360 TEX decoding;
- MAP layer overviews, including empty MAPs;
- DAT command-density timelines;
- ANM frame-range timelines;
- WAV waveforms;
- model placeholders for animation-only GMX files and empty path OBJ files;
- matching converted PNG, glTF, and WAV assets.

## Validation

On the 1,759-file structured research rip:

- 1,016 assets were classified as previewable;
- 1,016 thumbnails were generated or associated;
- zero previewable assets were left without a thumbnail;
- the main HTML measured 12,022 bytes;
- the same corpus's v2.4 single-file HTML measured 18,207,366 bytes;
- the HTML reduction was 99.934%;
- all relative references and payload keys resolved;
- the inventory, inline UI JavaScript, and all 32 payload shards passed Node.js syntax checks;
- all 15 built-in regression tests passed.

The complete viewer folder is larger than the HTML because detailed model/text data is intentionally retained as on-demand local payloads. Those files are not loaded during initial page startup.

## Compatibility note

Do not copy only `SIIG_Asset_Viewer.html`. Keep it beside `viewer_assets`. Existing v2.4 viewers can be regenerated in place with v2.5.0; the output directory is excluded from its own inventory so repeated builds do not recursively index prior viewer files.
