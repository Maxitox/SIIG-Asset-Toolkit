#!/usr/bin/env python3
"""Desktop control center for the SIIG Asset Toolkit.

The GUI intentionally wraps the existing audited CLI instead of duplicating format logic.
It uses only the Python standard library (Tkinter) and launches toolkit commands in a
background thread so long extraction/build operations do not freeze the window.
"""
from __future__ import annotations

import json
import os
import queue
import shutil
import shlex
import subprocess
import sys
import threading
import webbrowser
from pathlib import Path
from typing import Callable, Optional

ROOT = Path(__file__).resolve().parent
TOOLKIT = ROOT / "siig_toolkit.py"
VERSION_FILE = ROOT / "VERSION.txt"
GUI_VERSION = "0.57.0-dev25"


def toolkit_version() -> str:
    try:
        return VERSION_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        return "unknown"


def diagnostics() -> dict:
    try:
        import tkinter as tk  # noqa: F401
        tkinter_ok = True
    except Exception:
        tkinter_ok = False
    return {
        "gui_version": GUI_VERSION,
        "toolkit_version": toolkit_version(),
        "toolkit_exists": TOOLKIT.is_file(),
        "tkinter_available": tkinter_ok,
        "python": sys.version.split()[0],
        "tabs": ["Game Rip", "Mod Workspace", "GMX Workbench", "Utilities"],
        "principle": "GUI wraps the existing CLI; format logic stays in audited toolkit code",
        "gmx_scene_graph_report": True,
        "gmx_scene_graph_sync": True,
        "gmx_texture_graph_sync": True,
        "gmx_animation_graph_sync": True,
        "mod_gltf_texture_pipeline": True,
        "native_tex_layout_synthesis": True,
        "atlas_safe_workspace": True,
        "atlas_guide_rebuild_guard": True,
        "atlas_duplicate_slots_independent": True,
        "gmx_multibone_animation_sync": True,
        "gltf_cubicspline_animation_import": True,
        "gmx_template_free_compile": True,
        "gmx_canonical_root_synthesis": True,
        "gmx_rigid_skin_import": True,
        "gmx_blended_skin_rejection": True,
        "gmx_rigid_inverse_bind_rebake": True,
        "gmx_rigid_partitioning": True,
        "gmx_multi_file_assembly": True,
        "all_boss_matrix": True,
        "boss_families": 18,
        "boss_canonical_catalogs": 18,
        "boss_deep_runtime_reconstruction_families": 14,
        "boss_gameplay_pose_reconstruction_families": 3,
        "boss_native_inspection_only_families": 1,
        "progressive_ufo_one_click_assembly": True,
        "progressive_ufo_formation_assemblies": 2,
        "progressive_ufo_classic_assembly": True,
        "crab_one_click_assembly": True,
        "hornet_one_click_assembly": True,
        "hornet_exposed_core_assembly": False,
        "hornet_prism_spread_attack_assembly": True,
        "mandala_one_click_assembly": True,
        "ladybug_one_click_assembly": True,
        "ladybug_deployed_leg_assembly": True,
        "butterfly_one_click_assembly": True,
        "butterfly_phase_assemblies": 4,
        "unknown_internal_form_export": True,
        "unknown_internal_forms": 14,
        "unknown_unique_visual_forms": 13,
        "unknown_visual_duplicate": "uk08=uk01",
        "unknown_runtime_cycle_reference": True,
        "unknown_all_forms_export": True,
        "unknown_flicker_preview": True,
        "vertebrate_one_click_assembly": True,
        "vertebrate_phase_assemblies": 2,
        "centipede_one_click_assembly": True,
        "centipede_initial_ring_assembly": True,
        "gigantic_ufo_one_click_assembly": True,
        "gigantic_ufo_complete_assembly": True,
        "squid_one_click_assembly": True,
        "squid_phase_assemblies": 1,
        "squid_body_only_is_standalone_bos_016": True,
        "squid_locator_leg_assembly": True,
        "axon_one_click_assembly": True,
        "axon_form_assemblies": 2,
        "axon_exact_two_ring_assembly": True,
        "the_sun_one_click_assembly": True,
        "the_sun_form_assemblies": 4,
        "the_sun_opening_synchronized_snapshot": True,
        "the_sun_protection_barrier_segments": 48,
        "ultimate_ufo_one_click_assembly": True,
        "ultimate_ufo_complete_assembly": True,
        "ultimate_ufo_phase_assemblies": 8,
        "ultimate_ufo_fan_ring_rotation_action": True,
        "hornet_prism_wall_variants": 13,
        "hornet_propagation_seed_wave_family": True,
        "hornet_propagation_seeds": 13,
        "gui_modes": ["simple", "advanced"],
        "default_gui_mode": "simple",
        "mod_simple_list_assets": True,
        "mod_asset_tree_browser": True,
        "mod_audio_preview_extraction": True,
        "mod_audio_editing": True,
        "mod_audio_xbox_pcm16_rebuild": True,
        "mod_audio_ps3_sblk_rebuild": True,
        "mod_audio_xbox_variable_duration_rate_channels": True,
        "mod_audio_ps3_variable_duration_rate_repack": True,
        "mod_audio_ps3_multichannel_input_downmix": True,
        "mod_localization_canonical_edit_only": True,
        "mod_asset_persistent_status_marks": True,
        "mod_asset_statuses": ["untouched", "exported", "edited", "staged", "added"],
        "mod_asset_double_click_edit": True,
        "mod_xbox_package_replacements": True,
        "mod_xbox_package_replacement_folder": "build/xbox360_replacements",
        "mod_package_editor_agnostic": True,
        "mod_siigmod_optional_share_format": True,
        "mod_pack_success_path_feedback": True,
        "mod_task_failure_popup": True,
        "hover_context_help": True,
        "utilities_in_tab_help_box": True,
        "utilities_context_help_direct": True,
        "utilities_fixed_help_geometry": True,
        "global_fixed_help_geometry": True,
        "gmx_mode_scroll_reset": True,
        "mod_text_tsv_primary": True,
        "utilities_doctor_plain_name": "Diagnose toolkit / input",
        "game_rip_drag_drop": True,
        "game_rip_drag_drop_backend": "stdlib Windows WM_DROPFILES",
        "game_rip_drag_drop_accepts_files_and_folders": True,
        "game_rip_drop_starts_automatically": False,
        "game_rip_browse_fallback": True,
        "game_rip_live_progress": True,
        "game_rip_progress_widget": True,
        "game_rip_structured_progress": True,
        "game_rip_bounded_log_polling": True,
        "game_rip_dedicated_console": True,
        "game_rip_console_vertical_scroll": True,
        "game_rip_console_horizontal_scroll": True,
        "game_rip_builtin_post_verify": True,
        "game_rip_auto_open_viewer": True,
        "rip_update_tool": True,
        "rip_update_requires_original_game": False,
        "rip_update_profile_fingerprint": True,
        "rip_update_recovery_journal": True,
        "rip_update_incremental_manifest": True,
        "rip_update_stat_cache": True,
        "rip_update_scoped_overwrite_guard": True,
        "gui_persistent_local_preferences": True,
        "gui_preferences_excluded_from_rip_outputs": True,
        "game_outer_cache_visible_controls": True,
        "game_outer_cache_clear_confirmation": True,
        "game_outer_cache_size_status": True,
        "game_rip_compact_layout": True,
        "game_rip_console_protected_space": True,
        "game_rip_console_min_pixels": 150,
        "gmx_workbench_compact_layout": True,
        "global_help_always_visible": True,
        "global_help_above_notebook": True,
        "global_task_log_separate_window": True,
        "global_task_log_does_not_reduce_tab_height": True,
        "gmx_simple_assembly_tabs": True,
        "gmx_simple_conditional_centipede_options": True,
        "gmx_visual_pass_modes": ["separate", "solid", "outline", "combined"],
        "gmx_visual_pass_default": "separate",
        "gmx_visual_pass_native_face_bone": "_F",
        "gmx_visual_pass_native_edge_bone": "_E",
        "boss_compact_assembler": True,
        "gmx_workbench_scrollable": True,
        "gmx_workbench_mousewheel_scroll": True,
        "boss_model_folder_reuse": True,
        "boss_output_folder_reuse": True,
        "boss_simple_family_selector": True,
        "boss_simple_family_count": 18,
        "boss_nameless_internal_no_name": True,
        "entity_compact_assembler": True,
        "entity_assembly_families": 8,
        "entity_assembly_names": ["ENVY", "GREED", "WRATH", "KEEPER", "OPPRESSOR", "GLUTTONY", "VANITY", "TELEPORTER"],
        "entity_requested_core_families": 6,
        "entity_requested_core_names": ["ENVY", "KEEPER", "OPPRESSOR", "GLUTTONY", "VANITY", "TELEPORTER"],
        "entity_workbench_audit_dev24": True,
        "assembly_browser_preview": True,
        "advanced_assembly_folder_reuse": True,
        "envy_name_status": "user-identified / internal string not recovered",
        "envy_runtime_chain_reconstruction": True,
        "envy_runtime_factory_plus_one_verified": True,
        "keeper_locator_assembly": True,
        "oppressor_locator_assembly": True,
        "gluttony_locator_assembly": True,
        "vanity_dynamic_owned_set": True,
        "teleporter_dynamic_owned_set": True,
    }



def _select_single_drop_path(paths) -> tuple[Optional[str], Optional[str]]:
    """Normalize a shell drop and require exactly one source path."""
    unique: list[str] = []
    for raw in paths:
        value = os.path.normpath(str(raw).strip())
        if value and value not in unique:
            unique.append(value)
    if not unique:
        return None, "The drop did not contain a file or folder."
    if len(unique) != 1:
        return None, "Drop one game/package or extracted game folder at a time."
    return unique[0], None


class _WindowsFileDropTarget:
    """Small stdlib-only WM_DROPFILES bridge for Tk on Windows.

    Explorer sends WM_DROPFILES to the Tk toplevel.  Keeping this bridge here avoids
    adding tkinterdnd2/tkdnd binaries to the source-only toolkit release.
    """

    WM_DROPFILES = 0x0233
    GWL_WNDPROC = -4

    def __init__(self, root, callback: Callable[[tuple[str, ...], int, int], None]) -> None:
        if not sys.platform.startswith("win"):
            raise RuntimeError("Windows shell drag-and-drop is only available on Windows")
        import ctypes
        from ctypes import wintypes

        self._ctypes = ctypes
        self._wintypes = wintypes
        self.root = root
        self.callback = callback
        self.hwnd = int(root.winfo_id())
        self._active = False

        user32 = ctypes.windll.user32
        shell32 = ctypes.windll.shell32
        self.user32 = user32
        self.shell32 = shell32

        LRESULT = ctypes.c_ssize_t
        WNDPROC = ctypes.WINFUNCTYPE(LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
        self._WNDPROC = WNDPROC
        self._proc = WNDPROC(self._wndproc)

        if ctypes.sizeof(ctypes.c_void_p) == 8:
            self._get_wndproc = user32.GetWindowLongPtrW
            self._set_wndproc = user32.SetWindowLongPtrW
        else:
            self._get_wndproc = user32.GetWindowLongW
            self._set_wndproc = user32.SetWindowLongW
        self._get_wndproc.argtypes = [wintypes.HWND, ctypes.c_int]
        self._get_wndproc.restype = ctypes.c_void_p
        self._set_wndproc.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_void_p]
        self._set_wndproc.restype = ctypes.c_void_p
        user32.CallWindowProcW.argtypes = [ctypes.c_void_p, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
        user32.CallWindowProcW.restype = LRESULT
        shell32.DragAcceptFiles.argtypes = [wintypes.HWND, wintypes.BOOL]
        shell32.DragQueryFileW.argtypes = [wintypes.HANDLE, wintypes.UINT, wintypes.LPWSTR, wintypes.UINT]
        shell32.DragQueryFileW.restype = wintypes.UINT
        shell32.DragQueryPoint.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.POINT)]
        shell32.DragQueryPoint.restype = wintypes.BOOL
        shell32.DragFinish.argtypes = [wintypes.HANDLE]

        old = self._get_wndproc(self.hwnd, self.GWL_WNDPROC)
        if not old:
            raise OSError("Could not read the Tk window procedure")
        self._old_proc = ctypes.c_void_p(old)
        ctypes.set_last_error(0)
        result = self._set_wndproc(
            self.hwnd, self.GWL_WNDPROC, ctypes.cast(self._proc, ctypes.c_void_p)
        )
        if not result and ctypes.get_last_error():
            raise ctypes.WinError(ctypes.get_last_error())
        shell32.DragAcceptFiles(self.hwnd, True)
        self._active = True

    def _wndproc(self, hwnd, msg, wparam, lparam):
        if msg == self.WM_DROPFILES:
            try:
                count = int(self.shell32.DragQueryFileW(wparam, 0xFFFFFFFF, None, 0))
                paths: list[str] = []
                for index in range(count):
                    length = int(self.shell32.DragQueryFileW(wparam, index, None, 0))
                    buf = self._ctypes.create_unicode_buffer(length + 1)
                    self.shell32.DragQueryFileW(wparam, index, buf, length + 1)
                    paths.append(buf.value)
                point = self._wintypes.POINT()
                self.shell32.DragQueryPoint(wparam, self._ctypes.byref(point))
                payload = tuple(paths)
                x, y = int(point.x), int(point.y)
            except Exception:
                # A native window procedure must never let a Python exception escape.
                return 0
            finally:
                # The shell owns the HDROP handle until DragFinish.  Always release it,
                # even if querying one of the dropped paths fails unexpectedly.
                try:
                    self.shell32.DragFinish(wparam)
                except Exception:
                    pass
            try:
                self.root.after_idle(lambda: self.callback(payload, x, y))
            except Exception:
                pass
            return 0
        try:
            return self.user32.CallWindowProcW(self._old_proc, hwnd, msg, wparam, lparam)
        except Exception:
            # Defensive fallback: ctypes callbacks must not leak Python exceptions.
            return 0

    def close(self) -> None:
        if not self._active:
            return
        try:
            self.shell32.DragAcceptFiles(self.hwnd, False)
            self._set_wndproc(self.hwnd, self.GWL_WNDPROC, self._old_proc)
        except Exception:
            pass
        self._active = False


def _gui_settings_path() -> Path:
    """Return a per-user local settings path that is never written into rip outputs."""
    if sys.platform.startswith("win"):
        base = Path(os.environ.get("APPDATA") or (Path.home() / "AppData" / "Roaming"))
        return base / "SIIGAssetToolkit" / "gui_settings.json"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "SIIGAssetToolkit" / "gui_settings.json"
    base = Path(os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config"))
    return base / "siig-asset-toolkit" / "gui_settings.json"


def _read_gui_settings(path: Optional[Path] = None) -> dict:
    target = Path(path) if path is not None else _gui_settings_path()
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return {}
    return data if isinstance(data, dict) else {}


def _write_gui_settings(data: dict, path: Optional[Path] = None) -> None:
    target = Path(path) if path is not None else _gui_settings_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_name(target.name + ".tmp")
    temp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temp, target)



def _outer_cache_dir_for_output(output_root: Path) -> Path:
    """Return the persistent outer-container cache sidecar for one rip root."""
    output_root = Path(output_root).expanduser()
    return output_root.parent / f".{output_root.name}.siig_outer_cache"


def _tree_size_bytes_no_follow(root: Path) -> int:
    """Measure ordinary files below *root* without following symlinks."""
    root = Path(root)
    if root.is_symlink():
        return 0
    if root.is_file():
        try:
            return root.stat().st_size
        except OSError:
            return 0
    total = 0
    stack = [root]
    while stack:
        current = stack.pop()
        try:
            with os.scandir(current) as entries:
                for entry in entries:
                    try:
                        if entry.is_symlink():
                            continue
                        if entry.is_dir(follow_symlinks=False):
                            stack.append(Path(entry.path))
                        elif entry.is_file(follow_symlinks=False):
                            total += entry.stat(follow_symlinks=False).st_size
                    except OSError:
                        continue
        except OSError:
            continue
    return total


def _format_byte_size(size: int) -> str:
    value = float(max(0, int(size)))
    units = ("B", "KiB", "MiB", "GiB", "TiB")
    unit = units[0]
    for unit in units:
        if value < 1024.0 or unit == units[-1]:
            break
        value /= 1024.0
    if unit == "B":
        return f"{int(value)} {unit}"
    return f"{value:.1f} {unit}"

def _open_path(path: Path) -> None:
    try:
        if sys.platform.startswith("win"):
            os.startfile(str(path))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
    except Exception:
        if path.is_file() and path.suffix.lower() in {".html", ".htm"}:
            webbrowser.open(path.resolve().as_uri())


