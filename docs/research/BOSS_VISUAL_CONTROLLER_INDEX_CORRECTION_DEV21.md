# Visual-controller factory index correction — dev21

## Result
Retail Xbox `Function_821489F8` does **not** switch directly on the runtime/model type. Its dispatch is `switch(param_2 + 1)`.

The caller `Function_820E7AE8` passes the same `iVar8` both to `Function_821489F8(..., iVar8)` and to `FUN_820faab8(iVar8)`, which resolves the runtime model resource. Therefore a factory case label `N` belongs to runtime/model type `N-1`.

This closes a historical off-by-one attribution error in the dev19 THE SUN research. It does not alter the sealed dev19/dev20 archives; dev21 records the correction explicitly.

## THE MOON / THE SUN correction

- Runtime `0x46` **THE MOON** -> factory case `0x47` -> `Function_8212B638` (0x74-byte visual controller).
- Runtime `0x47` **THE SUN** -> factory case `0x48` -> `Function_8212BA68` (0x138-byte visual controller).
- THE SUN setup `Function_8212BB58` therefore belongs to THE SUN itself and allocates the `0xB2` group of eight plus the 48-slot `0xB3` pool.
- THE SUN updater `Function_8212BBF0` is consequently the direct owner of the four-group segmented long-wave visual already reconstructed in dev19.
- `Function_8212B760`, previously cited as THE SUN's internal-node controller, actually belongs to THE MOON. The six native `bos_002.gmx` tracks still prove THE SUN's extended-arm motion independently; only the executable-controller attribution changes.

## Cross-boss invariant

`reference/tables/BOSS_VISUAL_CONTROLLER_FACTORY_2.10.0-dev21.csv` records the corrected mapping for all 18 boss families. The dev21 selftest enforces `factory_case == runtime_type + 1` for every row and spot-checks the five bosses that were native-inspection-only in dev20.

## Evidence boundary

This table identifies the retail visual-controller class allocated for each runtime type. It does not, by itself, prove every controller state can be represented as one static assembly. Runtime-randomized, timed, or effect-only behavior remains evidence-bounded exactly as in the individual boss research.
