#!/usr/bin/env python3
"""Executable-backed iOS -> console SIIG code-lineage reference data.

This module contains only derived metadata and equations. It does not contain
proprietary executable bytes or decompiled game code.
"""
from __future__ import annotations

from typing import Any


IOS_CONSOLE_FUNCTION_LINEAGE = (
    {
        "subsystem": "MAP loader",
        "ios_symbol": "Invinf_LoadMap",
        "ios_address_armv7": "0x000900CC",
        "console_xbox_address": "0x82239190",
        "console_role": "load/allocate MAP layers",
        "confidence": "high",
        "preserved": "layer count; width/height descriptors; one cell buffer per layer; row-major u8 cells",
        "changed": "mobile MAP integer headers are little-endian; console headers are big-endian; resource packaging/path changed",
    },
    {
        "subsystem": "MAP runtime update",
        "ios_symbol": "calcMap",
        "ios_address_armv7": "0x0008D020",
        "console_xbox_address": "0x82239608",
        "console_role": "update MAP scrolling and visible ranges",
        "confidence": "high",
        "preserved": "three per-layer X/Y velocities; fixed-point position accumulation; clamped visible row/column ranges",
        "changed": "console implementation is reorganized around the console runtime and renderer",
    },
    {
        "subsystem": "MAP cell renderer",
        "ios_symbol": "drawMap2",
        "ios_address_armv7": "0x0008E5EC",
        "console_xbox_address": "0x8223AC28 + 0x8223A1B0",
        "console_role": "decode cells and submit 49-tile reflected variants",
        "confidence": "high",
        "preserved": "cell&0x3F tile code; 0 empty; tile indices 0..48 after subtract-one; 0x40 X reflection; 0x80 Y reflection",
        "changed": "platform-specific draw/geometry submission path",
    },
    {
        "subsystem": "MAP scroll command",
        "ios_symbol": "analyzeScript2 + setMapLayerSpeed",
        "ios_address_armv7": "0x00093CFC + 0x0008CFC4",
        "console_xbox_address": "0x820FB578 dispatcher; 2D scroll handlers in same script subsystem",
        "console_role": "SCROLL_01/02/03 set MAP layer 0/1/2 X/Y velocities",
        "confidence": "high",
        "preserved": "opcodes 0x6E/0x6F/0x70; three layer channels; speed normalization against 30-Hz authored timebase",
        "changed": "console SCROLL_01 Y also drives 3D wall/background; SCROLL_02 Y also drives 3D route/camera/field",
    },
    {
        "subsystem": "authored DAT loader",
        "ios_symbol": "Invinf_LoadScript",
        "ios_address_armv7": "0x0008FEFC",
        "console_xbox_address": "0x82239790 (June 10)",
        "console_build_addresses": {
            "xbox_may9": "0x8222C3B8",
            "xbox_may11": "0x8222DE78",
            "xbox_june10": "0x82239790",
            "xbox_retail": "0x82212888",
            "ps3_retail_opd": "0x000DF5C0",
        },
        "console_role": "shared DAT loader/index representation",
        "confidence": "high",
        "preserved": "version-1 command stream; big-endian 16-bit words; flattened word-data buffer plus per-command starting-word index; delta-frame timing",
        "changed": "addresses move across prototype/retail builds while the compact loader/index architecture remains recognizable",
    },
    {
        "subsystem": "script execution",
        "ios_symbol": "analyzeScript + analyzeScript_FPS60 + analyzeScript2",
        "ios_address_armv7": "0x00011C68 + 0x001308B4 + 0x00093CFC",
        "console_xbox_address": "0x820FB578",
        "console_role": "SgScript::AnalyzeScript candidate / June dispatcher",
        "confidence": "high-architectural",
        "preserved": "same low-range DAT command language and 30-Hz authored timing model",
        "changed": "mobile duplicates the primary enemy dispatcher for 30/60 Hz; console consolidates timing through a runtime frame multiplier and extends the command vocabulary through 0xCE",
    },
    {
        "subsystem": "generator DAT block loader",
        "ios_symbol": "stageScriptBlockLoad(NSString*,int)",
        "ios_address_armv7": "0x000DF89C",
        "console_xbox_address": "0x8226BC48",
        "console_role": "generator DAT block loading/assembly",
        "confidence": "high-structural",
        "preserved": "same DAT block serialization; append into generator script/index buffers; cumulative timeline across blocks",
        "changed": "console implementation/address naming reconstructed from debug executable rather than retained source symbols",
    },
    {
        "subsystem": "generator MAP initialization",
        "ios_symbol": "stageGenerateMapInit",
        "ios_address_armv7": "0x000E0128",
        "console_xbox_address": None,
        "console_ps3_address": "0x001327E8",
        "console_role": "generator output-map buffer initialization (exact PS3 retail initializer recovered; Xbox address still not pinned)",
        "confidence": "high-mobile / high-console-ps3",
        "preserved": "three generated output layers and fixed reusable-block assembly model",
        "changed": "PS3 retail allocates 0x3000 bytes per generated output layer versus iOS 0x1800; content-authoring rationale for the expanded console generator corpus remains open",
    },
    {
        "subsystem": "generator MAP assembly",
        "ios_symbol": "stageGenerateMap",
        "ios_address_armv7": "0x000E06D8",
        "console_xbox_address": "0x8226CB28 + 0x8226CD30",
        "console_role": "append generator MAP blocks + choose/load 24 named blocks",
        "confidence": "high",
        "preserved": "24-block generated stage; a_%03d.map..j_%03d.map naming family; three-layer map assembly; same 330-map generator family",
        "changed": "console split selection and append responsibilities into distinct recovered routines; stored MAP corpus capacity doubled",
    },
)


