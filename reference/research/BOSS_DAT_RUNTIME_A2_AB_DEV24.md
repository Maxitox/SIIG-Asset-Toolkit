# Retail boss/enemy DAT runtime pass — 0xA2 through 0xAB (dev24)

This note records the executable-backed semantic pass completed after WIP130. It intentionally separates retained source/debug labels from behavior-derived names. The common retail initializer `Function_820E7CE0` establishes args 0..4 as spawn condition, root/body HP, a raw scalar stored as arg2/512, controller X, and controller Z for this family block. `Function_820E7F68` then passes the address of arg5 to each class vtable +0x5C callback.

## 0xA2 PROGRESSIVE_UFO

Retail factory case A3 constructs `Function_821276D0`; opcode handler `Function_820E83E8`. Raw +0x5C stub `0x821245D8` copies two signed shorts. `Function_82126050` assigns arg5 to owned slots 1/2 and arg6 to slots 3/4. June 10 `Function_8213EC80` retains exact labels `middle_hp` and `small_hp`.

Schema: `spawn_condition, body_hp, common_speed_raw512, position_x, position_z, middle_hp, small_hp`.

## 0xA3 OCTOPUS

Retail factory case A4 constructs `Function_82123E18`; opcode handler `Function_820E8488`. The class +0x5C callback reads one following short, but every observed retail and June authored OCTOPUS command contains exactly five arguments. The read therefore lands on the following command boundary in authored data and is **not promoted** as a DAT field.

Schema: the five common fields only.

## 0xA4 BUTTERFLY

Retail +0x5C `Function_82110838` copies seven shorts and converts the final four from authored 30 Hz ticks to runtime 60 Hz. June `Function_821299B0` retains labels `hp_A`, `hp_B`, `hp_C`, `discharge_time_base`, `discharge_time_A`, `discharge_time_B`, `discharge_time_C`.

## 0xA5 AXON

Retail runtime+1 case A6 constructs `Function_82110378`. June cross-build strings `Axon::SetScriptData` / `Axon.cpp` resolve the class identity. Retail `Function_8210D750` copies four tail shorts; the first three are converted *2 and the fourth remains HP. June `Function_82126318` retains `normalShotInterval`, `homingShotInterval`, `homingHoldTime`, `bitHp`.

## 0xA6 WATER_STRIDER

Retail `Function_82134EF0` copies four tail shorts. Args5/6 are *2 and June `Function_821503C8` retains `dis_itv_twin_beam` and `dis_itv_shock_wave`. Arg7 gates the first attack-cycle branch (zero enables it); no retained source name was found. Arg8 is *2 and used by `Function_82135A18` as a state-2 dwell before fade-out; nonpositive values default to 210 runtime frames. One retail command omits arg8, so the decoder preserves the valid 8-argument form.

## 0xA7 CRAB

Retail runtime+1 case A8 constructs `Function_82119550`. June strings `Crab::SetScriptData` / `Crab.cpp` resolve the class identity. June `Function_82130640` retains `hp_fannel`, `hp_pot`, `dis_itv_fannel`, `dis_itv_pot`, `homing_itv_fannel` (source spelling preserved). The final value is converted with `pi/(180*256)`, so despite the `itv` spelling it is represented as an angular raw value rather than a frame interval. Some retail records omit this final value.

## 0xA8 ULTIMATE_UFO

Retail `Function_8212C278` copies nine tail shorts; the last four are converted *2. June debug labels prove `hp_fan`, `hp_ring`, `hp_tower`, `hp_umbrella`, `hp_laser`, then `discharge_itv_core/ring/tower/umbrella`.

## 0xA9 SQUID

Retail `Function_82127AB8` copies two shorts and converts both *2. June labels: `dirChangeShotInterval`, `fixShotInterval`.

## 0xAA VERTEBRATE

Retail `Function_821313A0` copies 27 shorts (args5..31). Args5..20 form a 16-entry selector/type map for selectors 0x0B..0x1A. `FUN_82131788` and `FUN_821317D8` use that map to choose one of five HP/limit pairs at args21..30. June debug registration labels each pair `hp` / `limit`; final arg31 is `dir_interval` and is converted *2.

## 0xAB NO_NAME

Raw retail +0x5C stub `0x8211F1A0` copies arg5/arg6. `Function_8211F370` forms a target vector `(arg5,0,arg6)` and moves the root toward it using the common arg2 speed. June retains `NoName::SetScriptData` / `NoName.cpp`.

## Evidence boundary

No proprietary executable or stage payload is bundled. This note contains derived facts and function/address references only. Exact retained labels are stated as such; WATER_STRIDER arg7/arg8 names are behavior-derived; OCTOPUS's boundary read is explicitly left unpromoted.
