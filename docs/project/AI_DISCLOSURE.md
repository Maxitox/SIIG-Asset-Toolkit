# AI-assisted development disclosure

OpenAI ChatGPT was used as an active research and development assistant. Its roles included:

- proposing reverse-engineering hypotheses;
- interpreting user-supplied Ghidra output and binary samples;
- drafting and revising Python and Java code;
- developing synthetic tests, corpus validation, and security checks;
- implementing MAP visualization and packaging workflows;
- producing documentation, provenance records, and release artifacts.

The project owner supplied the game data, prototype builds, Ghidra exports, PS3 SDAT decryptions, and contextual observations. Important claims were checked against supplied files, executable evidence, synthetic fixtures, or corpus-wide counts where feasible instead of being accepted solely from generated text.

No original game source code was available. The work is based on clean-room binary inspection, black-box file comparison, decompiler/listing evidence, public specifications, and explicitly attributed algorithmic references. Game binaries and extracted copyrighted assets are not included in the source-only toolkit release.

## Scope of source disclosure

The project records external sources explicitly consulted and code intentionally adapted in `reference/provenance/SOURCES.csv` and `reference/provenance/PROVENANCE.json`. The one known direct adaptation, Xenos tiled-texture addressing from Xenia, carries its license notice and a documented historical-revision limitation.

It is not possible to enumerate the full training dataset or all latent influences of an AI model. The safeguards used here are:

- release-time source and license audits;
- explicit adaptation notices;
- preference for clean-room implementations and synthetic tests;
- no copying from unclear-license sources;
- external tools kept unbundled;
- reproducible self-tests and output verification;
- visible documentation of unresolved semantics and test gaps;
- human review before publication.

AI-generated code can contain defects or accidental similarities. Future public releases should continue source-overlap review, security testing, and independent validation.
