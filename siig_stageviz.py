#!/usr/bin/env python3
"""Self-contained SIIG stage MAP/DAT explorer generator."""
from __future__ import annotations

import base64
import csv
import json
import math
import re
import struct
from collections import Counter
from pathlib import Path

import siig_toolkit as toolkit

STAGE_EXPLORER_VERSION = 8


# June 10 DebugOpt runtime table at 0x8204BD50.
STAGE_TILE_SET_IDS = (
    6, 7, 6, 7, 6, 8, 6, 7, 6, 7, 6, 8, 6, 7, 6, 7, 6, 8,
    6, 7, 6, 7, 6, 8, 6, 7, 6, 7, 6, 8, 6, 7, 6, 7, 6, 8,
    6, 7, 6, 6, 7, 7, 7, 6, 8, 6, 7, 6, 6, 7, 6, 7, 6, 8,
    6, 7, 6, 6, 7, 6, 7, 7, 8, 6, 7, 6, 6, 7, 6, 7, 6, 8,
    6, 7, 6,
)

# Function_822407D8 calls Function_821CEBA8(base=6, count=4,
# descriptor=0x820481C8). The descriptor entries are ordered as follows.
TILE_SET_TEXTURES = {
    6: "fence1_512.png",
    7: "fence2_512.png",
    8: "fence6_512a.png",
    9: "fence3_512.png",
}

# Every fence atlas is 1152x1152. The 49 shapes are row-major in a 7x7 table,
# on a 144-pixel pitch. Each logical sprite occupies a 96x96 source rectangle.
# The XEX renders at 3x coordinates, so 96 source pixels correspond to 32
# logical units, centered on a 30-unit MAP cell step.
ATLAS_LAYOUT = {
    "columns": 7,
    "rows": 7,
    "pitch_px": 144,
    "source_size_px": 96,
    "logical_sprite_units": 32,
    "map_cell_units": 30,
}
MAX_EMBEDDED_ATLAS_BYTES = 32 * 1024 * 1024


def _rle_bytes(data: bytes) -> list[list[int]]:
    if not data:
        return []
    result: list[list[int]] = []
    current = data[0]
    count = 1
    for value in data[1:]:
        if value == current:
            count += 1
        else:
            result.append([current, count])
            current = value
            count = 1
    result.append([current, count])
    return result


def _stage_media_root(input_path: Path) -> Path:
    # Xbox rips preserve ``Media`` while PS3 rips preserve the installed
    # ``USRDIR`` root. Prefer the canonical layouts, then accept any shallow
    # directory that owns a script/map pair so extracted/custom layouts work
    # without renaming platform-native folders.
    candidates = (
        input_path / "assets" / "Media",
        input_path / "assets" / "USRDIR",
        input_path / "Media",
        input_path / "USRDIR",
        input_path,
    )
    seen: set[Path] = set()
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError:
            continue
        if resolved in seen:
            continue
        seen.add(resolved)
        if (candidate / "script").is_dir() or (candidate / "map").is_dir():
            return candidate
    # Bounded fallback for users pointing at a parent directory rather than a
    # full-rip root. Only directory names that actually contain stage files
    # are accepted; generator/structured subtrees are not mistaken for the
    # main runtime stage table.
    for child in input_path.glob("*/*") if input_path.is_dir() else ():
        if not child.is_dir() or child.name.lower() in {"structured", "generator"}:
            continue
        script = child / "script"
        maps = child / "map"
        if (script.is_dir() and any(script.glob("*.dat"))) or (maps.is_dir() and any(maps.glob("*.map"))):
            return child
    raise toolkit.FormatError("could not find a stage script/map root below the supplied path")


def _png_dimensions(data: bytes) -> tuple[int, int]:
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise toolkit.FormatError("invalid PNG atlas")
    return struct.unpack(">II", data[16:24])


def _find_atlas_files(input_path: Path, media: Path) -> dict[int, Path]:
    names = {name.lower(): resource_id for resource_id, name in TILE_SET_TEXTURES.items()}
    found: dict[int, Path] = {}
    candidates = [
        media / "texture_map",
        input_path / "assets" / "Media" / "texture_map",
        input_path / "Media" / "texture_map",
        input_path / "texture_map",
    ]
    seen: set[Path] = set()
    for directory in candidates:
        try:
            resolved = directory.resolve()
        except OSError:
            continue
        if resolved in seen or not directory.is_dir():
            continue
        seen.add(resolved)
        for path in directory.iterdir():
            if path.is_file() and path.name.lower() in names:
                found.setdefault(names[path.name.lower()], path)
    # A shallowly different rip layout should still work. Restrict the fallback
    # to exact expected names so no unrelated image is embedded.
    if len(found) < 3 and input_path.is_dir():
        for path in input_path.rglob("*.png"):
            resource_id = names.get(path.name.lower())
            if resource_id is not None:
                found.setdefault(resource_id, path)
    return found


def _atlas_payload(input_path: Path, media: Path) -> dict[str, dict]:
    payload: dict[str, dict] = {}
    for resource_id, path in sorted(_find_atlas_files(input_path, media).items()):
        size = path.stat().st_size
        if size > MAX_EMBEDDED_ATLAS_BYTES:
            raise toolkit.FormatError(
                f"atlas {path.name} exceeds embedded-image limit "
                f"({size} > {MAX_EMBEDDED_ATLAS_BYTES} bytes)"
            )
        data = path.read_bytes()
        width, height = _png_dimensions(data)
        required = (ATLAS_LAYOUT["columns"] - 1) * ATLAS_LAYOUT["pitch_px"] + ATLAS_LAYOUT["source_size_px"]
        if width < required or height < required or width > 8192 or height > 8192:
            raise toolkit.FormatError(
                f"atlas {path.name} has unsupported dimensions {width}x{height}; "
                f"expected at least {required}x{required}"
            )
        payload[str(resource_id)] = {
            "resource_id": resource_id,
            "filename": path.name,
            "width": width,
            "height": height,
            "data_url": "data:image/png;base64," + base64.b64encode(data).decode("ascii"),
            **ATLAS_LAYOUT,
        }
    return payload


_STAGE_HTML_V5_PREFIX = '<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n<title>SIIG Stage Explorer</title>\n<style>\n:root{color-scheme:dark;background:#0d1017;color:#e7ebf3;font:14px system-ui,sans-serif}*{box-sizing:border-box}body{margin:0}\nheader{position:sticky;top:0;z-index:5;background:#121722;border-bottom:1px solid #2a3242;padding:12px 18px;display:flex;gap:14px;align-items:center;flex-wrap:wrap}\nh1{font-size:18px;margin:0 18px 0 0}.control{display:flex;gap:6px;align-items:center}select,input,button{background:#1a2130;color:#eef;border:1px solid #39445b;border-radius:6px;padding:6px 8px}button{cursor:pointer}\nmain{display:grid;grid-template-columns:minmax(360px,48%) 1fr;min-height:calc(100vh - 58px)}section{padding:16px;min-width:0}.maps{border-right:1px solid #2a3242;background:#0f131c}\n.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(90px,1fr));gap:8px;margin-bottom:12px}.card{background:#171d29;border:1px solid #283146;border-radius:8px;padding:9px}.card b{display:block;font-size:19px}.muted{color:#9ba7bd}\n.layer-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.layer{background:#171d29;border:1px solid #283146;border-radius:8px;overflow:hidden}.layer h3{font-size:13px;margin:0;padding:8px 10px;border-bottom:1px solid #283146}.canvas-wrap{height:56vh;overflow:auto;text-align:center;padding:8px;background:#07090d}.canvas-wrap canvas{image-rendering:pixelated;image-rendering:crisp-edges;transform-origin:top left;display:block;margin:0 auto}.legend{padding:8px;font-size:12px;white-space:pre-wrap;overflow-wrap:anywhere}\n.timeline-tools{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px}.table-wrap{overflow:auto;max-height:76vh;border:1px solid #283146;border-radius:8px}table{border-collapse:collapse;width:100%}th,td{padding:7px 8px;border-bottom:1px solid #222b3b;text-align:left;vertical-align:top}th{position:sticky;top:0;background:#171d29;z-index:1}.frame{font-variant-numeric:tabular-nums}.tag{display:inline-block;border-radius:999px;padding:2px 7px;background:#29344a;font-size:11px}.high{color:#8ee6a8}.medium{color:#f4d37c}.low{color:#e79898}.fields{font-family:ui-monospace,monospace;font-size:12px;color:#b9c5d9;white-space:normal}.files{margin:0 0 10px;line-height:1.5}.notice{background:#17271d;border:1px solid #315d40;padding:9px;border-radius:8px;margin-bottom:12px;color:#bfe8c9}.warning{background:#261f14;border-color:#5e4b25;color:#efd99e}.inspector{margin:10px 0;background:#111826;border:1px solid #2a3954;border-radius:8px;padding:9px;font-family:ui-monospace,monospace;min-height:38px}.check{display:flex;gap:5px;align-items:center}.check input{padding:0}.playback{display:flex;gap:7px;align-items:center;flex-wrap:wrap}.playback input[type=range]{width:220px}.runtime-status{font-family:ui-monospace,monospace;color:#b9c5d9}\n@media(max-width:1100px){main{display:block}.maps{border-right:0}.layer-grid{grid-template-columns:1fr}.canvas-wrap{height:48vh}}\n</style></head><body>\n<header><h1>SIIG Stage Explorer</h1><div class="control"><label>Stage</label><select id="stage"></select></div><div class="control"><label>Zoom</label><input id="zoom" type="range" min="50" max="500" value="150"><span id="zoomValue">1.5×</span></div><div class="control"><label>Map view</label><select id="mapMode"><option value="game">Game atlas tiles</option><option value="tile">Tile ID + flip shading</option><option value="raw">Raw byte</option><option value="base">Tile ID (1–49)</option><option value="flip">X/Y flip flags</option></select></div><label class="check"><input id="composite" type="checkbox" checked> zero-scroll composite</label><div class="playback"><button id="play">Play</button><button id="stepBack">−1</button><button id="stepForward">+1</button><input id="frame" type="range" min="0" max="0" value="0"><span id="frameValue" class="runtime-status">frame 0</span><select id="speed"><option value="0.25">0.25×</option><option value="0.5">0.5×</option><option value="1" selected>1×</option><option value="2">2×</option><option value="4">4×</option></select></div></header>\n<main><section class="maps"><div class="notice" id="notice"></div><div class="files muted" id="files"></div><div class="cards" id="cards"></div><div class="inspector" id="inspector">Click a rendered cell to inspect its raw value, tile ID, flips, and unscrolled game-space center. The runtime viewport uses SCROLL_01/02/03 as layer 0/1/2 X/Y velocity vectors.</div><div class="layer-grid" id="layers"></div></section>\n<section><div class="timeline-tools"><input id="search" placeholder="Search opcode, summary, or argument" size="34"><select id="category"><option value="">All categories</option></select><span class="muted" id="shown"></span></div><div class="table-wrap"><table><thead><tr><th>Frame</th><th>Command</th><th>Interpretation</th><th>Fields</th></tr></thead><tbody id="timeline"></tbody></table></div></section></main>\n<script id="data" type="application/json">'