# dev19 direct gameplay-code ancestry. Pool rows are source-only structural
# metadata reconstructed from named iOS functions and console constructors; no
# executable bytes or decompiled code are embedded.
STAGE3_BOSS_POOL_LINEAGE = (
    {"boss": "THE_MOON", "ios_opcode": "0x0046", "ios_pools": ((70, 5), (36, 20)), "console_pools": ((70, 5), (36, 20)), "preserved_slots": 2, "total_slots": 2},
    {"boss": "THE_SUN", "ios_opcode": "0x0047", "ios_pools": ((71, 9), (37, 8), (38, 36), (39, 20), (46, 4)), "console_pools": ((71, 9), (37, 8), (38, 60), (39, 20), (46, 4)), "preserved_slots": 4, "total_slots": 5, "changed_slot": {"type_id": 38, "ios_capacity": 36, "console_capacity": 60, "ios_handler": "dischargeTheSunWaveShot"}},
    {"boss": "GIGANTIC_UFO", "ios_opcode": "0x0048", "ios_pools": ((72, 59), (40, 20), (41, 20), (42, 4), (43, 2), (44, 2), (23, 10), (28, 10), (60, 30), (29, 30), (80, 4)), "console_pools": ((72, 59), (40, 20), (41, 20), (42, 4), (43, 2), (44, 2), (23, 10), (28, 10), (60, 30), (29, 30), (80, 4)), "preserved_slots": 11, "total_slots": 11},
    {"boss": "LADYBUG", "ios_opcode": "0x0049", "ios_pools": ((73, 5), (45, 40), (46, 20), (47, 4)), "console_pools": ((73, 5), (45, 40), (46, 20), (47, 4)), "preserved_slots": 4, "total_slots": 4},
    {"boss": "MANDALA", "ios_opcode": "0x004A", "ios_pools": ((74, 72), (48, 100), (49, 10), (50, 40)), "console_pools": ((74, 72), (48, 100), (49, 10), (50, 40)), "preserved_slots": 4, "total_slots": 4},
    {"boss": "UNKNOWN", "ios_opcode": "0x004B", "ios_pools": ((75, 11), (51, 30), (52, 30), (53, 80)), "console_pools": ((75, 11), (51, 30), (52, 30), (53, 80)), "preserved_slots": 4, "total_slots": 4},
)

