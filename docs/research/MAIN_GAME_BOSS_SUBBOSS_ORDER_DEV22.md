# Main-game boss and sub-boss ordering — dev22

Source status: **project-owner reference, not yet executable-verified in full**. The supplied list explicitly excludes bonus stages and may contain a few mistakes. Dev22 preserves that boundary rather than silently upgrading every appearance to executable fact.

## Main boss order

1. **THE MOON** — stage 3-1
2. **THE SUN** — stage 3-2
3. **GIGANTIC UFO** — stage 3-3
4. **LADYBUG** — stage 3-4
5. **MANDALA** — stage 3-5
6. **UNKNOWN** — stage 3-6
7. **CENTIPEDE** — stage 4-1
8. **HORNET** — stage 4-2
9. **PROGRESSIVE UFO** — stage 4-3
10. **OCTOPUS** — stage 4-4
11. **BUTTERFLY** — stage 4-5
12. **AXON** — stage 4-6
13. **WATER STRIDER** — stage 5-1
14. **CRAB** — stage 5-2
15. **ULTIMATE UFO** — stage 5-3
16. **SQUID** — stage 5-4
17. **VERTEBRATE** — stage 5-5
18. **NAMELESS** — stage 5-6 — toolkit runtime name `NO_NAME`

## Full supplied main-game list

- **SOL** — sub-boss in stage 1-6 and 3-5, generic enemy starting from 5-1
- **DIFUSSER** — sub-boss in 2-1, 3-1 and 3-5, generic enemy starting from 4-1
- **JOLYNE** — sub-boss in 2-2, 3-2 and 3-5, generic enemy starting from 4-2
- **SATORU UFO** — sub-boss in 2-3, 3-3 and 3-5, generic enemy starting from 4-3
- **DIFUSSER2** — sub-boss in 2-4, 3-4 and 3-5, generic enemy starting from 4-1
- **SPIDER** — sub-boss in 2-4, 3-4 and 3-5, generic enemy starting from 4-4
- **TELEPORTER** — sub-boss in 2-5 and 3-5, generic enemy starting from 5-4
- **VANITY** — sub-boss in 2-6 and 3-5, couldn't find more appearances inside the main mode
- **THE MOON** — boss in 3-1, sub-boss starting from 4-1
- **THE SUN** — boss in 3-2, sub-boss starting from 4-2
- **GIGANTIC UFO** — boss in 3-3, sub-boss in 4-3, generic enemy starting from 5-1
- **LADYBUG** — boss in 3-4, sub-boss starting from 4-4
- **MANDALA** — boss in 3-5, sub-boss in 4-5, generic enemy starting from 5-5
- **UNKNOWN** — boss in 3-6, sub-boss starting from 4-5
- **GREED** — sub-boss in 4-1, generic enemy starting from 5-1
- **CENTIPEDE** — boss in 4-1, sub-boss starting from 5-1
- **HORNET** — boss in 4-2, sub-boss starting from 5-2
- **PROGRESSIVE UFO** — boss in 4-3, sub-boss starting from 5-3
- **WRATH** — sub-boss in 4-4, generic enemy starting from 5-2
- **OCTOPUS** — boss in 4-4, sub-boss starting from 5-4
- **BUTTERFLY** — boss in 4-5, sub-boss starting from 5-5
- **AXON** — boss in 4-6, sub-boss starting from 5-5
- **WATER STRIDER** — boss in 5-1
- **CRAB** — boss in 5-2
- **ULTIMATE UFO** — boss in 5-3
- **GLUTTONY** — sub-boss in 5-4 and 5-5
- **SQUID** — boss in 5-4
- **VERTEBRATE** — boss in 5-5
- **NAMELESS** — boss in 5-6

## Naming reconciliation

`UNKNOWN` (3-6) and `NAMELESS` (5-6) are distinct bosses. Existing toolkit/runtime research labels the latter family `NO_NAME`; dev22 should present it to users as **NAMELESS (runtime NO_NAME)** while retaining `NO_NAME` in executable-facing metadata.
