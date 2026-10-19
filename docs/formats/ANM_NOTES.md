# Standalone ANM frame-range tables

The previous neutral `char[20] + float + integer` interpretation was incorrect. The June 10 executable establishes a fixed 28-byte record:

```text
+0x00  char[16]  model/group name
+0x10  be f32    start frame
+0x14  be f32    end frame
+0x18  be u32    loop flag
```

Consecutive records sharing the same name form one lookup group. The runtime initializes the current frame at the start or end boundary depending on playback direction, advances toward the opposite boundary, and either wraps or stops according to the loop flag.

Corpus validation:

- `enemy.anm`: 90 records, 60 groups
- `map.anm`: 67 records, 67 groups
- `player.anm`: 3 records, 3 groups
- 160 records total, all finite and non-descending

`anm2csv` now exports group and clip indices, exact start/end values, duration, Boolean loop state, and the raw integer.
