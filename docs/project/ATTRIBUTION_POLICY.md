# Attribution and provenance policy

Every release should satisfy these rules:

1. **Record explicit sources.** Add every repository, specification, article, tool, or user-provided evidence set that materially influenced implementation to `reference/provenance/SOURCES.csv` and `reference/provenance/PROVENANCE.json`.
2. **Pin imported code.** Copied or adapted code must record the exact repository, commit/tag, source file, function/range, license, and local modifications. When historical revision data is genuinely unavailable, state that limitation and do not invent it.
3. **Preserve notices.** Reproduce required copyright/license notices in `LICENSES/` and place an inline attribution beside adapted code.
4. **No unclear-license copying.** A source with no clear compatible license may be cited as research or used externally, but its code must not be copied or redistributed.
5. **Prefer clean-room work.** Proprietary formats should be implemented from observed files, behavior, specifications, and decompiler evidence, with synthetic and corpus tests showing how conclusions were reached.
6. **Distinguish specifications from source adaptations.** Following a normative format/algorithm document is not the same as copying implementation code; record both accurately.
7. **Keep external binaries external.** FFmpeg, vgmstream, Ghidra, XEXLoaderWV, TrueAncestor, and similar utilities are not bundled without a separate license/security review and fulfillment of redistribution terms.
8. **Disclose AI assistance.** Keep `docs/project/AI_DISCLOSURE.md` in releases and update it when the workflow materially changes.
9. **Avoid unapproved personal credit.** Contributor names are published only with permission; anonymous/project-role credit is acceptable.
10. **Do not redistribute game content.** Public source releases contain tooling, format notes, schemas, and validation metadata—not original binaries, extracted copyrighted assets, or explorers with embedded game atlases.
11. **Fail closed on new adaptations.** Any future copied/adapted implementation is excluded from release until its source, revision, local scope, license, notices, and compatibility are reviewed.
12. **Keep limitations visible.** Test gaps, unresolved semantics, and missing provenance details must remain explicit in release notes rather than being converted into unsupported claims.


## Excluded sources

Sources with terms or policies that prohibit the intended automated/AI-assisted use must not be accessed for this project. TCRF/the Cutting Room Floor is explicitly excluded. See `docs/project/SOURCE_EXCLUSIONS.md`.
