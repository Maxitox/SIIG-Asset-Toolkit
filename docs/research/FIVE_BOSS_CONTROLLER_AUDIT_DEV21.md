# Five-boss parallel controller audit — dev21

Dev20 deliberately left THE MOON, LADYBUG, OCTOPUS, WATER STRIDER, and NO_NAME as native-inspection-only. Dev21 traces their corrected visual-controller classes in parallel without inventing static gameplay poses that are not yet proven.

## THE MOON (`0x46` / `bos_001.gmx`)

Corrected factory case `0x47` constructs `Function_8212B638`. Its vtable uses setup `Function_8212B6F8` and node update `Function_8212B760`. Fresh retail `bos_001.gmx` has exactly three bones (`bos_001`, `TheMoon_F`, `TheMoon_E`), matching the controller's three-node behavior. The updater switches resource/state selection and applies runtime scale/rotation behavior to those nodes. This controller was historically misattributed to THE SUN because the factory's `+1` dispatch had not been accounted for.

The native body remains the safe canonical export until a specific controller-time/state snapshot is selected and validated.

## LADYBUG (`0x49` / `bos_004.gmx`)

Corrected factory case `0x4A` constructs `Function_8211EA18`. Setup `Function_8211EB88` resolves runtime `0xB6` (`bos_004a.gmx`) as a group of exactly four and creates four subordinate helper objects. Fresh `bos_004.gmx` contains the four native locators `lt_001..lt_004`; it also contains eight native 17-sample matrix tracks targeting the E/F body parts.

The four-model B6 ownership is therefore proven. Dev21 does not yet claim exact B6 locator attachment/visibility timing until the remaining helper-object path is traced.

## OCTOPUS (`0xA3` / `bos_010.gmx`)

Corrected factory case `0xA4` constructs the large 0x28C-byte `Function_82123E18` controller. Its class path creates the runtime `0xA3` model and explicitly resolves native locator `lt_000`. Fresh `bos_010.gmx` is already a large articulated asset: 22 meshes, 49 bones, and twelve 272-sample native matrix tracks distributed across the four three-segment leg chains.

No auxiliary GMX ownership is promoted from this local controller trace yet; native animation remains the authoritative inspection representation.

## WATER STRIDER (`0xA6` / `bos_014.gmx`)

Corrected factory case `0xA7` constructs `Function_821368E8` (0x2F0 bytes). Its vtable directly includes `Function_82136810`, the previously recovered repeating field/course updater. The updater advances the controller clock and wraps after `0x5A0` (1440), confirming the 1441-frame route belongs to WATER STRIDER's own visual-controller class rather than a neighboring boss.

Fresh `bos_014.gmx` contains 16 meshes, 30 bones, ten 91-sample tracks, three `lt_*` locators and four `lzr_*` locators. A canonical static route-state assembly is still withheld because the route is timed rather than one fixed transform.

## NO_NAME (`0xAB` / `bos_018a.gmx`)

Corrected factory case `0xAC` constructs `Function_82120B50` (0x240 bytes). Its vtable enters `Function_82120CA0`, which creates the runtime `0xAB` root and initializes large subordinate/helper pools; `Function_821208F8` advances its high-level controller state. Fresh `bos_018a.gmx` has one mesh, two bones and one 126-sample native track.

The trace does not yet prove that registry model `0xE5` / `bos_018.gmx` is a persistent NO_NAME child, so dev21 does not stack it into the canonical NO_NAME scene.

## Current status

All five bosses now have corrected controller-class attribution. Their dev20 native inspection catalogs remain valid and conservative. The next promotion criterion is unchanged: add a deep assembly only when membership, transforms/attachments, and state/visibility timing are executable- or native-asset-backed rather than inferred from screenshots.