_STAGE_HTML_V5_SUFFIX = '</script><script>\nconst DB=JSON.parse(document.getElementById(\'data\').textContent);\nconst stageSel=document.getElementById(\'stage\'),layersEl=document.getElementById(\'layers\'),timeline=document.getElementById(\'timeline\');\nconst search=document.getElementById(\'search\'),category=document.getElementById(\'category\'),zoom=document.getElementById(\'zoom\'),mapMode=document.getElementById(\'mapMode\'),composite=document.getElementById(\'composite\');\nconst inspector=document.getElementById(\'inspector\'),notice=document.getElementById(\'notice\'),zoomValue=document.getElementById(\'zoomValue\');\nconst play=document.getElementById(\'play\'),stepBack=document.getElementById(\'stepBack\'),stepForward=document.getElementById(\'stepForward\'),frameSlider=document.getElementById(\'frame\'),frameValue=document.getElementById(\'frameValue\'),speed=document.getElementById(\'speed\');\nconst atlasImages={},atlasPromises={};let runtimeView=null,playing=false,lastTick=0,frameCarry=0;\nfor(const [id,a] of Object.entries(DB.atlases||{})){const im=new Image();atlasImages[id]=im;atlasPromises[id]=new Promise((resolve,reject)=>{im.onload=()=>resolve(im);im.onerror=reject});im.src=a.data_url}\nfor(const s of DB.stages){const o=document.createElement(\'option\');o.value=s.name;o.textContent=s.display_name||s.name;stageSel.appendChild(o)}\nif(DB.default_stage)stageSel.value=DB.default_stage;\nconst cats=[...new Set(DB.stages.flatMap(s=>(s.script?.records||[]).map(r=>r.semantic.category)))].sort();for(const c of cats){const o=document.createElement(\'option\');o.value=c;o.textContent=c;category.appendChild(o)}\nfunction esc(v){return String(v??\'\').replace(/[&<>"\']/g,ch=>({\'&\':\'&amp;\',\'<\':\'&lt;\',\'>\':\'&gt;\',\'"\':\'&quot;\',"\'":\'&#39;\'}[ch]))}\nfunction unrle(rle,total){const a=new Uint8Array(total);let p=0;for(const [v,n] of rle){a.fill(v,p,p+n);p+=n}return a}\nfunction color(v,mode){if(v===0)return[4,6,10,255];const base=v&63,flags=v>>6;if(mode===\'flip\'){const cs=[[170,170,170],[80,180,255],[255,170,70],[220,90,220]];return[...cs[flags],255]}const id=mode===\'raw\'?v:base;const h=(id*47)%360,s=mode===\'tile\'?(flags===0?68:82):68,l=mode===\'tile\'?(42+flags*10):46,c=(1-Math.abs(2*l/100-1))*s/100,x=c*(1-Math.abs((h/60)%2-1)),m=l/100-c/2;let q=h<60?[c,x,0]:h<120?[x,c,0]:h<180?[0,c,x]:h<240?[0,x,c]:h<300?[x,0,c]:[c,0,x];return q.map(z=>Math.round((z+m)*255)).concat(255)}\nfunction renderStep(l){return Math.max(2,Math.min(15,Math.floor(16000/Math.max(1,l.height))))}\nfunction atlasFor(s){return DB.atlases?.[String(s.tile_set_id)]||null}\nfunction drawGameCells(ctx,l,cells,atlas,im,step,clear=true){if(clear){ctx.fillStyle=\'#05070a\';ctx.fillRect(0,0,l.width*step,l.height*step)}ctx.imageSmoothingEnabled=false;const dst=Math.max(2,Math.round(step*atlas.logical_sprite_units/atlas.map_cell_units));for(let p=0;p<cells.length;p++){const v=cells[p],id=v&63;if(!id)continue;const c=p%l.width,r=Math.floor(p/l.width),idx=id-1,sx=(idx%atlas.columns)*atlas.pitch_px,sy=Math.floor(idx/atlas.columns)*atlas.pitch_px;ctx.save();ctx.translate(c*step+step/2,r*step+step/2);ctx.scale((v&0x40)?-1:1,(v&0x80)?-1:1);ctx.drawImage(im,sx,sy,atlas.source_size_px,atlas.source_size_px,-dst/2,-dst/2,dst,dst);ctx.restore()}}\nfunction drawColorCells(ctx,l,cells,mode){const img=ctx.createImageData(l.width,l.height);for(let p=0;p<cells.length;p++)img.data.set(color(cells[p],mode),p*4);ctx.putImageData(img,0,0)}\nfunction drawColorComposite(ctx,w,h,ls,mode){const img=ctx.createImageData(w,h);for(let p=0;p<w*h;p++)img.data.set([5,7,10,255],p*4);for(const i of [2,1,0]){const l=ls[i];if(!l||!l.width||!l.height)continue;const cells=unrle(l.rle,l.width*l.height);for(let p=0;p<cells.length;p++){const v=cells[p];if(!v)continue;const c=p%l.width,r=Math.floor(p/l.width);img.data.set(color(v,mode),(r*w+c)*4)}}ctx.putImageData(img,0,0)}\nfunction attachInspector(can,l,cells,layerLabel,step){can.onclick=e=>{const rect=can.getBoundingClientRect(),x=(e.clientX-rect.left)*can.width/rect.width,y=(e.clientY-rect.top)*can.height/rect.height,col=Math.floor(x/step),row=Math.floor(y/step);if(col<0||row<0||col>=l.width||row>=l.height)return;const v=cells[row*l.width+col],id=v&63,flags=v>>6,flips=[\'none\',\'X\',\'Y\',\'X+Y\'][flags];inspector.textContent=`${layerLabel} · row ${row}, column ${col} · raw 0x${v.toString(16).padStart(2,\'0\').toUpperCase()} · tile ${id||\'empty\'} · flips ${flips} · center (${col*30+15}, ${row*30+15}) before layer scroll`}}\nasync function createLayerPanel(title,l,s,kind){const box=document.createElement(\'div\');box.className=\'layer\';box.innerHTML=`<h3>${title} · ${l.width}×${l.height}</h3><div class="canvas-wrap"><canvas></canvas></div><div class="legend"></div>`;layersEl.appendChild(box);const can=box.querySelector(\'canvas\'),leg=box.querySelector(\'.legend\');if(!l.width||!l.height){leg.textContent=\'Empty\';return}const cells=unrle(l.rle,l.width*l.height),atlas=atlasFor(s);let step=1;if(mapMode.value===\'game\'&&atlas&&atlasImages[String(s.tile_set_id)]){step=renderStep(l);can.width=l.width*step;can.height=l.height*step;const im=await atlasPromises[String(s.tile_set_id)];drawGameCells(can.getContext(\'2d\'),l,cells,atlas,im,step)}else{can.width=l.width;can.height=l.height;drawColorCells(can.getContext(\'2d\'),l,cells,mapMode.value===\'game\'?\'tile\':mapMode.value)}const z=Number(zoom.value)/100;can.style.width=`${can.width*z}px`;can.style.height=`${can.height*z}px`;attachInspector(can,l,cells,title,step);const vals=Object.entries(l.value_counts).sort((a,b)=>Number(a[0])-Number(b[0])),ids=Object.entries(l.base_id_counts||{}).sort((a,b)=>Number(a[0])-Number(b[0])),fl=l.flip_counts||{};leg.textContent=`nonzero ${l.nonzero_cells}/${l.cell_count} · flips none:${fl[\'0\']||0} X:${fl[\'1\']||0} Y:${fl[\'2\']||0} XY:${fl[\'3\']||0}\\ntile IDs: `+ids.map(([v,n])=>`${v}:${n}`).join(\' \')+`\\nraw: `+vals.map(([v,n])=>`${Number(v).toString(16).padStart(2,\'0\').toUpperCase()}:${n}`).join(\' \')}\nfunction scrollStateAt(s,targetFrame){const state=[{x:0,y:0,vx:0,vy:0},{x:0,y:0,vx:0,vy:0},{x:0,y:0,vx:0,vy:0}];let last=0;for(const e of (s.script?.scroll_events||[])){const stop=Math.min(targetFrame,e.frame),dt=stop-last;if(dt>0){for(const q of state){q.x+=q.vx*dt;q.y+=q.vy*dt}last=stop}if(e.frame>targetFrame)break;const q=state[e.layer];q.vx=e.x;q.vy=e.y}if(targetFrame>last){const dt=targetFrame-last;for(const q of state){q.x+=q.vx*dt;q.y+=q.vy*dt}}return state}\nfunction runtimeStatus(state,f){return `frame ${f} · `+state.map((q,i)=>`L${i} pos(${(q.x/256).toFixed(1)},${(q.y/256).toFixed(1)}) vel(${(q.vx/256).toFixed(2)},${(q.vy/256).toFixed(2)})`).join(\' · \')}\nasync function drawRuntimeViewport(){if(!runtimeView)return;const {can,ctx,s,ls,atlas,im,step}=runtimeView,f=Number(frameSlider.value),state=scrollStateAt(s,f),vw=16,vh=9;ctx.fillStyle=\'#05070a\';ctx.fillRect(0,0,can.width,can.height);for(const i of [2,1,0]){const l=ls[i],q=state[i];if(!l||!l.width||!l.height)continue;const cells=unrle(l.rle,l.width*l.height),ox=q.x/256/30,oy=q.y/256/30;for(let p=0;p<cells.length;p++){const v=cells[p],id=v&63;if(!id)continue;const col=p%l.width,row=Math.floor(p/l.width),dx=Math.round((col+ox)*step),dy=Math.round((row+oy)*step);if(dx<-step||dy<-step||dx>=vw*step||dy>=vh*step)continue;if(mapMode.value===\'game\'&&atlas&&im){const idx=id-1,sx=(idx%atlas.columns)*atlas.pitch_px,sy=Math.floor(idx/atlas.columns)*atlas.pitch_px,dst=Math.max(2,Math.round(step*atlas.logical_sprite_units/atlas.map_cell_units));ctx.save();ctx.translate(dx+step/2,dy+step/2);ctx.scale((v&0x40)?-1:1,(v&0x80)?-1:1);ctx.drawImage(im,sx,sy,atlas.source_size_px,atlas.source_size_px,-dst/2,-dst/2,dst,dst);ctx.restore()}else{ctx.fillStyle=`rgba(${color(v,mapMode.value===\'game\'?\'tile\':mapMode.value).slice(0,3).join(\',\')},1)`;ctx.fillRect(Math.floor(dx),Math.floor(dy),Math.ceil(step),Math.ceil(step))}}}frameValue.textContent=runtimeStatus(state,f)}\nasync function createRuntimeViewport(s,ls){if(!s.script?.scroll_events?.length||!ls.some(l=>l&&l.width&&l.height))return;const box=document.createElement(\'div\');box.className=\'layer\';box.innerHTML=`<h3>Runtime scroll viewport · 16×9 cells</h3><div class="canvas-wrap"><canvas></canvas></div><div class="legend">SCROLL_01/02/03 set the X/Y velocity of layers 0/1/2. Positions are integrated at the reference timebase; the engine applies its runtime time-scale divisor before accumulation.</div>`;layersEl.appendChild(box);const can=box.querySelector(\'canvas\'),ctx=can.getContext(\'2d\'),atlas=atlasFor(s),step=30;can.width=16*step;can.height=9*step;let im=null;if(atlas&&atlasImages[String(s.tile_set_id)])im=await atlasPromises[String(s.tile_set_id)];runtimeView={can,ctx,s,ls,atlas,im,step};const z=Math.min(1,Number(zoom.value)/100);can.style.width=`${can.width*z}px`;can.style.height=`${can.height*z}px`;await drawRuntimeViewport()}\nasync function createComposite(s,ls){if(!composite.checked)return;const live=ls.filter(l=>l&&l.width&&l.height);if(!live.length)return;const w=Math.max(...live.map(l=>l.width)),h=Math.max(...live.map(l=>l.height)),synthetic={width:w,height:h};const box=document.createElement(\'div\');box.className=\'layer\';box.innerHTML=`<h3>Zero-scroll composite · ${w}×${h}</h3><div class="canvas-wrap"><canvas></canvas></div><div class="legend">Draw order 2 → 1 → 0. Runtime per-layer scroll offsets are not applied.</div>`;layersEl.appendChild(box);const can=box.querySelector(\'canvas\'),atlas=atlasFor(s);let step=1;if(mapMode.value===\'game\'&&atlas&&atlasImages[String(s.tile_set_id)]){step=renderStep(synthetic);can.width=w*step;can.height=h*step;const ctx=can.getContext(\'2d\'),im=await atlasPromises[String(s.tile_set_id)];ctx.fillStyle=\'#05070a\';ctx.fillRect(0,0,can.width,can.height);for(const i of [2,1,0]){const l=ls[i];if(!l||!l.width||!l.height)continue;drawGameCells(ctx,l,unrle(l.rle,l.width*l.height),atlas,im,step,false)}}else{can.width=w;can.height=h;drawColorComposite(can.getContext(\'2d\'),w,h,ls,mapMode.value===\'game\'?\'tile\':mapMode.value)}{const z=Number(zoom.value)/100;can.style.width=`${can.width*z}px`;can.style.height=`${can.height*z}px`}}\nasync function drawMaps(s){layersEl.innerHTML=\'\';runtimeView=null;const ls=s.map?.layers||[];await createRuntimeViewport(s,ls);await createComposite(s,ls);for(let i=0;i<3;i++)await createLayerPanel(`Layer ${i}`,ls[i]||{width:0,height:0,rle:[],value_counts:{}},s,\'layer\')}\nfunction renderTimeline(s){const q=search.value.toLowerCase(),cat=category.value,all=s.script?.records||[],rs=all.filter(r=>(!cat||r.semantic.category===cat)&&(!q||JSON.stringify(r).toLowerCase().includes(q)));timeline.innerHTML=\'\';for(const r of rs){const tr=document.createElement(\'tr\'),fs=r.semantic.fields.map(f=>`${f.name}=${f.value}${f.unit?\' \'+f.unit:\'\'}`).join(\' · \');tr.innerHTML=`<td class="frame">${r.absolute_frame}</td><td><b>${esc(r.opcode_name)}</b><br><span class="tag">${esc(r.semantic.category)}</span> <span class="${esc(r.semantic.confidence)}">${esc(r.semantic.confidence)}</span></td><td>${esc(r.semantic.summary)}</td><td class="fields">${esc(fs||\'—\')}<br><span class="muted">raw ${esc(r.args_signed.join(\' \'))}</span></td>`;timeline.appendChild(tr)}document.getElementById(\'shown\').textContent=`${rs.length}/${all.length} commands`}\nasync function render(){const s=DB.stages.find(x=>x.name===stageSel.value)||DB.stages[0],rec=s.script?.records||[],map=s.map,atlas=atlasFor(s);playing=false;play.textContent=\'Play\';frameSlider.max=String(s.script?.duration_frames||0);frameSlider.value=\'0\';notice.className=\'notice\'+(atlas?\'\':\' warning\');notice.textContent=atlas?`Verified atlas rendering: resource ${s.tile_set_id} → ${atlas.filename}; tile IDs 1–49 use the 7×7 atlas and 0x40/0x80 are applied as X/Y reflections. SCROLL_01/02/03 are decoded as layer 0/1/2 X/Y velocities.`:`No verified PNG atlas is embedded for this entry. The explorer is using the categorical tile fallback; MAP bytes remain exact.`;document.getElementById(\'files\').innerHTML=`<b>${esc(s.display_name||s.name)}</b><br>kind: ${esc(s.entry_kind||\'asset\')} · script: ${esc(s.script_file||\'—\')}${s.script_missing?\' (missing)\':\'\'} · map: ${esc(s.map_file||\'—\')}${s.map_missing?\' (missing)\':\'\'} · tile set: ${s.tile_set_id??\'—\'}${s.tile_set_texture?\' → \'+esc(s.tile_set_texture):\'\'}`;document.getElementById(\'cards\').innerHTML=`<div class="card"><span class="muted">Commands</span><b>${rec.length}</b></div><div class="card"><span class="muted">Duration</span><b>${s.script?.duration_frames||0}</b><small> frames</small></div><div class="card"><span class="muted">MAP cells</span><b>${(map?.layers||[]).reduce((a,l)=>a+l.cell_count,0)}</b></div><div class="card"><span class="muted">Nonzero</span><b>${(map?.layers||[]).reduce((a,l)=>a+l.nonzero_cells,0)}</b></div><div class="card"><span class="muted">Tile set</span><b>${s.tile_set_id??\'—\'}</b><small>${s.tile_set_texture||\' resource ID\'}</small></div>`;await drawMaps(s);renderTimeline(s)}\nfunction updateZoom(){zoomValue.textContent=(Number(zoom.value)/100).toFixed(2).replace(/0+$/,\'\').replace(/\\.$/,\'\')+\'×\';document.querySelectorAll(\'canvas\').forEach(c=>{const z=Number(zoom.value)/100;c.style.width=`${c.width*z}px`;c.style.height=`${c.height*z}px`})}\nfunction animate(ts){if(!playing)return;if(!lastTick)lastTick=ts;const elapsed=(ts-lastTick)/1000*30*Number(speed.value)+frameCarry;const whole=Math.floor(elapsed);frameCarry=elapsed-whole;lastTick=ts;if(whole>0){const max=Number(frameSlider.max),next=Math.min(max,Number(frameSlider.value)+whole);frameSlider.value=String(next);drawRuntimeViewport();if(next>=max){playing=false;play.textContent=\'Play\';return}}requestAnimationFrame(animate)}\nplay.onclick=()=>{playing=!playing;play.textContent=playing?\'Pause\':\'Play\';lastTick=0;frameCarry=0;if(playing)requestAnimationFrame(animate)};stepBack.onclick=()=>{frameSlider.value=String(Math.max(0,Number(frameSlider.value)-1));drawRuntimeViewport()};stepForward.onclick=()=>{frameSlider.value=String(Math.min(Number(frameSlider.max),Number(frameSlider.value)+1));drawRuntimeViewport()};frameSlider.oninput=drawRuntimeViewport;stageSel.onchange=render;search.oninput=render;category.onchange=render;mapMode.onchange=render;composite.onchange=render;zoom.oninput=updateZoom;updateZoom();render();\n</script></body></html>'

