# Reference data

Machine-readable supporting material is grouped by purpose:

- [`tables/`](tables/) — DAT, MAP, stage-pairing, and tile-set CSV tables
- [`provenance/`](provenance/) — source and implementation provenance records
- [`systemfont/`](systemfont/) — BMFont descriptor, glyph table, and metadata
- [`samples/`](samples/) — small source-only format examples
- [`tables/ENTITY_MODEL_IDENTITIES_DEV24.csv`](tables/ENTITY_MODEL_IDENTITIES_DEV24.csv) — 82 project-owner player/enemy/sub-boss/boss/effect model-stem identities with explicit confirmed/speculative status
- [`research/ENTITY_MODEL_IDENTITIES_DEV24.md`](research/ENTITY_MODEL_IDENTITIES_DEV24.md) — evidence boundaries and CELL/LUST/SHUTTER runtime reconciliation for the friendly-name catalog
- [`tables/EST_EFFECT_MODEL_AUDIT_DEV24.csv`](tables/EST_EFFECT_MODEL_AUDIT_DEV24.csv) — `est_011`…`est_021` geometry fingerprints, duplicate groups, runtime-registry presence and ownership confidence
- [`research/EST_EFFECT_MODEL_AUDIT_DEV24.md`](research/EST_EFFECT_MODEL_AUDIT_DEV24.md) — living dev24 evidence-bounded effect/projectile model audit (WIP182 current)
- [`research/EST_012_TARGET_CUBE_DEV24.md`](research/EST_012_TARGET_CUBE_DEV24.md) — WIP181 JOLYNE/UNKNOWN target-cube identification and shared-resource evidence
- [`research/EST_020_021_BOMB_LIFECYCLE_DEV24.md`](research/EST_020_021_BOMB_LIFECYCLE_DEV24.md) — WIP182 OCTOPUS/GLUTTONY shared bomb → explosion identification with GLUTTONY `SG_BOMB` corroboration
- [`research/VISUALIZER_CHECK_FOLLOWUP_SWEEP_DEV24.md`](research/VISUALIZER_CHECK_FOLLOWUP_SWEEP_DEV24.md) — second June 10 Check Mode sweep, including the BG RGB with BG:A=0 constraint

Dev14 adds `tables/ULTIMATE_UFO_FINAL_RESET_AUDIT.csv`, which keeps the proven gate-clear mechanism separate from destructor-only removal, plus `tables/ULTIMATE_UFO_VISIBLE_REMOVAL_DEV14.csv` for the strictly observational June 10 frame boundary.