BOSS_CONSTRUCTOR_EVOLUTION = (
    {"boss": "THE_MOON", "may9_address": "0x821C8E80", "may11_address": "0x821CA918", "june10_address": "0x821D6E60", "retail_xbox_address": "0x821AFEB8", "retail_ps3_address": "0x000155A0", "mnemonic_lengths": {"may9": 162, "may11": 162, "june10": 145, "retail": 145}, "may9_to_may11_mnemonic_similarity": 1.0, "may11_to_june10_mnemonic_similarity": 0.87947883, "june10_to_retail_mnemonic_similarity": 1.0, "interpretation": "0x10C->0x120 entity-layout refactor; field movement and centralized frame-multiplier timing preserve gameplay mathematics"},
    {"boss": "THE_SUN", "may9_address": "0x821C9108", "may11_address": "0x821CABA0", "june10_address": "0x821D9268", "retail_xbox_address": "0x821B22C0", "retail_ps3_address": "0x00014A78", "mnemonic_lengths": {"may9": 370, "may11": 370, "june10": 348, "retail": 348}, "may9_to_may11_mnemonic_similarity": 1.0, "may11_to_june10_mnemonic_similarity": 0.86072423, "june10_to_retail_mnemonic_similarity": 1.0, "interpretation": "same May11->June10 engine/layout refactor around preserved boss construction"},
    {"boss": "GIGANTIC_UFO", "may9_address": "0x821CAEB8", "may11_address": "0x821CC950", "june10_address": "0x821D97D8", "retail_xbox_address": "0x821B2830", "retail_ps3_address": "0x000133C8", "mnemonic_lengths": {"may9": 837, "may11": 837, "june10": 779, "retail": 779}, "may9_to_may11_mnemonic_similarity": 1.0, "may11_to_june10_mnemonic_similarity": 0.87995050, "june10_to_retail_mnemonic_similarity": 1.0, "interpretation": "same May11->June10 engine/layout refactor around preserved boss construction"},
    {"boss": "LADYBUG", "may9_address": "0x821C9760", "may11_address": "0x821CB1F8", "june10_address": "0x821D7138", "retail_xbox_address": "0x821B0190", "retail_ps3_address": "0x00012AF0", "mnemonic_lengths": {"may9": 288, "may11": 288, "june10": 268, "retail": 268}, "may9_to_may11_mnemonic_similarity": 1.0, "may11_to_june10_mnemonic_similarity": 0.89208633, "june10_to_retail_mnemonic_similarity": 1.0, "interpretation": "same May11->June10 engine/layout refactor around preserved boss construction"},
    {"boss": "MANDALA", "may9_address": "0x821C9D58", "may11_address": "0x821CB7F0", "june10_address": "0x821D76E0", "retail_xbox_address": "0x821B0738", "retail_ps3_address": "0x00011A90", "mnemonic_lengths": {"may9": 601, "may11": 601, "june10": 562, "retail": 562}, "may9_to_may11_mnemonic_similarity": 1.0, "may11_to_june10_mnemonic_similarity": 0.92691316, "june10_to_retail_mnemonic_similarity": 1.0, "interpretation": "same May11->June10 engine/layout refactor around preserved boss construction"},
    {"boss": "UNKNOWN", "may9_address": "0x821CA6C0", "may11_address": "0x821CC158", "june10_address": "0x821D7FA8", "retail_xbox_address": "0x821B1000", "retail_ps3_address": "0x0001121C", "mnemonic_lengths": {"may9": 278, "may11": 278, "june10": 252, "retail": 252}, "may9_to_may11_mnemonic_similarity": 1.0, "may11_to_june10_mnemonic_similarity": 0.92075472, "june10_to_retail_mnemonic_similarity": 1.0, "interpretation": "same May11->June10 engine/layout refactor around preserved boss construction"},
)