# V6 keeps the verified V5 tile renderer but changes presentation defaults and
# adds an executable-backed level 4/5 route/placement inspection panel.
_STAGE_HTML_V6_PREFIX = (_STAGE_HTML_V5_PREFIX
    .replace('.canvas-wrap{height:56vh;overflow:auto;', '.canvas-wrap{min-height:220px;max-height:62vh;overflow:auto;')
    .replace('<label>Zoom</label><input id="zoom" type="range" min="50" max="500" value="150"><span id="zoomValue">1.5×</span>', '<label>Preview size</label><input id="zoom" type="range" min="25" max="250" value="100"><span id="zoomValue">1×</span><label class="check"><input id="fitPreview" type="checkbox" checked> fit panel</label>')
    .replace('<input id="composite" type="checkbox" checked> zero-scroll composite', '<input id="composite" type="checkbox"> overlay all MAP layers')
)

_STAGE3D_JS = r'''const STAGE3D_BOX_EDGES=[[0,1],[0,2],[0,4],[1,3],[1,5],[2,3],[2,6],[3,7],[4,5],[4,6],[5,7],[6,7]];
function stage3dProject(point,center,yaw,pitch){let x=point[0]-center[0],y=point[1]-center[1],z=point[2]-center[2];const cy=Math.cos(yaw),sy=Math.sin(yaw),cp=Math.cos(pitch),sp=Math.sin(pitch);const x1=x*cy-z*sy,z1=x*sy+z*cy;const y1=y*cp-z1*sp,z2=y*sp+z1*cp;return[x1,y1,z2]}
function stage3dProxyCorners(p){const o=p.position_preview;if(p.model_proxy_corners?.length===8)return p.model_proxy_corners;if(!p.model_aabb)return [[o[0]-20,o[1]-20,o[2]-20],[o[0]+20,o[1]-20,o[2]-20],[o[0]-20,o[1]+20,o[2]-20],[o[0]+20,o[1]+20,o[2]-20],[o[0]-20,o[1]-20,o[2]+20],[o[0]+20,o[1]-20,o[2]+20],[o[0]-20,o[1]+20,o[2]+20],[o[0]+20,o[1]+20,o[2]+20]];return []}
function stage3dPlacementText(p){const pos=(p.position_preview||[]).map(v=>Number(v).toFixed(2)).join(', '),local=(p.position_local||[]).map(v=>Number(v).toFixed(2)).join(', '),scale=(p.runtime_scale||[]).map(v=>Number(v).toFixed(3)).join(', '),rot=(p.rotation_degrees||[]).map(v=>Number(v).toFixed(2)).join(', ');const b=p.model_aabb?` · GMX AABB min(${p.model_aabb.min.map(v=>Number(v).toFixed(2)).join(', ')}) max(${p.model_aabb.max.map(v=>Number(v).toFixed(2)).join(', ')})`:' · GMX AABB unavailable';return `${p.model_file||p.model} · record ${p.record} slot ${p.slot} · world-preview (${pos}) · local (${local}) · runtime scale (${scale}) · stored rotation° (${rot})${b}`}
function stage3dNorm(v){const n=Math.hypot(v[0],v[1],v[2])||1;return[v[0]/n,v[1]/n,v[2]/n]}
function stage3dCross(a,b){return[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]}
function stage3dDot(a,b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]}
function stage3dRouteState(route,progress){if(!route.length)return{index:0,t:0,pos:[0,0,0],forward:[0,0,-1]};if(route.length===1)return{index:0,t:0,pos:route[0],forward:[0,0,-1]};const f=Math.max(0,Math.min(1,progress))*Math.max(0,route.length-1),i=Math.min(route.length-2,Math.max(0,Math.floor(f))),t=Math.max(0,Math.min(1,f-i)),a=route[i]||route[0],b=route[Math.min(route.length-1,i+1)]||a,pos=[a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,a[2]+(b[2]-a[2])*t],forward=stage3dNorm([b[0]-a[0],b[1]-a[1],b[2]-a[2]]);return{index:i,t,pos,forward}}
function stage3dTintBackground(ctx,can,data){const hint=data.background_hint||{};ctx.fillStyle=hint.base_color||'#07090d';ctx.fillRect(0,0,can.width,can.height);if(hint.kind==='gradient'){const g=ctx.createLinearGradient(0,0,0,can.height);g.addColorStop(0,hint.top_color||'#3a3d44');g.addColorStop(1,hint.bottom_color||'#080a0e');ctx.fillStyle=g;ctx.fillRect(0,0,can.width,can.height)}else if(hint.kind==='grid'||hint.kind==='fog_grid'){ctx.strokeStyle=hint.grid_color||'rgba(80,130,255,.22)';ctx.lineWidth=1;const gap=32;for(let x=-can.height;x<can.width+can.height;x+=gap){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x+can.height,can.height);ctx.stroke()}if(hint.kind==='fog_grid'){const fog=ctx.createRadialGradient(can.width*.5,can.height*.5,10,can.width*.5,can.height*.5,Math.max(can.width,can.height)*.7);fog.addColorStop(0,'rgba(255,255,255,.16)');fog.addColorStop(1,'rgba(255,255,255,0)');ctx.fillStyle=fog;ctx.fillRect(0,0,can.width,can.height)}}else if(hint.kind==='crosshair'){ctx.strokeStyle=hint.grid_color||'rgba(80,150,255,.34)';ctx.lineWidth=1;for(let x=can.width*.15;x<can.width;x+=can.width*.22){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,can.height);ctx.stroke()}for(let y=can.height*.15;y<can.height;y+=can.height*.22){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(can.width,y);ctx.stroke()}}}
function stage3dModelColor(name){let h=0;for(const ch of name)h=(h*33+ch.charCodeAt(0))%360;return h}
function drawStage3DOrbit(can,data,yaw,pitch,scopeStart=0,scopeEnd=null){const ctx=can.getContext('2d'),route=data.route||[],placements=(data.placements||[]).filter(p=>p.record>=scopeStart&&(scopeEnd===null||p.record<=scopeEnd)),routeSlice=route.slice(scopeStart,scopeEnd===null?undefined:Math.min(route.length,scopeEnd+2)),proxyCorners=placements.map(stage3dProxyCorners);stage3dTintBackground(ctx,can,data);const pts=routeSlice.concat(placements.map(p=>p.position_preview)).concat(proxyCorners.flat());if(!pts.length){ctx.fillStyle='#9ba7bd';ctx.fillText('No 3D layout points',16,28);return}const center=[0,0,0];for(const p of pts){center[0]+=p[0];center[1]+=p[1];center[2]+=p[2]}center[0]/=pts.length;center[1]/=pts.length;center[2]/=pts.length;const projected=pts.map(p=>stage3dProject(p,center,yaw,pitch));let minX=Math.min(...projected.map(p=>p[0])),maxX=Math.max(...projected.map(p=>p[0])),minY=Math.min(...projected.map(p=>p[1])),maxY=Math.max(...projected.map(p=>p[1]));const spanX=Math.max(1,maxX-minX),spanY=Math.max(1,maxY-minY),pad=28,scale=Math.min((can.width-pad*2)/spanX,(can.height-pad*2)/spanY);const toScreen=p=>{const q=stage3dProject(p,center,yaw,pitch);return[pad+(q[0]-minX)*scale,can.height-pad-(q[1]-minY)*scale,q[2]]};if(routeSlice.length>1){ctx.strokeStyle='#8ea5d6';ctx.lineWidth=2;ctx.beginPath();routeSlice.forEach((p,i)=>{const q=toScreen(p);if(i)ctx.lineTo(q[0],q[1]);else ctx.moveTo(q[0],q[1])});ctx.stroke()}const drawn=placements.map((p,i)=>({p,corners:proxyCorners[i].map(toScreen),q:toScreen(p.position_preview)})).sort((a,b)=>a.q[2]-b.q[2]);can._stage3dHits=[];for(const item of drawn){const h=stage3dModelColor(item.p.model);ctx.strokeStyle=`hsl(${h} 58% 62%)`;ctx.lineWidth=1;ctx.globalAlpha=item.p.model_aabb?0.72:0.35;for(const [a,b] of STAGE3D_BOX_EDGES){const p0=item.corners[a],p1=item.corners[b];ctx.beginPath();ctx.moveTo(p0[0],p0[1]);ctx.lineTo(p1[0],p1[1]);ctx.stroke()}ctx.globalAlpha=1;ctx.fillStyle=`hsl(${h} 68% 68%)`;ctx.beginPath();ctx.arc(item.q[0],item.q[1],3.5,0,Math.PI*2);ctx.fill();can._stage3dHits.push({x:item.q[0],y:item.q[1],p:item.p})}ctx.fillStyle='#e7ebf3';ctx.font='12px system-ui';ctx.fillText(`route cells ${data.record_count} · visible placements ${placements.length} · GMX bounds ${data.model_bounds_count||0}`,12,18)}
function drawStage3DTopDown(can,data,progress,finalOnly=false){const ctx=can.getContext('2d'),route=data.route||[],state=stage3dRouteState(route,progress),radius=finalOnly?Math.max(8,Math.min(24,Math.ceil(route.length*.035))):8,start=finalOnly?Math.max(0,route.length-1-radius):Math.max(0,state.index-radius),end=finalOnly?route.length-1:Math.min(route.length-1,state.index+radius),placements=(data.placements||[]).filter(p=>p.record>=start&&p.record<=end),visible=route.slice(start,end+1),proxyCorners=placements.map(stage3dProxyCorners);stage3dTintBackground(ctx,can,data);const pts=visible.concat(placements.map(p=>p.position_preview)).concat(proxyCorners.flat());if(!pts.length)return;let minX=Math.min(...pts.map(p=>p[0])),maxX=Math.max(...pts.map(p=>p[0])),minZ=Math.min(...pts.map(p=>p[2])),maxZ=Math.max(...pts.map(p=>p[2]));const pad=34,spanX=Math.max(800,maxX-minX),spanZ=Math.max(800,maxZ-minZ),scale=Math.min((can.width-pad*2)/spanX,(can.height-pad*2)/spanZ),cx=(minX+maxX)/2,cz=(minZ+maxZ)/2,toScreen=p=>[can.width/2+(p[0]-cx)*scale,can.height/2+(p[2]-cz)*scale];ctx.strokeStyle='#8ea5d6';ctx.lineWidth=3;ctx.beginPath();visible.forEach((p,i)=>{const q=toScreen(p);if(i)ctx.lineTo(q[0],q[1]);else ctx.moveTo(q[0],q[1])});ctx.stroke();can._stage3dHits=[];for(let i=0;i<placements.length;i++){const p=placements[i],q=toScreen(p.position_preview),h=stage3dModelColor(p.model),corners=proxyCorners[i].map(toScreen);ctx.strokeStyle=`hsl(${h} 58% 62%)`;ctx.lineWidth=1;ctx.globalAlpha=p.model_aabb?0.72:0.35;for(const [a,b] of STAGE3D_BOX_EDGES){const p0=corners[a],p1=corners[b];ctx.beginPath();ctx.moveTo(p0[0],p0[1]);ctx.lineTo(p1[0],p1[1]);ctx.stroke()}ctx.globalAlpha=1;ctx.fillStyle=`hsl(${h} 68% 68%)`;ctx.fillRect(q[0]-2,q[1]-2,4,4);can._stage3dHits.push({x:q[0],y:q[1],p})}const here=toScreen(state.pos);ctx.fillStyle='#fff';ctx.beginPath();ctx.arc(here[0],here[1],5,0,Math.PI*2);ctx.fill();ctx.fillStyle='#e7ebf3';ctx.font='12px system-ui';ctx.fillText(`${finalOnly?'final-route arena window':'top-down route-follow'} · cell ${state.index}/${Math.max(0,route.length-1)} · visible records ${start}–${end}`,12,18)}
function drawStage3DPOV(can,data,progress,finalOnly=false){const ctx=can.getContext('2d'),route=data.route||[],state=stage3dRouteState(route,finalOnly?1:progress),start=finalOnly?Math.max(0,route.length-16):Math.max(0,state.index-2),end=finalOnly?route.length-1:Math.min(route.length-1,state.index+18),placements=(data.placements||[]).filter(p=>p.record>=start&&p.record<=end),upSeed=Math.abs(state.forward[1])>.92?[1,0,0]:[0,1,0],right=stage3dNorm(stage3dCross(state.forward,upSeed)),up=stage3dNorm(stage3dCross(right,state.forward)),eye=[state.pos[0]-state.forward[0]*120+up[0]*100,state.pos[1]-state.forward[1]*120+up[1]*100,state.pos[2]-state.forward[2]*120+up[2]*100],focal=can.width*.72;stage3dTintBackground(ctx,can,data);function project(p){const rel=[p[0]-eye[0],p[1]-eye[1],p[2]-eye[2]],d=stage3dDot(rel,state.forward);if(d<=8)return null;return[can.width/2+stage3dDot(rel,right)*focal/d,can.height/2-stage3dDot(rel,up)*focal/d,d]}const routeVisible=route.slice(start,end+1);ctx.strokeStyle='#8ea5d6';ctx.lineWidth=2;ctx.beginPath();let started=false;for(const p of routeVisible){const q=project(p);if(!q)continue;if(started)ctx.lineTo(q[0],q[1]);else{ctx.moveTo(q[0],q[1]);started=true}}if(started)ctx.stroke();const drawn=[];for(const p of placements){const q=project(p.position_preview);if(q)drawn.push({p,q,corners:stage3dProxyCorners(p).map(project)})}drawn.sort((a,b)=>b.q[2]-a.q[2]);can._stage3dHits=[];for(const item of drawn){const h=stage3dModelColor(item.p.model);ctx.strokeStyle=`hsl(${h} 58% 62%)`;ctx.lineWidth=1;ctx.globalAlpha=item.p.model_aabb?0.72:0.35;for(const [a,b] of STAGE3D_BOX_EDGES){const p0=item.corners[a],p1=item.corners[b];if(!p0||!p1)continue;ctx.beginPath();ctx.moveTo(p0[0],p0[1]);ctx.lineTo(p1[0],p1[1]);ctx.stroke()}ctx.globalAlpha=1;ctx.fillStyle=`hsl(${h} 68% 68%)`;ctx.fillRect(item.q[0]-2,item.q[1]-2,4,4);can._stage3dHits.push({x:item.q[0],y:item.q[1],p:item.p})}ctx.strokeStyle='rgba(255,255,255,.45)';ctx.beginPath();ctx.moveTo(can.width/2-8,can.height/2);ctx.lineTo(can.width/2+8,can.height/2);ctx.moveTo(can.width/2,can.height/2-8);ctx.lineTo(can.width/2,can.height/2+8);ctx.stroke();ctx.fillStyle='#e7ebf3';ctx.font='12px system-ui';ctx.fillText(`${finalOnly?'final-route POV':'route-follow POV'} · cell ${state.index}/${Math.max(0,route.length-1)} · records ${start}–${end}`,12,18)}
function createStage3DPreview(s){const data=s.stage3d;if(!data)return;const box=document.createElement('div');box.className='layer';const defaultMode=data.recommended_view||'orbit';box.innerHTML=`<h3>3D stage route viewer · ${esc(data.source_file)}</h3><div class="canvas-wrap"><canvas width="760" height="430"></canvas></div><div class="legend"><div class="control" style="flex-wrap:wrap"><label>View</label><select class="view3d"><option value="orbit">Whole-route orbit</option><option value="topdown">Top-down route follow</option><option value="pov">Route-follow POV</option><option value="final">Final arena window</option></select><label>Route progress</label><input class="routeProgress" type="range" min="0" max="1000" value="0" style="width:220px"><span class="routeProgressText">0%</span><span class="orbitControls"><label>Yaw</label><input class="yaw" type="range" min="-180" max="180" value="35"><label>Pitch</label><input class="pitch" type="range" min="-85" max="85" value="28"></span><button type="button" class="reset3d">Reset view</button></div><br><b>Stage 4 defaults to a local top-down scrolling view; Stage 5 defaults to a forward route-follow POV.</b> Both are inspection cameras driven by the recovered 0x118 route cells, not claims of a byte-identical gameplay camera. “Final arena window” isolates the tail of the recovered route as a boss-area inspection aid. Wire boxes use GMX root AABBs with recovered runtime scale and the native S × Rz × Rx × Ry × T placement transform; stored rotations remain inspectable in degrees.</div>`;layersEl.appendChild(box);const can=box.querySelector('canvas'),view=box.querySelector('.view3d'),progress=box.querySelector('.routeProgress'),progressText=box.querySelector('.routeProgressText'),yaw=box.querySelector('.yaw'),pitch=box.querySelector('.pitch'),orbitControls=box.querySelector('.orbitControls');view.value=defaultMode;const redraw=()=>{const p=Number(progress.value)/1000,mode=view.value;progressText.textContent=`${(p*100).toFixed(1)}% · cell ${Math.round(p*Math.max(0,(data.route||[]).length-1))}/${Math.max(0,(data.route||[]).length-1)}`;orbitControls.style.display=mode==='orbit'?'inline-flex':'none';if(mode==='topdown')drawStage3DTopDown(can,data,p,false);else if(mode==='pov')drawStage3DPOV(can,data,p,false);else if(mode==='final'){progress.value='1000';progressText.textContent=`100% · final route tail`;drawStage3DTopDown(can,data,1,true)}else drawStage3DOrbit(can,data,Number(yaw.value)*Math.PI/180,Number(pitch.value)*Math.PI/180);sizeCanvas(can)};can.onclick=e=>{const r=can.getBoundingClientRect(),x=(e.clientX-r.left)*can.width/r.width,y=(e.clientY-r.top)*can.height/r.height;let best=null,dist=Infinity;for(const hit of can._stage3dHits||[]){const d=Math.hypot(hit.x-x,hit.y-y);if(d<dist){dist=d;best=hit}}if(best&&dist<=18)inspector.textContent=stage3dPlacementText(best.p)};for(const el of [view,progress,yaw,pitch])el.oninput=redraw;box.querySelector('.reset3d').onclick=()=>{view.value=defaultMode;progress.value='0';yaw.value='35';pitch.value='28';redraw()};redraw()}
'''

