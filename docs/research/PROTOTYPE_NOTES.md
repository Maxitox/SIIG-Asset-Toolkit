# Prototype findings and newly decoded formats

The May 9 (`r5046, DebugOpt`), May 11 (`r5176, DebugOpt`) and June 10 (`r6585, DebugOpt`) Xbox 360 prototypes were compared with retail (`r6803, Release`).

The May builds contain content removed before June 10: four boss-model variants, fourteen wall model/collision pairs, six stage-six layout files and `enemy1_512a.tex`. June 10 is already close to retail: 85 of 94 package files and 18 of 22 decompressed BBX archives are byte-identical.

## COL collision masks

Standalone `.col` resources are 1-bit bitmap masks, not triangle meshes:

```text
+0x00  u32 BE  width
+0x04  u32 BE  height
+0x08  u32 BE  variant (observed 1 or 4)
+0x0C  u32 BE  reserved (0)
+0x10  packed one-bit pixels, LSB-first
```

Use:

```bat
python siig_toolkit.py col2png extracted -o collision_png
```

## ANM tables

Standalone `.anm` resources consist of fixed 28-byte records:

```text
+0x00  char[20] model/resource name
+0x14  float BE parameter
+0x18  u32 BE flag
```

The numeric semantics remain deliberately unnamed until confirmed in executable code.

Use:

```bat
python siig_toolkit.py anm2csv extracted -o anm_tables
```

The one-click `rip-game` command now converts both formats automatically.