# dev20 direct state-machine ancestry. The console dispatcher retains the original
# iOS boss IDs 70..75 (0x46..0x4B), and each slot routes to a dedicated mover.
# Only addresses, normalized instruction fingerprints, constants, equations, and
# semantic observations are retained here; no proprietary decompiled code is bundled.
BOSS_MOVER_DISPATCHERS = {
    "xbox_may9": "0x8225E9D0",
    "xbox_may11": "0x82260668",
    "xbox_june10": "0x8226A988",
    "xbox_retail": "0x822434B8",
    "ps3_retail": "0x0012FB70",
}

BOSS_MOVER_LINEAGE = (
    {
        "boss": "THE_MOON", "type_id": 70, "opcode": "0x46", "ios_mover": "moveTheMoon", "ios_address_armv7": "0x000D0014",
        "xbox_addresses": {"may9": "0x82254920", "may11": "0x82256570", "june10": "0x822611D8", "retail": "0x82239D08"}, "ps3_retail_address": "0x0011459C",
        "mnemonic_lengths": {"may9": 1258, "may11": 1258, "june10": 1133, "retail": 1133},
        "similarity": {"may9_to_may11": 1.0, "may11_to_june10": 0.89251359, "june10_to_retail_raw": 1.0, "june10_to_retail_semantic_equivalent": True},
        "semantic_anchor": {"mobile_event_thresholds": [122, 132], "console_event_thresholds_base": [262, 272], "sound_id": "0x80", "vibration_value": 100, "threshold_spacing_preserved": 10, "note": "event order and spacing survive while the console intro counter/timing scheme is deliberately retimed"},
    },
    {
        "boss": "THE_SUN", "type_id": 71, "opcode": "0x47", "ios_mover": "moveTheSun", "ios_address_armv7": "0x000D8000",
        "xbox_addresses": {"may9": "0x82255CC8", "may11": "0x82257918", "june10": "0x82262390", "retail": "0x8223AEC0"}, "ps3_retail_address": "0x001121A4",
        "mnemonic_lengths": {"may9": 1391, "may11": 1391, "june10": 1248, "retail": 1248},
        "similarity": {"may9_to_may11": 1.0, "may11_to_june10": 0.72906404, "june10_to_retail_raw": 1.0, "june10_to_retail_semantic_equivalent": True},
        "semantic_anchor": {"target": 6144, "mobile_step": 512, "console_step_numerator": 15360, "console_step_base": 512, "pair_count": 4, "mobile_original_type": 71, "v2_bypasses_original_ramp": True, "note": "same four-pair +/-512 ramp toward 6144; console expresses the step through the 30-Hz timing denominator"},
    },
    {
        "boss": "GIGANTIC_UFO", "type_id": 72, "opcode": "0x48", "ios_mover": "moveGiganticUfo", "ios_address_armv7": "0x000D64F8",
        "xbox_addresses": {"may9": "0x822574A8", "may11": "0x822590F8", "june10": "0x82263910", "retail": "0x8223C440"}, "ps3_retail_address": "0x0010DB14",
        "mnemonic_lengths": {"may9": 2078, "may11": 2078, "june10": 2071, "retail": 2071},
        "similarity": {"may9_to_may11": 1.0, "may11_to_june10": 0.92745240, "june10_to_retail_raw": 0.99758571, "june10_to_retail_semantic_equivalent": True, "raw_difference_kind": "relocated global-address materialization only"},
        "semantic_anchor": {"mobile_original_offset": 4096, "mobile_v2_offset": 18432, "console_offset": 4096, "v2_offset_path_present_console": False, "original_pool_loop_count": 59, "note": "console follows the original type-72 placement path, not the V2 type-102 offset path"},
    },
    {
        "boss": "LADYBUG", "type_id": 73, "opcode": "0x49", "ios_mover": "moveLadybug", "ios_address_armv7": "0x000D4D7C",
        "xbox_addresses": {"may9": "0x82259520", "may11": "0x8225B170", "june10": "0x82265970", "retail": "0x8223E4A0"}, "ps3_retail_address": "0x00109DB8",
        "mnemonic_lengths": {"may9": 1948, "may11": 1955, "june10": 1851, "retail": 1851},
        "similarity": {"may9_to_may11": 0.99564438, "may11_to_june10": 0.82869154, "june10_to_retail_raw": 1.0, "june10_to_retail_semantic_equivalent": True},
        "semantic_anchor": {"state": "0x14", "growth_percent_per_update": 10, "saturation": 32767, "fields": ["+0xE8", "+0xEC", "+0xF0"], "may11_added_guard_global_state": "0x10", "guard_meaning": "unresolved", "retune_window": "May 9 -> May 11", "note": "May 11 adds a real global-state guard around an inherited 1.1x three-field growth/clear path; it persists thereafter"},
    },
    {
        "boss": "MANDALA", "type_id": 74, "opcode": "0x4A", "ios_mover": "moveMandala", "ios_address_armv7": "0x000D223C",
        "xbox_addresses": {"may9": "0x8225B390", "may11": "0x8225D000", "june10": "0x82267660", "retail": "0x82240190"}, "ps3_retail_address": "0x001084CC",
        "mnemonic_lengths": {"may9": 846, "may11": 846, "june10": 784, "retail": 784},
        "similarity": {"may9_to_may11": 1.0, "may11_to_june10": 0.89570552, "june10_to_retail_raw": 1.0, "june10_to_retail_semantic_equivalent": True},
        "semantic_anchor": {"first_ring_count": 20, "first_ring_coefficient": 109, "second_ring_count": 8, "second_ring_coefficient": 69, "alternating_direction_preserved": True, "note": "the same trig-derived 109/69 geometry coefficients survive; console replaces the mobile fixed center with runtime root/base placement"},
    },
    {
        "boss": "UNKNOWN", "type_id": 75, "opcode": "0x4B", "ios_mover": "moveUnknown", "ios_address_armv7": "0x000D2C30",
        "xbox_addresses": {"may9": "0x8225C0C8", "may11": "0x8225DD38", "june10": "0x822682A0", "retail": "0x82240DD0"}, "ps3_retail_address": "0x001039EC",
        "mnemonic_lengths": {"may9": 2191, "may11": 2191, "june10": 2046, "retail": 2046},
        "similarity": {"may9_to_may11": 1.0, "may11_to_june10": 0.91432617, "june10_to_retail_raw": 0.99853372, "june10_to_retail_semantic_equivalent": True, "raw_difference_kind": "relocated global-address materialization only"},
        "semantic_anchor": {"mobile_original_motion": 2560, "mobile_v2_motion_multiplier": 2, "console_motion": 2560, "helper_slots": ["+0x14", "+0x28"], "v2_doubling_present_console": False, "v2_destroy_present_console": False, "note": "console follows original type-75 +/-2560 motion and omits the V2 doubling/defeat branch"},
    },
)

