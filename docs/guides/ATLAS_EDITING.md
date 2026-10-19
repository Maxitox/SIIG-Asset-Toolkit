# Atlas Inspector / safe sprite editing

Many SIIG 2D textures are atlases: one TEX/PNG contains many independently sampled regions. Examples include `common512`, `common2_512`, and several enemy/boss sheets. Editing the whole sheet without knowing a region's sampling rectangle can crop artwork or contaminate neighboring sprites.

## Safe workflow

The Atlas Inspector is deliberately conservative. Its first job is to answer: **which pixels can I change without spilling into another detected region?**

From the desktop GUI, use **Utilities -> Atlas inspector / safe sprite regions** and choose an extracted atlas PNG. From the CLI:

```text
siig_toolkit.py atlas-inspect common512.png -o common512_atlas_workspace
```

The workspace contains:

- `atlas_clean.png` — an exact clean copy of the source atlas. This is the image intended for TEX rebuilds.
- `atlas_workspace.html` — interactive inspector with zoom, clickable regions, coordinates, labels, duplicate information, and clean per-region downloads.
- `atlas_regions.json` — machine-readable region IDs and rectangles.
- `atlas_labels.tsv` — user-editable semantic labels/notes for slots.
- `sprites/` — clean crops for individual detected slots.
- `atlas_guides_DO_NOT_IMPORT.png` — guide artwork only.
- `atlas_preview_DO_NOT_IMPORT.png` — atlas plus visible guide rectangles.

The two guide PNGs are intentionally marked with a SIIG metadata tag. `png2tex` refuses to rebuild either one, so visible guide rectangles cannot accidentally become game pixels through the normal toolkit workflow. Always rebuild from `atlas_clean.png` or another clean edited image.

## Slot identity and duplicate artwork

A sprite slot is identified by its **region**, not by its pixels. Two slots with byte-identical artwork remain separate slots with separate stable technical IDs such as:

```text
common512_slot_0037
common512_slot_0114
```

The inspector may mark them as members of one duplicate-content group, but it never merges them or assumes they have the same gameplay meaning. This is important for repeated UI glyphs, animation frames, and intentionally duplicated resources.

## Names: technical identity vs. interpretation

The toolkit does not invent names from appearance. Every region receives a technical slot ID first. A human-friendly label is optional and is kept separately in `atlas_labels.tsv` with notes/confidence.

Use a semantic label only when there is evidence for it: an executable/script reference, a known UI use, a controlled in-game replacement test, or another strong source. Unknown regions should remain `*_slot_NNNN` rather than receive a plausible-sounding guess.

Re-running the inspector in the same workspace preserves the existing `atlas_labels.tsv` annotations where slot IDs still match.

## Replacing one region without overflow

Export/download a clean region crop, edit it without changing its dimensions, then insert it with:

```text
siig_toolkit.py atlas-replace \
  --atlas atlas_clean.png \
  --manifest atlas_regions.json \
  --region common512_slot_0037 \
  --sprite edited_slot_0037.png \
  -o common512_edited.png
```

`atlas-replace` requires the replacement PNG to be exactly the region's width and height. It refuses oversized or undersized images rather than silently cropping or scaling them.

To audit a manually edited full atlas:

```text
siig_toolkit.py atlas-validate \
  --original atlas_clean.png \
  --edited common512_edited.png \
  --manifest atlas_regions.json \
  --region common512_slot_0037
```

Changed pixels outside the allowed region cause validation to fail. Repeat `--region` to authorize several edited slots. If no region is supplied, changes are allowed only inside the complete set of detected conservative regions.

## Important current limitation: these are not yet proven native UV allocations

The current automatic rectangles are **content-derived conservative regions**. They are intentionally *not* advertised as the game's authoritative sprite UV/allocation table.

That distinction matters:

- transparent padding legitimately owned by a sprite may lie outside a detected content region;
- one logical sprite containing disconnected islands may currently appear as more than one conservative region;
- two nearby pieces may need to be treated as one native allocation even though the image alone cannot prove that relationship;
- normalized UV values shown by the inspector describe the conservative rectangle, not a claim about recovered native metadata.

Therefore the current workflow is safe for **no-overflow replacement inside a detected rectangle**, but it can be more restrictive than the real game allocation. Do not use the current boxes as evidence for automatic repacking.

## Planned authoritative allocation/repacking work

The next research stage is recovery of the engine's actual atlas-region/UV references. Once those are proven, the same inspector data model can replace conservative boxes with authoritative allocations while preserving the technical slot IDs and user labels.

Only after every relevant reference can be rewritten safely should the toolkit enable advanced operations such as:

- consuming otherwise unused transparent padding;
- enlarging an existing allocation;
- moving/repacking existing regions;
- placing multiple regions differently within an atlas;
- creating genuinely new addressable sprite slots.

Those operations are intentionally separate from the default safe editor. A larger visual footprint is not, by itself, proof that the game will sample a larger rectangle.
