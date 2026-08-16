"""The Executive domain -- M7, opened on the REFUSED verdict.

Heading Phase 7 (line 186), L10 (line 37), the Kernel/Executive boundary
(section 5): the kernel never loops; the Executive never owns. Every module in
this package holds ZERO durable state. Executive working state is a derived
view over kernel ledgers, reconstructible at any moment; Acceptance Test 6
proves it by destruction at M7-d.

First citation: the M5 qualification verdict, REFUSED, durable at Foundry
commit `c1930d6` (`references/m5-gamma-4-qualification-record.md`). The
delegated-cognition chair is EMPTY as a designed initial state, and the loop
learns that by reading the record -- never from hardwiring (ninety-eighth
manifest entry, M7_GROUNDING.md sha256 437afc7b...).
"""
