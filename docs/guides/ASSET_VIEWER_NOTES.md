# Offline HTML asset viewer

`asset-viewer` creates a searchable local browser for a full rip or any extracted asset directory.

```bat
python siig_toolkit.py asset-viewer SIIG_Ripped -o SIIG_Ripped\asset_viewer
```

## Linked-data layout in viewer 2.0

Version 2.5.0 no longer places the complete inventory, base64 media, text excerpts, and model wireframes inside one enormous HTML document. A viewer now consists of:

```text
asset_viewer/
  SIIG_Asset_Viewer.html
  ASSET_VIEWER_REPORT.json
  viewer_assets/
    viewer_data.js
    payloads/payload_00.js ... payload_31.js
    thumbnails/*.png and *.svg
```

Keep the HTML and `viewer_assets` directory together. The HTML itself is intentionally small; the local inventory is loaded from `viewer_data.js`, and text/model detail shards are loaded only when an asset is inspected.

No network requests are made. Relative files, local scripts, thumbnails, and previews can normally be opened through `file://`. When a browser applies stricter local-file restrictions, use:

```bat
python siig_toolkit.py serve SIIG_Ripped
```

The server binds only to `127.0.0.1`.

## Performance changes

- Image and audio media are linked rather than base64-embedded.
- Cards are paginated and only the current page is added to the DOM.
- Images use intersection-based lazy loading.
- Detailed text and model data is split across at most 32 local payload shards.
- Rebuilding a viewer inside its source tree excludes the viewer's own output, preventing recursive growth.
- `--max-embed-mib` and `--max-single-preview-mib` remain accepted for compatibility but are deprecated and no longer embed media.
- `--max-text-preview-kib` controls the deferred excerpt size per text file.
- `--page-size` controls the initial number of cards per page.

## Thumbnail sources

The viewer produces or associates thumbnails for:

- PNG, JPEG, GIF, WebP, and BMP images;
- GMX, glTF, and OBJ models using generated wireframes;
- animation-only or empty models using an explicit model-information placeholder;
- Xbox 360 TEX files by decoding the texture locally;
- MAP files using three-layer categorical overviews, including explicit empty-MAP previews;
- DAT files using command-density timelines;
- ANM files using start/end-frame timelines;
- WAV files using sampled waveform previews;
- source assets with matching converted PNG, glTF, or WAV output;
- retained browser-incompatible audio/data (for example WMA/XMA/AT3 and XACT XWB/XSB) using an explicit file-type placeholder when no converted preview exists.

`ASSET_VIEWER_REPORT.json` records direct/derived thumbnail counts, missing-preview counts, HTML/data/payload sizes, and payload-shard totals.

## Validation

The v2.5.0 corpus test indexed 1,759 files totaling 300,776,833 bytes. All 1,016 assets classified as previewable received a thumbnail. The main HTML was 12,022 bytes; the same corpus produced an 18,207,366-byte v2.4 single-file viewer even without hashes, a 99.934% reduction in the HTML document.

Every generated relative reference and payload key was checked, and all executable JavaScript files passed Node.js syntax validation. Interactive browser testing is still recommended on the target desktop browser.

## Preview boundaries

- Wireframes are lightweight inspection aids, not a replacement for Blender. They use sampled local mesh-space geometry and do not reproduce every material, node transform, or animation state.
- Browser-incompatible XMA, AT3, WMA, XWB/XSB, and SBlk/VAG data remains inventoried. A related WAV is used when one exists; otherwise the viewer shows an explicit retained-native placeholder rather than pretending a media preview was decoded.
- Generated viewers and thumbnails may contain game-derived media and should remain private unless redistribution is permitted.
## Update-rip behavior

Asset Viewer is a browser for extracted/converted game assets. Stage Explorer and Visualizer Simulator are sibling tools and do not, by themselves, make the viewer stale. `update-rip` therefore does not rebuild Asset Viewer for a Stage Explorer/Visualizer-only migration.

When the viewer itself must be refreshed, updater staging excludes the existing canonical `asset_viewer/` directory from source inventory. This prevents recursive self-indexing of old viewer HTML, payload shards and thumbnails. Generator-only refreshes may seed reusable thumbnails, while actual indexed-source changes rebuild from the current source tree.