CONSOLE_ENEMY_HANDLER_LINEAGE = (
    {"opcode": 0x96, "script_name": "CIRCLE_INVADER"},
    {"opcode": 0x97, "script_name": None},
    {"opcode": 0x98, "script_name": None},
    {"opcode": 0x99, "script_name": "GREED"},
    {"opcode": 0x9A, "script_name": "LINE_INVADER"},
    {"opcode": 0x9B, "script_name": "WRATH"},
    {"opcode": 0x9C, "script_name": "GLUTTONY", "retune": "56-object helper type 55->72", "retune_window": "May 9 -> May 11"},
    {"opcode": 0x9D, "script_name": None},
    {"opcode": 0x9E, "script_name": "SG_GIGANTIC_UFO"},
    {"opcode": 0x9F, "script_name": None, "dispatcher_status": "NULL in May 9, May 11, June 10, and retail; absent from available DAT corpus"},
    {"opcode": 0xA0, "script_name": "CENTIPEDE"},
    {"opcode": 0xA1, "script_name": "HONET"},
    {"opcode": 0xA2, "script_name": "PROGRESSIVE_UFO"},
    {"opcode": 0xA3, "script_name": "OCTOPUS"},
    {"opcode": 0xA4, "script_name": "BUTTERFLY"},
    {"opcode": 0xA5, "script_name": None},
    {"opcode": 0xA6, "script_name": "WATER_STRIDER"},
    {"opcode": 0xA7, "script_name": "CRAB", "name_status": "resolved in 2.10.0-dev4: A7 registry root bos_013.gmx is explicitly tied to the Crab.cpp part-construction/runtime family and its CD/CC/CE/CF child table"},
    {"opcode": 0xA8, "script_name": "ULTIMATE_UFO", "retune": "type-55 helper pool capacity 20->40", "retune_window": "May 11 -> June 10"},
    {"opcode": 0xA9, "script_name": "SQUID"},
    {"opcode": 0xAA, "script_name": "VERTEBRATE", "retune": "one pool 4->20; one 80-object helper type 72->62", "retune_window": "May 11 -> June 10"},
    {"opcode": 0xAB, "script_name": "NO_NAME"},
)

