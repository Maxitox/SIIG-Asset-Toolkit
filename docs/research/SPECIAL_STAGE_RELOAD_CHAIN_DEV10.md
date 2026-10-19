# Special-stage reload chain — dev10

Dev10 closes the reload-parameter gap left open in dev8/dev9. The conclusion below is deliberately limited to behavior directly supported by executable instructions plus real retail DAT records.

## Retail Xbox 360 write

Retail script execution function `0x822157F0` handles opcode `0x78` (`WARNING` in the recovered DAT opcode table). In that case it reads the first signed script argument, writes `0` to the transition timer at script-state `+0x920`, and writes the argument to the reload parameter at `+0x91C`.

The transition path later reads that parameter. Retail `0x820E5A30` reaches reload dispatch at normalized transition frame 130 and calls `0x820EFC28(stage, parameter)`. That reload routine maps:

- parameter `12` / `0x0C` -> `Bmap13.bin`, field descriptor 1 -> `fld014.gmx`
- parameter `14` / `0x0E` -> `Bmap15.bin`, field descriptor 0 -> `fld015.gmx`

## Real retail DAT linkage

The retail stage corpus contains authored `WARNING [12]` before Water Strider (`0xA6`) and `WARNING [14]` before Ultimate UFO (`0xA8`). `level5_stage3.dat`, for example, requests `WARNING [14]` before its Ultimate UFO encounter. `extra5_stage6.dat` contains both `WARNING [12]` before Water Strider and a later `WARNING [14]` before Ultimate UFO.

This upgrades the old boss/field rows from a cross-system correlation to a direct script→state-write→reload-selection chain. The boss spawn opcode itself is still **not** the reload trigger.

## Cross-build support

May 9, May 11, June 10 and PS3 retail all retain the `AnalyzeWarning` script-command identity; June 10 additionally retains `SgScript::PreExecWarning`. The route/field tables and special-boss behavior continue to line up across the builds as documented in dev8/dev9. Dev10 does not assign unverified human camera-shot names to any opcode or phase.
