# GIGANTIC UFO presentation orientation correction — dev24 WIP175

## Status

The previous GIGANTIC UFO-specific presentation transform is **superseded**. WIP175 restores `gigantic_ufo_complete` to the same native model-facing convention used by the rest of the SIIG GMX corpus.

## Why the previous special case was wrong

The dev23-era work correctly recovered the multipart runtime hierarchy — one `bos_003.gmx` root and 36 `bos_003a.gmx` children attached to `lt_001..lt_036` — but later added a presentation-only `-90°` X root so the saucer appeared to face a chosen Blender direction.

Project-owner review clarified the missing visual convention: SIIG's models intentionally share the same native facing direction because gameplay views them from a top-down camera. GIGANTIC UFO was not an exceptional asset that needed its own facing correction. The special presentation root therefore created inconsistency rather than fixing one.

## WIP175 policy

WIP175 chooses the smallest correction consistent with the native corpus:

- remove the GIGANTIC-UFO-only presentation matrix;
- do **not** rotate all other bosses to match the earlier special case;
- preserve the recovered root/child hierarchy and all child-local matrices exactly;
- leave generic GMX→glTF axis conversion unchanged for every model;
- do not reinterpret a viewer-facing convention as a gameplay/runtime rotation.

This avoids introducing a global boss transform for which there is no recovered runtime requirement.

## Exact unaffected reconstruction

`gigantic_ufo_complete` remains:

- 1× runtime `0x9E` / `bos_003.gmx` root;
- 36× runtime `0xB5` / `bos_003a.gmx` weapon modules;
- child attachment order `lt_001` through `lt_036`;
- identity child-local matrices;
- three `0xB4` helper/control slots excluded because they are not model assets.

Only the extra presentation root has been removed.

## Historical note

The sealed dev23 documentation remains historical evidence of the earlier interpretation and is not rewritten. WIP175 explicitly supersedes that presentation conclusion while retaining the correct hierarchy research.
