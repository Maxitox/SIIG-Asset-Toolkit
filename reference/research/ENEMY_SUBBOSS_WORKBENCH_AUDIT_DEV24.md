# Enemy / Sub-boss GMX Workbench audit — dev24

This audit covers the six console enemy/sub-boss families explicitly requested for GMX assembly treatment: ENVY, KEEPER, OPPRESSOR, GLUTTONY, VANITY and TELEPORTER. It records what can be exported exactly from recovered runtime evidence and where the Workbench must remain dynamic/inspection-only rather than inventing a pose.

## Audit result

All six requested families already have material executable-backed Workbench coverage. No additional guessed rigid transforms are justified by the current evidence. dev24 therefore promotes the existing exact/dynamic boundaries into the GUI and improves assembly/preview usability instead of fabricating extra parts.

| Family | Models / ownership | Best promoted Workbench representation | Evidence boundary |
| --- | --- | --- | --- |
| ENVY | repeated `emy_045.gmx`, runtime `0x98` | exact normalized retail Level 4-2 20-member growth-complete chain plus compact six-member inspection reference | relative 10-unit / ±2 zig-zag geometry, heading and member count are exact; moving absolute base and live fly-away target behavior are not baked |
| KEEPER | `emy_032.gmx` + eight `emy_032a.gmx` (`0xAC`) | exact root + `lt_001..lt_008` helper hierarchy | odd helper indices receive exact 180° local Y rotation; no extra guessed movement is added |
| OPPRESSOR | `emy_043.gmx` + AD×1 / AE×2 / AF×8 (`emy_043a/b/c`) | exact 12-model ownership/order on `lt_001..lt_011` | helper transforms are locator-driven; the hierarchy is exact without inventing stage-specific world poses |
| GLUTTONY | `emy_050.gmx` + two `emy_050a.gmx` B0 helpers | exact body + `lt_001/lt_002` helpers, with exact helper-yaw law in metadata | live aim target comes from gameplay state, so no arbitrary target-facing yaw is frozen into the static assembly |
| VANITY | `sbs_002.gmx` + two `sbs_002a.gmx` B1 helpers | exact main-game arrival formation, exact primary-only state-2 local-Y descent, plus ownership-only inspection set | state-2 X/Z steering and independent helper activity remain live; only proven components are animated |
| TELEPORTER | three `sbs_003.gmx` roots + `sbs_003a..i.gmx` helpers | exact retail Stage 5-4 left/right state 0→4 transfer actions and reachable state-2 snapshots, plus ownership-only set | action stops before next randomized state-0 X; no random next-cycle placement is invented |

## Workbench / GUI changes from the audit

- The compact Entity Assembler correctly reports eight available families total: the six requested families above plus the subsequently reconstructed GREED and WRATH.
- The six originally requested families remain tracked separately as the core audit set so their coverage cannot silently regress.
- Boss and Entity compact assemblers now include **Assemble + preview**. It builds the existing local Asset Viewer against the shared output folder and opens the generated browser so assembled glTFs can be inspected as model previews.
- Advanced one-click assembly actions reuse the same remembered model folder and deterministic output folder used by the compact assembler. The model folder is requested only when it is not already valid; switching between advanced assembly families no longer reopens both folder/save dialogs every time.
- Previewing does not change reconstruction evidence. The Asset Viewer shows derived glTF wireframe/model previews; it does not claim to reproduce proprietary materials/shaders or gameplay rendering.

## Provenance rule

The Workbench must keep these categories distinct:

1. **exact static hierarchy / transform** — directly recovered runtime locator ownership or deterministic transform;
2. **exact runtime action** — deterministic recovered state/action samples that can be exported as animation;
3. **normalized exact relationship** — exact relative geometry with deliberately removed dynamic world anchor;
4. **inspection-only ownership set** — exact model ownership but no asserted gameplay pose;
5. **unresolved live behavior** — player/RNG/state-dependent behavior retained as metadata rather than guessed.

This rule is intentionally stricter than producing a visually plausible composite. A missing live transform is preferable to a fabricated canonical pose.
