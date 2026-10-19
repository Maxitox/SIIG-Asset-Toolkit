# Ultimate UFO May 9 debug-state reconstruction — dev12

Dev12 combines May 9 prototype executable evidence with project-owner prototype-footage observations. The two evidence classes are kept separate: executable-derived field names/timing are treated as direct evidence, while visible gameplay-role labels are recorded as corroborating human observation.

## Debug HUD is executable-backed

May 9 contains a boss-specific debug draw at `0x82141EC0` with the literal strings:

- `Mframe=%d Sframe=%d, state=%d`
- `L2:SKIP`
- `Umb : col=%d, dis=%d`
- `Tow : col=%d, dis=%d`
- `Fan : col=%d, dis=%d`
- `Ring: col=%d, dis=%d`

The draw routine passes Ultimate UFO fields `+0x1C4`, `+0x1C8`, and `+0x1B0` as Mframe, Sframe, and state respectively. It reads bytes `+0x20/+0x21` from four owned objects at `+0x1F4`, `+0x1F0`, `+0x1E0`, and `+0x1E4` for the displayed `col`/`dis` pairs.

This closes the eight phase-table bytes. Their executable-backed order is:

`Umb.col, Umb.dis, Tow.col, Tow.dis, Fan.col, Fan.dis, Ring.col, Ring.dis`.

The gameplay meanings of Umb/Tow/Fan/Ring are supplied by project-owner May 9 footage/model observation: umbrella/top laser assembly, top towers, fan blades, and cannon rings. Those role expansions are not claimed to be executable strings.

## Mframe / Sframe mechanics

May 9 `UltimateUfo::MoveMain` equivalent `0x82142008` proves the timer relationship:

1. If Sframe is positive, decrement it.
2. If the Mframe-advance flag is enabled and Sframe is now below 1, increment Mframe.
3. Write the current Mframe into the active route controller with `0x820FCA08`.

The debug `L2:SKIP` input uses mask `0x400` and sets Sframe directly to zero. This explains why the debug shortcut can appear inactive if used while no Sframe hold is pending. A second debug input mask `0x800` toggles Mframe advance-enable; the physical button label for that mask remains unresolved.

## Phase interpretation

The named col/dis bytes now independently corroborate the footage sequence. Examples:

- phase/state 2: Umb = `1/1`;
- phase/state 3: Tow = `1/1`, Umb = `0/0`;
- phase/state 6: Fan and Ring = `1/1`;
- phase/state 8: Fan = `0/0`, Ring remains `1/1`.

May 9's table also retains the literal state-5 hold at Mframe 4231 / Sframe 200 and state-9 core hold at Mframe 5897 / Sframe 2000. The state-9 code can clear Sframe early when its owned event/core condition completes.

The project-owner footage maps state 10 to core/HP destruction, state 11 to the airlock-door escape, and state 12 to final boss deletion. Executable timings are 5898, 5902, and 6200 respectively, so state 10 is only a four-Mframe bridge into state 11.

## Registry correction from dev11

Dev11 incorrectly interpreted May runtime ID `0xD9` through the later retail registry and labeled the late model `bos_015l.gmx`.

The actual per-build runtime registry proves:

- May 9: `0xD9 -> bos_015k.gmx`
- May 11: `0xD9 -> bos_015k.gmx`
- June 10: `0xD8 -> bos_015k.gmx`
- Xbox retail: `0xD8 -> bos_015k.gmx`
- PS3 retail: `0xD8 -> bos_015k.gmx`

Thus the late controlled asset is consistently `bos_015k.gmx`; its numeric runtime type shifted between May and June. Project-owner model/footage observation identifies `bos_015k.gmx` as the sliding airlock-door component.

## Open point

The observed state-3 Mframe pause near 3120 and the literal next phase trigger 3123 are both retained. Update/display ordering or another advance gate may explain the three-frame difference; dev12 does not force them to match.
