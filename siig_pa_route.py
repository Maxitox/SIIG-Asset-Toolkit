#!/usr/bin/env python3
"""Executable-backed PA-route / special-route research helpers for SIIG.

This module intentionally distinguishes direct executable evidence from strong
cross-system correlations. It does not automatically activate PA-route playback.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable, Mapping, Sequence


@dataclass(frozen=True)
class PaRouteBuildGate:
    build: str
    platform: str
    gate_function: str
    category_function: str | None
    requires_category_zero: bool
    requires_state_218: int | None
    requires_state_21c: int | None
    setup_calls_pa_route: bool
    evidence: str


BUILD_GATES: tuple[PaRouteBuildGate, ...] = (
    PaRouteBuildGate(
        "ps3_retail", "ps3", "0x000EA2E0", None, True, 4, 1, True,
        "direct retail decompilation: inlined stage/category classifier + state checks; stage setup vtable +0x08 requests index 0",
    ),
    PaRouteBuildGate(
        "xbox360_retail", "xbox360", "0x8221CBE0", "0x8212C000", True, 4, 1, True,
        "direct retail decompilation: category helper + state checks; stage setup invokes route vtable +0x08 with index 0",
    ),
    PaRouteBuildGate(
        "xbox360_june10", "xbox360", "0x82243F78", "0x821013E0", True, 4, 1, True,
        "direct June 10 decompilation; Route::SetPaRoute debug string identifies the vtable target",
    ),
    PaRouteBuildGate(
        "xbox360_may11", "xbox360", "0x82238A18", "0x820FF990", False, 4, 1, True,
        "direct May 11 decompilation: state checks only; category filter is absent",
    ),
    PaRouteBuildGate(
        "xbox360_may9", "xbox360", "not observed in corresponding setup", "0x820FF2D8", False, None, None, False,
        "Route::SetPaRoute exists, but the corresponding stage-setup routine does not invoke the PA-route activation branch",
    ),
)


PA_ROUTE_FUNCTIONS: tuple[dict, ...] = (
    {"build":"ps3_retail","set_pa_route":"0x0015AEBC","activation_wrapper":"0x001580DC","stage_setup":"0x00161134","debug_name":"Route::SetPaRoute (name recovered from Xbox prototypes)","camera_format":"cam%02d_op1.gmx"},
    {"build":"xbox360_retail","set_pa_route":"0x820EAFC8","activation_wrapper":"0x820EABE8","stage_setup":"0x820EFA98","debug_name":"Route::SetPaRoute (name recovered from Xbox prototypes)","camera_format":"cam%02d_op1.gmx"},
    {"build":"xbox360_june10","set_pa_route":"0x820FDE88","activation_wrapper":"0x820FDAE0","stage_setup":"0x82104860","debug_name":"Route::SetPaRoute","camera_format":"cam%02d_op1.gmx"},
    {"build":"xbox360_may11","set_pa_route":"0x820FCD50","activation_wrapper":"0x820FC9A8","stage_setup":"0x82101C90","debug_name":"Route::SetPaRoute","camera_format":"cam%02d_op1.gmx"},
    {"build":"xbox360_may9","set_pa_route":"0x820FCB28","activation_wrapper":"0x820FC718","stage_setup":"corresponding setup does not activate PA-route","debug_name":"Route::SetPaRoute","camera_format":"cam%02d_op1.gmx"},
)


# Dev10 closes the boss-stage reload mapping with the script opcode 0x78 handler:
# the handler copies its first signed argument to the reload-parameter field and
# starts the transition timer. Real retail DATs use WARNING[12] before Water
# Strider and WARNING[14] before Ultimate UFO. The reload routine then maps 12/14
# to Bmap13/Bmap15 and field descriptor 1/0 respectively.
BOSS_FIELD_CORRELATIONS: tuple[dict, ...] = (
    {
        "opcode": 0xA6,
        "opcode_name": "WATER_STRIDER",
        "boss_class": "WaterStrider",
        "field_descriptor_index": 1,
        "field_model": "fld014.gmx",
        "descriptor_start": 0,
        "descriptor_end": 1440,
        "loop": True,
        "special_parameter": 0x0C,
        "special_bmap": "Bmap13.bin",
        "confidence": "direct_script_executable_chain",
        "evidence": "retail level/extra DAT uses opcode 0x78 WARNING[12]; retail handler 0x822157F0 writes arg 12 to reload parameter +0x91C and timer 0 to +0x920; reload 0x820EFC28 maps 0x0C to Bmap13 and descriptor 1/fld014; WaterStrider route driver wraps 0..1440",
    },
    {
        "opcode": 0xA8,
        "opcode_name": "ULTIMATE_UFO",
        "boss_class": "UltimateUfo",
        "field_descriptor_index": 0,
        "field_model": "fld015.gmx",
        "descriptor_start": 0,
        "descriptor_end": 6300,
        "loop": False,
        "special_parameter": 0x0E,
        "special_bmap": "Bmap15.bin",
        "confidence": "direct_script_executable_chain",
        "evidence": "retail level/extra DAT uses opcode 0x78 WARNING[14]; retail handler 0x822157F0 writes arg 14 to reload parameter +0x91C and timer 0 to +0x920; reload 0x820EFC28 maps 0x0E to Bmap15 and descriptor 0/fld015; UltimateUfo route is finite into the 6000s",
    },
)


SPECIAL_STAGE_RELOAD_CHAIN: tuple[dict, ...] = (
    {"opcode":0x78,"opcode_name":"WARNING","script_argument":0x0C,"boss_opcode":0xA6,"boss":"WaterStrider","reload_parameter":0x0C,"bmap":"Bmap13.bin","field_descriptor_index":1,"field_model":"fld014.gmx","handler_xbox_retail":"0x822157F0","reload_xbox_retail":"0x820EFC28","handler_write":"arg[0] -> state +0x91C; 0 -> transition timer +0x920","reload_time_normalized_frame":130},
    {"opcode":0x78,"opcode_name":"WARNING","script_argument":0x0E,"boss_opcode":0xA8,"boss":"UltimateUfo","reload_parameter":0x0E,"bmap":"Bmap15.bin","field_descriptor_index":0,"field_model":"fld015.gmx","handler_xbox_retail":"0x822157F0","reload_xbox_retail":"0x820EFC28","handler_write":"arg[0] -> state +0x91C; 0 -> transition timer +0x920","reload_time_normalized_frame":130},
)

ULTIMATE_UFO_DEATH_CHAIN: tuple[dict, ...] = (
    {"step":"hp_zero_dispatch","xbox360_retail":"0x820FBD30","evidence":"when a tracked health slot subtracts to <1, dispatches vtable +0x3C(part,state=1) then +0x44(part)"},
    {"step":"ufo_part_state_override","xbox360_retail":"0x8212DCB0","evidence":"UltimateUfo override records part-1 state in byte +0x1EE and performs special-stage coupled state/destruction handling"},
    {"step":"prototype_vanish","xbox360_may9":"0x821410A8","xbox360_may11":"0x821423B8","debug_name":"UltimateUfo::Vanish","evidence":"prototype symbols name vtable +0x48; Vanish(1) checks part 1, emits an effect at its owned-part position, then invokes the part-state handler"},
    {"step":"delete_lv5_boss_dispatch","xbox360_may9":"0x8215B1F0","xbox360_may11":"0x8215C330","xbox360_june10":"0x82166190","ps3_retail":"0x00203308","evidence":"script AnalyzeDelLv5Boss selects entity types 0xA6..0xAB (including Ultimate UFO 0xA8) and invokes each matching boss part's vtable +0x48"},
    {"step":"retail_phase12","xbox360_retail":"0x8212EC50","trigger_frame":6030,"evidence":"on phase entry, propagates part-1 state to part 0; if +0x1EE is nonzero it invokes destruction for part 0 and enables the recurring explosion-emission flag +0x1EC"},
    {"step":"retail_phase13","xbox360_retail":"0x8212EC50","trigger_frame":6200,"evidence":"on phase entry disables the owned object referenced at UFO +0x25C/part slot 0x97 via 0x820F2CF8(...,0)"},
)


# Dev12 corrects the cross-build late-route registry interpretation.
# All four Xbox builds use bos_015k.gmx for the late owned object: May 9/11
# register that model as type 0xD9, while June 10/retail shift it to 0xD8.
# Model semantic labels remain separate from executable facts: the executable
# proves the GMX identity; the airlock-door label comes from project-owner
# gameplay/model observation and is retained as corroborating evidence.
ULTIMATE_UFO_LATE_OBJECTS: tuple[dict, ...] = (
    {
        "build":"xbox360_retail", "model_id":0xD8, "model":"bos_015k.gmx",
        "owner_field":"+0x25C (word 0x97)", "setup_function":"0x8212FC80",
        "move_main":"0x8212EC50", "phase11_frame":5902, "final_phase":13, "final_frame":6200,
        "phase11_action":"play child animation/state index 0 when child +0x10 is inactive",
        "final_action":"disable owned model object via 0x820F2CF8(object,0)",
        "confidence":"direct_executable_model_identity",
        "evidence":"setup loads registry ID 0xD8 through 0x820FAAB8 and stores the resulting object at +0x25C; registry entry 0xD8 names bos_015k.gmx; MoveMain phase 11 and phase 13 consume that same field",
    },
    {
        "build":"xbox360_june10", "model_id":0xD8, "model":"bos_015k.gmx",
        "owner_field":"+0x260 (word 0x98)", "setup_function":"0x8214AE58",
        "move_main":"0x82149DF8", "phase11_frame":5902, "final_phase":13, "final_frame":6200,
        "phase11_action":"play child animation/state index 0 when child +0x10 is inactive",
        "final_action":"disable owned model object via 0x82108B28(object,0)",
        "confidence":"direct_executable_model_identity",
        "evidence":"setup loads registry ID 0xD8 through 0x82111918 and stores the resulting object at +0x260; registry entry 0xD8 names bos_015k.gmx; MoveMain phase 11 and phase 13 consume that same field",
    },
    {
        "build":"xbox360_may11", "model_id":0xD9, "model":"bos_015k.gmx",
        "owner_field":"+0x1E8 (word 0x7A)", "setup_function":"0x82143E40-range",
        "move_main":"0x821431D0", "phase11_frame":5902, "final_phase":12, "final_frame":6200,
        "phase11_action":"play child animation/state index 0 when child +0x10 is inactive",
        "final_action":"disable the corresponding owned model object",
        "confidence":"direct_executable_model_identity",
        "evidence":"setup path at 0x821440C4 loads registry ID 0xD9 and stores the resulting object at +0x1E8; May 11 runtime registry 0xD9 names bos_015k.gmx; the old phase 11/final phase 12 path consumes that same field",
    },
    {
        "build":"xbox360_may9", "model_id":0xD9, "model":"bos_015k.gmx",
        "owner_field":"+0x1DC (word 0x77)", "setup_function":"0x82142CE0-range",
        "move_main":"0x82142008", "phase11_frame":5902, "final_phase":12, "final_frame":6200,
        "phase11_action":"play child animation/state index 0 when child +0x10 is inactive",
        "final_action":"disable the corresponding owned model object",
        "confidence":"direct_executable_model_identity",
        "evidence":"setup path at 0x82142F5C loads registry ID 0xD9 and stores the resulting object at +0x1DC; May 9 runtime registry 0xD9 names bos_015k.gmx; the old phase 11/final phase 12 path consumes that same field",
    },
)


def ultimate_ufo_late_objects() -> list[dict]:
    """Return executable-backed late-route owned-model identities by build."""
    return [dict(item) for item in ULTIMATE_UFO_LATE_OBJECTS]


# May 9's Ultimate UFO debug overlay makes the phase-table bytes directly
# nameable. The HUD draws these four object pairs from +0x20/+0x21.
ULTIMATE_UFO_PART_STATUS_FIELDS: tuple[str, ...] = (
    "umb_col", "umb_dis", "tow_col", "tow_dis",
    "fan_col", "fan_dis", "ring_col", "ring_dis",
)

ULTIMATE_UFO_PART_STATUS_OBJECTS: tuple[dict, ...] = (
    {"part":"Umb","owner_offset":"+0x1F4","col_offset":"+0x20","dis_offset":"+0x21","debug_string":"Umb : col=%d, dis=%d","observed_role":"top/umbrella assembly and surrounding small laser cannons","role_evidence":"project-owner May 9 footage/model observation; executable proves only debug label/fields"},
    {"part":"Tow","owner_offset":"+0x1F0","col_offset":"+0x20","dis_offset":"+0x21","debug_string":"Tow : col=%d, dis=%d","observed_role":"small laser towers on top of the boss","role_evidence":"project-owner May 9 footage/model observation; executable proves only debug label/fields"},
    {"part":"Fan","owner_offset":"+0x1E0","col_offset":"+0x20","dis_offset":"+0x21","debug_string":"Fan : col=%d, dis=%d","observed_role":"fan blades around the giant laser cannon","role_evidence":"project-owner May 9 footage/model observation; executable proves only debug label/fields"},
    {"part":"Ring","owner_offset":"+0x1E4","col_offset":"+0x20","dis_offset":"+0x21","debug_string":"Ring: col=%d, dis=%d","observed_role":"rings near the start of the giant laser cannon","role_evidence":"project-owner May 9 footage/model observation; executable proves only debug label/fields"},
)

ULTIMATE_UFO_DEBUG_HUD: dict = {
    "build":"xbox360_may9",
    "draw_function":"0x82141EC0",
    "move_main":"0x82142008",
    "mframe_offset":"+0x1C4 (word 0x71)",
    "sframe_offset":"+0x1C8 (word 0x72)",
    "state_offset":"+0x1B0 (word 0x6C)",
    "advance_enable_offset":"+0x1CC (word 0x73)",
    "hud_format":"Mframe=%d Sframe=%d, state=%d",
    "skip_label":"L2:SKIP",
    "skip_input_mask":"0x400",
    "skip_effect":"sets Sframe to 0",
    "advance_toggle_input_mask":"0x800",
    "advance_toggle_effect":"toggles Mframe advance-enable; physical button label unresolved",
    "timer_rule":"Sframe decrements while >0; Mframe increments only when advance-enable != 0 and Sframe < 1",
    "evidence":"May 9 debug strings/xrefs and Function_82142008/Function_82141EC0 decompilation",
}

# Direct build-by-build route-clock chain. Ultimate UFO's Mframe is not merely
# a boss timer: it is written to the active field animation model clock.
ULTIMATE_UFO_MFRAME_ROUTE_CHAIN: tuple[dict, ...] = (
    {"build":"xbox360_may9","move_main":"0x82142008","route_frame_setter":"0x820FCA08","mframe_field":"+0x1C4 / word 0x71","field_model":"fld015.gmx","field_start":0,"field_end":6300,"loop":False},
    {"build":"xbox360_may11","move_main":"0x821431D0","route_frame_setter":"0x820FCC30","mframe_field":"+0x1D0 / word 0x74","field_model":"fld015.gmx","field_start":0,"field_end":6300,"loop":False},
    {"build":"xbox360_june10","move_main":"0x82149DF8","route_frame_setter":"0x820FDD68","mframe_field":"word 0x79 in evolved object layout","field_model":"fld015.gmx","field_start":0,"field_end":6300,"loop":False},
    {"build":"xbox360_retail","move_main":"0x8212EC50","route_frame_setter":"0x820EAED8","mframe_field":"evolved retail Mframe field","field_model":"fld015.gmx","field_start":0,"field_end":6300,"loop":False},
    {"build":"ps3_retail","move_main":"0x001D2988","route_frame_setter":"0x0015A2DC","mframe_field":"evolved retail Mframe field","field_model":"fld015.gmx","field_start":0,"field_end":6300,"loop":False},
)

# The normal stage and Extra/Bonus 5-6 intentionally diverge at destruction.
# The fast-destroy selector is direct retail Xbox + PS3 evidence.
ULTIMATE_UFO_STAGE_PROFILES: tuple[dict, ...] = (
    {
        "profile":"normal_5_3", "script":"level5_stage3.dat", "stage_label":"5-3",
        "ufo_script_frame":781, "next_camera_index":4, "next_camera_script_frame":912,
        "camera_delta_ticks":131, "fast_destroy_branch":False,
        "destruction_policy":"preserve normal late route: state 10 -> state 11 airlock sequence -> later destruction/final phases",
        "evidence":"retail DAT timeline + UltimateUfo MoveMain; state-11 airlock label is project-owner May 9 footage observation",
    },
    {
        "profile":"bonus_5_6", "script":"extra5_stage6.dat", "stage_label":"DLC Bonus 5-6",
        "ufo_script_frame":33749, "next_camera_index":4, "next_camera_script_frame":34779,
        "camera_delta_ticks":1030, "fast_destroy_branch":True,
        "fast_destroy_selector":"category 5 && state +0x218 == 5 && state +0x21C == 6",
        "xbox360_retail_branch":"0x8212DCB0", "ps3_retail_branch":"0x001D3380",
        "destruction_policy":"on part-1/core destroyed state, immediately mirror state to part 0, destroy part 0, then clear pending +0x1EE state",
        "evidence":"direct retail Xbox/PS3 special-case branch; gameplay boss-order/handoff context is project-owner observation",
    },
)

# PA camera is a two-stage system: a temporary cam01 animation followed by the
# normal procedural camera transformed through the current field orientation.
PA_CAMERA_LIFECYCLE: tuple[dict, ...] = (
    {"step":"activate_pa_camera","ps3_retail":"0x001580DC","effect":"successful SetPaRoute sets animated-camera flag +0x108=1"},
    {"step":"sample_animated_eye_target","ps3_retail":"0x00157A10 -> 0x0015B094","effect":"while +0x108 is set, sample cam1/int1 and add current FieldPos"},
    {"step":"advance_and_finish","ps3_retail":"0x00157A10 -> 0x0015B1C8","effect":"advance camera animation clock; clear +0x108 and reset clock at animation end"},
    {"step":"sample_field_matrix","ps3_retail":"0x0015ABCC -> 0x00159D58","effect":"sample active field GMX matrix; extract translation to FieldPos and zero matrix translation, retaining orientation"},
    {"step":"procedural_fallback","ps3_retail":"0x00157A10","effect":"when animated flag is clear, transform current camera-preset eye/target through field orientation and FieldPos"},
)

# Real fld015.gmx samples plus preset-4 procedural camera geometry. The late
# route has a +90-degree X orientation; preset 4's local eye offset (0,40,60)
# therefore becomes (0,-60,+40), a rear-follow offset along the late +Y route.
# Dynamic horizontal response alters local/world X only in this orientation.
ULTIMATE_UFO_LATE_CAMERA_GEOMETRY: tuple[dict, ...] = (
    {"mframe":5897,"phase":9,"field_x":0.0,"field_y":97.25340270996094,"field_z":32.0348014831543,"eye_x":0.0,"eye_y":37.25340270996094,"eye_z":72.03480529785156,"target_x":0.0,"target_y":97.25340270996094,"target_z":32.0348014831543},
    {"mframe":5898,"phase":10,"field_x":0.0,"field_y":97.25980377197266,"field_z":32.03269958496094,"eye_x":0.0,"eye_y":37.259803771972656,"eye_z":72.03269958496094,"target_x":0.0,"target_y":97.25980377197266,"target_z":32.03269958496094},
    {"mframe":5902,"phase":11,"field_x":0.0,"field_y":97.41230010986328,"field_z":31.98259925842285,"eye_x":0.0,"eye_y":37.41230010986328,"eye_z":71.98259735107422,"target_x":0.0,"target_y":97.41230010986328,"target_z":31.98259925842285},
    {"mframe":6030,"phase":12,"field_x":0.0,"field_y":196.29100036621094,"field_z":-14.158300399780273,"eye_x":0.0,"eye_y":136.29100036621094,"eye_z":25.841699600219727,"target_x":0.0,"target_y":196.29100036621094,"target_z":-14.158300399780273},
    {"mframe":6200,"phase":13,"field_x":0.0,"field_y":606.1170043945312,"field_z":-16.442100524902344,"eye_x":0.0,"eye_y":546.1170043945312,"eye_z":23.557899475097656,"target_x":0.0,"target_y":606.1170043945312,"target_z":-16.442100524902344},
    {"mframe":6300,"phase":13,"field_x":0.0,"field_y":950.8079833984375,"field_z":-18.7544002532959,"eye_x":0.0,"eye_y":890.8079833984375,"eye_z":21.2455997467041,"target_x":0.0,"target_y":950.8079833984375,"target_z":-18.7544002532959},
)

PS3_CAMERA_PRESET_DIRECT_CALLERS: tuple[dict, ...] = (
    {"caller":"0x0014F604","role":"DAT Analyze3DCameraChange01 handler","call":"SetCameraPreset(index, authored_duration)","ultimate_ufo_direct_caller":False},
    {"caller":"0x00160E10","role":"stage camera refresh when stage-camera enable byte is set","call":"SetCameraPreset(current_stage_camera,0)","ultimate_ufo_direct_caller":False},
    {"caller":"0x00161380","role":"stage camera object initialization","call":"SetCameraPreset(0,0)","ultimate_ufo_direct_caller":False},
    {"caller":"0x00161BD8","role":"stage setup sequence camera refresh","call":"SetCameraPreset(current_stage_camera,0)","ultimate_ufo_direct_caller":False},
    {"caller":"0x001D8690","role":"Vertebrate-specific transition (cross-build June debug provenance)","call":"SetCameraPreset(0,120)","ultimate_ufo_direct_caller":False},
)

ULTIMATE_UFO_LATE_CAMERA_CONCLUSION: dict = {
    "normal_stage_last_authored_preset_before_ufo_route":"preset 4 at script frame 912 after ULTIMATE_UFO frame 781",
    "preset4_eye_offset":"(0,40,60)",
    "late_fld015_orientation":"+90 degrees X",
    "transformed_eye_offset":"(0,-60,+40)",
    "classification":"rear_follow_geometry",
    "confidence":"strong_executable_asset_chain",
    "direct_preset_setter_scan":"PS3 retail 0x0015B524 has five direct callers in the decompiled export; none is UltimateUfo. The only boss-specific direct caller maps cross-build to Vertebrate.",
    "boundary":"preset 4 is the last authored DAT preset before the normal 5-3 UFO route, UltimateUfo MoveMain has no preset setter, and no direct PS3 preset-setter caller is UltimateUfo; indirect/function-pointer or otherwise unresolved external writes are not exhaustively ruled out",
}


# Dev13: retail Ultimate UFO also participates in the camera controller's
# transition-acceptance gate.  The PS3 preset setter proves that +0x11C is not a
# geometric camera parameter: timed transitions (>0 duration) are accepted only
# while the gate is nonzero, whereas immediate transitions remain accepted and
# re-enable the gate.  UltimateUfo's part-0/state-0 reset clears the gate outside
# the Extra 5-6 fast-destroy branch.
ULTIMATE_UFO_CAMERA_TRANSITION_GATE: tuple[dict, ...] = (
    {
        "step":"camera_preset_gate_semantics",
        "ps3_retail":"0x0015B524",
        "controller_offset":"+0x11C",
        "effect":"timed preset changes require gate != 0; immediate duration-0 changes are accepted and set gate=1",
        "confidence":"direct_executable",
    },
    {
        "step":"ufo_part0_state0_gate_clear",
        "xbox360_retail":"0x8212DCB0",
        "ps3_retail":"0x001D3380",
        "condition":"part index 0, state 0, except the category-5 / (5,6) Extra fast-destroy path",
        "effect":"clear camera controller +0x11C to 0",
        "confidence":"direct_executable_cross_platform",
    },
    {
        "step":"static_preset_writer_audit",
        "ps3_retail":"0x0015B524",
        "effect":"five direct callers in complete export; DAT + three stage setup/refresh paths + Vertebrate transition; no UltimateUfo direct caller",
        "confidence":"complete_direct_caller_scan",
    },
)


# The May prototypes make the old ending unusually explicit: phase 12 at Mframe
# 6200 directly invokes the object's vtable +0x48 with part 0.  Prototype debug
# strings identify that operation as UltimateUfo::Vanish.  June/retail split the
# ending into destruction at 6030 and bos_015k shutdown at 6200; their MoveMain
# no longer contains the direct final part-0 +0x48 call, so the later final reset
# remains an engine-owned follow-up rather than a phase-table action.
ULTIMATE_UFO_FINAL_VANISH_EVOLUTION: tuple[dict, ...] = (
    {
        "build":"xbox360_may9",
        "move_main":"0x82142008",
        "phase":12,
        "trigger_frame":6200,
        "action":"vtable +0x48(part 0)",
        "vanish_function":"0x821410A8",
        "debug_name":"UltimateUfo::Vanish",
        "confidence":"direct_executable_debug_name",
    },
    {
        "build":"xbox360_may11",
        "move_main":"0x821431D0",
        "phase":12,
        "trigger_frame":6200,
        "action":"vtable +0x48(part 0)",
        "vanish_function":"0x821423B8",
        "debug_name":"UltimateUfo::Vanish",
        "confidence":"direct_executable_debug_name",
    },
    {
        "build":"xbox360_june10",
        "move_main":"0x82149DF8",
        "phase12_frame":6030,
        "phase12_action":"part-0 destruction path; enable recurring explosion state",
        "phase13_frame":6200,
        "phase13_action":"disable bos_015k owned object",
        "direct_final_vanish_in_move_main":False,
        "confidence":"direct_executable",
    },
    {
        "build":"xbox360_retail",
        "move_main":"0x8212EC50",
        "phase12_frame":6030,
        "phase12_action":"part-0 destruction path; enable recurring explosion state",
        "phase13_frame":6200,
        "phase13_action":"disable bos_015k owned object",
        "direct_final_vanish_in_move_main":False,
        "confidence":"direct_executable",
    },
)

# Dev14 final-reset caller audit.  This deliberately separates visible/entity
# teardown from the part-0/state-0 reset that clears the retail camera gate.
# Addresses are retail Xbox 360 unless a row says otherwise.
ULTIMATE_UFO_FINAL_RESET_AUDIT: tuple[dict, ...] = (
    {
        "step":"phase12_destruction",
        "address":"0x8212EC50",
        "trigger":"Mframe 6030",
        "operation":"vtable +0x3C(part 0, state +0x1EE=1), then +0x44(part 0)",
        "calls_part0_state0":False,
        "clears_camera_gate":False,
        "status":"proven_not_gate_clear",
    },
    {
        "step":"phase13_owned_object_shutdown",
        "address":"0x8212EC50",
        "trigger":"Mframe 6200",
        "operation":"Function_820F2CF8(bos_015k owned object, 0)",
        "calls_part0_state0":False,
        "clears_camera_gate":False,
        "status":"proven_not_gate_clear",
    },
    {
        "step":"post_phase_move_main_tail",
        "address":"0x8212EC50",
        "trigger":"every update after phase dispatch",
        "operation":"camera/owned-object updates, recurring explosion emitter, Mframe advance, route-frame write",
        "calls_part0_state0":False,
        "clears_camera_gate":False,
        "status":"no_final_reset_in_move_main",
    },
    {
        "step":"generic_vanish_reset",
        "address":"0x820FBEE8",
        "trigger":"vtable +0x48(part)",
        "operation":"dispatch vtable +0x3C(part, state 0)",
        "calls_part0_state0":True,
        "clears_camera_gate":True,
        "status":"proven_mechanism_caller_unresolved",
    },
    {
        "step":"ufo_part_state_gate_clear",
        "address":"0x8212DCB0 / instruction 0x8212DD20",
        "trigger":"part 0 and state 0, except Extra 5-6 branch",
        "operation":"clear stage +0x1CC and camera controller byte +0x11C",
        "calls_part0_state0":True,
        "clears_camera_gate":True,
        "status":"proven_clear_site",
    },
    {
        "step":"generic_lifetime_watchdog",
        "address":"0x820FB280",
        "trigger":"elapsed timer > 25200",
        "operation":"vtable +0x48 for every part, then vtable +0x20",
        "calls_part0_state0":True,
        "clears_camera_gate":True,
        "status":"proven_failsafe_not_assigned_as_normal_ending",
    },
    {
        "step":"normal_stage_script_cleanup",
        "address":"level5_stage3.dat",
        "trigger":"after ULTIMATE_UFO spawn",
        "operation":"no DEL_ALL_ENEMY or DEL_LV5_BOSS record; DEL_ZAKO excludes type 0xA8",
        "calls_part0_state0":False,
        "clears_camera_gate":False,
        "status":"applicable_authored_cleanup_excluded",
    },
    {
        "step":"flagged_entity_removal",
        "address":"0x82148748 -> 0x8214A368",
        "trigger":"entity +0x2D removal flag and manager gate",
        "operation":"invoke destructor and clear manager slot; no vtable +0x48 dispatch",
        "calls_part0_state0":False,
        "clears_camera_gate":False,
        "status":"destruction_is_not_reset",
    },
    {
        "step":"camera_controller_initialization",
        "address":"0x820ECFD8",
        "trigger":"camera controller construction",
        "operation":"initialize camera gate +0x11C to 1",
        "calls_part0_state0":False,
        "clears_camera_gate":False,
        "status":"proven_reinitialization_not_clear",
    },
)

CAMERA_SELECTIONS: tuple[dict, ...] = (
    {
        "index": 0,
        "resource": "cam01_op1.gmx",
        "retail_stage_setup_observed": True,
        "controller_start": 0,
        "controller_end_exclusive": 200,
        "loop": False,
        "evidence": "retail PS3/Xbox stage setup invokes Route vtable +0x08 with argument 0",
    },
    {
        "index": 1,
        "resource": "cam02_op1.gmx",
        "retail_stage_setup_observed": False,
        "controller_start": 0,
        "controller_end_exclusive": 200,
        "loop": False,
        "evidence": "Route::SetPaRoute accepts index 1 and formats cam02_op1.gmx; no proven retail activation callsite selecting index 1 has been found yet",
    },
)



# Dev9 executable-backed boss-route timelines.  These values come from the
# literal tables consumed by the named boss update functions.  Retail Xbox,
# retail PS3 and June 10 are byte-identical for both tables.
BOSS_ROUTE_FUNCTIONS: tuple[dict, ...] = (
    {"build":"xbox360_retail","ultimate_move_main":"0x8212EC50","water_update_act":"0x82135670","water_loop_driver":"0x82136810"},
    {"build":"xbox360_june10","ultimate_move_main":"0x82149DF8","water_update_act":"0x82150BA8","water_loop_driver":"0x82151D98"},
    {"build":"xbox360_may11","ultimate_move_main":"0x821431D0","water_update_act":"0x82149490","water_loop_driver":"not recovered as retail-equivalent"},
    {"build":"xbox360_may9","ultimate_move_main":"0x82142008","water_update_act":"0x82148078","water_loop_driver":"not recovered as retail-equivalent"},
    {"build":"ps3_retail","ultimate_move_main":"0x001D2988","water_update_act":"0x001DEB68","water_loop_driver":"0x001E04D0"},
)

# start/end are inclusive.  The three trailing bytes are copied from the
# compact retail/June table and deliberately kept opaque until their consumers
# are semantically named.  The first flag byte is also executable data.
WATER_STRIDER_SEGMENTS: tuple[dict, ...] = tuple(
    {"index":i,"start":a,"end":b,"flags":flags} for i,(a,b,flags) in enumerate((
        (0,109,(0,1,0)), (110,180,(1,1,0)), (181,244,(0,1,0)),
        (245,340,(1,1,0)), (341,379,(0,1,0)), (380,435,(0,0,0)),
        (436,454,(0,1,1)), (455,520,(1,1,0)), (521,669,(0,1,0)),
        (670,770,(1,0,0)), (771,784,(0,0,0)), (785,860,(0,1,1)),
        (861,899,(0,1,0)), (900,1185,(1,0,0)), (1186,1260,(1,0,0)),
        (1261,1380,(0,0,0)), (1381,1440,(0,0,1)),
    ))
)

ULTIMATE_UFO_RETAIL_PHASES: tuple[dict, ...] = tuple(
    {"phase":phase,"trigger_frame":frame,"delay_frames":delay,"part_flags":flags,"part_status":dict(zip(ULTIMATE_UFO_PART_STATUS_FIELDS, flags))} for phase,frame,delay,flags in (
        (1, 0, 0, (0, 0, 0, 0, 0, 0, 0, 0)),
        (2, 1750, 0, (1, 1, 0, 0, 0, 0, 0, 0)),
        (3, 2250, 0, (0, 0, 1, 1, 0, 0, 0, 0)),
        (4, 3123, 0, (0, 0, 0, 0, 0, 0, 0, 0)),
        (5, 4231, 200, (0, 0, 0, 0, 0, 0, 0, 0)),
        (6, 4450, 0, (0, 0, 0, 0, 1, 1, 1, 1)),
        (7, 5100, 0, (0, 0, 0, 0, 1, 1, 1, 1)),
        (8, 5300, 0, (0, 0, 0, 0, 0, 0, 1, 1)),
        (9, 5897, 0, (0, 0, 0, 0, 0, 0, 0, 0)),
        (10, 5898, 0, (0, 0, 0, 0, 0, 0, 0, 0)),
        (11, 5902, 0, (0, 0, 0, 0, 0, 0, 0, 0)),
        (12, 6030, 0, (0, 0, 0, 0, 0, 0, 0, 0)),
        (13, 6200, 0, (0, 0, 0, 0, 0, 0, 0, 0)),
    )
)

ULTIMATE_UFO_PROTOTYPE_PHASES: tuple[dict, ...] = tuple(
    {"phase":phase,"trigger_frame":frame,"delay_frames":delay,"part_flags":flags,"part_status":dict(zip(ULTIMATE_UFO_PART_STATUS_FIELDS, flags))} for phase,frame,delay,flags in (
        (1, 0, 0, (0, 0, 0, 0, 0, 0, 0, 0)),
        (2, 1800, 0, (1, 1, 0, 0, 0, 0, 0, 0)),
        (3, 2300, 0, (0, 0, 1, 1, 0, 0, 0, 0)),
        (4, 3123, 0, (0, 0, 0, 0, 0, 0, 0, 0)),
        (5, 4231, 200, (0, 0, 0, 0, 0, 0, 0, 0)),
        (6, 4600, 0, (0, 0, 0, 0, 1, 1, 1, 1)),
        (7, 5100, 0, (0, 0, 0, 0, 1, 1, 1, 1)),
        (8, 5300, 0, (0, 0, 0, 0, 0, 0, 1, 1)),
        (9, 5897, 2000, (0, 0, 0, 0, 0, 0, 0, 0)),
        (10, 5898, 0, (0, 0, 0, 0, 0, 0, 0, 0)),
        (11, 5902, 0, (0, 0, 0, 0, 0, 0, 0, 0)),
        (12, 6200, 0, (0, 0, 0, 0, 0, 0, 0, 0)),
    )
)

def water_strider_route_frame(frame: int) -> dict:
    """Evaluate the retail Water Strider course clock (0..1440, then wrap)."""
    raw = int(frame)
    wrapped = raw % 1441
    seg = next(item for item in WATER_STRIDER_SEGMENTS if item["start"] <= wrapped <= item["end"])
    return {"input_frame":raw,"route_frame":wrapped,"loop_length":1441,"segment":dict(seg)}

def ultimate_ufo_phase(frame: int, *, build: str = "retail") -> dict:
    """Return the latest executable phase record at or before *frame*."""
    key = build.strip().lower()
    proto = key in {"may9","may11","xbox360_may9","xbox360_may11","prototype"}
    table = ULTIMATE_UFO_PROTOTYPE_PHASES if proto else ULTIMATE_UFO_RETAIL_PHASES
    f = max(0, int(frame))
    active = table[0]
    for item in table:
        if item["trigger_frame"] <= f:
            active = item
        else:
            break
    return {"input_frame":int(frame),"route_frame":f,"finite":True,"table":"prototype_may9_may11" if proto else "retail_june10_ps3","active":dict(active)}

def special_stage_reload_for_warning(value: int) -> dict | None:
    """Resolve an executable-backed opcode-0x78 special-stage request."""
    for item in SPECIAL_STAGE_RELOAD_CHAIN:
        if item["script_argument"] == int(value):
            return dict(item)
    return None


def ultimate_ufo_death_sequence() -> list[dict]:
    """Return the conservative executable-backed Ultimate UFO destruction chain."""
    return [dict(item) for item in ULTIMATE_UFO_DEATH_CHAIN]


def ultimate_ufo_stage_profile(profile: str) -> dict:
    """Return the normal 5-3 or Bonus 5-6 executable-backed behavior profile."""
    key = profile.strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {"5_3":"normal_5_3", "normal":"normal_5_3", "level5_stage3":"normal_5_3",
               "5_6":"bonus_5_6", "bonus":"bonus_5_6", "extra5_stage6":"bonus_5_6"}
    key = aliases.get(key, key)
    for item in ULTIMATE_UFO_STAGE_PROFILES:
        if item["profile"] == key:
            return dict(item)
    raise ValueError(f"unknown Ultimate UFO stage profile: {profile}")


def ultimate_ufo_mframe_route_chain() -> list[dict]:
    """Return direct Mframe -> fld015 frame setter evidence for all five builds."""
    return [dict(item) for item in ULTIMATE_UFO_MFRAME_ROUTE_CHAIN]


def pa_camera_lifecycle() -> list[dict]:
    """Return the executable-backed animated-to-procedural PA camera lifecycle."""
    return [dict(item) for item in PA_CAMERA_LIFECYCLE]


def ultimate_ufo_late_camera_geometry() -> list[dict]:
    """Return real fld015 late samples evaluated with procedural preset 4."""
    return [dict(item) for item in ULTIMATE_UFO_LATE_CAMERA_GEOMETRY]


def ultimate_ufo_camera_transition_gate() -> list[dict]:
    """Return retail camera transition-gate semantics tied to Ultimate UFO reset."""
    return [dict(item) for item in ULTIMATE_UFO_CAMERA_TRANSITION_GATE]


def ultimate_ufo_final_vanish_evolution() -> list[dict]:
    """Return May prototype final-Vanish and later-build ending evolution."""
    return [dict(item) for item in ULTIMATE_UFO_FINAL_VANISH_EVOLUTION]


def ultimate_ufo_final_reset_audit() -> list[dict]:
    """Return the dev14 retail final-reset and camera-gate caller audit."""
    return [dict(item) for item in ULTIMATE_UFO_FINAL_RESET_AUDIT]


def stage_category(stage_id: int) -> int:
    """Return the retail stage/category bucket reconstructed from the executable."""
    value = int(stage_id)
    if value < 0x1F:
        return 0
    if value < 0x28:
        return 1
    if value < 0x31:
        return 2
    if value < 0x3A:
        return 3
    if value < 0x43:
        return 4
    if value < 0x4C:
        return 5
    if value < 0xAF:
        return 6
    if value == 9999:
        return 7
    return 0


def build_gate(build: str) -> PaRouteBuildGate:
    key = build.strip().lower()
    aliases = {
        "ps3":"ps3_retail", "retail_ps3":"ps3_retail",
        "xbox":"xbox360_retail", "xbox360":"xbox360_retail", "retail_xbox":"xbox360_retail",
        "june10":"xbox360_june10", "may11":"xbox360_may11", "may9":"xbox360_may9",
    }
    key = aliases.get(key, key)
    for item in BUILD_GATES:
        if item.build == key:
            return item
    raise ValueError(f"unknown PA-route build: {build}")


def evaluate_gate(build: str, *, stage_id: int, state_218: int, state_21c: int) -> dict:
    item = build_gate(build)
    category = stage_category(stage_id)
    if not item.setup_calls_pa_route:
        eligible = False
        reason = "corresponding stage setup does not invoke the PA-route activation branch"
    else:
        eligible = True
        reasons: list[str] = []
        if item.requires_category_zero and category != 0:
            eligible = False
            reasons.append(f"stage category is {category}, expected 0")
        if item.requires_state_218 is not None and state_218 != item.requires_state_218:
            eligible = False
            reasons.append(f"state +0x218 is {state_218}, expected {item.requires_state_218}")
        if item.requires_state_21c is not None and state_21c != item.requires_state_21c:
            eligible = False
            reasons.append(f"state +0x21C is {state_21c}, expected {item.requires_state_21c}")
        reason = "eligible under reconstructed gate" if eligible else "; ".join(reasons)
    return {
        "build": item.build,
        "stage_id": int(stage_id),
        "stage_category": category,
        "state_218": int(state_218),
        "state_21c": int(state_21c),
        "eligible": bool(eligible),
        "reason": reason,
        "gate": asdict(item),
    }


def camera_selection(index: int) -> dict:
    for item in CAMERA_SELECTIONS:
        if item["index"] == int(index):
            return dict(item)
    raise ValueError("PA-route camera index must be 0 or 1")


def boss_correlation_for_opcode(opcode: int) -> dict | None:
    for item in BOSS_FIELD_CORRELATIONS:
        if item["opcode"] == int(opcode):
            return dict(item)
    return None


def analyze_parsed_dat(parsed: Mapping) -> dict:
    occurrences: list[dict] = []
    transitions: list[dict] = []
    for record in parsed.get("records", []):
        opcode = int(record.get("opcode", -1))
        mapping = boss_correlation_for_opcode(opcode)
        if mapping is not None:
            occurrences.append({
                "record_index": record.get("index"),
                "absolute_frame": record.get("absolute_frame"),
                "opcode": record.get("opcode"),
                "opcode_hex": record.get("opcode_hex"),
                "opcode_name": record.get("opcode_name"),
                "correlation": mapping,
            })
        if opcode == 0x78:
            args = record.get("args_signed") or record.get("args") or []
            if args:
                transition = special_stage_reload_for_warning(int(args[0]))
                if transition is not None:
                    transitions.append({"record_index":record.get("index"),"absolute_frame":record.get("absolute_frame"),"script_value":int(args[0]),"transition":transition})
    return {
        "format": "SIIG_PA_ROUTE_INFO",
        "dat_entry_count": parsed.get("entry_count"),
        "dat_duration_frames": parsed.get("duration_frames"),
        "boss_occurrences": occurrences,
        "boss_occurrence_count": len(occurrences),
        "special_stage_transitions": transitions,
        "special_stage_transition_count": len(transitions),
        "warning": "A boss spawn opcode alone is not an activation trigger. Opcode 0x78 values 12/14 are now direct executable-backed special-stage reload requests; their surrounding script timing remains authored DAT behavior.",
    }


def reference_snapshot() -> dict:
    return {
        "format": "SIIG_PA_ROUTE_REFERENCE",
        "build_gates": [asdict(item) for item in BUILD_GATES],
        "functions": [dict(item) for item in PA_ROUTE_FUNCTIONS],
        "camera_selections": [dict(item) for item in CAMERA_SELECTIONS],
        "boss_field_correlations": [dict(item) for item in BOSS_FIELD_CORRELATIONS],
        "special_stage_reload_chain": [dict(item) for item in SPECIAL_STAGE_RELOAD_CHAIN],
        "ultimate_ufo_death_chain": [dict(item) for item in ULTIMATE_UFO_DEATH_CHAIN],
        "ultimate_ufo_late_objects": [dict(item) for item in ULTIMATE_UFO_LATE_OBJECTS],
        "ultimate_ufo_debug_hud": dict(ULTIMATE_UFO_DEBUG_HUD),
        "ultimate_ufo_part_status_objects": [dict(item) for item in ULTIMATE_UFO_PART_STATUS_OBJECTS],
        "ultimate_ufo_stage_profiles": [dict(item) for item in ULTIMATE_UFO_STAGE_PROFILES],
        "ultimate_ufo_mframe_route_chain": [dict(item) for item in ULTIMATE_UFO_MFRAME_ROUTE_CHAIN],
        "pa_camera_lifecycle": [dict(item) for item in PA_CAMERA_LIFECYCLE],
        "ultimate_ufo_late_camera_geometry": [dict(item) for item in ULTIMATE_UFO_LATE_CAMERA_GEOMETRY],
        "ultimate_ufo_late_camera_conclusion": dict(ULTIMATE_UFO_LATE_CAMERA_CONCLUSION),
        "ultimate_ufo_camera_transition_gate": [dict(item) for item in ULTIMATE_UFO_CAMERA_TRANSITION_GATE],
        "ultimate_ufo_final_vanish_evolution": [dict(item) for item in ULTIMATE_UFO_FINAL_VANISH_EVOLUTION],
        "ultimate_ufo_final_reset_audit": [dict(item) for item in ULTIMATE_UFO_FINAL_RESET_AUDIT],
        "ps3_camera_preset_direct_callers": [dict(item) for item in PS3_CAMERA_PRESET_DIRECT_CALLERS],
        "boss_route_functions": [dict(item) for item in BOSS_ROUTE_FUNCTIONS],
        "water_strider_segments": [dict(item) for item in WATER_STRIDER_SEGMENTS],
        "ultimate_ufo_retail_phases": [dict(item) for item in ULTIMATE_UFO_RETAIL_PHASES],
        "ultimate_ufo_prototype_phases": [dict(item) for item in ULTIMATE_UFO_PROTOTYPE_PHASES],
        "limits": [
            "PA is retained as the executable/debug name; its expansion is unknown.",
            "Retail stage setup is directly observed selecting camera index 0; cam02 activation is not yet proven.",
            "Water Strider retail/June/PS3 course clock wraps after frame 1440; May prototypes contain the same 0..1440 segment boundaries but their surrounding driver evolved.",
            "Ultimate UFO retail/June/PS3 uses the 13-phase table; May 9/May 11 use an earlier 12-phase table. All Xbox builds target executable model bos_015k.gmx in the late route; May 9/11 use runtime ID 0xD9 while June/retail use 0xD8. The airlock-door role is corroborating project-owner observation rather than an executable string.",
            "The normal 5-3 late preset-4 + fld015 geometry is now classified as rear-follow geometry from an executable/asset chain; the exact rendered shot still depends on runtime dynamic-X input and an exhaustive exclusion of every non-DAT external preset write.",
            "Retail part-0/state-0 reset clears the camera controller timed-transition gate outside Extra 5-6; this is a transition lock, not a camera eye/target value. May 9/11 phase 12 explicitly invokes UltimateUfo::Vanish(0) at Mframe 6200. June/retail do not clear the gate at their 6030 state-1 destruction or 6200 bos_015k shutdown; the ordinary later +0x48 caller remains unresolved.",
            "cam02 activation remains unproven.",
            "Boss-to-field-model mapping is now direct through opcode 0x78 script values 12/14, the retail transition-state writes, and reload selection.",
            "DAT boss spawn presence is not by itself an automatic PA-route activation trigger.",
        ],
    }