_STAGE_HTML_V6_SUFFIX = _STAGE_HTML_V5_SUFFIX
_STAGE_HTML_V6_SUFFIX = _STAGE_HTML_V6_SUFFIX.replace(
    "const search=document.getElementById('search'),category=document.getElementById('category'),zoom=document.getElementById('zoom'),mapMode=document.getElementById('mapMode'),composite=document.getElementById('composite');",
    "const search=document.getElementById('search'),category=document.getElementById('category'),zoom=document.getElementById('zoom'),fitPreview=document.getElementById('fitPreview'),mapMode=document.getElementById('mapMode'),composite=document.getElementById('composite');"
)
_STAGE_HTML_V6_SUFFIX = _STAGE_HTML_V6_SUFFIX.replace(
    "function renderStep(l){return Math.max(2,Math.min(15,Math.floor(16000/Math.max(1,l.height))))}",
    "function renderStep(l){return Math.max(2,Math.min(15,Math.floor(16000/Math.max(1,l.height))))}\nfunction sizeCanvas(c){const requested=Number(zoom.value)/100;let z=requested;if(fitPreview.checked&&c.parentElement){const avail=Math.max(80,c.parentElement.clientWidth-18);z=Math.min(requested,avail/Math.max(1,c.width))}c.style.width=`${Math.max(1,c.width*z)}px`;c.style.height=`${Math.max(1,c.height*z)}px`}"
)
_STAGE_HTML_V6_SUFFIX = _STAGE_HTML_V6_SUFFIX.replace("const z=Number(zoom.value)/100;can.style.width=`${can.width*z}px`;can.style.height=`${can.height*z}px`;attachInspector", "sizeCanvas(can);attachInspector")
_STAGE_HTML_V6_SUFFIX = _STAGE_HTML_V6_SUFFIX.replace("const z=Math.min(1,Number(zoom.value)/100);can.style.width=`${can.width*z}px`;can.style.height=`${can.height*z}px`;await drawRuntimeViewport()", "sizeCanvas(can);await drawRuntimeViewport()")
_STAGE_HTML_V6_SUFFIX = _STAGE_HTML_V6_SUFFIX.replace("{const z=Number(zoom.value)/100;can.style.width=`${can.width*z}px`;can.style.height=`${can.height*z}px`}}", "{sizeCanvas(can)}}")
_STAGE_HTML_V6_SUFFIX = _STAGE_HTML_V6_SUFFIX.replace(
    "async function drawMaps(s){layersEl.innerHTML='';runtimeView=null;const ls=s.map?.layers||[];await createRuntimeViewport(s,ls);await createComposite(s,ls);for(let i=0;i<3;i++)await createLayerPanel(`Layer ${i}`,ls[i]||{width:0,height:0,rle:[],value_counts:{}},s,'layer')}",
    _STAGE3D_JS + "\nasync function drawMaps(s){layersEl.innerHTML='';runtimeView=null;const ls=s.map?.layers||[];createStage3DPreview(s);await createRuntimeViewport(s,ls);await createComposite(s,ls);for(let i=0;i<3;i++)await createLayerPanel(`Layer ${i}`,ls[i]||{width:0,height:0,rle:[],value_counts:{}},s,'layer')}"
)
_STAGE_HTML_V6_SUFFIX = _STAGE_HTML_V6_SUFFIX.replace(
    "notice.textContent=atlas?`Verified atlas rendering: resource ${s.tile_set_id} → ${atlas.filename}; tile IDs 1–49 use the 7×7 atlas and 0x40/0x80 are applied as X/Y reflections. SCROLL_01/02/03 are decoded as layer 0/1/2 X/Y velocities.`:",
    "notice.textContent=atlas?`Verified atlas rendering: resource ${s.tile_set_id} → ${atlas.filename}; tile IDs 1–49 use the 7×7 atlas and 0x40/0x80 are applied as X/Y reflections. Individual layers are shown separately by default; the all-layer overlay is optional because transparent layers can look visually dense. SCROLL_01/02/03 are decoded as layer 0/1/2 X/Y velocities.`:"
)
_STAGE_HTML_V6_SUFFIX = _STAGE_HTML_V6_SUFFIX.replace(
    "function updateZoom(){zoomValue.textContent=(Number(zoom.value)/100).toFixed(2).replace(/0+$/,'').replace(/\\.$/,'')+'×';document.querySelectorAll('canvas').forEach(c=>{const z=Number(zoom.value)/100;c.style.width=`${c.width*z}px`;c.style.height=`${c.height*z}px`})}",
    "function updateZoom(){zoomValue.textContent=(Number(zoom.value)/100).toFixed(2).replace(/0+$/,'').replace(/\\.$/,'')+'×'+(fitPreview.checked?' · fit':'');document.querySelectorAll('canvas').forEach(sizeCanvas)}"
)
_STAGE_HTML_V6_SUFFIX = _STAGE_HTML_V6_SUFFIX.replace("zoom.oninput=updateZoom;updateZoom();render();", "zoom.oninput=updateZoom;fitPreview.onchange=updateZoom;window.addEventListener('resize',updateZoom);updateZoom();render();")


