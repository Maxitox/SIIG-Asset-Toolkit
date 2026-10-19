# Visualizer SequenceSet change timing — dev24 WIP173

## Status

**Recovered from the June 10 Xbox 360 executable.** This supersedes the earlier
placeholder interpretation of `VL_CHANGETIME` as an unresolved interpolation
control. It is a SequenceSet row-change timing range.

## DAT command

`VL_CHANGETIME` is opcode `0xCD`. The stage-script dispatcher forwards the
first two signed parameters to `Function_82175DB0`.

`Function_82175DB0`:

1. asserts `max >= min`;
2. stores the two integers as the VisualizerScript change-time bounds;
3. immediately calls `Function_82175CC0` to select the current threshold.

`Function_82175CC0` computes:

```text
span = max - min
if span == 0:
    threshold = min
else:
    threshold = min + Random30() % span
```

The upper bound is therefore **exclusive** whenever the bounds differ. Equal
bounds are a fixed threshold and do not consume an RNG value.

The VisualizerScript constructor initializes both bounds to **18000**.

## SequenceSet stepping

`VL_SEQUENCESET`/`Function_82175C10` stores the selected SequenceSet id and
resets:

- sequence slot = 0;
- change counter = 0;
- dirty/apply flag = true.

On each active Visualizer update, `Function_82177648` first applies the current
ParameterSet when the dirty flag is set. It then compares the current threshold
against the counter:

```text
if threshold < counter:
    slot += 1
    if slot >= sequence_length or sequence[slot] == -1:
        slot = 0
    counter = 0
    dirty = true
    threshold = pick_change_time()
else:
    counter += 1
```

The newly selected slot is therefore applied on the **following active
Visualizer update**, not inside the update that arms the row change. The `-1`
entry in SequenceSet is a terminator/wrap marker.

This is the exact executable control flow; WIP173 reproduces the same dirty
flag, counter comparison, wrap rule and re-roll point.

## RNG

`Function_82175CC0` calls `Function_8249A9D8`. That wrapper concatenates two
15-bit CRT random values into one 30-bit value:

```text
Random30 = rand15_second | (rand15_first << 15)
```

`Function_824A9E88` is the familiar Microsoft CRT LCG:

```text
state = state * 0x343FD + 0x269EC3   (mod 2^32)
rand15 = (state >> 16) & 0x7FFF
```

`Function_8249A9B0` seeds the CRT state from `Function_82495800`, a timer-derived
runtime value. The exact seed for an arbitrary captured play session is thus
not authored in DAT or SequenceSet data.

The browser simulator exposes a **sim-only 32-bit seed** so a stochastic stage
sequence can be reproduced while retaining the exact native RNG algorithm and
range semantics. A different seed can be chosen to observe another valid run.

## Simulator change

Visualizer dataset **v17** adds an executable-backed SequenceSet runtime for
decoded stage playback. Seeking a DAT frame deterministically rebuilds the
VisualizerScript sequence state from frame zero with the selected simulator
seed. Live timeline following then advances the recovered state one 60 Hz
logical stage frame at a time.

The timeline status now reports sequence id, current ParameterSet, sequence
slot, change range, selected threshold, counter and RNG state. This removes the
old behavior where every `VL_SEQUENCESET` event simply pinned the first active
ParameterSet forever.

## Remaining visualizer boundaries

This closes `VL_CHANGETIME` timing semantics. It does **not** close:

- the exact upstream XAudio2 volume-meter processing/callback cadence;
- bit-identical Xenos render-target alpha storage/compositing;
- any final host/browser presentation differences that are not yet recovered
  from the native final composite path.