WORLD5_DEVELOPMENT_CHRONOLOGY = (
    {"opcode": 0xA6, "script_name": "WATER_STRIDER", "normal_stage": "5-1", "may9": "trial 5-1 only; not normal 5-1", "may11": "normal 5-1 integrated", "june10": "normal 5-1 integrated", "retail": "normal 5-1 integrated"},
    {"opcode": 0xA7, "script_name": "CRAB", "normal_stage": "5-2", "may9": "boss slot present in normal 5-2", "may11": "boss slot present", "june10": "boss slot present", "retail": "boss slot present", "note": "CRAB identification resolved in 2.10.0-dev4 by explicit A7 bos_013.gmx registry + Crab.cpp part-construction/runtime linkage"},
    {"opcode": 0xA8, "script_name": "ULTIMATE_UFO", "normal_stage": "5-3", "may9": "normal 5-3 integrated", "may11": "normal 5-3 integrated", "june10": "normal 5-3 integrated", "retail": "normal 5-3 integrated"},
    {"opcode": 0xA9, "script_name": "SQUID", "normal_stage": "5-4", "may9": "not normal-stage content", "may11": "not normal-stage content", "june10": "first preserved normal-stage integration", "retail": "normal 5-4 integrated"},
    {"opcode": 0xAA, "script_name": "VERTEBRATE", "normal_stage": "5-5", "may9": "not normal-stage content", "may11": "not normal-stage content", "june10": "first preserved normal-stage integration", "retail": "normal 5-5 integrated"},
    {"opcode": 0xAB, "script_name": "NO_NAME", "normal_stage": "5-6", "may9": "hidden 3Db_026.dat generator test only", "may11": "hidden 3Db_026.dat generator test only", "june10": "first preserved normal-stage integration", "retail": "normal 5-6 integrated"},
)


CONSOLE_OPCODE_EXPANSION = (
    {"range": "0x96-0xAB", "family": "new/expanded console enemies and 3D bosses", "examples": "CIRCLE_INVADER, GREED, WRATH, WATER_STRIDER, ULTIMATE_UFO, SQUID, VERTEBRATE, NO_NAME"},
    {"range": "0xB4-0xBE", "family": "3D stage controls", "examples": "3D Back Scroll, 3D Wall Scroll, 3D Back Color, 3D Camera Change 01, 3D Demo, 3D Back Animation, 3D Field Rotate Control"},
    {"range": "0xC8-0xCE", "family": "Visualizer controls", "examples": "VL_START, VL_END, VL_DISP_ON/OFF, VL_SEQUENCESET, VL_CHANGETIME, VL_VOLUME_SCALE"},
)