def main() -> int:
    if "--check" in sys.argv:
        print(json.dumps(diagnostics(), indent=2))
        return 0
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox, simpledialog, ttk
    except Exception as exc:
        print(f"Tkinter is unavailable: {exc}", file=sys.stderr)
        return 2

    class App(tk.Tk):
        def __init__(self) -> None:
            super().__init__()
            self.title(f"SIIG Asset Toolkit {toolkit_version()} — Desktop")
            self.geometry("1120x780")
            self.minsize(900, 650)
            self._queue: queue.Queue = queue.Queue()
            self._busy = False
            self._active_command = ""
            self._buttons: list[ttk.Button] = []
            self._status = tk.StringVar(value="Ready")
            self._settings = _read_gui_settings()
            self.advanced_mode = tk.BooleanVar(value=bool(self._settings.get("advanced_mode", False)))
            self._mode_label = tk.StringVar(value="Mode: Simple")
            self._help_default = "Hover over a box or button to see what it does. Simple mode hides specialist controls; Advanced mode shows everything."
            self._advanced_widgets: list[object] = []
            self._simple_widgets: list[object] = []
            self._drop_target = None
            self._viewer_servers: list[subprocess.Popen] = []
            self._build_ui()
            self._restore_preferences()
            self.game_output.trace_add("write", self._mark_outer_cache_status_stale)
            self.after(120, self._refresh_outer_cache_status)
            self._apply_mode()
            self.after_idle(self._restore_help)
            self._install_game_drop()
            self.protocol("WM_DELETE_WINDOW", self._on_close)
            self.after(80, self._poll_queue)

        def _on_close(self) -> None:
            self._save_preferences()
            target = self._drop_target
            self._drop_target = None
            if target is not None:
                target.close()
            for proc in self._viewer_servers:
                try:
                    proc.terminate()
                except Exception:
                    pass
            self._viewer_servers.clear()
            self.destroy()

        def _restore_preferences(self) -> None:
            values = self._settings if isinstance(self._settings, dict) else {}
            for name in ("game_input", "game_output", "game_visual_pass", "mod_rip", "mod_ws", "gmx_template", "gmx_output", "gmx_visual_pass", "boss_model_dir", "boss_output_dir"):
                var = getattr(self, name, None)
                value = values.get(name)
                if var is not None and isinstance(value, str) and value:
                    var.set(value)
            for name in ("game_resume", "game_open_viewer", "game_outer_cache", "gmx_flip"):
                var = getattr(self, name, None)
                if var is not None and name in values:
                    var.set(bool(values[name]))

        def _save_preferences(self) -> None:
            values = {"schema_version": 1, "advanced_mode": bool(self.advanced_mode.get())}
            for name in ("game_input", "game_output", "game_visual_pass", "mod_rip", "mod_ws", "gmx_template", "gmx_output", "gmx_visual_pass", "boss_model_dir", "boss_output_dir"):
                var = getattr(self, name, None)
                if var is not None:
                    values[name] = str(var.get())
            for name in ("game_resume", "game_open_viewer", "game_outer_cache", "gmx_flip"):
                var = getattr(self, name, None)
                if var is not None:
                    values[name] = bool(var.get())
            try:
                _write_gui_settings(values)
                self._settings = values
            except OSError:
                # Preferences are convenience-only; never block toolkit work.
                pass

        def _build_ui(self) -> None:
            outer = ttk.Frame(self, padding=10)
            outer.pack(fill="both", expand=True)
            header = ttk.Frame(outer)
            header.pack(fill="x", pady=(0, 8))
            ttk.Label(header, text="SIIG Asset Toolkit", font=("TkDefaultFont", 16, "bold")).pack(side="left")
            ttk.Label(header, text=f"  {toolkit_version()}  •  GUI {GUI_VERSION}").pack(side="left", padx=6)
            ttk.Label(header, textvariable=self._status).pack(side="right", padx=(10, 0))
            mode_switch = ttk.Checkbutton(header, text="Advanced mode", variable=self.advanced_mode, command=self._apply_mode)
            mode_switch.pack(side="right", padx=(10, 0))
            ttk.Label(header, textvariable=self._mode_label).pack(side="right")
            self._register_help(mode_switch, "Switch between the beginner-friendly Simple interface and the full Advanced interface. Advanced mode does not unlock hidden format features; it only shows the specialist controls.")

            note = ttk.Label(
                outer,
                text="Desktop control center. Simple mode is recommended if you are new to the toolkit; native parsing/building still uses the same audited CLI code underneath.",
                foreground="#555555",
            )
            note.pack(fill="x", pady=(0, 8))

            # Build the notebook before the global help strip so every tab can
            # register contextual help, but do not let auxiliary UI steal the
            # notebook's vertical working area. WIP193/WIP194 packed the expanding
            # notebook before the old bottom help/log panes, which left those panes
            # at ~1 px. The first WIP195 draft reserved both panes at the bottom,
            # fixing the help box but shrinking Game Rip enough to clip its protected
            # console. The final layout keeps a compact help strip *above* the
            # notebook and moves the task log to a separate on-demand window.
            self.tabs = ttk.Notebook(outer)
            self._tab_game(ttk.Frame(self.tabs, padding=12))
            self._tab_mod(ttk.Frame(self.tabs, padding=12))
            self._tab_gmx(ttk.Frame(self.tabs, padding=12))
            self._tab_util(ttk.Frame(self.tabs, padding=12))
            self.tabs.bind("<<NotebookTabChanged>>", lambda _event: self._restore_help())

            # Context help must never resize the notebook while the pointer moves.
            # WIP196 used a wrapped Label whose requested height changed with every
            # help string; Utilities in particular appeared to "shake" vertically.
            # Reserve a fixed two-line strip and clip/wrap inside that reservation.
            help_frame = ttk.LabelFrame(outer, text="What does this do?", padding=(6, 3), height=58)
            help_frame.pack(side="top", fill="x", expand=False, pady=(0, 6))
            help_frame.pack_propagate(False)
            self.help_text = tk.StringVar(value=self._help_default)
            self.help_box = ttk.Label(help_frame, textvariable=self.help_text, justify="left", anchor="nw", wraplength=1020)
            self.help_box.pack(fill="both", expand=True)
            help_frame.bind("<Configure>", lambda event: self.help_box.configure(wraplength=max(320, event.width - 22)), add="+")

            self.tabs.pack(side="top", fill="both", expand=True)

            # Task output is retained exactly as before, but lives in a separate
            # window so a long log can never flatten Game Rip / Mod Workspace.
            self._log_window = tk.Toplevel(self)
            self._log_window.title("SIIG Asset Toolkit — Task log / results")
            self._log_window.geometry("900x380")
            self._log_window.minsize(620, 260)
            self._log_window.withdraw()
            self._log_window.protocol("WM_DELETE_WINDOW", self._log_window.withdraw)
            log_frame = ttk.LabelFrame(self._log_window, text="Task log / results", padding=6)
            log_frame.pack(fill="both", expand=True, padx=8, pady=(8, 4))
            self.log = tk.Text(log_frame, height=12, wrap="word")
            scroll = ttk.Scrollbar(log_frame, orient="vertical", command=self.log.yview)
            self.log.configure(yscrollcommand=scroll.set)
            self.log.pack(side="left", fill="both", expand=True)
            scroll.pack(side="right", fill="y")
            log_toolbar = ttk.Frame(self._log_window)
            log_toolbar.pack(fill="x", padx=8, pady=(0, 8))
            clear = ttk.Button(log_toolbar, text="Clear log", command=lambda: self.log.delete("1.0", "end"))
            clear.pack(side="left")
            copy = ttk.Button(log_toolbar, text="Copy log", command=self._copy_log)
            copy.pack(side="left", padx=5)
            close = ttk.Button(log_toolbar, text="Hide", command=self._log_window.withdraw)
            close.pack(side="right")

            task_log_button = ttk.Button(header, text="Task log…", command=self._show_task_log)
            task_log_button.pack(side="right", padx=(6, 0))
            self._register_help(task_log_button, "Open the separate task log/results window. Keeping it separate prevents logs from reducing the working height of Game Rip and Mod Workspace.")
            self._register_help(clear, "Clear the task log. This does not delete or undo any files or toolkit work.")
            self._register_help(copy, "Copy the entire task log to the clipboard so you can save it or send it for troubleshooting.")
            self._register_help(close, "Hide the task log window. Logged text is retained until you clear it or close the toolkit.")

            self._set_help(self._help_default)

        def _register_help(self, widget, text: str) -> None:
            """Show contextual help for any interactive control without intrusive pop-ups."""
            widget.bind("<Enter>", lambda _event, target=widget, message=text: self._show_context_help(target, message), add="+")
            widget.bind("<FocusIn>", lambda _event, target=widget, message=text: self._show_context_help(target, message), add="+")
            widget.bind("<FocusOut>", lambda _event: self._restore_help(), add="+")
            widget.bind("<Leave>", lambda _event: self._restore_help(), add="+")

        def _show_context_help(self, widget, text: str) -> None:
            # Utilities owns a dedicated fixed-size help surface. Updating both it
            # and the global strip on every hover was redundant and amplified the
            # old content-driven layout jitter. Other tabs use the global strip.
            if hasattr(self, "util_tab") and hasattr(self, "util_help_box"):
                current = widget
                while current is not None:
                    if current is self.util_tab:
                        self._set_util_help(text)
                        return
                    current = getattr(current, "master", None)
            self._set_help(text)

        def _set_util_help(self, text: str) -> None:
            if not hasattr(self, "util_help_box"):
                return
            self.util_help_box.configure(state="normal")
            self.util_help_box.delete("1.0", "end")
            self.util_help_box.insert("1.0", text)
            self.util_help_box.configure(state="disabled")

        def _set_help(self, text: str) -> None:
            if hasattr(self, "help_text"):
                self.help_text.set(text)
                return
            # Compatibility fallback for older/local Text-based help surfaces.
            if not hasattr(self, "help_box"):
                return
            try:
                self.help_box.configure(state="normal")
                self.help_box.delete("1.0", "end")
                self.help_box.insert("1.0", text)
                self.help_box.configure(state="disabled")
            except Exception:
                pass

        def _show_task_log(self) -> None:
            if not hasattr(self, "_log_window"):
                return
            try:
                self._log_window.deiconify()
                self._log_window.lift()
                self._log_window.focus_force()
            except Exception:
                pass

        def _restore_help(self) -> None:
            if not hasattr(self, "tabs"):
                return
            try:
                tab_name = self.tabs.tab(self.tabs.select(), "text")
            except Exception:
                tab_name = ""
            defaults = {
                "Game Rip": "Game Rip extracts the game/package into a verified working copy and builds convenient converted previews. Hover over a control for details.",
                "Mod Workspace": "Simple mode: create a workspace, click List Assets, then use the tree below to export/open files for editing. Persistent marks distinguish untouched, exported, edited, staged and added assets before Build → Verify → Pack.",
                "GMX Workbench": "Simple mode: choose a GMX, export it for Blender, edit the glTF, then rebuild a new GMX. Advanced mode exposes low-level graph/schema/JSON controls.",
                "Utilities": getattr(self, "util_help_default", "Utilities contains diagnostics, self-tests, reference reports and generated offline viewers. Hover over a control for details."),
            }
            message = defaults.get(tab_name, self._help_default)
            self._set_help(message)
            if tab_name == "Utilities" and hasattr(self, "util_help_box"):
                self._set_util_help(message)

        def _mode_only(self, widget, *, advanced: bool = False, simple: bool = False) -> None:
            if advanced:
                self._advanced_widgets.append(widget)
            if simple:
                self._simple_widgets.append(widget)

        def _apply_mode(self) -> None:
            advanced = bool(self.advanced_mode.get())
            self._mode_label.set("Mode: Advanced" if advanced else "Mode: Simple")
            for widget in self._advanced_widgets:
                try:
                    widget.grid() if advanced else widget.grid_remove()
                except Exception:
                    pass
            for widget in self._simple_widgets:
                try:
                    widget.grid_remove() if advanced else widget.grid()
                except Exception:
                    pass
            if hasattr(self, "mod_mode_note"):
                self.mod_mode_note.set(
                    "Advanced mode shows direct resource keys, raw glTF/TEX import, optional .siigmod sharing tools, and package inspection."
                    if advanced else
                    "Simple mode: edit assets, Build replacement files, Verify, then open build/xbox360_replacements and replace the matching .bin.gz files in a COPY of the Xbox STFS with any compatible package editor. .siigmod is optional for sharing a delta with another toolkit user."
                )
            if hasattr(self, "gmx_mode_note"):
                self.gmx_mode_note.set(
                    "Advanced mode shows JSON editing, graph/schema synchronization, generic assembly and template-free construction controls."
                    if advanced else
                    "Simple mode: export/edit/rebuild GMX files, or use the compact tabbed assembler below."
                )
            # Geometry changes in Advanced mode alter the GMX canvas scrollregion.
            # Recompute after Tk has applied grid_remove/grid, and always return to
            # the top when entering Simple mode so a stale deep Advanced yview
            # cannot leave the compact page apparently blank or unscrollable.
            if hasattr(self, "gmx_canvas"):
                self.after_idle(lambda a=advanced: self._refresh_gmx_scroll_after_mode(a))
            self._restore_help()

        def _refresh_gmx_scroll_after_mode(self, advanced: bool) -> None:
            if not hasattr(self, "gmx_canvas"):
                return
            try:
                self.update_idletasks()
                bbox = self.gmx_canvas.bbox("all")
                if bbox:
                    self.gmx_canvas.configure(scrollregion=bbox)
                if not advanced:
                    self.gmx_canvas.yview_moveto(0.0)
            except Exception:
                pass

        def _entry_row(self, parent, row: int, label: str, var, kind: str = "file", save: bool = False, filetypes=None, help_text: str = "", advanced_only: bool = False, compact: bool = False) -> None:
            help_text = help_text or f"Set {label}. Use Browse if you do not want to type the path manually."
            row_pady = 2 if compact else 4
            label_widget = ttk.Label(parent, text=label)
            label_widget.grid(row=row, column=0, sticky="w", padx=(0, 8), pady=row_pady)
            entry = ttk.Entry(parent, textvariable=var)
            entry.grid(row=row, column=1, sticky="ew", pady=row_pady)
            def browse() -> None:
                initial = Path(var.get()).expanduser() if var.get() else Path.home()
                if kind == "dir":
                    value = filedialog.askdirectory(initialdir=str(initial if initial.is_dir() else initial.parent))
                elif save:
                    value = filedialog.asksaveasfilename(initialdir=str(initial.parent), initialfile=initial.name, filetypes=filetypes or [("All files", "*.*")])
                else:
                    value = filedialog.askopenfilename(initialdir=str(initial if initial.is_dir() else initial.parent), filetypes=filetypes or [("All files", "*.*")])
                if value:
                    var.set(value)
            browse_button = ttk.Button(parent, text="Browse…", command=browse)
            browse_button.grid(row=row, column=2, padx=(8, 0), pady=row_pady)
            parent.columnconfigure(1, weight=1)
            for widget in (label_widget, entry, browse_button):
                self._register_help(widget, help_text)
                if advanced_only:
                    self._mode_only(widget, advanced=True)

        def _action(self, parent, text: str, command: Callable[[], None], row: int, col: int = 0, span: int = 1, help_text: str = "", compact: bool = False) -> None:
            button = ttk.Button(parent, text=text, command=command)
            pad = 2 if compact else 4
            button.grid(row=row, column=col, columnspan=span, sticky="ew", padx=pad, pady=pad)
            self._buttons.append(button)
            self._register_help(button, help_text or f"Run {text}. The command and its results will appear in the task log below.")

        def _tab_game(self, tab) -> None:
            self.tabs.add(tab, text="Game Rip")
            self.game_tab = tab
            self.game_input = tk.StringVar()
            self.game_output = tk.StringVar(value=str(Path.cwd() / "SIIG_Ripped"))
            self.game_resume = tk.BooleanVar(value=True)
            self.game_open_viewer = tk.BooleanVar(value=True)
            self.game_outer_cache = tk.BooleanVar(value=True)
            self.game_outer_cache_status = tk.StringVar(value="Cache: checking…")
            self.game_visual_pass = tk.StringVar(value="Separate solid + outline (native/default)")
            self.game_drop_note = tk.StringVar(value="Drop a game/package or extracted game folder here, or use Browse…")
            tab.columnconfigure(1, weight=1)
            # The console is the information-dense part of this tab.  Protect a
            # useful minimum height so new options can never flatten it again.
            tab.rowconfigure(9, weight=1, minsize=150)

            ttk.Label(tab, text="Full-game extraction and verification", font=("TkDefaultFont", 12, "bold")).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 4))

            # Compact drop target: still a full Windows WM_DROPFILES target, but no
            # longer consumes the height of several ordinary controls.
            self.game_drop_zone = ttk.LabelFrame(tab, text="Drop game input", padding=(6, 3))
            self.game_drop_zone.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 4))
            drop_label = ttk.Label(self.game_drop_zone, textvariable=self.game_drop_note, anchor="center", justify="center", wraplength=980)
            drop_label.pack(fill="x", expand=True, ipady=2)
            drop_help = "Windows: drag one Xbox 360 STFS/XBLA package, PS3 package, supported archive, or extracted game folder from Explorer onto this strip. Dropping only selects the source; Rip + verify still starts the extraction."
            self._register_help(self.game_drop_zone, drop_help)
            self._register_help(drop_label, drop_help)

            self._entry_row(tab, 2, "Game/package", self.game_input, help_text="Choose the Xbox 360 STFS/game package, PS3 package/extracted game input, or another supported game source you want the toolkit to rip. On Windows you can also drag it into the strip above.", compact=True)
            self._entry_row(tab, 3, "Rip output", self.game_output, kind="dir", help_text="Choose where the extracted and converted game files should be written. The toolkit creates its organized rip structure here.", compact=True)

            options_row = ttk.Frame(tab)
            options_row.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(1, 3))
            options_row.columnconfigure(2, weight=1)
            resume = ttk.Checkbutton(options_row, text="Resume/reuse unchanged work", variable=self.game_resume)
            resume.grid(row=0, column=0, sticky="w", padx=(0, 16))
            self._register_help(resume, "Recommended. Reuses already completed extraction/conversion work when the source has not changed, which makes repeated runs much faster.")
            open_viewer = ttk.Checkbutton(options_row, text="Open Asset Viewer after verified rip", variable=self.game_open_viewer)
            open_viewer.grid(row=0, column=1, sticky="w")
            self._register_help(open_viewer, "Recommended for first-time use. A successful rip already builds the Asset Viewer; this opens it automatically after verification succeeds.")

            # One-row cache strip: visible and understandable without consuming the
            # console's space.  Destructive clearing remains separately confirmed.
            cache_frame = ttk.LabelFrame(tab, text="Source-package cache", padding=(6, 3))
            cache_frame.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(1, 4))
            cache_frame.columnconfigure(1, weight=1)
            keep_cache = ttk.Checkbutton(cache_frame, text="Keep for faster resume/update", variable=self.game_outer_cache)
            keep_cache.grid(row=0, column=0, sticky="w", padx=(0, 12))
            self._register_help(keep_cache, "Recommended when ripping from ZIP/STFS/PKG. Keeps the unpacked outer source beside the rip so later resume/update work can skip expensive package extraction. This cache contains no unique edits and can be deleted safely.")
            cache_status = ttk.Label(cache_frame, textvariable=self.game_outer_cache_status)
            cache_status.grid(row=0, column=1, sticky="w")
            self._register_help(cache_status, "Shows whether the sidecar source-package cache exists for the selected Rip output and its current disk usage.")
            refresh_cache = ttk.Button(cache_frame, text="Refresh", command=self._refresh_outer_cache_status)
            refresh_cache.grid(row=0, column=2, sticky="e", padx=(8, 0))
            self._register_help(refresh_cache, "Re-scan the sidecar source-package cache for the selected Rip output and refresh its size.")
            clear_cache = ttk.Button(cache_frame, text="Clear cache…", command=self._clear_outer_cache)
            clear_cache.grid(row=0, column=3, sticky="e", padx=(5, 0))
            self._buttons.append(clear_cache)
            self._register_help(clear_cache, "Delete the cached unpacked ZIP/STFS/PKG source after an explicit warning. This never deletes SIIG_Ripped or Mod Workspaces, but a later resume may need to unpack the original package again.")

            ttk.Label(tab, text="GMX visual pass").grid(row=6, column=0, sticky="w", padx=(0, 8), pady=2)
            game_pass_combo = ttk.Combobox(tab, textvariable=self.game_visual_pass, state="readonly", values=(
                "Separate solid + outline (native/default)", "Solid only", "Outline only", "Combined solid + outline animation"
            ))
            game_pass_combo.grid(row=6, column=1, columnspan=2, sticky="ew", pady=2)
            self._register_help(game_pass_combo, "Controls the glTF visual passes produced during a full rip. Separate is the native/default view; the other modes isolate or combine the _F solid and _E outline representations.")

            actions = ttk.Frame(tab)
            actions.grid(row=7, column=0, columnspan=3, sticky="ew", pady=(3, 4))
            for c in range(3):
                actions.columnconfigure(c, weight=1)
            self._action(actions, "Check input", self._doctor_game_input, 0, 0, help_text="Run the non-destructive preflight check on the selected package/folder before extracting it.", compact=True)
            self._action(actions, "Rip + verify", self._rip_game, 0, 1, help_text="Run the complete extraction/conversion workflow and then independently verify the resulting manifest, hashes, privacy metadata and partial-file state.", compact=True)
            self._action(actions, "Update existing rip", self._update_existing_rip, 0, 2, help_text="Fast incremental migration of a completed rip without the original STFS/PKG/game folder. It reuses retained sources and only rebuilds stale components.", compact=True)
            self._action(actions, "Verify existing rip", lambda: self._run(["verify-output", self.game_output.get()]), 1, 0, help_text="Independently check an already completed rip for missing, changed or invalid outputs. This does not modify the rip.", compact=True)
            self._action(actions, "Open Asset Viewer", self._open_or_build_viewer, 1, 1, help_text="Open the viewer already generated by the rip, or build it if this older rip does not have one yet.", compact=True)
            self._action(actions, "Open rip folder", lambda: _open_path(Path(self.game_output.get())), 1, 2, help_text="Open the selected rip-output directory in your normal file manager.", compact=True)

            progress_frame = ttk.LabelFrame(tab, text="Live rip progress", padding=(6, 3))
            progress_frame.grid(row=8, column=0, columnspan=3, sticky="ew", pady=(1, 4))
            progress_frame.columnconfigure(0, weight=1)
            self.game_progress_phase = tk.StringVar(value="Phase: ready")
            self.game_progress = tk.StringVar(value="Ready to rip.")
            self.game_progress_counts = tk.StringVar(value="Assets 0 · glTF 0 · PNG 0 · errors 0")
            ttk.Label(progress_frame, textvariable=self.game_progress_phase, font=("TkDefaultFont", 9, "bold")).grid(row=0, column=0, sticky="w")
            ttk.Label(progress_frame, textvariable=self.game_progress_counts).grid(row=0, column=1, sticky="e", padx=(12, 0))
            ttk.Label(progress_frame, textvariable=self.game_progress, wraplength=900).grid(row=1, column=0, columnspan=2, sticky="w", pady=(1, 0))
            self.game_progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate")
            self.game_progress_bar.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(3, 0))
            self._register_help(progress_frame, "Shows the current rip phase and running extracted/converted/error counts. The rip console directly below preserves the complete per-file stream instead of replacing the previous line.")

            console_frame = ttk.LabelFrame(tab, text="Rip/update console · complete per-file log", padding=(6, 3))
            console_frame.grid(row=9, column=0, columnspan=3, sticky="nsew", pady=(1, 0))
            console_frame.rowconfigure(0, weight=1, minsize=110)
            console_frame.columnconfigure(0, weight=1)
            self.game_rip_console = tk.Text(console_frame, height=8, wrap="none", font="TkFixedFont")
            rip_vscroll = ttk.Scrollbar(console_frame, orient="vertical", command=self.game_rip_console.yview)
            rip_hscroll = ttk.Scrollbar(console_frame, orient="horizontal", command=self.game_rip_console.xview)
            self.game_rip_console.configure(yscrollcommand=rip_vscroll.set, xscrollcommand=rip_hscroll.set)
            self.game_rip_console.grid(row=0, column=0, sticky="nsew")
            rip_vscroll.grid(row=0, column=1, sticky="ns")
            rip_hscroll.grid(row=1, column=0, sticky="ew")
            rip_tools = ttk.Frame(console_frame)
            rip_tools.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(3, 0))
            clear_console = ttk.Button(rip_tools, text="Clear", command=lambda: self.game_rip_console.delete("1.0", "end"))
            clear_console.pack(side="left")
            copy_console = ttk.Button(rip_tools, text="Copy", command=self._copy_rip_console)
            copy_console.pack(side="left", padx=(5, 0))
            self._register_help(clear_console, "Clear only the visible rip/update console. No files or rip work are deleted.")
            self._register_help(copy_console, "Copy the complete rip/update console to the clipboard for troubleshooting or archival.")
            self._register_help(console_frame, "Console-style rip/update stream. Every line emitted by rip-game or update-rip is appended here. The compact layout reserves a minimum readable console height so option panels cannot flatten it.")

        def _install_game_drop(self) -> None:
            if not hasattr(self, "game_drop_note"):
                return
            if not sys.platform.startswith("win"):
                self.game_drop_note.set("Drag-and-drop game selection is available on Windows. On this platform, use Browse… below.")
                return
            try:
                self.update_idletasks()
                self._drop_target = _WindowsFileDropTarget(self, self._on_windows_file_drop)
                self.game_drop_note.set("Drop one game/package or extracted game folder here. Then click Rip game.")
            except Exception as exc:
                self.game_drop_note.set(f"Drag-and-drop could not be enabled ({exc}). Use Browse… below.")

        def _drop_hits_game_zone(self, x: int, y: int) -> bool:
            try:
                zone = self.game_drop_zone
                left = zone.winfo_rootx() - self.winfo_rootx()
                top = zone.winfo_rooty() - self.winfo_rooty()
                return left <= x < left + zone.winfo_width() and top <= y < top + zone.winfo_height()
            except Exception:
                return False

        def _on_windows_file_drop(self, paths: tuple[str, ...], x: int, y: int) -> None:
            if not self._drop_hits_game_zone(x, y):
                self._status.set("Drop ignored — use the Game Rip drop box")
                return
            selected, error = _select_single_drop_path(paths)
            if error:
                messagebox.showinfo("Game input drop", error)
                return
            assert selected is not None
            self.game_input.set(selected)
            name = Path(selected).name or selected
            self.game_drop_note.set(f"Selected: {name}\nClick Rip game to start, or drop another source to replace it.")
            self._status.set("Game input selected")
            self.tabs.select(self.game_tab)
            self._append(f"\n[drag/drop] Selected game input: {selected}\n")

        def _tab_mod(self, tab) -> None:
            self.tabs.add(tab, text="Mod Workspace")
            self.mod_rip = tk.StringVar()
            self.mod_ws = tk.StringVar(value=str(Path.cwd() / "SIIG_Mod_Workspace"))
            self.mod_archive = tk.StringVar()
            self.mod_resource = tk.StringVar()
            self.mod_gltf = tk.StringVar()
            self.mod_mode_note = tk.StringVar()
            self.mod_asset_summary = tk.StringVar(value="Click List Assets after creating or choosing a workspace.")
            self._mod_tree_items = {}
            self._mod_browser_loaded = False
            self._mod_pending_open = None
            ttk.Label(tab, text="Mod Workspace", font=("TkDefaultFont", 12, "bold")).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 4))
            ttk.Label(tab, textvariable=self.mod_mode_note, wraplength=900).grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 8))
            self._entry_row(tab, 2, "Verified game rip", self.mod_rip, kind="dir", help_text="Choose the verified rip you made in Game Rip. Mod Workspace uses this as the clean source when building or applying changes.")
            self._entry_row(tab, 3, "Mod workspace folder", self.mod_ws, kind="dir", help_text="Choose the folder where your editable mod project will live. Create Workspace will prepare it for you.")

            # Direct GMX-resource plumbing remains available in Advanced mode, but the
            # Simple tree browser can now select/export ordinary resources itself.
            self._entry_row(tab, 4, "GMX archive key", self.mod_archive, help_text="Advanced: internal BBX/archive key that identifies which container owns the GMX resource you want to replace.", advanced_only=True)
            self._entry_row(tab, 5, "GMX resource", self.mod_resource, help_text="Advanced: exact GMX resource name/path inside the selected archive key.", advanced_only=True)
            self._entry_row(tab, 6, "Edited glTF", self.mod_gltf, filetypes=[("glTF 2.0", "*.gltf"), ("All files", "*.*")], help_text="Advanced: an edited glTF that should be compiled and imported directly into the selected GMX resource, including compatible texture changes.", advanced_only=True)

            simple_actions = ttk.LabelFrame(tab, text="Beginner workflow", padding=6)
            simple_actions.grid(row=7, column=0, columnspan=3, sticky="ew", pady=8)
            self._mode_only(simple_actions, simple=True)
            for c in range(4): simple_actions.columnconfigure(c, weight=1)
            self._action(simple_actions, "1. Create workspace", self._mod_create_workspace, 0, 0, help_text="Create a new editable mod workspace from the verified game rip. Do this once when starting a mod project.")
            self._action(simple_actions, "2. List Assets", self._mod_list_assets, 0, 1, help_text="Open the simple asset tree below. Select or double-click a resource to export/open its editable representation. Persistent status marks show what changed.")
            self._action(simple_actions, "3. Build replacement files", self._mod_build_changes, 0, 2, help_text="Compile Edited/Staged/Added assets and create complete Xbox replacement containers under build/xbox360_replacements at their original STFS paths.")
            self._action(simple_actions, "4. Verify build", self._mod_verify_build, 0, 3, help_text="Verify rebuilt BBX archives plus generated Xbox package replacement payloads before deployment.")
            self._action(simple_actions, "5. Open Xbox replacements", self._mod_open_replacements, 1, 0, 2, help_text="Open build/xbox360_replacements. These complete .bin.gz/.gz containers are ready to replace at the matching paths inside a COPY of the STFS package using any compatible package editor (for example Velocity, Horizon or Le Fluffie).")
            self._action(simple_actions, "Open workspace", lambda: _open_path(Path(self.mod_ws.get())), 1, 2, help_text="Open the workspace folder in your file manager.")
            self._action(simple_actions, "Share .siigmod… (optional)", self._pack_mod, 1, 3, help_text="Optional sharing format: save only the mod delta for another SIIG Asset Toolkit user with the same clean rip. This is not the file you inject into an Xbox package.")

            advanced_actions = ttk.LabelFrame(tab, text="Advanced workspace tools", padding=6)
            advanced_actions.grid(row=7, column=0, columnspan=3, sticky="ew", pady=8)
            self._mode_only(advanced_actions, advanced=True)
            for c in range(4): advanced_actions.columnconfigure(c, weight=1)
            self._action(advanced_actions, "Initialize", self._mod_create_workspace, 0, 0, help_text="Initialize a mod workspace from the selected verified rip.")
            self._action(advanced_actions, "List Assets", self._mod_list_assets, 0, 1, help_text="Open or refresh the same archive/resource tree used by Simple mode, including persistent edit-state marks.")
            self._action(advanced_actions, "Build replacement files", self._mod_build_changes, 0, 2, help_text="Build pending workspace changes and emit complete replacement containers, including build/xbox360_replacements for Xbox 360 package deployment.")
            self._action(advanced_actions, "Verify build", self._mod_verify_build, 0, 3, help_text="Run structural verification on the rebuilt BBX and deployment-ready replacement files.")
            self._action(advanced_actions, "Open replacements", self._mod_open_replacements, 1, 0, help_text="Open build/xbox360_replacements when Xbox deployment-ready files exist.")
            self._action(advanced_actions, "Share .siigmod…", self._pack_mod, 1, 1, help_text="Optional baseline-dependent delta package for sharing with another toolkit user; not an STFS replacement file.")
            self._action(advanced_actions, "Inspect .siigmod…", self._inspect_mod, 1, 2, help_text="Read and validate a .siigmod package without applying it.")
            self._action(advanced_actions, "Apply .siigmod…", self._apply_mod, 1, 3, help_text="Apply a shared .siigmod delta to the selected verified source rip and build it into this workspace.")
            self._action(advanced_actions, "Open workspace", lambda: _open_path(Path(self.mod_ws.get())), 2, 0, help_text="Open the current mod workspace folder in your file manager.")
            self._action(advanced_actions, "Import glTF + TEX", self._mod_import_gltf, 2, 1, 2, help_text="Advanced: compile the selected edited glTF into the specified GMX resource and synchronize compatible texture replacements through the workspace pipeline.")

            browser = ttk.LabelFrame(tab, text="Workspace assets", padding=6)
            browser.grid(row=8, column=0, columnspan=3, sticky="nsew", pady=(2, 8))
            browser.columnconfigure(0, weight=1)
            browser.rowconfigure(1, weight=1)
            self.mod_asset_browser = browser
            summary_bar = ttk.Frame(browser)
            summary_bar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5))
            summary_bar.columnconfigure(0, weight=1)
            ttk.Label(summary_bar, textvariable=self.mod_asset_summary).grid(row=0, column=0, sticky="w")
            ttk.Button(summary_bar, text="Open selected", command=self._mod_open_edit_selected).grid(row=0, column=1, padx=(6, 0))
            ttk.Button(summary_bar, text="Refresh marks", command=self._mod_list_assets).grid(row=0, column=2, padx=(6, 0))
            tree = ttk.Treeview(browser, columns=("status", "kind", "size"), show="tree headings", height=12, selectmode="browse")
            tree.heading("#0", text="Archive / asset")
            tree.heading("status", text="Status")
            tree.heading("kind", text="Type")
            tree.heading("size", text="Size")
            tree.column("#0", width=470, minwidth=220, stretch=True)
            tree.column("status", width=105, minwidth=90, stretch=False)
            tree.column("kind", width=95, minwidth=75, stretch=False)
            tree.column("size", width=90, minwidth=70, stretch=False, anchor="e")
            vscroll = ttk.Scrollbar(browser, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=vscroll.set)
            tree.grid(row=1, column=0, sticky="nsew")
            vscroll.grid(row=1, column=1, sticky="ns")
            tree.tag_configure("edited", font=("TkDefaultFont", 9, "bold"))
            tree.tag_configure("staged", font=("TkDefaultFont", 9, "bold"))
            tree.tag_configure("added", font=("TkDefaultFont", 9, "bold"))
            tree.tag_configure("archive_override", font=("TkDefaultFont", 9, "bold"))
            tree.bind("<Double-1>", lambda _event: self._mod_open_edit_selected(), add="+")
            tree.bind("<<TreeviewSelect>>", lambda _event: self._mod_tree_selection_changed(), add="+")
            self.mod_asset_tree = tree
            self._register_help(tree, "Archives are top-level branches. Resource rows keep persistent status marks: Untouched, Exported, Edited, Staged or Added. Double-click a resource to export/open it for editing; use Refresh marks after saving in another application.")
            browser.grid_remove()

            ttk.Label(tab, text="The asset tree is the recommended Simple-mode entry point. The safe rigid-mesh path partitions disjoint single-joint islands automatically; cross-joint triangles and true blended skinning remain rejected because SIIG's native per-vertex weight format has not been proven.", wraplength=900).grid(row=9, column=0, columnspan=3, sticky="w", pady=4)
            tab.rowconfigure(8, weight=1)
            tab.columnconfigure(1, weight=1)

        def _tab_gmx(self, tab) -> None:
            # The workbench remains vertically scrollable, but Simple mode is now
            # intentionally compact: one-row core workflow plus tabbed assemblers.
            self.tabs.add(tab, text="GMX Workbench")
            tab.rowconfigure(0, weight=1)
            tab.columnconfigure(0, weight=1)
            gmx_canvas = tk.Canvas(tab, highlightthickness=0, borderwidth=0)
            self.gmx_canvas = gmx_canvas
            gmx_scroll = ttk.Scrollbar(tab, orient="vertical", command=gmx_canvas.yview)
            gmx_canvas.configure(yscrollcommand=gmx_scroll.set)
            gmx_canvas.grid(row=0, column=0, sticky="nsew")
            gmx_scroll.grid(row=0, column=1, sticky="ns")
            gmx_body = ttk.Frame(gmx_canvas)
            gmx_window = gmx_canvas.create_window((0, 0), window=gmx_body, anchor="nw")
            gmx_body.bind("<Configure>", lambda _event: gmx_canvas.configure(scrollregion=gmx_canvas.bbox("all")), add="+")
            gmx_canvas.bind("<Configure>", lambda event: gmx_canvas.itemconfigure(gmx_window, width=event.width), add="+")

            def _gmx_mousewheel(event) -> None:
                delta = getattr(event, "delta", 0)
                if delta:
                    step = -1 if delta > 0 else 1
                    if abs(delta) >= 120:
                        step = -int(delta / 120)
                    gmx_canvas.yview_scroll(step, "units")
                elif getattr(event, "num", None) == 4:
                    gmx_canvas.yview_scroll(-1, "units")
                elif getattr(event, "num", None) == 5:
                    gmx_canvas.yview_scroll(1, "units")

            for widget in (gmx_canvas, gmx_body):
                widget.bind("<MouseWheel>", _gmx_mousewheel, add="+")
                widget.bind("<Button-4>", _gmx_mousewheel, add="+")
                widget.bind("<Button-5>", _gmx_mousewheel, add="+")
            self._register_help(gmx_scroll, "Scroll through the full GMX Workbench. Mouse-wheel scrolling also works while the pointer is over the workbench background.")
            tab = gmx_body
            tab.columnconfigure(1, weight=1)

            self.gmx_template = tk.StringVar()
            self.gmx_gltf = tk.StringVar()
            self.gmx_output = tk.StringVar()
            self.gmx_json = tk.StringVar()
            self.gmx_flip = tk.BooleanVar(value=False)
            self.gmx_sync_graph = tk.BooleanVar(value=False)
            self.gmx_sync_scene = tk.BooleanVar(value=False)
            self.gmx_sync_texture = tk.BooleanVar(value=False)
            self.gmx_synthesize_schemas = tk.BooleanVar(value=False)
            self.gmx_sync_animation = tk.BooleanVar(value=False)
            self.gmx_sync_rigid_skins = tk.BooleanVar(value=False)
            self.gmx_mode_note = tk.StringVar()
            self.progressive_ufo_formation = tk.StringVar(value="Original — first runtime formation")
            self.ultimate_ufo_state = tk.StringVar(value="COMPLETE — 126 allocated hierarchy")
            self.butterfly_phase = tk.StringVar(value="1 — phase 1 / body only")
            self.unknown_form = tk.StringVar(value="01 — uk01")
            self.vertebrate_phase = tk.StringVar(value="1 — phase 1 / rotating immense tower")
            self.squid_phase = tk.StringVar(value="1 — phase 1 / eight legs")
            self.axon_form = tk.StringVar(value="Expanded — core + 16 petals")
            self.the_sun_form = tk.StringVar(value="Opening state 0 — body frame 0 + 48 barriers")
            self.hornet_prism_slot = tk.StringVar(value="22")
            self.hornet_propagation_seed = tk.StringVar(value="22")
            self.hornet_propagation_wave = tk.StringVar(value="3")
            self.ultimate_ufo_core = tk.StringVar(value="Authored by selected state")
            self.boss_model_dir = tk.StringVar()
            self.boss_output_dir = tk.StringVar(value=str(Path.cwd() / "siig_boss_assemblies"))
            self.boss_family = tk.StringVar(value="THE MOON")
            self.boss_variant = tk.StringVar()
            self.centipede_bos007_segments = tk.StringVar()
            self.centipede_bos007a_segments = tk.StringVar()
            self.entity_family = tk.StringVar(value="ENVY")
            self.entity_variant = tk.StringVar()
            self.gmx_visual_pass = tk.StringVar(value="Separate solid + outline (native/default)")

            ttk.Label(tab, text="GMX Workbench", font=("TkDefaultFont", 12, "bold")).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 2))
            ttk.Label(tab, textvariable=self.gmx_mode_note, wraplength=1000).grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 4))
            self._entry_row(tab, 2, "Original/native GMX", self.gmx_template, filetypes=[("SIIG GMX", "*.gmx"), ("All files", "*.*")], help_text="Choose the original GMX model. Export for Blender converts this file; Rebuild GMX uses it as the structural template unless you use the advanced template-free creator.", compact=True)
            self._entry_row(tab, 3, "Edited glTF", self.gmx_gltf, filetypes=[("glTF 2.0", "*.gltf"), ("All files", "*.*")], help_text="Choose the glTF you edited in Blender or another glTF editor. Export for Blender fills this automatically with the newly exported glTF path.", compact=True)
            self._entry_row(tab, 4, "Output GMX", self.gmx_output, save=True, filetypes=[("SIIG GMX", "*.gmx")], help_text="Advanced: choose the exact output filename. If left blank, Rebuild GMX automatically writes <original>.edited.gmx beside the source model.", advanced_only=True, compact=True)
            self._entry_row(tab, 5, "Editable GMX JSON", self.gmx_json, save=True, filetypes=[("JSON", "*.json")], help_text="Advanced: path for the low-level editable GMX JSON representation used by Export editable JSON / Build JSON → GMX.", advanced_only=True, compact=True)

            ttk.Label(tab, text="Visual pass").grid(row=6, column=0, sticky="w", padx=(0, 8), pady=2)
            pass_combo = ttk.Combobox(tab, textvariable=self.gmx_visual_pass, state="readonly", values=(
                "Separate solid + outline (native/default)",
                "Solid only",
                "Outline only",
                "Combined solid + outline animation",
            ))
            pass_combo.grid(row=6, column=1, columnspan=2, sticky="ew", pady=2)
            self._register_help(pass_combo, "Choose how native _F face/solid and _E edge/outline passes are exported. Separate preserves native passes/tracks; Solid or Outline isolates one pass; Combined keeps both visuals in one animation export.")

            advanced_options = ttk.LabelFrame(tab, text="Advanced import options", padding=4)
            advanced_options.grid(row=7, column=0, columnspan=3, sticky="ew", pady=4)
            self._mode_only(advanced_options, advanced=True)
            options = [
                ("Flip UV V on glTF import/export", self.gmx_flip, "Flip the V texture coordinate during glTF conversion. Leave this off unless your workflow specifically requires it."),
                ("Sync native MESH/ARRY graph", self.gmx_sync_graph, "Rebuild the native mesh/index graph from the glTF rather than preserving the donor graph."),
                ("Sync BONE/PARE + material/shader scene graph", self.gmx_sync_scene, "Rebuild decoded bone/parent/material/shader relationships from glTF."),
                ("Sync TXIF texture bindings", self.gmx_sync_texture, "Rebuild native texture binding records from the glTF material/texture graph."),
                ("Synthesize native vertex/material schemas", self.gmx_synthesize_schemas, "Allow donor-free synthesis of decoded standard native vertex/material schemas."),
                ("Sync MOTN/ANIM animation graph", self.gmx_sync_animation, "Rebuild native 30 Hz MOTN/ANIM tracks from supported glTF animation channels."),
                ("Import rigid glTF skins + inverse-bind rebake", self.gmx_sync_rigid_skins, "Import single-joint rigid glTF skinning and rebake inverse-bind transforms. True blended weights remain unsupported."),
            ]
            # Two columns halve the Advanced-mode vertical footprint without hiding options.
            for index, (text, var, help_text) in enumerate(options):
                row, col = divmod(index, 2)
                cb = ttk.Checkbutton(advanced_options, text=text, variable=var)
                cb.grid(row=row, column=col, sticky="w", padx=(0, 14), pady=1)
                self._register_help(cb, help_text)
            advanced_options.columnconfigure(0, weight=1)
            advanced_options.columnconfigure(1, weight=1)

            simple_actions = ttk.LabelFrame(tab, text="Simple workflow", padding=4)
            simple_actions.grid(row=8, column=0, columnspan=3, sticky="ew", pady=4)
            self._mode_only(simple_actions, simple=True)
            for c in range(4):
                simple_actions.columnconfigure(c, weight=1)
            self._action(simple_actions, "1. Export for Blender", self._export_gltf, 0, 0, help_text="Convert the selected original GMX into a glTF you can open in Blender. After export, the Edited glTF box is filled automatically.", compact=True)
            self._action(simple_actions, "2. Rebuild GMX", self._import_gltf, 0, 1, help_text="Compile the selected edited glTF back into a new GMX using the original GMX as a conservative structural template.", compact=True)
            self._action(simple_actions, "Inspect GMX", self._inspect_gmx, 0, 2, help_text="Show a structural scan of the selected GMX in the task log. This is read-only and safe.", compact=True)
            self._action(simple_actions, "Open model folder", lambda: _open_path(Path(self.gmx_template.get()).parent), 0, 3, help_text="Open the folder containing the selected original GMX.", compact=True)

            assembly_box = ttk.LabelFrame(simple_actions, text="Assembly workspace", padding=4)
            assembly_box.grid(row=1, column=0, columnspan=4, sticky="ew", padx=2, pady=(4, 2))
            for c in (1, 4):
                assembly_box.columnconfigure(c, weight=1)
            ttk.Label(assembly_box, text="Models").grid(row=0, column=0, sticky="w", padx=(2, 4), pady=2)
            boss_models_entry = ttk.Entry(assembly_box, textvariable=self.boss_model_dir)
            boss_models_entry.grid(row=0, column=1, sticky="ew", pady=2)
            browse_models = ttk.Button(assembly_box, text="Browse…", command=self._browse_boss_model_dir)
            browse_models.grid(row=0, column=2, sticky="ew", padx=(4, 12), pady=2)
            ttk.Label(assembly_box, text="Output").grid(row=0, column=3, sticky="w", padx=(0, 4), pady=2)
            boss_output_entry = ttk.Entry(assembly_box, textvariable=self.boss_output_dir)
            boss_output_entry.grid(row=0, column=4, sticky="ew", pady=2)
            browse_output = ttk.Button(assembly_box, text="Browse…", command=self._browse_boss_output_dir)
            browse_output.grid(row=0, column=5, sticky="ew", padx=(4, 2), pady=2)
            for widget in (boss_models_entry, browse_models, boss_output_entry, browse_output):
                self._register_help(widget, "Boss and enemy/sub-boss assemblers share these remembered folders, so switching presets never requires browsing again.")

            assembly_tabs = ttk.Notebook(assembly_box)
            assembly_tabs.grid(row=1, column=0, columnspan=6, sticky="ew", pady=(3, 0))
            boss_box = ttk.Frame(assembly_tabs, padding=3)
            entity_box = ttk.Frame(assembly_tabs, padding=3)
            assembly_tabs.add(boss_box, text="Bosses")
            assembly_tabs.add(entity_box, text="Enemies / sub-bosses")
            self.gmx_assembly_tabs = assembly_tabs

            for c in range(4):
                boss_box.columnconfigure(c, weight=1)
                entity_box.columnconfigure(c, weight=1)

            ttk.Label(boss_box, text="Boss").grid(row=0, column=0, sticky="w", padx=2, pady=2)
            family_combo = ttk.Combobox(boss_box, textvariable=self.boss_family, state="readonly", values=tuple(self._compact_boss_options()), width=22)
            family_combo.grid(row=0, column=1, sticky="ew", padx=2, pady=2)
            family_combo.bind("<<ComboboxSelected>>", self._refresh_compact_boss_variants)
            ttk.Label(boss_box, text="Variant").grid(row=0, column=2, sticky="w", padx=2, pady=2)
            self.boss_variant_combo = ttk.Combobox(boss_box, textvariable=self.boss_variant, state="readonly", width=32)
            self.boss_variant_combo.grid(row=0, column=3, sticky="ew", padx=2, pady=2)
            self._action(boss_box, "Assemble", self._compact_boss_assemble, 1, 0, help_text="Assemble the selected evidence-backed boss preset into the shared output folder.", compact=True)
            self._action(boss_box, "Assemble + preview", self._compact_boss_preview, 1, 1, help_text="Assemble the selected boss preset, refresh the local Asset Viewer and open it.", compact=True)
            self._action(boss_box, "Save manifest", self._compact_boss_manifest, 1, 2, help_text="Write the selected assembly manifest to the shared output folder.", compact=True)
            self._action(boss_box, "Open output", lambda: _open_path(Path(self.boss_output_dir.get())), 1, 3, help_text="Open the shared assembly output folder.", compact=True)

            self.centipede_options_frame = ttk.Frame(boss_box)
            self.centipede_options_frame.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(2, 0))
            self.centipede_options_frame.columnconfigure(1, weight=1)
            self.centipede_options_frame.columnconfigure(3, weight=1)
            ttk.Label(self.centipede_options_frame, text="bos_007 segments").grid(row=0, column=0, sticky="w", padx=(2, 4), pady=1)
            cent_head = ttk.Entry(self.centipede_options_frame, textvariable=self.centipede_bos007_segments)
            cent_head.grid(row=0, column=1, sticky="ew", padx=(0, 8), pady=1)
            ttk.Label(self.centipede_options_frame, text="bos_007a segments").grid(row=0, column=2, sticky="w", padx=(0, 4), pady=1)
            cent_body = ttk.Entry(self.centipede_options_frame, textvariable=self.centipede_bos007a_segments)
            cent_body.grid(row=0, column=3, sticky="ew", pady=1)
            self._register_help(cent_head, "CENTIPEDE-only optional inspection override. Enter 1-based segments/ranges such as 2,5-8 for bos_007.gmx.")
            self._register_help(cent_body, "CENTIPEDE-only optional inspection override. Enter 1-based segments/ranges such as 1,32 for bos_007a.gmx. A segment cannot be in both boxes.")

            ttk.Label(entity_box, text="Entity").grid(row=0, column=0, sticky="w", padx=2, pady=2)
            entity_combo = ttk.Combobox(entity_box, textvariable=self.entity_family, state="readonly", values=tuple(self._compact_entity_options()), width=22)
            entity_combo.grid(row=0, column=1, sticky="ew", padx=2, pady=2)
            entity_combo.bind("<<ComboboxSelected>>", self._refresh_compact_entity_variants)
            ttk.Label(entity_box, text="Variant").grid(row=0, column=2, sticky="w", padx=2, pady=2)
            self.entity_variant_combo = ttk.Combobox(entity_box, textvariable=self.entity_variant, state="readonly", width=34)
            self.entity_variant_combo.grid(row=0, column=3, sticky="ew", padx=2, pady=2)
            self._action(entity_box, "Assemble", self._compact_entity_assemble, 1, 0, help_text="Assemble the selected console enemy/sub-boss preset using the shared model/output folders.", compact=True)
            self._action(entity_box, "Assemble + preview", self._compact_entity_preview, 1, 1, help_text="Assemble the selected entity preset, refresh the local Asset Viewer and open it.", compact=True)
            self._action(entity_box, "Save manifest", self._compact_entity_manifest, 1, 2, help_text="Write the selected entity assembly manifest beside the assembled glTF outputs.", compact=True)
            self._action(entity_box, "Open output", lambda: _open_path(Path(self.boss_output_dir.get())), 1, 3, help_text="Open the shared assembly output folder.", compact=True)

            self._register_help(boss_box, "Compact boss assembler. Choose a family and evidence-backed variant; shared folders stay remembered. CENTIPEDE-only segment overrides appear only when CENTIPEDE is selected.")
            self._register_help(entity_box, "Compact enemy/sub-boss assembler for ENVY, GREED, WRATH, KEEPER, OPPRESSOR, GLUTTONY, VANITY and TELEPORTER. Evidence scope and unresolved runtime behavior remain documented in the task/help surfaces rather than occupying permanent vertical space.")
            self._refresh_compact_boss_variants()
            self._refresh_compact_entity_variants()

            advanced_actions = ttk.LabelFrame(tab, text="Advanced GMX tools", padding=4)
            advanced_actions.grid(row=8, column=0, columnspan=3, sticky="ew", pady=4)
            self._mode_only(advanced_actions, advanced=True)
            for c in range(4): advanced_actions.columnconfigure(c, weight=1)
            self._action(advanced_actions, "Inspect GMX", self._inspect_gmx, 0, 0, help_text="Read-only structural scan of the selected native GMX.")
            self._action(advanced_actions, "Export glTF", self._export_gltf, 0, 1, help_text="Export the selected GMX into an editable glTF scene.")
            self._action(advanced_actions, "Import glTF → GMX", self._import_gltf, 0, 2, help_text="Template-backed glTF import using the selected advanced synchronization options.")
            self._action(advanced_actions, "Export editable JSON", self._export_gmx_json, 0, 3, help_text="Export a low-level editable JSON representation of the selected GMX for expert structural work.")
            self._action(advanced_actions, "Build JSON → GMX", self._build_gmx_json, 1, 0, help_text="Build a GMX from the editable JSON while preserving unsupported/opaque data from the selected template where required.")
            self._action(advanced_actions, "Open model folder", lambda: _open_path(Path(self.gmx_template.get()).parent), 1, 1, help_text="Open the selected GMX's containing directory.")
            self._action(advanced_actions, "Scene graph report", self._gmx_scene_report, 1, 2, help_text="Generate an HTML report of the decoded GMX scene/bone/material/animation relationships and open it.")
            self._action(advanced_actions, "Create new GMX", self._create_gmx_new, 1, 3, help_text="Compile a supported glTF into a completely new GMX without an original GMX template. Still subject to the toolkit's documented native-format boundaries.")
            ttk.Label(advanced_actions, text="PROGRESSIVE UFO formation").grid(row=2, column=0, sticky="w", padx=4, pady=4)
            progressive_advanced = ttk.Combobox(advanced_actions, textvariable=self.progressive_ufo_formation, state="readonly", width=28, values=self._progressive_ufo_formation_values())
            progressive_advanced.grid(row=2, column=1, sticky="ew", padx=4, pady=4)
            self._register_help(progressive_advanced, "Select the original first runtime formation or the exact recurring state-5/state-8 classic-UFO pose table.")
            self._action(advanced_actions, "PROGRESSIVE UFO manifest", self._progressive_ufo_manifest, 2, 2, help_text="Write the selected evidence-backed PROGRESSIVE UFO assembly definition to JSON for inspection or manual editing.")
            self._action(advanced_actions, "Assemble PROGRESSIVE UFO", self._assemble_progressive_ufo, 2, 3, help_text="Export the selected executable-backed five-part PROGRESSIVE UFO formation.")
            self._action(advanced_actions, "CRAB manifest", self._crab_manifest, 3, 0, help_text="Write the evidence-backed CRAB animated locator hierarchy to JSON. The old landed and first-visible baked snapshots remain available from the compact boss selector.")
            self._action(advanced_actions, "Assemble CRAB", self._assemble_crab, 3, 1, 3, help_text="Export CRAB as a locator-driven animated hierarchy. Native A7 articulated-leg and CD shell animation remains live instead of being frozen to one sample.")
            self._action(advanced_actions, "MANDALA manifest", self._mandala_manifest, 4, 0, help_text="Write the five-build executable-backed MANDALA initial-combat assembly definition: 40 visible instances at the state-7 activation boundary.")
            self._action(advanced_actions, "Assemble MANDALA", self._assemble_mandala, 4, 1, 3, help_text="Export MANDALA's state-7 activation snapshot. Native GMX animations are preserved; no arbitrary internal sample or radial-facing rotation is baked.")
            self._action(advanced_actions, "Armor manifest", self._hornet_manifest, 5, 0, help_text="Write the executable/model-backed full-armor HORNET assembly definition: A1 plus exactly 125 BF armor cubes at the sample-0 C1 formation-rig locator positions.")
            self._action(advanced_actions, "Assemble armor", self._assemble_hornet, 5, 1, help_text="Export HORNET's fully revealed 5×5×5 BF armor formation. C1 is meshless and C0 is a separate attack pool.")
            hornet_note = ttk.Label(advanced_actions, text="Exposed attack: use bos_008b prism/spread controls below", wraplength=360)
            hornet_note.grid(row=5, column=2, columnspan=2, sticky="w", padx=4, pady=4)
            self._register_help(hornet_note, "dev22 correction: HORNET's exposed-form workflow is represented by the bos_008b prism/spread attack. The legacy A1-only state-3 catalog remains CLI-compatible but is not presented as the exposed attack assembly.")
            ttk.Label(advanced_actions, text="ULTIMATE UFO state").grid(row=6, column=0, sticky="w", padx=4, pady=4)
            ultimate_advanced = ttk.Combobox(advanced_actions, textvariable=self.ultimate_ufo_state, state="readonly", width=28, values=self._ultimate_ufo_state_values())
            ultimate_advanced.grid(row=6, column=1, sticky="ew", padx=4, pady=4)
            self._register_help(ultimate_advanced, "Choose one of the eight executable-backed ULTIMATE UFO state snapshots. COMPLETE is the allocation/hierarchy view; numbered entries are explicit controller-activity subsets. Phase-table collision/destructibility flags are not treated as render-visibility proof.")
            self._action(advanced_actions, "ULTIMATE UFO manifest", self._ultimate_ufo_manifest, 6, 2, help_text="Write the selected ULTIMATE UFO manifest: either the complete 126-instance allocated hierarchy or one of the eight controller-activity subsets.")
            self._action(advanced_actions, "Assemble ULTIMATE UFO", self._assemble_ultimate_ufo, 6, 3, help_text="Export the selected ULTIMATE UFO state using the exact named lt_### attachment hierarchy from the retail executable.")
            ttk.Label(advanced_actions, text="HORNET prism root slot").grid(row=7, column=0, sticky="w", padx=4, pady=4)
            prism_combo = ttk.Combobox(advanced_actions, textvariable=self.hornet_prism_slot, state="readonly", width=18, values=("0", "2", "6", "8", "18", "20", "22", "24", "26", "36", "38", "42", "44"))
            prism_combo.grid(row=7, column=1, sticky="ew", padx=4, pady=4)
            self._register_help(prism_combo, "Advanced: choose one of the 13 exact runtime cells HORNET may randomly assign to its A1 core during the prism-wall attack. There is intentionally no single canonical random outcome.")
            self._action(advanced_actions, "Prism-wall manifest", self._hornet_prism_manifest, 7, 2, help_text="Write the selected evidence-backed HORNET prism-wall variant: one A1 core in the chosen runtime cell plus 44 C0 prisms in every other 5×9 grid cell.")
            self._action(advanced_actions, "Assemble prism wall", self._assemble_hornet_prism, 7, 3, help_text="Export the selected HORNET prism-wall runtime variant. BF armor and the invisible C1 rig are omitted because they are not visible in this settled attack formation.")
            ttk.Label(advanced_actions, text="HORNET propagation seed").grid(row=8, column=0, sticky="w", padx=4, pady=4)
            propagation_seed_combo = ttk.Combobox(advanced_actions, textvariable=self.hornet_propagation_seed, state="readonly", width=18, values=("0", "2", "6", "8", "18", "20", "22", "24", "26", "36", "38", "42", "44"))
            propagation_seed_combo.grid(row=8, column=1, sticky="ew", padx=4, pady=4)
            self._register_help(propagation_seed_combo, "Advanced: choose the inherited prism-wall A1 slot that seeds HORNET's later state-6 C0 propagation. Only the 13 executable-backed runtime seeds are available.")
            ttk.Label(advanced_actions, text="Propagation wave").grid(row=8, column=2, sticky="w", padx=4, pady=4)
            propagation_wave_combo = ttk.Combobox(advanced_actions, textvariable=self.hornet_propagation_wave, state="readonly", width=12, values=tuple(str(i) for i in range(10)))
            propagation_wave_combo.grid(row=8, column=3, sticky="ew", padx=4, pady=4)
            self._register_help(propagation_wave_combo, "Advanced: choose the activation wave. Wave 0 is the seed cell only; later waves alternate orthogonal and diagonal expansion. Some seeds finish before wave 9; invalid combinations are rejected rather than guessed.")
            self._action(advanced_actions, "Propagation manifest", self._hornet_propagation_manifest, 9, 0, 2, help_text="Write the selected HORNET state-6 propagation activation snapshot. A1 is hidden in this state; only C0 prisms reached by the selected seed/wave are included.")
            self._action(advanced_actions, "Assemble propagation", self._assemble_hornet_propagation, 9, 2, 2, help_text="Export the selected HORNET state-6 propagation activation snapshot using the exact 5×9 runtime grid. Beam/effect objects are intentionally omitted because they are not GMX assembly members.")
            ttk.Label(advanced_actions, text="BUTTERFLY phase").grid(row=10, column=0, sticky="w", padx=4, pady=4)
            butterfly_advanced = ttk.Combobox(advanced_actions, textvariable=self.butterfly_phase, state="readonly", width=28, values=self._butterfly_phase_values())
            butterfly_advanced.grid(row=10, column=1, sticky="ew", padx=4, pady=4)
            self._register_help(butterfly_advanced, "Select an exact BUTTERFLY phase. Retail loader records prove the body type, C7/C8/C9 module counts, and locator ranges for all four forms.")
            self._action(advanced_actions, "BUTTERFLY manifest", self._butterfly_manifest, 10, 2, help_text="Write the selected phase manifest with exact C7/C8/C9 module membership and lt_### attachment names.")
            self._action(advanced_actions, "Assemble BUTTERFLY", self._assemble_butterfly, 10, 3, help_text="Export the selected BUTTERFLY phase with native body animation and locator-attached wing modules.")
            ttk.Label(advanced_actions, text="UNKNOWN form").grid(row=11, column=0, sticky="w", padx=4, pady=4)
            unknown_advanced = ttk.Combobox(advanced_actions, textvariable=self.unknown_form, state="readonly", width=28, values=self._unknown_form_values())
            unknown_advanced.grid(row=11, column=1, sticky="ew", padx=4, pady=4)
            self._register_help(unknown_advanced, "Select ALL, the normalized uk01..uk12 30 Hz flicker preview, or one exact uk01..uk14 BONE branch. uk13/uk14 remain registered but are not selected by the normal 12-tick console gameplay cycle.")
            self._action(advanced_actions, "UNKNOWN manifest", self._unknown_manifest, 11, 2, help_text="Write the selected UNKNOWN manifest: all 14 branches, flicker preview, or one native branch.")
            self._action(advanced_actions, "Export UNKNOWN", self._assemble_unknown, 11, 3, help_text="Export all forms, the optional 30 Hz branch-visibility preview, or one exact ukXX subtree. No fake multipart transform is introduced.")
            ttk.Label(advanced_actions, text="VERTEBRATE phase").grid(row=12, column=0, sticky="w", padx=4, pady=4)
            vertebrate_advanced = ttk.Combobox(advanced_actions, textvariable=self.vertebrate_phase, state="readonly", width=28, values=self._vertebrate_phase_values())
            vertebrate_advanced.grid(row=12, column=1, sticky="ew", padx=4, pady=4)
            self._register_help(vertebrate_advanced, "Select the executable-backed VERTEBRATE body phase. Phase 1 includes the recovered alternating ±0.5°/tick piece-spin action. Phase 2 includes the corrected slot-0 +45° native Y tilt before the common +90° runtime Z target. bos_017b..j remain separate attack auxiliaries.")
            self._action(advanced_actions, "VERTEBRATE manifest", self._vertebrate_manifest, 12, 2, help_text="Write the selected two-phase VERTEBRATE structural assembly manifest for inspection or manual editing.")
            self._action(advanced_actions, "Assemble VERTEBRATE", self._assemble_vertebrate, 12, 3, help_text="Export the phase-1 rotating tower or corrected phase-2 endcap pair using executable-backed transforms and runtime actions.")
            self._action(advanced_actions, "CENTIPEDE manifest", self._centipede_manifest, 13, 0, 2, help_text="Write the exact initial 32-link ring manifest, including runtime head/body/tail roles and the evidence-backed split/reformation metadata.")
            self._action(advanced_actions, "Assemble CENTIPEDE", self._assemble_centipede, 13, 2, 2, help_text="Export the executable-backed initial CENTIPEDE ring. Dynamic split/reform/final-phase positions are intentionally not frozen into a fake canonical layout.")
            self._action(advanced_actions, "GIGANTIC UFO manifest", self._gigantic_ufo_manifest, 14, 0, 2, help_text="Write the executable-backed GIGANTIC UFO manifest: one 0x9E root and 36 0xB5 weapon modules attached to lt_001..lt_036; non-model B4 helper slots are excluded.")
            self._action(advanced_actions, "Assemble GIGANTIC UFO", self._assemble_gigantic_ufo, 14, 2, 2, help_text="Export the complete GIGANTIC UFO visual hierarchy using the native root locator transforms.")
            ttk.Label(advanced_actions, text="SQUID multipart").grid(row=15, column=0, sticky="w", padx=4, pady=4)
            squid_advanced = ttk.Combobox(advanced_actions, textvariable=self.squid_phase, state="readonly", width=28, values=self._squid_phase_values())
            squid_advanced.grid(row=15, column=1, sticky="ew", padx=4, pady=4)
            self._register_help(squid_advanced, "The multipart preset is the animated bos_016.gmx body plus eight native-locator legs. The body-only state is already standalone bos_016.gmx, so dev22 no longer exposes a redundant phase-2 assembly.")
            self._action(advanced_actions, "SQUID + legs manifest", self._squid_manifest, 15, 2, help_text="Write the exact SQUID body + eight-leg locator assembly manifest.")
            self._action(advanced_actions, "Assemble SQUID + legs", self._assemble_squid, 15, 3, help_text="Export the only multipart SQUID preset. For body-only SQUID, export bos_016.gmx directly.")
            ttk.Label(advanced_actions, text="AXON form").grid(row=16, column=0, sticky="w", padx=4, pady=4)
            axon_advanced = ttk.Combobox(advanced_actions, textvariable=self.axon_form, state="readonly", width=28, values=self._axon_form_values())
            axon_advanced.grid(row=16, column=1, sticky="ew", padx=4, pady=4)
            self._register_help(axon_advanced, "Select AXON's native A5 body or the stable expanded CA+16×CB two-ring reconstruction. The expanded form also recreates the 16 procedural C1C1C1 piston lines used by retail; the redundant CA-only core preset is no longer promoted in the GUI.")
            self._action(advanced_actions, "AXON manifest", self._axon_manifest, 16, 2, help_text="Write the selected AXON runtime assembly manifest, including exact subordinate record membership, ring angles, radii, Y offsets and phase-0 transform provenance.")
            self._action(advanced_actions, "Assemble AXON", self._assemble_axon, 16, 3, help_text="Export the selected executable-backed AXON form. Expanded petals use the exact per-frame retail placement/orientation equations at the deterministic phase-angle-0 snapshot.")
            ttk.Label(advanced_actions, text="THE SUN form").grid(row=17, column=0, sticky="w", padx=4, pady=4)
            the_sun_advanced = ttk.Combobox(advanced_actions, textvariable=self.the_sun_form, state="readonly", width=28, values=self._the_sun_form_values())
            the_sun_advanced.grid(row=17, column=1, sticky="ew", padx=4, pady=4)
            self._register_help(the_sun_advanced, "Native 0x47 body, later sample-40 extended arms, exact 48-instance B3 field, or the executable-synchronized opening snapshot where state 0 keeps the body at frame 0 while the barrier field reaches full.")
            self._action(advanced_actions, "THE SUN manifest", self._the_sun_manifest, 17, 2, help_text="Write the selected THE SUN evidence-backed assembly manifest with exact pose or B3 group/segment metadata.")
            self._action(advanced_actions, "Assemble THE SUN", self._assemble_the_sun, 17, 3, help_text="Export the selected THE SUN inspection form. The barrier form uses the recovered retail fixed-point-derived positions and is explicitly not labeled as the wave beam.")
            ttk.Label(advanced_actions, text="ULTIMATE UFO core override").grid(row=18, column=0, sticky="w", padx=4, pady=4)
            ultimate_core_combo = ttk.Combobox(advanced_actions, textvariable=self.ultimate_ufo_core, state="readonly", width=28, values=("Authored by selected state", "Force visible (inspection)", "Force hidden (inspection)"))
            ultimate_core_combo.grid(row=18, column=1, columnspan=3, sticky="ew", padx=4, pady=4)
            self._register_help(ultimate_core_combo, "Optional D9/bos_015l core visibility override. Authored preserves the selected runtime-state/allocation subset; forced visible/hidden are inspection overrides and do not claim native gameplay visibility.")
            self._action(advanced_actions, "Assemble GMXs…", self._assemble_gmx_manifest, 19, 0, 4, help_text="Use a custom multi-GMX assembly manifest to combine several native GMX files into one editable glTF scene.")
            ttk.Label(tab, text="Simple mode keeps template-backed editing conservative; Advanced mode exposes topology, schema and animation controls.", wraplength=1000).grid(row=10, column=0, columnspan=3, sticky="w", pady=(3, 0))

            def _bind_gmx_wheel_tree(widget) -> None:
                for child in widget.winfo_children():
                    # Do not steal the wheel from selectors or nested scrollable
                    # controls; frames/labels/buttons/entries can safely scroll
                    # the workbench while hovered.
                    if not isinstance(child, (ttk.Combobox, tk.Text, ttk.Treeview)):
                        child.bind("<MouseWheel>", _gmx_mousewheel, add="+")
                        child.bind("<Button-4>", _gmx_mousewheel, add="+")
                        child.bind("<Button-5>", _gmx_mousewheel, add="+")
                    _bind_gmx_wheel_tree(child)
            _bind_gmx_wheel_tree(gmx_body)

        def _tab_util(self, tab) -> None:
            self.tabs.add(tab, text="Utilities")
            self.util_tab = tab
            self.util_input = tk.StringVar()
            self.viewer_input = tk.StringVar()
            self.viewer_output = tk.StringVar(value=str(Path.cwd() / "siig_asset_viewer"))
            self.visualizer_input = tk.StringVar()
            self.visualizer_output = tk.StringVar(value=str(Path.cwd() / "siig_visualizer_simulator"))
            self.util_help_default = (
                "Utilities are optional support tools; they do not modify your game rip unless a generated-output command explicitly says so. "
                "Diagnose toolkit / input runs read-only checks; Run selftests checks the toolkit itself; Asset capabilities and Boss matrix print reference reports; "
                "Build viewer and Visualizer simulator create offline viewing tools in the output folders you choose. Hover or focus any control for its exact purpose."
            )
            ttk.Label(tab, text="Diagnostics, reference and generated viewers", font=("TkDefaultFont", 12, "bold")).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))
            self._entry_row(tab, 1, "Diagnostic input (optional)", self.util_input, help_text="Optional file/folder input for Diagnose toolkit / input. Leave blank to check only the toolkit installation and dependencies. This diagnostic is read-only.")
            self._entry_row(tab, 2, "Asset directory", self.viewer_input, kind="dir", help_text="Choose a directory of extracted/converted assets you want to browse with the local web asset viewer. The source directory is only read; Build viewer writes to Viewer output.")
            self._entry_row(tab, 3, "Viewer output", self.viewer_output, kind="dir", help_text="Choose where Build viewer should write the generated offline browser asset viewer.")
            self._entry_row(tab, 4, "Visualizer rip (optional)", self.visualizer_input, kind="dir", help_text="Optional full rip directory used as source data for the Visualizer simulator. The rip is read-only; the simulator is written to Visualizer output.")
            self._entry_row(tab, 5, "Visualizer output", self.visualizer_output, kind="dir", help_text="Choose where the offline SIIG Visualizer Simulator HTML and generated support files should be written.")
            actions = ttk.Frame(tab); actions.grid(row=6, column=0, columnspan=3, sticky="ew", pady=8)
            for c in range(4): actions.columnconfigure(c, weight=1)
            self._action(actions, "Diagnose toolkit / input", self._doctor, 0, 0, help_text="Run read-only diagnostics for the toolkit and, optionally, the selected game/package/folder. Checks Python/Tkinter support, bundled files, FFmpeg availability and recognizable input/platform details; it does not repair or modify anything.")
            self._action(actions, "Run selftests", lambda: self._run(["selftest"]), 0, 1, help_text="Run the toolkit's dependency-free internal regression suite. Useful after extracting/updating the toolkit or when troubleshooting. It does not modify your rip or Mod Workspace.")
            self._action(actions, "Asset capabilities", lambda: self._run(["asset-capabilities"]), 0, 2, help_text="Print the current asset support matrix: which SIIG asset families can be viewed, converted, edited, rebuilt/round-tripped or synthesized. This is a reference report only.")
            self._action(actions, "Build viewer", self._util_viewer, 0, 3, help_text="Generate and open the offline Asset Viewer for Asset directory. It writes generated viewer files only to Viewer output and leaves the source assets unchanged.")
            self._action(actions, "Boss matrix", lambda: self._run(["boss-matrix"]), 1, 0, 2, help_text="Print the research/reconstruction status for all 18 console boss families, including known catalogs and evidence grades. This does not assemble or modify a boss; assembly lives in GMX Workbench.")
            self._action(actions, "Visualizer simulator (PoC)", self._util_visualizer, 1, 2, 2, help_text="Build and open the offline Visualizer Simulator proof of concept. A supplied rip is read as source data; generated simulator files go only to Visualizer output.")
            self._action(actions, "Atlas inspector / safe sprite regions", self._util_atlas, 2, 0, 4, help_text="Build a non-destructive atlas editing workspace from an extracted PNG. Guides live in separate marked files and are blocked from TEX rebuild; identical-looking regions keep separate stable slot IDs. Current automatic regions are conservative visible-content bounds while native UV tables remain under research.")

            info = ttk.LabelFrame(tab, text="What does this utility do?", padding=5, height=92)
            info.grid(row=7, column=0, columnspan=3, sticky="ew", pady=(4, 8))
            info.grid_propagate(False)
            info.columnconfigure(0, weight=1); info.rowconfigure(0, weight=1)
            self.util_help_box = tk.Text(info, height=4, wrap="word", relief="flat", padx=4, pady=3)
            self.util_help_box.grid(row=0, column=0, sticky="nsew")
            self.util_help_box.configure(state="disabled")
            self._set_util_help(self.util_help_default)

            docs = ttk.Button(tab, text="Open toolkit documentation folder", command=lambda: _open_path(ROOT / "docs"))
            docs.grid(row=8, column=0, sticky="w", padx=4, pady=4)
            self._register_help(docs, "Open the bundled documentation and research notes in your file manager. This only opens the folder; it does not modify toolkit or game files.")
            tab.columnconfigure(1, weight=1)

        def _copy_log(self) -> None:
            self.clipboard_clear(); self.clipboard_append(self.log.get("1.0", "end-1c"))

        def _copy_rip_console(self) -> None:
            if not hasattr(self, "game_rip_console"):
                return
            self.clipboard_clear(); self.clipboard_append(self.game_rip_console.get("1.0", "end-1c"))

        def _append_rip_console(self, text: str) -> None:
            if not hasattr(self, "game_rip_console"):
                return
            self.game_rip_console.insert("end", text)
            self.game_rip_console.see("end")

        def _append(self, text: str) -> None:
            self.log.insert("end", text)
            self.log.see("end")

        def _set_busy(self, busy: bool) -> None:
            self._busy = busy
            for button in self._buttons:
                try: button.configure(state="disabled" if busy else "normal")
                except Exception: pass
            self._status.set("Working…" if busy else "Ready")

        def _run(self, args: list[str], on_done: Optional[Callable[[int], None]] = None) -> None:
            args = [str(x) for x in args if str(x) != ""]
            if args and args[0] in {"gmx2gltf", "gmx-assemble", "gmx-assemble-catalog"} and "--visual-pass" not in args:
                args.extend(["--visual-pass", self._gmx_visual_pass_arg()])
            if self._busy:
                messagebox.showinfo("SIIG Toolkit", "Another toolkit task is already running.")
                return
            if not TOOLKIT.is_file():
                messagebox.showerror("SIIG Toolkit", f"Missing {TOOLKIT}")
                return
            self._active_command = args[0] if args else ""
            self._save_preferences()
            self._set_busy(True)
            cmd = [sys.executable, str(TOOLKIT), *args]
            command_line = "$ " + " ".join(shlex.quote(x) for x in cmd) + "\n"
            self._append("\n" + command_line)
            if self._active_command in {"rip-game", "update-rip"}:
                self._append_rip_console(command_line)
            def worker() -> None:
                code = 1
                tail: list[str] = []
                try:
                    env = dict(os.environ)
                    env["PYTHONUNBUFFERED"] = "1"
                    proc = subprocess.Popen(cmd, cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", bufsize=1, env=env)
                    assert proc.stdout is not None
                    for line in proc.stdout:
                        tail.append(line.rstrip())
                        if len(tail) > 10:
                            tail.pop(0)
                        self._queue.put(("line", line))
                    code = proc.wait()
                except Exception as exc:
                    message = f"GUI launcher error: {exc}"
                    tail.append(message)
                    self._queue.put(("line", message + "\n"))
                self._queue.put(("done", code, on_done, "\n".join(tail)))
            threading.Thread(target=worker, daemon=True).start()

        def _run_capture_json(self, args: list[str], on_done: Callable[[dict], None]) -> None:
            args = [str(x) for x in args if str(x) != ""]
            if self._busy:
                messagebox.showinfo("SIIG Toolkit", "Another toolkit task is already running.")
                return
            if not TOOLKIT.is_file():
                messagebox.showerror("SIIG Toolkit", f"Missing {TOOLKIT}")
                return
            self._active_command = args[0] if args else ""
            self._save_preferences()
            self._set_busy(True)
            cmd = [sys.executable, str(TOOLKIT), *args]
            self._append("\n$ " + " ".join(shlex.quote(x) for x in cmd) + "\n")
            def worker() -> None:
                code = 1
                payload = None
                error = ""
                try:
                    proc = subprocess.run(cmd, cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
                    code = proc.returncode
                    if code == 0:
                        payload = json.loads(proc.stdout)
                    else:
                        error = (proc.stderr or proc.stdout or f"exit {code}").strip()
                except Exception as exc:
                    error = f"GUI launcher error: {exc}"
                self._queue.put(("json_done", code, on_done, payload, error))
            threading.Thread(target=worker, daemon=True).start()

        def _reset_rip_progress(self) -> None:
            self._rip_progress_counts = {"assets": 0, "gltf": 0, "png": 0, "errors": 0}
            if hasattr(self, "game_progress_phase"):
                self.game_progress_phase.set("Phase: preparing input")
            if hasattr(self, "game_progress_counts"):
                self.game_progress_counts.set("Assets 0 · glTF 0 · PNG 0 · errors 0")

        def _consume_rip_progress_line(self, line: str) -> None:
            message = line.strip()
            if not message:
                return
            counts = getattr(self, "_rip_progress_counts", None)
            if not isinstance(counts, dict):
                self._reset_rip_progress(); counts = self._rip_progress_counts
            lower = message.lower()
            phase = None
            if lower.startswith("update-rip preflight"):
                phase = "checking existing rip"
            elif lower.startswith("updating archive "):
                phase = "refreshing extracted archives"
            elif lower.startswith("update-rip: stat cache reused"):
                phase = "reusing verified update hashes"
            elif lower.startswith("update-rip: overwrite guard"):
                phase = "checking component before replacement"
            elif lower.startswith("update-rip: manifest refresh"):
                phase = "refreshing output manifest"
            elif lower.startswith("update-rip: archive conversions already current"):
                phase = "reusing current archive conversions"
            elif lower.startswith("update-rip: localization exports already current"):
                phase = "reusing current localization"
            elif lower.startswith("update-rip: system-font exports already current"):
                phase = "reusing current system font"
            elif lower.startswith("update-rip: rebuilding localization"):
                phase = "refreshing localization"
            elif lower.startswith("update-rip: rebuilding system-font"):
                phase = "refreshing system font"
            elif lower.startswith("update-rip: rebuilding decoded audio"):
                phase = "refreshing audio"
            elif lower.startswith("update-rip: rebuilding structured"):
                phase = "refreshing structured exports"
            elif lower.startswith("update-rip: rebuilding stage explorer"):
                phase = "refreshing Stage Explorer (PoC)"
            elif lower.startswith("update-rip: rebuilding visualizer"):
                phase = "refreshing Visualizer Simulator"
            elif lower.startswith("update-rip: rebuilding asset viewer"):
                phase = "refreshing Asset Viewer"
            elif lower.startswith("update-rip: verifying refreshed output"):
                phase = "verifying updated rip"
            elif lower.startswith("update verification passed"):
                phase = "updated rip verified"
            elif lower.startswith("rip update complete"):
                phase = "update complete"
            elif lower.startswith("decrypting container "):
                phase = "decrypting container"
            elif lower.startswith("decompressing "):
                phase = "decompressing archive"
            elif lower.startswith("extracting "):
                phase = "extracting BBX resources"
            elif lower.startswith("resume: unchanged archive skipped"):
                phase = "reusing unchanged extraction"
            elif lower.startswith("extracted ") and " from " in lower:
                phase = "extracting resources"
                counts["assets"] += 1
            elif lower.startswith("added converted gltf "):
                phase = "converting GMX → glTF"
                counts["gltf"] += 1
            elif lower.startswith("added converted png "):
                phase = "converting TEX → PNG"
                counts["png"] += 1
            elif lower.startswith("error ") or lower.startswith("error:"):
                phase = "error"
                counts["errors"] += 1
            elif lower.startswith("verifying rip output"):
                phase = "verifying output hashes"
            elif lower.startswith("verification passed"):
                phase = "verified"
            elif lower.startswith("verification failed"):
                phase = "verification failed"
                counts["errors"] += 1
            elif lower.startswith("full-game rip complete"):
                phase = "finalizing validation"
            elif lower.startswith("rip completed successfully"):
                phase = "complete"
            elif lower.startswith("rip completed with errors"):
                phase = "complete with errors"
            if phase and hasattr(self, "game_progress_phase"):
                self.game_progress_phase.set("Phase: " + phase)
            compact = message if len(message) <= 180 else message[:177] + "..."
            self.game_progress.set(compact)
            if hasattr(self, "game_progress_counts"):
                self.game_progress_counts.set(f"Assets {counts['assets']} · glTF {counts['gltf']} · PNG {counts['png']} · errors {counts['errors']}")
            self._status.set("Rip: " + (compact if len(compact) <= 72 else compact[:69] + "..."))

        def _poll_queue(self) -> None:
            # Do not drain an unbounded producer queue in one Tk callback. During a
            # full rip the CLI can emit hundreds of per-resource lines faster than
            # Tk can repaint; the old while-True drain could therefore make the log
            # *look* frozen even though the worker was streaming correctly. Process
            # a bounded batch and return to Tk so the Text widget repaints live.
            max_messages = 120
            processed = 0
            try:
                while processed < max_messages:
                    item = self._queue.get_nowait()
                    processed += 1
                    if item[0] == "line":
                        line = item[1]
                        self._append(line)
                        if self._active_command in {"rip-game", "update-rip"} and hasattr(self, "game_progress"):
                            self._append_rip_console(line)
                            self._consume_rip_progress_line(line)
                    elif item[0] == "json_done":
                        code, callback, payload, error = item[1], item[2], item[3], item[4]
                        self._append(f"[exit {code}]\n")
                        self._active_command = ""
                        self._set_busy(False)
                        if code == 0 and isinstance(payload, dict):
                            callback(payload)
                        else:
                            if error:
                                self._append(error + "\n")
                            messagebox.showerror("Mod Workspace", error or f"Asset listing failed (exit {code}).")
                    elif item[0] == "done":
                        code, callback = item[1], item[2]
                        tail = item[3] if len(item) > 3 else ""
                        active = self._active_command
                        self._append(f"[exit {code}]\n")
                        if active in {"rip-game", "update-rip"}:
                            self._append_rip_console(f"[exit {code}]\n")
                        self._active_command = ""
                        self._set_busy(False)
                        if code != 0 and active not in {"rip-game", "update-rip"}:
                            detail = (tail or "No additional error text was produced.").strip()
                            if len(detail) > 900:
                                detail = detail[-900:]
                            messagebox.showerror("SIIG Toolkit task failed", f"{active or 'Command'} failed (exit {code}).\n\n{detail}\n\nThe full output is available from Task log…")
                        if active in {"rip-game", "update-rip"} and hasattr(self, "game_progress"):
                            noun = "Rip update" if active == "update-rip" else "Rip"
                            self.game_progress.set(f"{noun} completed successfully." if code == 0 else f"{noun} finished with errors (exit {code}).")
                            if hasattr(self, "game_progress_phase"):
                                self.game_progress_phase.set("Phase: complete" if code == 0 else "Phase: complete with errors")
                            if hasattr(self, "game_progress_bar"):
                                self.game_progress_bar.stop()
                        if callback:
                            callback(code)
            except queue.Empty:
                pass
            self.after(15 if not self._queue.empty() else 80, self._poll_queue)

        @staticmethod
        def _visual_pass_arg(value: str) -> str:
            normalized = value.strip().lower()
            if normalized.startswith("solid only"):
                return "solid"
            if normalized.startswith("outline only"):
                return "outline"
            if normalized.startswith("combined"):
                return "combined"
            return "separate"

        def _gmx_visual_pass_arg(self) -> str:
            return self._visual_pass_arg(self.gmx_visual_pass.get())

        def _mark_outer_cache_status_stale(self, *_args) -> None:
            if hasattr(self, "game_outer_cache_status"):
                self.game_outer_cache_status.set("Cache status: output changed — click Refresh info")

        def _selected_outer_cache_path(self) -> Optional[Path]:
            value = self.game_output.get().strip() if hasattr(self, "game_output") else ""
            if not value:
                return None
            return _outer_cache_dir_for_output(Path(value))

        def _refresh_outer_cache_status(self) -> None:
            cache = self._selected_outer_cache_path()
            if cache is None:
                self.game_outer_cache_status.set("Cache status: choose a Rip output folder")
                return
            try:
                if cache.is_symlink():
                    self.game_outer_cache_status.set("Cache status: sidecar is a symlink (not followed)")
                    return
                if not cache.exists():
                    self.game_outer_cache_status.set("Cache status: not present")
                    return
                size = _tree_size_bytes_no_follow(cache)
                self.game_outer_cache_status.set(f"Cache status: present · {_format_byte_size(size)}")
            except OSError as exc:
                self.game_outer_cache_status.set(f"Cache status: unavailable ({exc})")

        def _clear_outer_cache(self) -> None:
            cache = self._selected_outer_cache_path()
            if cache is None:
                return messagebox.showinfo("Clear source-package cache", "Choose a Rip output folder first.")
            if not cache.exists() and not cache.is_symlink():
                self._refresh_outer_cache_status()
                return messagebox.showinfo("Clear source-package cache", "No source-package cache exists for the selected rip.")
            size_text = "unknown size"
            if not cache.is_symlink():
                size_text = _format_byte_size(_tree_size_bytes_no_follow(cache))
            warning = (
                f"Delete the source-package cache ({size_text}) for the selected rip?\n\n"
                "This permanently deletes only cached unpacked ZIP/STFS/PKG source files. "
                "It does NOT delete SIIG_Ripped, extracted assets, edits, or Mod Workspaces.\n\n"
                "The next full rip/resume that needs the original package may have to unpack it again and can take longer.\n\n"
                "Continue?"
            )
            if not messagebox.askyesno("Clear source-package cache?", warning, icon="warning"):
                return
            try:
                if cache.is_symlink() or cache.is_file():
                    cache.unlink()
                else:
                    shutil.rmtree(cache)
            except OSError as exc:
                self._refresh_outer_cache_status()
                return messagebox.showerror("Clear source-package cache", f"Could not clear the cache:\n{exc}")
            self._refresh_outer_cache_status()
            self._append("Source-package cache cleared for the selected rip. The rip itself was not changed.\n")
            messagebox.showinfo(
                "Source-package cache cleared",
                "The cache was deleted. The rip and Mod Workspaces were not changed. A later resume may need to unpack the original source package again.",
            )

        def _doctor_game_input(self) -> None:
            if not self.game_input.get():
                return messagebox.showerror("Input check", "Choose an input first.")
            self._run(["doctor", self.game_input.get()])

        def _rip_game(self) -> None:
            if not self.game_input.get():
                return messagebox.showerror("Game rip", "Choose an input first.")
            if not self.game_output.get():
                return messagebox.showerror("Game rip", "Choose an output folder first.")
            args = ["rip-game", self.game_input.get(), "-o", self.game_output.get(), "--gmx-visual-pass", self._visual_pass_arg(self.game_visual_pass.get())]
            if self.game_resume.get():
                args.append("--resume")
                if not self.game_outer_cache.get():
                    args.append("--no-outer-cache")
            self._reset_rip_progress()
            if hasattr(self, "game_rip_console"):
                self.game_rip_console.delete("1.0", "end")
                self._append_rip_console("SIIG full-game rip · complete per-file stream\n")
            self.game_progress.set("Starting full-game rip...")
            self.game_progress_bar.start(12)
            self._run(args, on_done=self._rip_finished)

        def _update_existing_rip(self) -> None:
            if not self.game_output.get():
                return messagebox.showerror("Update rip", "Choose the existing rip output folder first.")
            output_root = Path(self.game_output.get()).expanduser()
            if not (output_root / "validation" / "RIP_REPORT.json").is_file():
                return messagebox.showerror("Update rip", "The selected folder does not look like a completed SIIG rip (validation/RIP_REPORT.json is missing).")
            if not (output_root / "decompressed_bbx").is_dir():
                return messagebox.showerror("Update rip", "This rip does not contain decompressed_bbx, so it cannot be refreshed without the original game input.")
            self._reset_rip_progress()
            if hasattr(self, "game_rip_console"):
                self.game_rip_console.delete("1.0", "end")
                self._append_rip_console("SIIG rip updater · retained-source refresh stream\n")
            self.game_progress.set("Checking existing rip and update profile...")
            self.game_progress_bar.start(12)
            self._run(["update-rip", str(output_root)], on_done=self._update_rip_finished)

        def _update_rip_finished(self, code: int) -> None:
            self.game_progress_bar.stop()
            self._refresh_outer_cache_status()
            if code != 0:
                return
            output_root = Path(self.game_output.get()).expanduser()
            if hasattr(self, "mod_rip"):
                self.mod_rip.set(str(output_root))
            self._save_preferences()
            if self.game_open_viewer.get():
                html_path = output_root / "asset_viewer" / "SIIG_Asset_Viewer.html"
                if html_path.is_file():
                    self._launch_asset_viewer(output_root, html_path)

        def _rip_finished(self, code: int) -> None:
            self.game_progress_bar.stop()
            self._refresh_outer_cache_status()
            if code != 0:
                return
            output_root = Path(self.game_output.get()).expanduser()
            if hasattr(self, "mod_rip"):
                self.mod_rip.set(str(output_root))
            self._save_preferences()
            if self.game_open_viewer.get():
                html_path = output_root / "asset_viewer" / "SIIG_Asset_Viewer.html"
                if html_path.is_file():
                    self._launch_asset_viewer(output_root, html_path)

        def _launch_asset_viewer(self, root: Path, html_path: Path) -> None:
            if not html_path.is_file():
                messagebox.showerror("Asset Viewer", f"Viewer file was not created: {html_path}")
                return
            try:
                relative = html_path.resolve().relative_to(root.resolve()).as_posix()
            except ValueError:
                _open_path(html_path)
                return
            cmd = [sys.executable, str(TOOLKIT), "serve", str(root), "--port", "0", "--open-path", relative]
            kwargs = {"cwd": str(ROOT), "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
            if sys.platform.startswith("win") and hasattr(subprocess, "CREATE_NO_WINDOW"):
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
            try:
                proc = subprocess.Popen(cmd, **kwargs)
                self._viewer_servers = [item for item in self._viewer_servers if item.poll() is None]
                self._viewer_servers.append(proc)
                self._append(f"Asset Viewer localhost bridge started for {html_path.name}. Open file uses the OS-default application.\n")
            except Exception:
                _open_path(html_path)

        def _open_or_build_viewer(self) -> None:
            root = Path(self.game_output.get()).expanduser()
            html_path = root / "asset_viewer" / "SIIG_Asset_Viewer.html"
            if html_path.is_file():
                self._launch_asset_viewer(root, html_path)
            else:
                self._build_viewer()

        def _build_viewer(self) -> None:
            root = Path(self.game_output.get())
            out = root / "asset_viewer"
            html_path = out / "SIIG_Asset_Viewer.html"
            self._run(["asset-viewer", str(root), "-o", str(out)], lambda code: self._launch_asset_viewer(root, html_path) if code == 0 else None)

        @staticmethod
        def _mod_status_label(status: str) -> str:
            return {
                "untouched": "Untouched",
                "exported": "Exported",
                "edited": "Edited",
                "staged": "Staged",
                "added": "Added",
                "missing": "Missing edit",
                "archive_override": "Staged archive",
            }.get(str(status), str(status).replace("_", " ").title())

        @staticmethod
        def _mod_size_label(value) -> str:
            try:
                size = int(value)
            except (TypeError, ValueError):
                return ""
            if size < 1024:
                return f"{size} B"
            if size < 1024 * 1024:
                return f"{size / 1024:.1f} KiB"
            return f"{size / (1024 * 1024):.1f} MiB"

        def _mod_create_workspace(self) -> None:
            if not self.mod_rip.get() or not self.mod_ws.get():
                return messagebox.showerror("Mod Workspace", "Choose both the verified game rip and the mod workspace folder first.")
            self._run(["mod-init", self.mod_rip.get(), "-o", self.mod_ws.get()], lambda code: self._mod_list_assets() if code == 0 else None)

        def _mod_build_changes(self) -> None:
            workspace = Path(self.mod_ws.get())
            def done(code: int) -> None:
                if code != 0:
                    return
                if self._mod_browser_loaded:
                    self._mod_list_assets()
                replacements = workspace / "build" / "xbox360_replacements"
                if replacements.is_dir() and any(path.is_file() and path.name not in {"README.txt", "XBOX360_REPLACEMENTS.json"} for path in replacements.rglob("*")):
                    messagebox.showinfo("Mod build complete", "Xbox replacement containers are ready under build/xbox360_replacements. This folder now contains the deployment copies only (including Xbox .bin.gz.sdat gzip containers). Use Open Xbox replacements, then replace the matching paths inside a COPY of the package with any compatible Xbox 360 package editor.")
                else:
                    messagebox.showinfo("Mod build complete", "The mod build completed. No Xbox package replacement folder was produced for this workspace/platform; see Task log or MOD_BUILD_REPORT.json for packaging status.")
            self._run(["mod-build", str(workspace), "--clean"], done)

        def _mod_verify_build(self) -> None:
            def done(code: int) -> None:
                if code == 0:
                    if self._mod_browser_loaded:
                        self._mod_list_assets()
                    messagebox.showinfo("Mod Workspace", "Build verification passed.")
            self._run(["mod-verify", self.mod_ws.get()], done)

        def _mod_open_replacements(self) -> None:
            workspace = Path(self.mod_ws.get())
            replacements = workspace / "build" / "xbox360_replacements"
            payloads = [path for path in replacements.rglob("*") if path.is_file() and path.name not in {"README.txt", "XBOX360_REPLACEMENTS.json"}] if replacements.is_dir() else []
            if not payloads:
                return messagebox.showinfo("Xbox replacements", "No Xbox replacement files are built yet. Click Build replacement files first.")
            _open_path(replacements)

        def _mod_list_assets(self) -> None:
            workspace = Path(self.mod_ws.get())
            if not (workspace / "project.json").is_file():
                return messagebox.showerror("Mod Workspace", "Create the workspace first, or choose an existing SIIG Mod Workspace folder containing project.json.")
            self._run_capture_json(["mod-browser", str(workspace)], self._mod_populate_asset_tree)

        def _mod_populate_asset_tree(self, report: dict) -> None:
            tree = self.mod_asset_tree
            tree.delete(*tree.get_children())
            self._mod_tree_items = {}
            for aidx, archive in enumerate(report.get("archives", [])):
                archive_key = str(archive.get("archive_key", ""))
                aid = f"archive:{aidx}"
                status = str(archive.get("status", "untouched"))
                archive_type = "AUDIO · EDIT" if archive.get("archive_action") == "audio_edit" else "archive"
                tree.insert("", "end", iid=aid, text=archive_key, values=(self._mod_status_label(status), archive_type, f"{archive.get('entry_count', 0)} files"), tags=(status,))
                self._mod_tree_items[aid] = {"kind": "archive", **archive}
                for ridx, resource in enumerate(archive.get("resources", [])):
                    rid = f"resource:{aidx}:{ridx}"
                    rstatus = str(resource.get("status", "untouched"))
                    suffix = str(resource.get("suffix") or "").lstrip(".") or str(resource.get("builder") or "file")
                    tree.insert(aid, "end", iid=rid, text=str(resource.get("output_file", "")), values=(self._mod_status_label(rstatus), suffix.upper(), self._mod_size_label(resource.get("bytes"))), tags=(rstatus,))
                    self._mod_tree_items[rid] = {"kind": "resource", "archive_key": archive_key, **resource}
            totals = report.get("status_totals", {}) or {}
            self.mod_asset_summary.set(
                f"{report.get('resource_count', 0)} assets · "
                f"{totals.get('edited', 0)} edited · {totals.get('staged', 0)} staged · "
                f"{totals.get('added', 0)} added · {totals.get('exported', 0)} exported"
            )
            self.mod_asset_browser.grid()
            self._mod_browser_loaded = True
            pending = self._mod_pending_open
            self._mod_pending_open = None
            if pending:
                archive_key, resource_name = pending
                for iid, item in self._mod_tree_items.items():
                    if resource_name == "__archive__" and item.get("kind") == "archive" and item.get("archive_key") == archive_key:
                        tree.selection_set(iid); tree.see(iid)
                        self._mod_open_edit_selected()
                        break
                    if item.get("kind") == "resource" and item.get("archive_key") == archive_key and item.get("output_file") == resource_name:
                        tree.selection_set(iid); tree.see(iid)
                        self._mod_open_edit_selected()
                        break

        def _mod_tree_selection_changed(self) -> None:
            selected = self.mod_asset_tree.selection()
            if not selected:
                return
            item = self._mod_tree_items.get(selected[0], {})
            if item.get("kind") == "resource" and str(item.get("output_file", "")).lower().endswith(".gmx"):
                self.mod_archive.set(str(item.get("archive_key", "")))
                self.mod_resource.set(str(item.get("output_file", "")))

        def _mod_open_edit_selected(self) -> None:
            selected = self.mod_asset_tree.selection()
            if not selected:
                return messagebox.showinfo("Mod Workspace", "Select an asset in the tree first.")
            iid = selected[0]
            item = self._mod_tree_items.get(iid, {})
            if item.get("kind") == "archive":
                workspace = Path(self.mod_ws.get())
                view_paths = [str(path) for path in item.get("archive_view_paths", []) if str(path)]
                if item.get("archive_action") == "audio_edit":
                    editable_paths = [str(path) for path in item.get("archive_editable_paths", []) if str(path)]
                    if editable_paths:
                        target = workspace / editable_paths[0]
                        if target.exists():
                            _open_path(target.parent if len(editable_paths) > 1 else target)
                            return
                    self._mod_pending_open = (str(item.get("archive_key", "")), "__archive__")
                    self._run(["mod-export-archive", str(workspace), str(item.get("archive_key", ""))], lambda code: self._mod_list_assets() if code == 0 else setattr(self, "_mod_pending_open", None))
                    return
                editable_paths = [str(path) for path in item.get("archive_editable_paths", []) if str(path)]
                if editable_paths:
                    target = workspace / editable_paths[0]
                    if target.exists():
                        _open_path(target.parent if len(editable_paths) > 1 else target)
                        return
                source_name = str(item.get("source_game_path", "")).replace("\\", "/").lower()
                if "/text.bin" in source_name or "/message.bin" in source_name or source_name.startswith("text.bin") or source_name.startswith("message.bin"):
                    self._mod_pending_open = (str(item.get("archive_key", "")), "__archive__")
                    self._run(["mod-export-archive", str(workspace), str(item.get("archive_key", ""))], lambda code: self._mod_list_assets() if code == 0 else setattr(self, "_mod_pending_open", None))
                    return
                current = bool(self.mod_asset_tree.item(iid, "open"))
                self.mod_asset_tree.item(iid, open=not current)
                return
            archive_key = str(item.get("archive_key", ""))
            resource = str(item.get("output_file", ""))
            editable_paths = [str(path) for path in item.get("editable_paths", []) if str(path)]
            workspace = Path(self.mod_ws.get())
            if item.get("action") == "audio_edit":
                archive_item = next((value for value in self._mod_tree_items.values() if value.get("kind") == "archive" and value.get("archive_key") == archive_key), {})
                archive_editables = [str(path) for path in archive_item.get("archive_editable_paths", []) if str(path)]
                if archive_editables and (workspace / archive_editables[0]).exists():
                    target = workspace / archive_editables[0]
                    _open_path(target.parent if len(archive_editables) > 1 else target)
                    return
                self._mod_pending_open = (archive_key, "__archive__")
                self._run(["mod-export-archive", str(workspace), archive_key], lambda code: self._mod_list_assets() if code == 0 else setattr(self, "_mod_pending_open", None))
                return
            if editable_paths:
                target = workspace / editable_paths[0]
                if target.exists():
                    _open_path(target)
                    return
            status = str(item.get("status", "untouched"))
            if status in {"staged", "added"}:
                staged = workspace / ("added" if status == "added" else "staged") / archive_key / resource
                if staged.exists():
                    _open_path(staged.parent)
                    return
            self._mod_pending_open = (archive_key, resource)
            self._run(["mod-export", str(workspace), archive_key, resource], lambda code: self._mod_list_assets() if code == 0 else setattr(self, "_mod_pending_open", None))

        def _pack_mod(self) -> None:
            out = filedialog.asksaveasfilename(
                title="Save optional shareable .siigmod delta",
                defaultextension=".siigmod",
                filetypes=[("SIIG mod package", "*.siigmod")],
            )
            if not out:
                return
            destination = Path(out)
            def done(code: int) -> None:
                if code != 0:
                    return
                if not destination.is_file():
                    messagebox.showerror("Share .siigmod", "The pack command reported success, but the selected output file is missing. Check Task log…")
                    return
                messagebox.showinfo(
                    "Share .siigmod",
                    f"Saved the optional shareable mod delta to:\n{destination}\n\nThis .siigmod is for another SIIG Asset Toolkit user with a matching clean rip; it is not a replacement container for an Xbox package.",
                )
                _open_path(destination.parent)
            self._run(["mod-pack", self.mod_ws.get(), "-o", str(destination)], done)

        def _inspect_mod(self) -> None:
            path = filedialog.askopenfilename(filetypes=[("SIIG mod package", "*.siigmod"), ("All files", "*.*")])
            if path: self._run(["mod-package-info", path])

        def _apply_mod(self) -> None:
            path = filedialog.askopenfilename(filetypes=[("SIIG mod package", "*.siigmod"), ("All files", "*.*")])
            if path:
                if not self.mod_rip.get():
                    return messagebox.showerror("Apply mod", "Choose the verified source rip first.")
                self._run(["mod-apply", path, self.mod_rip.get(), self.mod_ws.get(), "--build"])

        def _mod_import_gltf(self) -> None:
            if not self.mod_archive.get() or not self.mod_resource.get() or not self.mod_gltf.get():
                return messagebox.showerror("Import glTF + TEX", "Enter the GMX archive key/resource and choose the edited glTF first.")
            args = ["mod-import-gltf", self.mod_ws.get(), self.mod_archive.get(), self.mod_resource.get(), self.mod_gltf.get()]
            self._run(args)

        def _inspect_gmx(self) -> None:
            if self.gmx_template.get(): self._run(["scan", self.gmx_template.get()])

        def _export_gltf(self) -> None:
            template = Path(self.gmx_template.get())
            if not template.is_file(): return messagebox.showerror("GMX", "Choose a native GMX first.")
            out = filedialog.askdirectory(title="Choose glTF output directory")
            if not out: return
            args = ["gmx2gltf", str(template), "-o", out]
            if self.gmx_flip.get(): args.append("--flip-v")
            def done(code: int) -> None:
                if code == 0:
                    gltf = Path(out) / (template.stem + ".gltf")
                    if gltf.exists(): self.gmx_gltf.set(str(gltf))
            self._run(args, done)

        def _import_gltf(self) -> None:
            template = Path(self.gmx_template.get()); gltf = Path(self.gmx_gltf.get())
            if not template.is_file() or not gltf.is_file(): return messagebox.showerror("GMX", "Choose both the native GMX template and edited glTF.")
            out = self.gmx_output.get() or str(template.with_name(template.stem + ".edited.gmx")); self.gmx_output.set(out)
            args = ["gltf2gmx-template", str(gltf), "--template", str(template), "-o", out]
            if self.gmx_flip.get(): args.append("--flip-v")
            if self.gmx_sync_graph.get(): args.append("--sync-mesh-graph")
            if self.gmx_sync_scene.get(): args.append("--sync-scene-graph")
            if self.gmx_sync_texture.get(): args.append("--sync-texture-graph")
            if self.gmx_synthesize_schemas.get(): args.append("--synthesize-native-schemas")
            if self.gmx_sync_animation.get(): args.append("--sync-animation-graph")
            if self.gmx_sync_rigid_skins.get(): args.append("--sync-rigid-skins")
            self._run(args)

        def _create_gmx_new(self) -> None:
            gltf = Path(self.gmx_gltf.get())
            if not gltf.is_file():
                return messagebox.showerror("GMX", "Choose an edited glTF first.")
            out = self.gmx_output.get() or str(gltf.with_suffix(".gmx"))
            self.gmx_output.set(out)
            args = ["gltf2gmx-new", str(gltf), "-o", out]
            if self.gmx_flip.get():
                args.append("--flip-v")
            self._run(args)

        def _compact_boss_options(self) -> dict[str, tuple[tuple[str, str], ...]]:
            """Main-game boss order, keeping inspection-only families explicit."""
            prism_slots = (0, 2, 6, 8, 18, 20, 22, 24, 26, 36, 38, 42, 44)
            # Ordering follows the project owner's main-game boss list.  The
            # final 5-6 boss is displayed as NAMELESS while its established
            # internal/runtime label remains NO_NAME.
            return {
                "THE MOON": (("Native inspection only — animated body", "the_moon_native_body"),),
                "THE SUN": (("Opening state 0 — body frame 0 + 48 barriers", "the_sun_opening_full_barriers"), ("Native animated body", "the_sun_native_body"), ("Extended arms — sample 40 (states 9/10/11)", "the_sun_extended_arms"), ("Protection barriers — 48 B3 segments", "the_sun_protection_barriers")),
                "GIGANTIC UFO": (("Complete 1 + 36 locator hierarchy", "gigantic_ufo_complete"),),
                "LADYBUG": (("Stage 3-4 — body + 4 deployed legs", "ladybug_stage3_4_deployed_legs"), ("Native body only", "ladybug_native_body")),
                "MANDALA": (("ALL 72 members — phase-0 inspection", "mandala_all_members_phase0"), ("Initial combat — 40-member state-7 boundary", "mandala_initial_combat"), ("Inner circles — state-8 phase-0 reference", "mandala_state8_inner_circles_phase0")),
                "UNKNOWN": (("ALL — all 14 native branches", "unknown_all_forms"), ("FLICKER — uk01..uk12 @ 30 Hz", "unknown_all_forms_flicker")) + tuple((f"uk{form:02d}" + (" — same visual as uk01" if form == 8 else ""), f"unknown_form_{form:02d}") for form in range(1, 15)),
                "CENTIPEDE": (("Initial 32-link combat ring", "centipede_initial_combat_ring"),),
                "HORNET": (("Full armor — 125 BF cubes", "hornet_full_armor"),) + tuple((f"Prism/spread attack — root slot {slot:02d}", f"hornet_prism_wall_{slot:02d}") for slot in prism_slots),
                "PROGRESSIVE UFO": (("Original — first runtime formation", "progressive_ufo"), ("Classic — recurring states 5/8", "progressive_ufo_classic")),
                "OCTOPUS": (("Retail gameplay spawn — articulated root", "octopus_retail_spawn"), ("Native inspection only", "octopus_native_body")),
                "BUTTERFLY": tuple((f"Phase {phase}", f"butterfly_phase_{phase}") for phase in range(1, 5)),
                "AXON": (("Native animated whole body", "axon_native_body"), ("Expanded core + 16 petals + piston rods", "axon_expanded_petals")),
                "WATER STRIDER": (("Retail gameplay spawn — root at authored X/Z", "water_strider_retail_spawn"), ("Native inspection only — timed field route remains separate", "water_strider_native_body")),
                "CRAB": (("Animated locator hierarchy — articulated legs + shell actions", "crab_animated_hierarchy"), ("Landed / combat-ready snapshot", "crab"), ("First-visible airborne snapshot", "crab_first_visible")),
                "ULTIMATE UFO": (("COMPLETE — 126 allocated hierarchy", "ultimate_ufo_complete"),) + tuple((f"State {state:02d}", f"ultimate_ufo_state_{state:02d}") for state in (2, 3, 6, 7, 8, 9, 11, 12)),
                "SQUID": (("Body + 8 locator-attached legs", "squid_phase1_legs"),),
                "VERTEBRATE": (("Phase 1 — rotating immense tower", "vertebrate_phase1_tower"), ("Phase 2 — corrected endcap pair", "vertebrate_phase2_endcaps")),
                "NAMELESS": (("Main/Bonus gameplay spawn — internal NO_NAME", "no_name_retail_main_spawn"), ("Extra 2-8 — point-to-point approach", "no_name_extra2_stage8_approach"), ("Native inspection only", "no_name_native_body")),
            }

        def _compact_entity_options(self) -> dict[str, tuple[tuple[str, str], ...]]:
            return {
                "ENVY": (
                    ("Retail Level 4-2 — growth-complete chain 20 / heading 3", "envy_retail_level4_2_growth_complete"),
                    ("Compact chain reference — 6 members / heading 0", "envy_zigzag_preview_06"),
                ),
                "GREED": (
                    ("Retail Level 4-1 — exact spawn anchor", "greed_retail_level4_1_spawn"),
                    ("Retail Level 4-1 — normal-timing approach trace", "greed_retail_level4_1_approach_trace"),
                    ("Retail Level 4-1 — hover center / target anchor", "greed_retail_level4_1_hover_entry"),
                ),
                "WRATH": (("Retail Level 4-4 — exact 55-sample approach + anchor", "wrath_retail_level4_4_approach"),),
                "KEEPER": (("Root + 8 locator helpers", "keeper_complete"),),
                "OPPRESSOR": (("Root + 11 ordered helpers", "oppressor_complete"),),
                "GLUTTONY": (("Body + paired B0 helpers", "gluttony_complete"),),
                "VANITY": (
                    ("Main-game arrival — exact X±74 helper formation", "vanity_main_game_arrival"),
                    ("State 2 entry records — normalized exact X±74 relationship", "vanity_state2_entry_relative"),
                    ("State 2 primary descent — exact local Y action", "vanity_state2_primary_descent_local"),
                    ("Owned root + 2 B1 helpers — identity inspection", "vanity_owned_visual_set"),
                ),
                "TELEPORTER": (
                    ("Retail 5-4 left transfer — full states 0→4", "teleporter_retail_5_4_left_transfer_cycle"),
                    ("Retail 5-4 right transfer — full states 0→4", "teleporter_retail_5_4_right_transfer_cycle"),
                    ("Retail 5-4 left — reachable state 2 tick 7", "teleporter_retail_5_4_left_state2_tick7"),
                    ("Retail 5-4 right — reachable state 2 tick 7", "teleporter_retail_5_4_right_state2_tick7"),
                    ("Owned 3 roots + 9 helpers — identity inspection", "teleporter_owned_visual_set"),
                ),
            }

        def _refresh_compact_entity_variants(self, *_args) -> None:
            if not hasattr(self, "entity_variant_combo"):
                return
            options = self._compact_entity_options().get(self.entity_family.get(), ())
            values = tuple(label for label, _catalog in options)
            self.entity_variant_combo.configure(values=values)
            if self.entity_variant.get() not in values:
                self.entity_variant.set(values[0] if values else "")

        def _compact_entity_catalog_key(self) -> str:
            family = self.entity_family.get()
            variant = self.entity_variant.get()
            for label, catalog in self._compact_entity_options().get(family, ()):
                if label == variant:
                    return catalog
            raise ValueError("Choose an enemy/sub-boss family and one of its listed evidence-backed variants.")

        def _preview_assembly_folder(self, output_dir: Path) -> None:
            output_dir = Path(output_dir).expanduser()
            if not output_dir.is_dir():
                return messagebox.showerror("Assembly preview", "The assembly output folder does not exist yet.")
            viewer_dir = output_dir / "_asset_viewer"
            html_path = viewer_dir / "SIIG_Asset_Viewer.html"
            self._run(["asset-viewer", str(output_dir), "-o", str(viewer_dir)], lambda code: self._launch_asset_viewer(output_dir, html_path) if code == 0 else None)

        def _assemble_catalog_remembered(self, catalog: str, *, extra_args: Optional[list[str]] = None, preview: bool = False, open_output: bool = True) -> None:
            try:
                root, out = self._compact_boss_paths(catalog, ".gltf")
            except (ValueError, OSError) as exc:
                return messagebox.showerror("GMX Assembler", str(exc))
            args = ["gmx-assemble-catalog", catalog, "--root", str(root), "-o", str(out)]
            if extra_args:
                args.extend(str(value) for value in extra_args)
            if self.gmx_flip.get():
                args.append("--flip-v")
            def done(code: int) -> None:
                if code != 0:
                    return
                if preview:
                    self._preview_assembly_folder(out.parent)
                elif open_output:
                    _open_path(out.parent)
            self._run(args, done)

        def _compact_entity_preview(self) -> None:
            try:
                catalog = self._compact_entity_catalog_key()
            except ValueError as exc:
                return messagebox.showerror("Entity Assembler", str(exc))
            self._assemble_catalog_remembered(catalog, preview=True)

        def _compact_boss_preview(self) -> None:
            try:
                catalog = self._compact_boss_catalog_key()
            except ValueError as exc:
                return messagebox.showerror("Boss Assembler", str(exc))
            extra: list[str] = []
            if catalog.startswith("ultimate_ufo_"):
                extra.extend(["--ultimate-core", self._ultimate_ufo_core_arg()])
            extra.extend(self._centipede_override_args(catalog))
            self._assemble_catalog_remembered(catalog, extra_args=extra, preview=True)

        def _remembered_model_root(self, title: str) -> Optional[Path]:
            current = Path(self.boss_model_dir.get()).expanduser() if self.boss_model_dir.get() else None
            if current is not None and current.is_dir():
                return current
            initial = current if current is not None else Path.home()
            value = filedialog.askdirectory(title=title, initialdir=str(initial if initial.is_dir() else initial.parent))
            if not value:
                return None
            root = Path(value)
            self.boss_model_dir.set(str(root))
            return root

        def _advanced_catalog_assemble(self, catalog: str, title: str, *, extra_args: Optional[list[str]] = None) -> None:
            root = self._remembered_model_root(title)
            if root is None:
                return
            out_dir = Path(self.boss_output_dir.get()).expanduser() if self.boss_output_dir.get() else Path.cwd() / "siig_boss_assemblies"
            out_dir.mkdir(parents=True, exist_ok=True)
            self.boss_output_dir.set(str(out_dir))
            out = out_dir / f"{catalog}.gltf"
            args = ["gmx-assemble-catalog", catalog, "--root", str(root), "-o", str(out)]
            if extra_args:
                args.extend(str(value) for value in extra_args)
            if self.gmx_flip.get():
                args.append("--flip-v")
            self._run(args, lambda code: _open_path(out.parent) if code == 0 else None)

        def _compact_entity_manifest(self) -> None:
            try:
                catalog = self._compact_entity_catalog_key()
                _root, out = self._compact_boss_paths(catalog, ".assembly.json")
            except (ValueError, OSError) as exc:
                return messagebox.showerror("Entity Assembler", str(exc))
            self._run(["gmx-assembly-template", catalog, "-o", str(out)], lambda code: _open_path(out.parent) if code == 0 else None)

        def _compact_entity_assemble(self) -> None:
            try:
                catalog = self._compact_entity_catalog_key()
            except ValueError as exc:
                return messagebox.showerror("Entity Assembler", str(exc))
            self._assemble_catalog_remembered(catalog)

        def _refresh_compact_boss_variants(self, *_args) -> None:
            if not hasattr(self, "boss_variant_combo"):
                return
            family = self.boss_family.get()
            options = self._compact_boss_options().get(family, ())
            values = tuple(label for label, _catalog in options)
            self.boss_variant_combo.configure(values=values)
            if self.boss_variant.get() not in values:
                self.boss_variant.set(values[0] if values else "")
            if hasattr(self, "centipede_options_frame"):
                if family == "CENTIPEDE":
                    self.centipede_options_frame.grid()
                else:
                    self.centipede_options_frame.grid_remove()

        def _compact_boss_catalog_key(self) -> str:
            family = self.boss_family.get()
            variant = self.boss_variant.get()
            for label, catalog in self._compact_boss_options().get(family, ()):
                if label == variant:
                    return catalog
            raise ValueError("Choose a boss family and one of its listed evidence-backed variants.")

        def _browse_boss_model_dir(self) -> None:
            initial = Path(self.boss_model_dir.get()).expanduser() if self.boss_model_dir.get() else Path.home()
            value = filedialog.askdirectory(title="Choose folder containing extracted boss GMX files", initialdir=str(initial if initial.is_dir() else initial.parent))
            if value:
                self.boss_model_dir.set(value)

        def _browse_boss_output_dir(self) -> None:
            initial = Path(self.boss_output_dir.get()).expanduser() if self.boss_output_dir.get() else Path.cwd()
            value = filedialog.askdirectory(title="Choose folder for assembled boss glTF files", initialdir=str(initial if initial.is_dir() else initial.parent))
            if value:
                self.boss_output_dir.set(value)

        def _compact_boss_paths(self, catalog: str, extension: str) -> tuple[Path, Path]:
            root = Path(self.boss_model_dir.get()).expanduser() if self.boss_model_dir.get() else None
            if root is None or not root.is_dir():
                raise ValueError("Choose the Boss Assembler model folder once before assembling.")
            out_dir = Path(self.boss_output_dir.get()).expanduser() if self.boss_output_dir.get() else None
            if out_dir is None:
                raise ValueError("Choose the Boss Assembler output folder once before assembling.")
            out_dir.mkdir(parents=True, exist_ok=True)
            suffix = extension if extension.startswith(".") else "." + extension
            return root, out_dir / f"{catalog}{suffix}"

        def _centipede_override_args(self, catalog: str) -> list[str]:
            if catalog != "centipede_initial_combat_ring":
                return []
            args: list[str] = []
            head = self.centipede_bos007_segments.get().strip()
            body = self.centipede_bos007a_segments.get().strip()
            if head:
                args.extend(["--centipede-bos007", head])
            if body:
                args.extend(["--centipede-bos007a", body])
            return args

        def _compact_boss_manifest(self) -> None:
            try:
                catalog = self._compact_boss_catalog_key()
                _root, out = self._compact_boss_paths(catalog, ".assembly.json")
            except (ValueError, OSError) as exc:
                return messagebox.showerror("Boss Assembler", str(exc))
            args = ["gmx-assembly-template", catalog, "-o", str(out)]
            if catalog.startswith("ultimate_ufo_"):
                args.extend(["--ultimate-core", self._ultimate_ufo_core_arg()])
            args.extend(self._centipede_override_args(catalog))
            self._run(args, lambda code: _open_path(out.parent) if code == 0 else None)

        def _compact_boss_assemble(self) -> None:
            try:
                catalog = self._compact_boss_catalog_key()
            except ValueError as exc:
                return messagebox.showerror("Boss Assembler", str(exc))
            extra: list[str] = []
            if catalog.startswith("ultimate_ufo_"):
                extra.extend(["--ultimate-core", self._ultimate_ufo_core_arg()])
            extra.extend(self._centipede_override_args(catalog))
            self._assemble_catalog_remembered(catalog, extra_args=extra)

        @staticmethod
        def _ultimate_ufo_state_values() -> tuple[str, ...]:
            return (
                "COMPLETE — 126 allocated hierarchy",
                "2 — UMB activity", "3 — TOW activity", "6 — FAN + RING activity",
                "7 — FAN + RING activity (second fan)", "8 — RING activity",
                "9 — CORE HOLD activity", "11 — AIRLOCK activity", "12 — AIRLOCK LATE activity",
            )

        @staticmethod
        def _progressive_ufo_formation_values() -> tuple[str, ...]:
            return (
                "Original — first runtime formation",
                "Classic — recurring states 5/8",
            )

        def _progressive_ufo_catalog_key(self) -> str:
            value = self.progressive_ufo_formation.get().strip().lower()
            if value.startswith("original"):
                return "progressive_ufo"
            if value.startswith("classic"):
                return "progressive_ufo_classic"
            raise ValueError(f"Unknown PROGRESSIVE UFO formation selection: {self.progressive_ufo_formation.get()!r}")

        def _ultimate_ufo_catalog_key(self) -> str:
            raw = self.ultimate_ufo_state.get().strip()
            if raw.upper().startswith("COMPLETE"):
                return "ultimate_ufo_complete"
            try:
                state = int(raw.split()[0])
            except (ValueError, IndexError):
                raise ValueError("Choose one of the listed ULTIMATE UFO states.")
            if state not in (2, 3, 6, 7, 8, 9, 11, 12):
                raise ValueError("Choose one of the listed ULTIMATE UFO states.")
            return f"ultimate_ufo_state_{state:02d}"

        def _ultimate_ufo_core_arg(self) -> str:
            value = self.ultimate_ufo_core.get().strip().lower()
            if value.startswith("force visible"):
                return "visible"
            if value.startswith("force hidden"):
                return "hidden"
            return "authored"

        def _ultimate_ufo_manifest(self) -> None:
            try:
                key = self._ultimate_ufo_catalog_key()
            except ValueError as exc:
                return messagebox.showerror("ULTIMATE UFO", str(exc))
            out = filedialog.asksaveasfilename(title="Save ULTIMATE UFO state assembly manifest", defaultextension=".json", filetypes=[("JSON", "*.json")])
            if out:
                self._run(["gmx-assembly-template", key, "-o", out, "--ultimate-core", self._ultimate_ufo_core_arg()])

        def _assemble_ultimate_ufo(self) -> None:
            try:
                key = self._ultimate_ufo_catalog_key()
            except ValueError as exc:
                return messagebox.showerror("ULTIMATE UFO", str(exc))
            self._advanced_catalog_assemble(key, "Choose directory containing extracted bos_015*.gmx files", extra_args=["--ultimate-core", self._ultimate_ufo_core_arg()])

        @staticmethod
        def _butterfly_phase_values() -> tuple[str, ...]:
            return (
                "1 — phase 1 / body only",
                "2 — phase 2 / first wings",
                "3 — phase 3 / extended wings",
                "4 — phase 4 / final wings",
            )

        def _butterfly_catalog_key(self) -> str:
            raw = self.butterfly_phase.get().strip()
            try:
                phase = int(raw.split()[0])
            except (ValueError, IndexError):
                raise ValueError("Choose one of the four BUTTERFLY phases.")
            if phase not in (1, 2, 3, 4):
                raise ValueError("Choose one of the four BUTTERFLY phases.")
            return f"butterfly_phase_{phase}"

        def _butterfly_manifest(self) -> None:
            try:
                key = self._butterfly_catalog_key()
            except ValueError as exc:
                return messagebox.showerror("BUTTERFLY", str(exc))
            out = filedialog.asksaveasfilename(
                title="Save BUTTERFLY phase assembly manifest",
                defaultextension=".json",
                filetypes=[("JSON", "*.json")],
            )
            if out:
                self._run(["gmx-assembly-template", key, "-o", out])

        def _assemble_butterfly(self) -> None:
            try:
                key = self._butterfly_catalog_key()
            except ValueError as exc:
                return messagebox.showerror("BUTTERFLY", str(exc))
            self._advanced_catalog_assemble(key, "Choose directory containing retail bos_011*.gmx files")

        @staticmethod
        def _unknown_form_values() -> tuple[str, ...]:
            return (
                "ALL — all 14 native branches",
                "FLICKER — uk01..uk12 @ 30 Hz preview",
                *(f"{i:02d} — uk{i:02d}" + (" (same visual as uk01)" if i == 8 else "") for i in range(1, 15)),
            )

        def _unknown_catalog_key(self) -> str:
            raw = self.unknown_form.get().strip()
            upper = raw.upper()
            if upper.startswith("ALL"):
                return "unknown_all_forms"
            if upper.startswith("FLICKER"):
                return "unknown_all_forms_flicker"
            try:
                form = int(raw.split()[0])
            except (ValueError, IndexError):
                raise ValueError("Choose ALL, FLICKER, or one of UNKNOWN's 14 named native forms.")
            if form not in range(1, 15):
                raise ValueError("Choose ALL, FLICKER, or one of UNKNOWN's 14 named native forms.")
            return f"unknown_form_{form:02d}"

        def _unknown_manifest(self) -> None:
            try:
                key = self._unknown_catalog_key()
            except ValueError as exc:
                return messagebox.showerror("UNKNOWN", str(exc))
            out = filedialog.asksaveasfilename(
                title="Save UNKNOWN form manifest",
                defaultextension=".json",
                filetypes=[("JSON", "*.json")],
            )
            if out:
                self._run(["gmx-assembly-template", key, "-o", out])

        def _assemble_unknown(self) -> None:
            try:
                key = self._unknown_catalog_key()
            except ValueError as exc:
                return messagebox.showerror("UNKNOWN", str(exc))
            root = self._remembered_model_root("Choose directory containing retail bos_006.gmx")
            if root is None:
                return
            source_path = root / "bos_006.gmx"
            if not source_path.is_file():
                return messagebox.showerror("UNKNOWN", f"The remembered model folder does not contain bos_006.gmx: {root}")
            self._advanced_catalog_assemble(key, "Choose directory containing retail bos_006.gmx")

        @staticmethod
        def _vertebrate_phase_values() -> tuple[str, ...]:
            return (
                "1 — phase 1 / rotating immense tower",
                "2 — phase 2 / corrected endcaps",
            )

        def _vertebrate_catalog_key(self) -> str:
            raw = self.vertebrate_phase.get().strip()
            try:
                phase = int(raw.split()[0])
            except (ValueError, IndexError):
                raise ValueError("Choose one of the two VERTEBRATE structural phases.")
            if phase == 1:
                return "vertebrate_phase1_tower"
            if phase == 2:
                return "vertebrate_phase2_endcaps"
            raise ValueError("Choose one of the two VERTEBRATE structural phases.")

        def _vertebrate_manifest(self) -> None:
            try:
                key = self._vertebrate_catalog_key()
            except ValueError as exc:
                return messagebox.showerror("VERTEBRATE", str(exc))
            out = filedialog.asksaveasfilename(
                title="Save VERTEBRATE phase assembly manifest",
                defaultextension=".json",
                filetypes=[("JSON", "*.json")],
            )
            if out:
                self._run(["gmx-assembly-template", key, "-o", out])

        def _assemble_vertebrate(self) -> None:
            try:
                key = self._vertebrate_catalog_key()
            except ValueError as exc:
                return messagebox.showerror("VERTEBRATE", str(exc))
            self._advanced_catalog_assemble(key, "Choose directory containing retail bos_017.gmx / bos_017a.gmx")

        def _centipede_manifest(self) -> None:
            out = filedialog.asksaveasfilename(
                title="Save CENTIPEDE initial-ring assembly manifest",
                defaultextension=".json",
                filetypes=[("JSON", "*.json")],
            )
            if out:
                args = ["gmx-assembly-template", "centipede_initial_combat_ring", "-o", out]
                args.extend(self._centipede_override_args("centipede_initial_combat_ring"))
                self._run(args)

        def _assemble_centipede(self) -> None:
            extra = self._centipede_override_args("centipede_initial_combat_ring")
            self._advanced_catalog_assemble("centipede_initial_combat_ring", "Choose directory containing retail bos_007.gmx / bos_007a.gmx", extra_args=extra)

        @staticmethod
        def _squid_phase_values() -> tuple[str, ...]:
            return ("Body + 8 legs — multipart assembly",)

        def _squid_catalog_key(self) -> str:
            return "squid_phase1_legs"

        def _squid_manifest(self) -> None:
            try:
                key = self._squid_catalog_key()
            except ValueError as exc:
                return messagebox.showerror("SQUID", str(exc))
            out = filedialog.asksaveasfilename(
                title="Save SQUID phase assembly manifest",
                defaultextension=".json",
                filetypes=[("JSON", "*.json")],
            )
            if out:
                self._run(["gmx-assembly-template", key, "-o", out])

        def _assemble_squid(self) -> None:
            try:
                key = self._squid_catalog_key()
            except ValueError as exc:
                return messagebox.showerror("SQUID", str(exc))
            self._advanced_catalog_assemble(key, "Choose directory containing retail bos_016.gmx / bos_016a.gmx")

        @staticmethod
        def _the_sun_form_values() -> tuple[str, ...]:
            return (
                "Opening state 0 — body frame 0 + 48 barriers",
                "Native — animated body",
                "Extended arms — native sample 40",
                "Protection barriers — 48 B3 segments",
            )

        def _the_sun_catalog_key(self) -> str:
            value = self.the_sun_form.get().strip().lower()
            if value.startswith("opening"):
                return "the_sun_opening_full_barriers"
            if value.startswith("native"):
                return "the_sun_native_body"
            if value.startswith("extended"):
                return "the_sun_extended_arms"
            if value.startswith("protection"):
                return "the_sun_protection_barriers"
            raise ValueError("Choose one of the four THE SUN inspection forms.")

        def _the_sun_manifest(self) -> None:
            try:
                key = self._the_sun_catalog_key()
            except ValueError as exc:
                return messagebox.showerror("THE SUN", str(exc))
            out = filedialog.asksaveasfilename(
                title="Save THE SUN assembly manifest",
                defaultextension=".json",
                filetypes=[("JSON", "*.json")],
            )
            if out:
                self._run(["gmx-assembly-template", key, "-o", out])

        def _assemble_the_sun(self) -> None:
            try:
                key = self._the_sun_catalog_key()
            except ValueError as exc:
                return messagebox.showerror("THE SUN", str(exc))
            self._advanced_catalog_assemble(key, "Choose directory containing retail bos_002.gmx / bos_002b.gmx")

        @staticmethod
        def _axon_form_values() -> tuple[str, ...]:
            return (
                "Native — animated whole body",
                "Expanded — core + 16 petals + piston rods",
            )

        def _axon_catalog_key(self) -> str:
            value = self.axon_form.get().strip().lower()
            if value.startswith("native"):
                return "axon_native_body"
            if value.startswith("expanded"):
                return "axon_expanded_petals"
            raise ValueError("Choose one of the two promoted AXON runtime forms.")

        def _axon_manifest(self) -> None:
            try:
                key = self._axon_catalog_key()
            except ValueError as exc:
                return messagebox.showerror("AXON", str(exc))
            out = filedialog.asksaveasfilename(
                title="Save AXON form assembly manifest",
                defaultextension=".json",
                filetypes=[("JSON", "*.json")],
            )
            if out:
                self._run(["gmx-assembly-template", key, "-o", out])

        def _assemble_axon(self) -> None:
            try:
                key = self._axon_catalog_key()
            except ValueError as exc:
                return messagebox.showerror("AXON", str(exc))
            self._advanced_catalog_assemble(key, "Choose directory containing retail bos_012.gmx / bos_012a.gmx / bos_012b.gmx")

        def _gigantic_ufo_manifest(self) -> None:
            out = filedialog.asksaveasfilename(
                title="Save GIGANTIC UFO assembly manifest",
                defaultextension=".json",
                filetypes=[("JSON", "*.json")],
            )
            if out:
                self._run(["gmx-assembly-template", "gigantic_ufo_complete", "-o", out])

        def _assemble_gigantic_ufo(self) -> None:
            self._advanced_catalog_assemble("gigantic_ufo_complete", "Choose directory containing retail bos_003.gmx / bos_003a.gmx")

        def _mandala_manifest(self) -> None:
            out = filedialog.asksaveasfilename(title="Save MANDALA complete 72-member inspection manifest", defaultextension=".json", filetypes=[("JSON", "*.json")])
            if out:
                self._run(["gmx-assembly-template", "mandala_all_members_phase0", "-o", out])

        def _assemble_mandala(self) -> None:
            self._advanced_catalog_assemble("mandala_all_members_phase0", "Choose directory containing bos_005.gmx / bos_005a.gmx / bos_005b.gmx / bos_005c.gmx / bos_005d.gmx / bos_005e.gmx")

        def _progressive_ufo_manifest(self) -> None:
            try:
                key = self._progressive_ufo_catalog_key()
            except ValueError as exc:
                return messagebox.showerror("PROGRESSIVE UFO", str(exc))
            out = filedialog.asksaveasfilename(title="Save PROGRESSIVE UFO assembly manifest", defaultextension=".json", filetypes=[("JSON", "*.json")])
            if out:
                self._run(["gmx-assembly-template", key, "-o", out])

        def _assemble_progressive_ufo(self) -> None:
            try:
                key = self._progressive_ufo_catalog_key()
            except ValueError as exc:
                return messagebox.showerror("PROGRESSIVE UFO", str(exc))
            self._advanced_catalog_assemble(key, "Choose directory containing bos_009.gmx / bos_009a.gmx / bos_009b.gmx")

        def _crab_manifest(self) -> None:
            out = filedialog.asksaveasfilename(title="Save CRAB assembly manifest", defaultextension=".json", filetypes=[("JSON", "*.json")])
            if out:
                self._run(["gmx-assembly-template", "crab_animated_hierarchy", "-o", out])

        def _assemble_crab(self) -> None:
            self._advanced_catalog_assemble("crab_animated_hierarchy", "Choose directory containing bos_013.gmx / bos_013a.gmx / bos_013b.gmx / bos_013c.gmx / bos_013d.gmx")

        def _hornet_manifest(self) -> None:
            out = filedialog.asksaveasfilename(title="Save HORNET full-armor assembly manifest", defaultextension=".json", filetypes=[("JSON", "*.json")])
            if out:
                self._run(["gmx-assembly-template", "hornet_full_armor", "-o", out])

        def _assemble_hornet(self) -> None:
            self._advanced_catalog_assemble("hornet_full_armor", "Choose directory containing bos_008.gmx / bos_008a.gmx")

        def _hornet_exposed_manifest(self) -> None:
            out = filedialog.asksaveasfilename(title="Save HORNET exposed-core assembly manifest", defaultextension=".json", filetypes=[("JSON", "*.json")])
            if out:
                self._run(["gmx-assembly-template", "hornet_exposed_core", "-o", out])

        def _assemble_hornet_exposed(self) -> None:
            self._advanced_catalog_assemble("hornet_exposed_core", "Choose directory containing bos_008.gmx")

        def _assemble_hornet_prism_prompt(self) -> None:
            allowed = (0, 2, 6, 8, 18, 20, 22, 24, 26, 36, 38, 42, 44)
            slot = simpledialog.askinteger(
                "HORNET prism attack",
                "Choose a runtime prism root slot:\n" + ", ".join(str(v) for v in allowed),
                initialvalue=int(self.hornet_prism_slot.get() or 22), parent=self,
            )
            if slot is None:
                return
            if slot not in allowed:
                return messagebox.showerror("HORNET prism attack", "Choose one of the listed runtime-valid root slots.")
            self.hornet_prism_slot.set(str(slot))
            self._assemble_hornet_prism()

        def _hornet_prism_catalog_key(self) -> str:
            try:
                slot = int(self.hornet_prism_slot.get())
            except ValueError:
                raise ValueError("Choose one of the listed HORNET prism-wall root slots.")
            allowed = (0, 2, 6, 8, 18, 20, 22, 24, 26, 36, 38, 42, 44)
            if slot not in allowed:
                raise ValueError("Choose one of the listed HORNET prism-wall root slots.")
            return f"hornet_prism_wall_{slot:02d}"

        def _hornet_prism_manifest(self) -> None:
            try:
                key = self._hornet_prism_catalog_key()
            except ValueError as exc:
                return messagebox.showerror("HORNET prism wall", str(exc))
            out = filedialog.asksaveasfilename(title="Save HORNET prism-wall assembly manifest", defaultextension=".json", filetypes=[("JSON", "*.json")])
            if out:
                self._run(["gmx-assembly-template", key, "-o", out])

        def _assemble_hornet_prism(self) -> None:
            try:
                key = self._hornet_prism_catalog_key()
            except ValueError as exc:
                return messagebox.showerror("HORNET prism wall", str(exc))
            self._advanced_catalog_assemble(key, "Choose directory containing bos_008.gmx / bos_008b.gmx")

        def _hornet_propagation_catalog_key(self) -> str:
            try:
                seed = int(self.hornet_propagation_seed.get())
                wave = int(self.hornet_propagation_wave.get())
            except ValueError:
                raise ValueError("Choose a listed HORNET propagation seed and wave.")
            allowed = (0, 2, 6, 8, 18, 20, 22, 24, 26, 36, 38, 42, 44)
            if seed not in allowed or not 0 <= wave <= 9:
                raise ValueError("Choose a listed HORNET propagation seed and wave.")
            return f"hornet_propagation_{seed:02d}_wave_{wave:02d}"

        def _hornet_propagation_manifest(self) -> None:
            try:
                key = self._hornet_propagation_catalog_key()
            except ValueError as exc:
                return messagebox.showerror("HORNET propagation", str(exc))
            out = filedialog.asksaveasfilename(title="Save HORNET propagation snapshot manifest", defaultextension=".json", filetypes=[("JSON", "*.json")])
            if out:
                self._run(["gmx-assembly-template", key, "-o", out])

        def _assemble_hornet_propagation(self) -> None:
            try:
                key = self._hornet_propagation_catalog_key()
            except ValueError as exc:
                return messagebox.showerror("HORNET propagation", str(exc))
            self._advanced_catalog_assemble(key, "Choose directory containing bos_008b.gmx")

        def _assemble_gmx_manifest(self) -> None:
            initial_manifest_dir = Path(self.boss_output_dir.get()).expanduser() if self.boss_output_dir.get() else Path.cwd()
            manifest = filedialog.askopenfilename(title="Choose GMX assembly manifest", initialdir=str(initial_manifest_dir if initial_manifest_dir.is_dir() else initial_manifest_dir.parent), filetypes=[("JSON", "*.json"), ("All files", "*.*")])
            if not manifest:
                return
            root = self._remembered_model_root("Choose directory containing referenced GMX files")
            if root is None:
                return
            out_dir = Path(self.boss_output_dir.get()).expanduser() if self.boss_output_dir.get() else Path.cwd() / "siig_boss_assemblies"
            out_dir.mkdir(parents=True, exist_ok=True)
            self.boss_output_dir.set(str(out_dir))
            out = out_dir / (Path(manifest).stem + ".gltf")
            args = ["gmx-assemble", manifest, "--root", str(root), "-o", str(out)]
            if self.gmx_flip.get():
                args.append("--flip-v")
            self._run(args, lambda code: _open_path(out.parent) if code == 0 else None)

        def _gmx_scene_report(self) -> None:
            template = Path(self.gmx_template.get())
            if not template.is_file(): return messagebox.showerror("GMX", "Choose a native GMX first.")
            out = template.with_name(template.stem + ".scene.html")
            self._run(["gmx-scene-report", str(template), "-o", str(out)], lambda code: _open_path(out) if code == 0 else None)

        def _export_gmx_json(self) -> None:
            template = Path(self.gmx_template.get())
            if not template.is_file(): return messagebox.showerror("GMX", "Choose a native GMX first.")
            out = self.gmx_json.get() or str(template.with_suffix(".gmx.edit.json")); self.gmx_json.set(out)
            self._run(["gmx-edit-export", str(template), "-o", out])

        def _build_gmx_json(self) -> None:
            template = Path(self.gmx_template.get()); doc = Path(self.gmx_json.get())
            if not template.is_file() or not doc.is_file(): return messagebox.showerror("GMX", "Choose a GMX template and editable JSON.")
            out = self.gmx_output.get() or str(template.with_name(template.stem + ".edited.gmx")); self.gmx_output.set(out)
            self._run(["gmx-build", str(doc), "--template", str(template), "-o", out])

        def _doctor(self) -> None:
            args = ["doctor"]
            if self.util_input.get(): args.append(self.util_input.get())
            self._run(args)

        def _util_viewer(self) -> None:
            if not self.viewer_input.get(): return messagebox.showerror("Asset viewer", "Choose an asset directory first.")
            out = Path(self.viewer_output.get())
            viewer_root = Path(self.viewer_input.get())
            self._run(["asset-viewer", self.viewer_input.get(), "-o", str(out)], lambda code: self._launch_asset_viewer(viewer_root, out / "SIIG_Asset_Viewer.html") if code == 0 else None)

        def _util_visualizer(self) -> None:
            out = Path(self.visualizer_output.get())
            args = ["visualizer-sim"]
            if self.visualizer_input.get():
                args.append(self.visualizer_input.get())
            args.extend(["-o", str(out)])
            self._run(args, lambda code: _open_path(out / "SIIG_Visualizer_Simulator.html") if code == 0 else None)

        def _util_atlas(self) -> None:
            source = filedialog.askopenfilename(
                title="Choose extracted atlas PNG",
                filetypes=[("PNG images", "*.png"), ("All files", "*.*")],
            )
            if not source:
                return
            suggested = Path(source).with_name(Path(source).stem + "_atlas_workspace")
            output = filedialog.askdirectory(
                title="Choose Atlas Inspector output folder",
                initialdir=str(suggested.parent),
            )
            if not output:
                return
            out = Path(output) / suggested.name
            self._run(["atlas-inspect", source, "-o", str(out)], lambda code: _open_path(out / "atlas_workspace.html") if code == 0 else None)

    app = App()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
