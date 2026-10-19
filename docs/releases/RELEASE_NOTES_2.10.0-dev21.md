# SIIG Asset Toolkit 2.10.0-dev21

Dev21 combines the first post-unification boss-controller audit with a faster desktop Game Rip input workflow.

- Corrects the retail visual-controller dispatch invariant: `Function_821489F8` switches on `runtime_type + 1`, proven by caller `Function_820E7AE8` passing the same runtime index to both the factory and the model-resource resolver.
- Adds a corrected visual-controller map for all **18** boss families, including constructor and object size.
- Corrects the dev19 attribution boundary without touching sealed history: THE MOON `0x46` owns case `0x47` / `Function_8212B638`; THE SUN `0x47` owns case `0x48` / `Function_8212BA68`. THE SUN therefore directly owns `Function_8212BB58` B2/B3 allocation and the `Function_8212BBF0` 48-segment long-wave path.
- Continues THE MOON, LADYBUG, OCTOPUS, WATER STRIDER and NO_NAME in parallel. Controller classes are now attributed correctly; LADYBUG's four `0xB6` auxiliaries and WATER STRIDER's 1441-frame route ownership are concrete new anchors. The five families remain native-inspection-only until static assembly transforms/state timing are proven.
- Extends `boss-matrix` with corrected visual-controller runtime type, factory case, constructor and allocation size. Fresh Xbox 360 retail validation still finds **18/18** canonical root GMXs.
- GUI **0.32.0-dev21** adds dependency-free Windows Explorer drag-and-drop to Game Rip. Drop exactly one supported package/file or extracted game folder into the drop box; the source is selected immediately, but **Rip game** remains an explicit action. Browse remains available as the fallback.
- The drag/drop implementation uses only Python stdlib/Tk + Windows `WM_DROPFILES`; no tkdnd/tkinterdnd binary is bundled. The original Tk window procedure is restored on GUI close.
- Dependency-free regression suite remains **102/102**.

Evidence boundaries remain conservative. A traced controller class is not automatically treated as a reconstructable static pose, and the actual Windows shell delivery path remains an environment-specific GUI gate that cannot be exercised in the Linux release-build container.