def ios_console_lineage_reference() -> dict[str, Any]:
    """Return source-only executable-lineage facts through dev20 research."""
    return {
        "format": "SIIG_IOS_CONSOLE_CODE_LINEAGE",
        "schema_version": 3,
        "mobile_command_dispatch": {
            "primary_analyzer": {"symbol": "analyzeScript", "serialized_opcode_min": 0x02, "serialized_opcode_max": 0x83},
            "fps60_primary_analyzer": {"symbol": "analyzeScript_FPS60", "serialized_opcode_min": 0x02, "serialized_opcode_max": 0x83},
            "secondary_analyzer": {"symbol": "analyzeScript2", "serialized_opcode_min": 0x6E, "serialized_opcode_max": 0x8D},
            "effective_mobile_frontier": 0x8D,
            "console_table_frontier": 0xCE,
            "note": "0x83 is only the primary iOS analyzer frontier; 0x84..0x8D are handled by analyzeScript2.",
        },
        "timing_model": {
            "authored_hz": 30,
            "ios_delta_runtime_formula": "runtime_delta = authored_delta * runtime_fps / 30",
            "ios_scroll_runtime_formula": "runtime_speed = authored_speed * 30 / runtime_fps",
            "console_duration_formula": "runtime_updates = authored_ticks * frame_multiplier",
            "console_velocity_formula": "runtime_velocity = authored_velocity / frame_multiplier",
            "console_update_hz_formula": "runtime_updates_per_second = 30 * frame_multiplier",
            "interpretation": "same 30-Hz authored-time invariant; console centralizes the 30/60 timing policy that mobile partly handled with duplicated primary analyzers",
        },
        "generator_model": {
            "ios_output_layers": 3,
            "ios_bytes_per_output_layer": 6144,
            "ios_block_iterations": 24,
            "ordinary_block_width": 8,
            "ordinary_block_height": 32,
            "capacity_identity": "6144 = 24 * 8 * 32",
            "ios_generator_map_files": 330,
            "ios_nonempty_generator_layers": 645,
            "ios_generator_cells": 121472,
            "console_generator_map_files": 330,
            "console_nonempty_generator_layers": 645,
            "console_generator_cells": 242944,
            "console_to_ios_cell_ratio": 2.0,
            "console_ps3_output_layers": 3,
            "console_ps3_init_address": "0x001327E8",
            "console_ps3_append_address": "0x001329DC",
            "console_ps3_capacity_factors": [32, 32, 32],
            "console_ps3_capacity_multiplier": 384,
            "console_ps3_bytes_per_output_layer": 12288,
            "console_to_ios_output_capacity_ratio": 2.0,
            "capacity_resolution": "iOS 0x1800 bytes/layer -> PS3 retail 0x3000 bytes/layer; PS3 stageGenerateMapInit computes each capacity as 0x20 * 0x180 and the append path bounds writes against the same product",
            "warning": "the runtime output-buffer doubling is proven, but nonzero cells are not doubled; this does not prove that console resource content is a simple duplication or why designers chose the expanded authored corpus",
        },
        "function_lineage": [dict(x) for x in IOS_CONSOLE_FUNCTION_LINEAGE],
        "stage3_boss_pool_lineage": [dict(x) for x in STAGE3_BOSS_POOL_LINEAGE],
        "boss_constructor_evolution": [dict(x) for x in BOSS_CONSTRUCTOR_EVOLUTION],
        "boss_mover_dispatchers": dict(BOSS_MOVER_DISPATCHERS),
        "boss_mover_lineage": [dict(x) for x in BOSS_MOVER_LINEAGE],
        "console_enemy_handler_lineage": [dict(x) for x in CONSOLE_ENEMY_HANDLER_LINEAGE],
        "world5_development_chronology": [dict(x) for x in WORLD5_DEVELOPMENT_CHRONOLOGY],
        "console_opcode_expansion": [dict(x) for x in CONSOLE_OPCODE_EXPANSION],
        "evidence_policy": {
            "high": "both sides have instruction-level or executable-backed structural evidence",
            "high-structural": "behavior/data structure matches strongly but exact console symbol/address attribution is incomplete",
            "continuity_reconstruction": "dev20 re-supplied raw Xbox/PS3 Ghidra exports recover the six exact constructor fingerprints and direct boss-mover addresses; dev19 historical files remain unchanged as the prior checkpoint",
            "raw_mover_similarity": "mnemonic ratios are fingerprints, not semantic equivalence; June->retail GIGANTIC_UFO/UNKNOWN raw deltas normalize to relocated global-address materialization only",
            "no_binary_distribution": True,
        },
    }