# V6 tile inspection keeps full atlas detail available even when a very long
# layer overview has to be reduced to fit the panel.
_attach_start = _STAGE_HTML_V6_SUFFIX.index("function attachInspector")
_attach_end = _STAGE_HTML_V6_SUFFIX.index("async function createLayerPanel", _attach_start)
_attach_v6 = r'''function attachInspector(can,l,cells,layerLabel,step,s){can.onclick=async e=>{const rect=can.getBoundingClientRect(),x=(e.clientX-rect.left)*can.width/rect.width,y=(e.clientY-rect.top)*can.height/rect.height,col=Math.floor(x/step),row=Math.floor(y/step);if(col<0||row<0||col>=l.width||row>=l.height)return;const v=cells[row*l.width+col],id=v&63,flags=v>>6,flips=['none','X','Y','X+Y'][flags],atlas=atlasFor(s),nativeSize=atlas?.source_size_px||96;inspector.innerHTML=`<div>${layerLabel} · row ${row}, column ${col} · raw 0x${v.toString(16).padStart(2,'0').toUpperCase()} · tile ${id||'empty'} · flips ${flips} · center (${col*30+15}, ${row*30+15}) before layer scroll</div><div style="margin-top:7px;display:flex;gap:12px;align-items:flex-start;flex-wrap:wrap"><div><div class="muted" style="margin-bottom:4px">Native tile ${nativeSize}×${nativeSize} px (1:1)</div><canvas id="tileDetail" width="${nativeSize}" height="${nativeSize}" style="width:${nativeSize}px;height:${nativeSize}px;image-rendering:pixelated;max-width:100%"></canvas></div><div><div class="muted" style="margin-bottom:4px">Pixel-inspection magnifier</div><canvas id="tileDetailZoom" width="192" height="192" style="width:192px;height:192px;image-rendering:pixelated;max-width:100%"></canvas></div></div>`;const detail=document.getElementById('tileDetail'),zoomDetail=document.getElementById('tileDetailZoom'),dctx=detail.getContext('2d'),zctx=zoomDetail.getContext('2d');for(const [ctx,w,h] of [[dctx,nativeSize,nativeSize],[zctx,192,192]]){ctx.fillStyle='#05070a';ctx.fillRect(0,0,w,h);ctx.imageSmoothingEnabled=false}if(id&&atlas&&atlasImages[String(s.tile_set_id)]){const im=await atlasPromises[String(s.tile_set_id)],idx=id-1,sx=(idx%atlas.columns)*atlas.pitch_px,sy=Math.floor(idx/atlas.columns)*atlas.pitch_px;const draw=(ctx,size)=>{ctx.save();ctx.translate(size/2,size/2);ctx.scale((v&0x40)?-1:1,(v&0x80)?-1:1);ctx.drawImage(im,sx,sy,atlas.source_size_px,atlas.source_size_px,-size/2,-size/2,size,size);ctx.restore()};draw(dctx,nativeSize);draw(zctx,192)}else{for(const [ctx,size] of [[dctx,nativeSize],[zctx,192]]){ctx.fillStyle='#9ba7bd';ctx.font='12px system-ui';ctx.fillText(id?'atlas unavailable':'empty cell',8,size/2)}}}}
'''
_STAGE_HTML_V6_SUFFIX = _STAGE_HTML_V6_SUFFIX[:_attach_start] + _attach_v6 + _STAGE_HTML_V6_SUFFIX[_attach_end:]
_STAGE_HTML_V6_SUFFIX = _STAGE_HTML_V6_SUFFIX.replace("attachInspector(can,l,cells,title,step);", "attachInspector(can,l,cells,title,step,s);")
_STAGE_HTML_V6_SUFFIX = _STAGE_HTML_V6_SUFFIX.replace(
    "ctx.fillStyle='#05070a';ctx.fillRect(0,0,can.width,can.height);for(const i of [2,1,0])",
    "stage3dTintBackground(ctx,can,s);for(const i of [2,1,0])"
)
_STAGE_HTML_V6_SUFFIX = _STAGE_HTML_V6_SUFFIX.replace(
    "<div class=\"card\"><span class=\"muted\">Tile set</span><b>${s.tile_set_id??'—'}</b><small>${s.tile_set_texture||' resource ID'}</small></div>`",
    "<div class=\"card\"><span class=\"muted\">Tile set</span><b>${s.tile_set_id??'—'}</b><small>${s.tile_set_texture||' resource ID'}</small></div><div class=\"card\"><span class=\"muted\">Background ref</span><b style=\"font-size:13px\">${esc(s.background_hint?.label||'Neutral')}</b><small>${esc(s.background_hint?.provenance||'')}</small></div><div class=\"card\"><span class=\"muted\">Boss background refs</span><b style=\"font-size:13px\">${(s.boss_background_hints||[]).length?esc((s.boss_background_hints||[]).map(x=>`${x.boss} @ ${x.frame}`).join(' · ')):'—'}</b><small>${(s.boss_background_hints||[]).length?esc((s.boss_background_hints||[]).map(x=>x.label).join(' · ')):'DAT-backed encounter frames + separate gameplay-reference visuals'}</small></div>`"
)

