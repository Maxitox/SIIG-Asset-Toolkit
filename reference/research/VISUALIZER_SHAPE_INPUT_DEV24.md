# Visualizer SHAPE input fidelity — dev24

## Result

Retail `visualizer.bin` contains the exact ten resources already recovered by name/order: `WhiteCircle`, `line`, `3line`, `square`, `triangle` and their five `*2` variants. A private retail Xbox full-rip probe converted all ten through the toolkit's existing TEX→PNG path; every result is exactly **128×128**, matching the executable source-image footprint.

The Visualizer Simulator dataset v6 now searches a user-supplied full rip for those exact converted PNG names under the Visualizer extraction tree. If all or some are present, their PNG bytes are embedded only in the **locally generated HTML** as data URIs. No proprietary pixels are added to the source-only toolkit.

The serialized Xbox TEX resource header is now decoded too. All ten retail SHAPE TEX files share the same six-dword fetch constant; X/Y/Z addressing is repeat, mag/min/mip filtering is point, and anisotropy is disabled. The locally generated browser therefore disables image smoothing around the transformed real-SHAPE draw. See `VISUALIZER_SHAPE_SAMPLER_DEV24.md`.

The retail `ScreenSpritePS` path is now decoded as `sampled_shape.rgba × runtime_tint.rgba`, followed by SrcAlpha/OneMinusSrcAlpha source-over blending. Browser rendering therefore retains each supplied PNG's original RGBA, multiplies all four channels by the recovered runtime tint, and keeps point sampling for the transformed draw. The earlier luminance×alpha mask / `source-in` bridge has been removed. If no real PNG is available, the procedural stand-in remains a source-only approximation.

## Private validation

`validation/VISUALIZER_SHAPE_INPUT_2.10.0-dev24.json` records dimensions and PNG SHA-256 values only. `validation/VISUALIZER_SHAPE_SAMPLER_2.10.0-dev24.json` records the common resource-header/fetch metadata. Neither contains sprite pixels; the retail image bytes remain outside the source package.
