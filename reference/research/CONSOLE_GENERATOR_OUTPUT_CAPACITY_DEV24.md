# Console generator output-capacity closure — dev24 WIP163

Status: **runtime capacity mechanism resolved; authored-corpus rationale still open**.

## What was unresolved

Earlier mobile/console lineage work proved the same 330 generator MAP files and 645 nonempty layers on iOS and console, while the console corpus contains exactly twice the total stored cells. It also proved the iOS generated-output capacity as **6,144 bytes (`0x1800`) per layer**, but the matching console allocation path had not been isolated.

## Retail PS3 initializer

The retained retail PS3 executable identifies `stageGenerateMapInit` at `0x001327E8` through its allocator debug string. It creates three output-layer records and reads three adjacent big-endian capacity factors from `0x004B152C`, `0x004B1530`, and `0x004B1534`. The retained listing decodes all three factors as **`0x20`**. For each layer the initializer computes:

```text
capacity = 0x20 * 0x180
         = 0x3000
         = 12,288 bytes
```

The following generator MAP append routine at `0x001329DC` checks each destination write against that same `factor * 0x180` bound before copying a source MAP byte. It also advances the accumulated destination count by `width * height`, confirming this is the actual generated-layer byte capacity rather than unrelated allocator padding.

## iOS ancestor comparison

The retained iOS lineage validation proves:

```text
iOS generated layer = 6,144 bytes = 0x1800
                    = 24 blocks * 8 columns * 32 rows
```

Therefore the executable-level generated-output capacity changed exactly:

```text
0x1800 -> 0x3000
6,144  -> 12,288 bytes/layer
ratio  = 2.0
```

This closes the old **runtime output-buffer capacity** uncertainty. The three-layer architecture and 24-block assembly model remain continuous across the mobile/console lineage.

## Boundary retained

This does **not** prove that console generator MAP content is a byte-for-byte doubled copy of the iOS content: the observed nonzero-cell totals differ nonlinearly (38,253 iOS vs 62,223 console). It also does not reveal the designers' source-level reason for authoring a corpus with exactly twice the total stored-cell count. That higher-level content-authoring rationale remains open in the living dev24 boundary registry.

## Evidence retained in source-only form

- iOS derived capacity: `validation/IOS_CONSOLE_CODE_LINEAGE_DEV18.json`
- PS3 initializer: `0x001327E8` (`stageGenerateMapInit`)
- PS3 append/bounds path: `0x001329DC`
- PS3 factor table: `0x004B152C..0x004B1537` = three big-endian `0x20` values
- Machine-readable closure: `validation/CONSOLE_GENERATOR_OUTPUT_CAPACITY_2.10.0-dev24.json`

No executable bytes or proprietary MAP payloads are bundled.