# V8 deliberately reclassifies the browser surface as a proof-of-concept
# research inspector.  The decoded MAP/DAT data remains useful, but the host
# presentation does not reproduce the complete gameplay renderer or execute
# the full stage script.  Experimental motion/route previews are therefore
# visually and semantically subordinate to the exact static inspection views.
_STAGE_HTML_V8_PREFIX = (_STAGE_HTML_V6_PREFIX
    .replace('<title>SIIG Stage Explorer</title>', '<title>SIIG Stage Explorer — Proof of Concept</title>')
    .replace('<header><h1>SIIG Stage Explorer</h1>', '<header><h1>SIIG Stage Explorer <span class="tag">proof of concept</span></h1>')
    .replace('<button id="play">Play</button>', '<button id="play">Preview motion</button>')
    .replace('<span id="frameValue" class="runtime-status">frame 0</span>', '<span id="frameValue" class="runtime-status">SCROLL frame 0</span>')
    .replace('<main><section class="maps"><div class="notice" id="notice"></div>', '<main><section class="maps"><div class="notice warning"><b>Proof of concept / research inspector.</b> Static MAP cells and decoded DAT records are the strongest part of this tool. The motion and 3D panels are approximate inspection previews, not faithful gameplay playback or a frame-accurate map viewer.</div><div class="notice" id="notice"></div>')
)
_STAGE_HTML_V8_SUFFIX = _STAGE_HTML_V6_SUFFIX
_STAGE_HTML_V8_SUFFIX = _STAGE_HTML_V8_SUFFIX.replace(
    '<h3>Runtime scroll viewport · 16×9 cells</h3>',
    '<h3>Experimental SCROLL preview · 16×9 cells</h3>'
)
_STAGE_HTML_V8_SUFFIX = _STAGE_HTML_V8_SUFFIX.replace(
    'SCROLL_01/02/03 set the X/Y velocity of layers 0/1/2. Positions are integrated at the reference timebase; the engine applies its runtime time-scale divisor before accumulation.',
    'SCROLL_01/02/03 set the X/Y velocity of layers 0/1/2. This preview integrates only those recovered scroll vectors. It does not execute the rest of the stage DAT, reproduce the native renderer/camera, or claim gameplay-accurate sequencing.'
)
_STAGE_HTML_V8_SUFFIX = _STAGE_HTML_V8_SUFFIX.replace(
    '<h3>3D stage route viewer · ${esc(data.source_file)}</h3>',
    '<h3>Experimental 3D route / placement inspector · ${esc(data.source_file)}</h3>'
)
_STAGE_HTML_V8_SUFFIX = _STAGE_HTML_V8_SUFFIX.replace(
    '<b>Stage 4 defaults to a local top-down scrolling view; Stage 5 defaults to a forward route-follow POV.</b> Both are inspection cameras driven by the recovered 0x118 route cells, not claims of a byte-identical gameplay camera.',
    '<b>Proof-of-concept 3D inspection only.</b> Stage 4 defaults to a local top-down view and Stage 5 to a forward route-follow POV. These cameras visualize recovered 0x118 route/placement data; they are not a reconstruction of the gameplay camera or stage sequence.'
)
_STAGE_HTML_V8_SUFFIX = _STAGE_HTML_V8_SUFFIX.replace(
    "async function drawMaps(s){layersEl.innerHTML='';runtimeView=null;const ls=s.map?.layers||[];createStage3DPreview(s);await createRuntimeViewport(s,ls);await createComposite(s,ls);for(let i=0;i<3;i++)await createLayerPanel(`Layer ${i}`,ls[i]||{width:0,height:0,rle:[],value_counts:{}},s,'layer')}",
    "async function drawMaps(s){layersEl.innerHTML='';runtimeView=null;const ls=s.map?.layers||[];for(let i=0;i<3;i++)await createLayerPanel(`Layer ${i} · decoded MAP data`,ls[i]||{width:0,height:0,rle:[],value_counts:{}},s,'layer');await createComposite(s,ls);await createRuntimeViewport(s,ls);createStage3DPreview(s)}"
)
_STAGE_HTML_V8_SUFFIX = _STAGE_HTML_V8_SUFFIX.replace(
    '<div class="card"><span class="muted">Duration</span><b>${s.script?.duration_frames||0}</b><small> frames</small></div>',
    '<div class="card"><span class="muted">Script span</span><b>${s.script?.duration_frames||0}</b><small> decoded frames</small></div>'
)
_STAGE_HTML_V8_SUFFIX = _STAGE_HTML_V8_SUFFIX.replace(
    "function runtimeStatus(state,f){return `frame ${f} · `+state.map((q,i)=>`L${i} pos(${(q.x/256).toFixed(1)},${(q.y/256).toFixed(1)}) vel(${(q.vx/256).toFixed(2)},${(q.vy/256).toFixed(2)})`).join(' · ')}",
    "function runtimeStatus(state,f){return `SCROLL frame ${f} · `+state.map((q,i)=>`L${i} pos(${(q.x/256).toFixed(1)},${(q.y/256).toFixed(1)}) vel(${(q.vx/256).toFixed(2)},${(q.vy/256).toFixed(2)})`).join(' · ')}"
)
_STAGE_HTML_V8_SUFFIX = _STAGE_HTML_V8_SUFFIX.replace(
    "frameSlider.max=String(s.script?.duration_frames||0);frameSlider.value='0';notice.className=",
    "frameSlider.max=String(s.script?.duration_frames||0);frameSlider.value='0';const hasMotion=!!s.script?.scroll_events?.length;for(const el of [play,stepBack,stepForward,frameSlider,speed])el.disabled=!hasMotion;frameValue.textContent=hasMotion?'SCROLL frame 0':'no recovered SCROLL preview';notice.className="
)
_STAGE_HTML_V8_SUFFIX = _STAGE_HTML_V8_SUFFIX.replace("play.textContent='Play'", "play.textContent='Preview motion'")
_STAGE_HTML_V8_SUFFIX = _STAGE_HTML_V8_SUFFIX.replace("play.textContent=playing?'Pause':'Play'", "play.textContent=playing?'Pause preview':'Preview motion'")
_STAGE_HTML_V8_SUFFIX = _STAGE_HTML_V8_SUFFIX.replace(
    "stageSel.onchange=render;search.oninput=render;category.onchange=render;mapMode.onchange=render;composite.onchange=render;zoom.oninput=updateZoom;",
    "const currentStage=()=>DB.stages.find(x=>x.name===stageSel.value)||DB.stages[0];stageSel.onchange=render;search.oninput=()=>renderTimeline(currentStage());category.onchange=()=>renderTimeline(currentStage());mapMode.onchange=render;composite.onchange=render;zoom.oninput=updateZoom;"
)


def _html(dataset: dict) -> str:
    payload = json.dumps(dataset, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return _STAGE_HTML_V8_PREFIX + payload + _STAGE_HTML_V8_SUFFIX


def _load_pairing() -> list[dict[str, str]]:
    toolkit_dir = Path(__file__).resolve().parent
    candidates = (
        toolkit_dir / "reference" / "tables" / "STAGE_PAIRING.csv",
        toolkit_dir / "STAGE_PAIRING.csv",  # legacy v2.5.0-and-earlier layout
    )
    path = next((candidate for candidate in candidates if candidate.is_file()), None)
    if path is None:
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))

def _script_payload(path: Path) -> dict:
    parsed = toolkit.parse_dat_bytes(path.read_bytes())
    records = [{
        "index": record["index"],
        "absolute_frame": record["absolute_frame"],
        "opcode": record["opcode"],
        "opcode_name": record["opcode_name"],
        "args_signed": record["args_signed"],
        "semantic": record["semantic"],
    } for record in parsed["records"]]
    layer_by_name = {"SCROLL_01": 0, "SCROLL_02": 1, "SCROLL_03": 2}
    scroll_events = []
    for record in records:
        layer = layer_by_name.get(record["opcode_name"])
        args = record["args_signed"]
        if layer is None or len(args) < 2:
            continue
        scroll_events.append({
            "frame": record["absolute_frame"],
            "layer": layer,
            "x": args[0],
            "y": args[1],
        })
    return {
        "entry_count": parsed["entry_count"],
        "duration_frames": parsed["duration_frames"],
        "records": records,
        "scroll_events": scroll_events,
    }


def _map_payload(path: Path) -> dict:
    parsed = toolkit.parse_map_bytes(path.read_bytes())
    return {
        "layer_count": parsed["layer_count"],
        "layers": [{
            "index": layer["index"],
            "width": layer["width"],
            "height": layer["height"],
            "cell_count": layer["cell_count"],
            "nonzero_cells": layer["nonzero_cells"],
            "unique_values": layer["unique_values"],
            "value_counts": {str(int(key, 16)): value for key, value in layer["value_counts"].items()},
            "base_id_counts": {str(key): value for key, value in sorted(Counter(cell & 0x3F for cell in layer["cells"] if cell).items())},
            "flip_counts": {str(key): value for key, value in sorted(Counter(cell >> 6 for cell in layer["cells"] if cell).items())},
            "rle": _rle_bytes(layer["cells"]),
        } for layer in parsed["layers"]],
    }



def _gmx_name_index(input_path: Path) -> dict[str, Path]:
    """Index extracted GMX files by basename for lightweight 3D stage proxies."""
    assets_root = input_path / "assets"
    # A normal rip keeps every extracted GMX below assets/.  Avoid walking the
    # entire rip a second time when that canonical root exists; fall back to
    # input_path only for hand-picked/minimal test folders.
    roots = [assets_root] if assets_root.is_dir() else [input_path]
    result: dict[str, Path] = {}
    seen: set[Path] = set()
    for root in roots:
        try:
            resolved = root.resolve()
        except OSError:
            continue
        if resolved in seen or not root.is_dir():
            continue
        seen.add(resolved)
        try:
            for path in root.rglob("*.gmx"):
                result.setdefault(path.name.lower(), path)
        except OSError:
            continue
    return result


def _gmx_root_aabb(path: Path) -> dict | None:
    """Read only the proven GMX root AABB; no mesh decode is required."""
    try:
        with path.open("rb") as handle:
            raw = handle.read(0x30)
        if len(raw) < 0x30 or raw[:4] != toolkit.GMX_MAGIC:
            return None
        values = struct.unpack_from(">6f", raw, 0x10)
        if not all(math.isfinite(value) for value in values):
            return None
        minimum = [float(value) for value in values[:3]]
        maximum = [float(value) for value in values[3:]]
        if any(maximum[i] < minimum[i] for i in range(3)):
            return None
        return {
            "min": minimum,
            "max": maximum,
            "size": [maximum[i] - minimum[i] for i in range(3)],
        }
    except (OSError, struct.error):
        return None



BOSS_BACKGROUND_REFERENCES = {
    "THE_MOON": {
        "kind": "grid", "base_color": "#000000", "grid_color": "rgba(90,140,255,.30)",
        "label": "THE MOON · World 2-style blue grid",
        "detail": "Project-owner gameplay reference: reuses the World 2-style grid presentation.",
    },
    "THE_SUN": {
        "kind": "dual_grid", "base_color": "#000000", "grid_color": "rgba(80,135,255,.38)",
        "label": "THE SUN · black + top/bottom blue grids",
        "detail": "Project-owner gameplay reference: black field with blue grid planes above and below.",
    },
    "GIGANTIC_UFO": {
        "kind": "lower_grid", "base_color": "#000000", "grid_color": "rgba(80,135,255,.38)",
        "label": "GIGANTIC UFO · black + lower blue grid",
        "detail": "Project-owner gameplay reference: THE SUN-like presentation without the top grid plane.",
    },
    "LADYBUG": {
        "kind": "trapezoid_phase", "base_color": "#000000", "grid_color": "rgba(80,170,255,.48)",
        "label": "LADYBUG · blue trapezoids → black",
        "detail": "Project-owner gameplay reference: glowing blue trapezoids in phase 1, then black in phase 2; transition timing is not inferred here.",
    },
    "MANDALA": {
        "kind": "circle_rings", "base_color": "#000000", "grid_color": "rgba(70,145,255,.42)",
        "label": "MANDALA · expanding blue circle outlines",
        "detail": "Project-owner gameplay reference: blue circle outlines grow outward from the center; exact timing is not reconstructed here.",
    },
    "UNKNOWN": {
        "kind": "radial_lines", "base_color": "#000000", "grid_color": "rgba(105,150,255,.38)",
        "label": "UNKNOWN · spinning radial-line reference",
        "detail": "Project-owner gameplay reference: spinning radial lines; exact angular speed/timing is not reconstructed here.",
    },
}


def _boss_background_hints(script_payload: dict | None) -> list[dict]:
    """Attach owner-observed boss-background references to executable-backed DAT spawns.

    The encounter name/frame comes from decoded DAT.  The visual description remains a
    clearly separate project-owner gameplay reference and is never promoted to runtime
    background-renderer evidence.
    """
    result: list[dict] = []
    if not script_payload:
        return result
    for record in script_payload.get("records", []):
        name = str(record.get("opcode_name", "")).upper()
        ref = BOSS_BACKGROUND_REFERENCES.get(name)
        if ref is None:
            continue
        item = dict(ref)
        item.update({
            "boss": name,
            "frame": int(record.get("absolute_frame", 0)),
            "provenance": "boss/frame from decoded DAT; visual description from project-owner gameplay reference",
        })
        result.append(item)
    return result


def _stage3d_transform_point(
    point: list[float] | tuple[float, float, float],
    runtime_scale: list[float] | tuple[float, float, float],
    rotation_degrees: list[float] | tuple[float, float, float],
    origin: list[float] | tuple[float, float, float],
) -> list[float]:
    """Apply the recovered native stage-placement transform to one point.

    Retail Xbox 360 and PS3 stage placement use the same row-vector order:
    ``S * Rz(z) * Rx(x) * Ry(y) * T``.  The 0x118 stage record stores
    rotation in degrees; scale has already been expanded to the runtime
    ``stored_scale * 5`` values before reaching this helper.
    """
    x, y, z = (float(point[i]) * float(runtime_scale[i]) for i in range(3))
    rx, ry, rz = (math.radians(float(v)) for v in rotation_degrees)

    # Row-vector Rz.
    cz, sz = math.cos(rz), math.sin(rz)
    x, y = x * cz - y * sz, x * sz + y * cz
    # Row-vector Rx.
    cx, sx = math.cos(rx), math.sin(rx)
    y, z = y * cx - z * sx, y * sx + z * cx
    # Row-vector Ry.
    cy, sy = math.cos(ry), math.sin(ry)
    x, z = x * cy + z * sy, -x * sy + z * cy

    return [x + float(origin[0]), y + float(origin[1]), z + float(origin[2])]


def _stage3d_proxy_corners(
    aabb: dict | None,
    runtime_scale: list[float] | tuple[float, float, float],
    rotation_degrees: list[float] | tuple[float, float, float],
    origin: list[float] | tuple[float, float, float],
) -> list[list[float]]:
    """Return the eight native-transform corners for a GMX root AABB."""
    if not aabb:
        return []
    lo, hi = aabb.get("min"), aabb.get("max")
    if not isinstance(lo, list) or not isinstance(hi, list) or len(lo) != 3 or len(hi) != 3:
        return []
    return [
        _stage3d_transform_point([x, y, z], runtime_scale, rotation_degrees, origin)
        for z in (lo[2], hi[2])
        for y in (lo[1], hi[1])
        for x in (lo[0], hi[0])
    ]


def _stage_background_hint(script_file: str) -> dict:
    """Return a display-only background reference from project-owner gameplay observations.

    These hints intentionally remain separate from executable-backed MAP/DAT semantics.
    They make the Stage Explorer resemble the observed game presentation without claiming
    that the background renderer itself has been reconstructed byte-for-byte.
    """
    name = Path(script_file or "").name.lower()
    match = re.fullmatch(r"level([1-5])_stage([1-6])\.dat", name)
    neutral = {
        "kind": "solid",
        "base_color": "#05070a",
        "label": "Neutral",
        "provenance": "toolkit neutral fallback",
    }
    if not match:
        return neutral
    world, stage = int(match.group(1)), int(match.group(2))
    owner = "project-owner gameplay reference; display-only, not executable-derived"
    if world == 1:
        if stage == 6:
            return {"kind": "solid", "base_color": "#000000", "label": "World 1-6 black", "provenance": owner}
        return {
            "kind": "gradient", "base_color": "#20242a", "top_color": "#5b6068", "bottom_color": "#101319",
            "label": "World 1 gray gradient", "provenance": owner,
        }
    if world == 2:
        return {
            "kind": "grid", "base_color": "#000000", "grid_color": "rgba(90,140,255,.30)",
            "label": "World 2 fast diagonal grid" + (" / side-plane reference" if stage == 6 else ""), "provenance": owner,
        }
    if world == 3:
        if stage == 1:
            return {"kind": "solid", "base_color": "#3b080d", "label": "World 3-1 red", "provenance": owner}
        if stage == 2:
            return {"kind": "solid", "base_color": "#082f16", "label": "World 3-2 green", "provenance": owner}
        if stage == 3:
            return {"kind": "grid", "base_color": "#000000", "grid_color": "rgba(50,110,255,.34)", "label": "World 3-3 black + blue grid", "provenance": owner}
        if stage == 4:
            return {"kind": "solid", "base_color": "#28113e", "label": "World 3-4 purple", "provenance": owner}
        if stage == 5:
            return {"kind": "solid", "base_color": "#35383d", "label": "World 3-5 gray", "provenance": owner}
        return {"kind": "crosshair", "base_color": "#050a18", "grid_color": "rgba(80,150,255,.34)", "label": "World 3-6 blue crosshair reference", "provenance": owner}
    if world == 4:
        palette = {
            1: "#3b080d", 2: "#082f16", 3: "#050a18", 4: "#28113e", 5: "#35383d", 6: "#050a18",
        }
        return {
            "kind": "visualizer_hint", "base_color": palette[stage],
            "label": f"World 4 visualizer reference · World 3 palette slot {stage}", "provenance": owner,
        }
    if world == 5 and stage == 6:
        return {
            "kind": "fog_grid", "base_color": "#101216", "grid_color": "rgba(240,245,255,.42)",
            "label": "World 5-6 white bulging-grid / fog reference", "provenance": owner,
        }
    return {
        "kind": "visualizer_hint", "base_color": "#080b12",
        "label": "World 5 mixed gradient / visualizer reference", "provenance": owner,
    }

def _stage3d_payload(media: Path, script_file: str, gmx_index: dict[str, Path] | None = None) -> dict | None:
    """Return a compact executable-backed layout preview for main level 4/5 stages."""
    match = re.fullmatch(r"level([45])_stage([1-6])\.dat", Path(script_file).name, flags=re.IGNORECASE)
    if not match:
        return None
    stage_path = media / "3ddata" / "stage" / f"map{match.group(1)}_{match.group(2)}.bin"
    if not stage_path.is_file():
        return None
    parsed = toolkit.parse_stage3d_map_bytes(stage_path.read_bytes(), source_name=stage_path.name)
    records = parsed["records"]
    route = []
    if records:
        route.append(records[0]["path_start"])
        route.extend(record["path_end"] for record in records)
    placements = []
    for record in records:
        center = record["cell_center"]
        for placement in record["placements"]:
            if not placement["used"]:
                continue
            local = placement["position"]
            preview = [float(center[i]) + float(local[i]) for i in range(3)]
            model_file = placement["model_file"]
            model_path = (gmx_index or {}).get(model_file.lower())
            aabb = _gmx_root_aabb(model_path) if model_path else None
            runtime_scale = [float(v) for v in placement["runtime_scale"]]
            rotation_degrees = [float(v) for v in placement["rotation_degrees"]]
            proxy_corners = _stage3d_proxy_corners(aabb, runtime_scale, rotation_degrees, preview)
            placements.append({
                "record": record["index"],
                "slot": placement["slot"],
                "model": placement["model_name"],
                "model_file": model_file,
                "model_asset_found": bool(model_path),
                "model_aabb": aabb,
                "model_proxy_corners": proxy_corners,
                "position_local": [float(v) for v in local],
                "position_preview": preview,
                "runtime_scale": runtime_scale,
                "rotation_degrees": rotation_degrees,
            })
    world = int(match.group(1))
    stage_index = int(match.group(2))
    background_hint = _stage_background_hint(script_file)
    return {
        "source_file": stage_path.name,
        "stage_kind": parsed["stage_kind"],
        "world": world,
        "stage_index": stage_index,
        "recommended_view": "topdown" if world == 4 else "pov",
        "background_hint": background_hint,
        "record_count": parsed["active_records"],
        "route": route,
        "placements": placements,
        "placement_count": len(placements),
        "model_asset_count": sum(1 for placement in placements if placement.get("model_asset_found")),
        "model_bounds_count": sum(1 for placement in placements if placement.get("model_aabb")),
        "preview_position_rule": "cell_center + stored placement position (inspection layout only)",
        "model_proxy_rule": "GMX root AABB transformed with native row-vector S * Rz(z) * Rx(x) * Ry(y) * T using recovered runtime_scale, stored degree rotations, and the recovered placement origin",
        "model_proxy_transform_order": "S * Rz(z) * Rx(x) * Ry(y) * T",
        "textured_meshes": False,
    }

def build_stage_explorer(input_path: Path, output: Path) -> dict:
    media = _stage_media_root(input_path)
    script_dir, map_dir = media / "script", media / "map"
    script_paths = {path.name.lower(): path for path in script_dir.glob("*.dat")} if script_dir.is_dir() else {}
    map_paths = {path.name.lower(): path for path in map_dir.glob("*.map")} if map_dir.is_dir() else {}
    if not script_paths and not map_paths:
        raise toolkit.FormatError("no stage DAT or MAP files were found")

    atlases = _atlas_payload(input_path, media)
    gmx_index = _gmx_name_index(input_path)
    pairing = _load_pairing()
    stages: list[dict] = []
    referenced_scripts: set[str] = set()
    referenced_maps: set[str] = set()

    if pairing:
        for row_index, row in enumerate(pairing):
            stage_no = int(row["stage_no"])
            variant = row["variant"]
            script_file = row["script_file"]
            map_file = row["map_file"]
            script_path = script_paths.get(script_file.lower()) if script_file else None
            map_path = map_paths.get(map_file.lower()) if map_file else None
            if script_file:
                referenced_scripts.add(script_file.lower())
            if map_file:
                referenced_maps.add(map_file.lower())
            stem = Path(script_file or map_file).stem
            if row["entry_kind"] == "runtime_stage":
                display = f"Stage {stage_no:03d} · {stem}"
                name = f"stage_{stage_no:03d}_{stem}"
            elif row["entry_kind"] == "trial_variant":
                display = f"Trial variant · {stem} (stage {stage_no:03d})"
                name = f"trial_stage_{stage_no:03d}_{stem}"
            else:
                display = f"Map-only slot {stage_no:03d} · {stem}"
                name = f"map_slot_{stage_no:03d}_{stem}"
            tile_set_id = STAGE_TILE_SET_IDS[stage_no - 1] if 1 <= stage_no <= len(STAGE_TILE_SET_IDS) else None
            item: dict = {
                "name": name,
                "display_name": display,
                "entry_kind": row["entry_kind"],
                "stage_no": stage_no,
                "variant": variant,
                "script_file": script_file,
                "map_file": map_file,
                "evidence": row["evidence"],
                "script_missing": bool(script_file and not script_path),
                "map_missing": bool(map_file and not map_path),
                "pairing_index": row_index,
                "tile_set_id": tile_set_id,
                "tile_set_texture": TILE_SET_TEXTURES.get(tile_set_id, "") if tile_set_id is not None else "",
                "background_hint": _stage_background_hint(script_file),
            }
            if script_path:
                item["script"] = _script_payload(script_path)
                item["boss_background_hints"] = _boss_background_hints(item["script"])
                stage3d = _stage3d_payload(media, script_file, gmx_index)
                if stage3d:
                    item["stage3d"] = stage3d
            if map_path:
                item["map"] = _map_payload(map_path)
            stages.append(item)
    else:
        names = sorted(set(Path(key).stem for key in script_paths) | set(Path(key).stem for key in map_paths), key=str.lower)
        for name in names:
            script_path = script_paths.get((name + ".dat").lower())
            map_path = map_paths.get((name + ".map").lower())
            item: dict = {
                "name": name,
                "display_name": name,
                "entry_kind": "fallback_stem_pair",
                "script_file": script_path.name if script_path else "",
                "map_file": map_path.name if map_path else "",
                "tile_set_id": None,
                "tile_set_texture": "",
                "background_hint": _stage_background_hint(script_path.name if script_path else ""),
            }
            if script_path:
                item["script"] = _script_payload(script_path)
                item["boss_background_hints"] = _boss_background_hints(item["script"])
                stage3d = _stage3d_payload(media, script_path.name, gmx_index)
                if stage3d:
                    item["stage3d"] = stage3d
            if map_path:
                item["map"] = _map_payload(map_path)
            stages.append(item)

    for map_key in sorted(set(map_paths) - referenced_maps):
        map_path = map_paths[map_key]
        stem = map_path.stem
        stages.append({
            "name": f"unreferenced_map_{stem}",
            "display_name": f"Unreferenced package MAP · {stem}",
            "entry_kind": "unreferenced_package_map",
            "stage_no": None,
            "variant": "unreferenced",
            "script_file": "",
            "map_file": map_path.name,
            "evidence": "present in map BBX but absent from the June 10 runtime map-slot table",
            "tile_set_id": None,
            "tile_set_texture": "",
            "map": _map_payload(map_path),
        })

    for script_key in sorted(set(script_paths) - referenced_scripts):
        script_path = script_paths[script_key]
        stem = script_path.stem
        stages.append({
            "name": f"unreferenced_script_{stem}",
            "display_name": f"Unreferenced package DAT · {stem}",
            "entry_kind": "unreferenced_package_script",
            "stage_no": None,
            "variant": "unreferenced",
            "script_file": script_path.name,
            "map_file": "",
            "evidence": "present in script BBX but absent from the June 10 runtime script table",
            "tile_set_id": None,
            "tile_set_texture": "",
            "background_hint": _stage_background_hint(script_path.name),
            "script": _script_payload(script_path),
        })
        stages[-1]["boss_background_hints"] = _boss_background_hints(stages[-1]["script"])

    dataset = {
        "format": "SIIG_STAGE_EXPLORER",
        "version": STAGE_EXPLORER_VERSION,
        "source": media.name,
        "maturity": "proof_of_concept",
        "fidelity": "research_inspector_not_gameplay_renderer",
        "stage_count": len(stages),
        "runtime_pair_count": len(pairing),
        "default_stage": next((stage["name"] for stage in stages if sum(layer["cell_count"] for layer in stage.get("map", {}).get("layers", [])) > 0 and stage.get("script")), stages[0]["name"]),
        "atlases": atlases,
        "atlas_layout": ATLAS_LAYOUT,
        "tile_set_textures": {str(key): value for key, value in TILE_SET_TEXTURES.items()},
        "stages": stages,
        "notes": {
            "pairing": "June 10 runtime map slots and script slots are paired by executable table index",
            "missing_maps": "some expected normal level 4/5 MAP files are absent from the package; the loader tolerates this",
            "unreferenced_maps": "package MAP files absent from the runtime table are shown separately",
            "map_layers": "three independently scrolling 2D tile/sprite layers; SCROLL_01/02/03 set layer 0/1/2 X/Y velocities",
            "map_cell": "0 is empty; lower six bits are one-based tile IDs 1..49",
            "map_flips": "0x40 is X reflection; 0x80 is Y reflection",
            "map_cell_size": "30 units; renderer places tile centers at cell*30+15 plus scroll offset",
            "tile_set_mapping": "resource IDs 6, 7, 8, 9 map to fence1, fence2, fence6, fence3 through the 0x820481C8 registration descriptor",
            "atlas_layout": "49 row-major shapes in a 7x7 table; 144-pixel pitch and 96-pixel source rectangles",
            "composite": "the optional static composite uses draw order 2,1,0 at zero scroll; it is off by default because overlaying all three transparent layers can look visually dense",
            "preview_sizing": "previews fit their panel by default and retain a manual scale control without requiring horizontal scrolling",
            "motion_preview": "experimental host-side SCROLL_01/02/03 integration only; it does not execute the full DAT sequence or reproduce native renderer/camera timing",
            "sprite_presentation": "browser atlas presentation is an inspection aid; converted TEX pixels, CSS scaling and host canvas sampling are not claimed pixel-identical to native output",
            "background_reference": "World 1-5 background hints are project-owner gameplay observations used only as display presets; they are explicitly separate from executable-backed MAP/DAT semantics",
            "stage3d_preview": "main level 4/5 stages show executable-backed route/placement data with local route-follow views: level 4 defaults to top-down scrolling, level 5 to POV; the inspection camera is not claimed byte-identical to gameplay; GMX-root AABB proxies use the recovered native S * Rz(z) * Rx(x) * Ry(y) * T placement transform",
            "not_wall_geometry": "Media/map and Media/generator MAP files do not place 3D wall GMX models",
            "semantic_policy": "XEX-backed fields are named; unresolved words remain generic",
        },
    }
    output.mkdir(parents=True, exist_ok=True)
    toolkit.write_text_atomic(output / "SIIG_Stage_Explorer.html", _html(dataset), encoding="utf-8")
    manifest = {
        "format": dataset["format"],
        "version": dataset["version"],
        "stage_count": dataset["stage_count"],
        "entry_count": dataset["stage_count"],
        "runtime_pair_count": dataset["runtime_pair_count"],
        "embedded_atlases": [{
            "resource_id": int(resource_id),
            "filename": atlas["filename"],
            "width": atlas["width"],
            "height": atlas["height"],
        } for resource_id, atlas in sorted(atlases.items(), key=lambda item: int(item[0]))],
        "stages": [{
            "name": stage["name"],
            "display_name": stage["display_name"],
            "entry_kind": stage["entry_kind"],
            "stage_no": stage.get("stage_no"),
            "script_file": stage.get("script_file", ""),
            "map_file": stage.get("map_file", ""),
            "script_missing": stage.get("script_missing", False),
            "map_missing": stage.get("map_missing", False),
            "commands": stage.get("script", {}).get("entry_count", 0),
            "duration_frames": stage.get("script", {}).get("duration_frames", 0),
            "map_layers": stage.get("map", {}).get("layer_count", 0),
            "map_cells": sum(layer["cell_count"] for layer in stage.get("map", {}).get("layers", [])),
            "map_nonzero": sum(layer["nonzero_cells"] for layer in stage.get("map", {}).get("layers", [])),
            "tile_set_id": stage.get("tile_set_id"),
            "tile_set_texture": stage.get("tile_set_texture", ""),
            "background_reference": stage.get("background_hint", {}).get("label", ""),
            "background_reference_provenance": stage.get("background_hint", {}).get("provenance", ""),
            "boss_background_references": [{
                "boss": ref.get("boss", ""),
                "frame": ref.get("frame", 0),
                "label": ref.get("label", ""),
                "provenance": ref.get("provenance", ""),
            } for ref in stage.get("boss_background_hints", [])],
            "evidence": stage.get("evidence", ""),
        } for stage in stages],
        "notes": dataset["notes"],
    }
    toolkit.write_json_private(output / "STAGE_MANIFEST.json", manifest)
    toolkit.write_text_atomic(
        output / "README.txt",
        "Open SIIG_Stage_Explorer.html in a modern browser.\n"
        "The file is self-contained and makes no network requests.\n"
        "Runtime DAT/MAP pairing follows the June 10 XEX tables by stage index.\n"
        "Game-atlas mode embeds verified fence atlases when their converted PNG files are present.\n"
        "MAP cells are 2D tile/sprite data: 0 empty, IDs 1-49, 0x40 X flip, 0x80 Y flip.\n"
        "This Stage Explorer is a proof of concept / research inspector, not a faithful gameplay map viewer.\n"
        "Static decoded MAP cells and DAT records are the authoritative inspection surfaces.\n"
        "The experimental motion panel integrates SCROLL_01/02/03 only; it does not execute the complete stage sequence.\n",
        encoding="utf-8",
    )
    return manifest
