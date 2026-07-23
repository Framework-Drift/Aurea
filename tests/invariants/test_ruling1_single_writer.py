"""
RULING 1 — ROUTE-THROUGH: one WRITER per store.

No module but the canonical owner executes a store write. Gated generators
(DBE, MSSL, TCAML, ECI, ELM, CTL...) emit REQUESTS; the owner executes.

    scar store        -> ScarLogicCore        (src/filtration/scar_logic_core.py)
    Codex doctrine    -> SAE, via Codex       (src/doctrine/codex.py)
    identity threads  -> RIL                  (src/identity/ril.py)

WHY THIS TEST EXISTS
--------------------
The single-writer invariant does not die from a loud violation. It dies from a
hundred defensible conveniences — a helper that writes straight to the store
"just for this case," each one locally reasonable, each one passing review in
isolation. Static scanning is the only thing that sees the hundredth one.

Reads are allowed. Any module may read a store. This governs WRITES.
"""

from __future__ import annotations

import pytest

from tests.invariants import _ast as H

# Canonical owner per store. Only these files may mutate the collection.
#
# NOTE (provenance): `scars` is confirmed against live code. `doctrines` is CONFIRMED
# as of 2026-07-11 (Ruling 5): Codex owns the store, SAE is sole executor, and
# DoctrineSpine was stripped of `self.doctrines` + `mutate_doctrine()`. `threads` is
# still the EXPECTED attribute name for ril.py, which remains a stub. If the authored
# module uses a different attribute name, update it HERE — do not delete the check.
STORE_OWNERS: dict[str, str] = {
    "scars": "src/filtration/scar_logic_core.py",
    "doctrines": "src/doctrine/codex.py",
    "threads": "src/identity/ril.py",
    # Ruling 12 G4 (2026-07-21) put the Nova Echo Index in the ownership
    # tables; registered here 2026-07-22 (Ruling-13 pass) so the assertion is
    # SCANNED, not just asserted. Trivially green while Nova is unwired -
    # load-bearing the moment Stage 2 gives other modules a Nova handle.
    "echo_index": "src/expansion/nova.py",
}


@pytest.mark.parametrize("store_attr,owner", sorted(STORE_OWNERS.items()))
def test_single_writer_per_store(store_attr: str, owner: str) -> None:
    violations: list[H.Violation] = []

    for path in H.src_files():
        if H.rel(path) == owner:
            continue  # the owner is allowed to write its own store
        tree = H.parse(path)
        if tree is None:
            continue
        for lineno, detail in H.find_store_mutations(tree, store_attr):
            violations.append(H.Violation(path, lineno, detail))

    assert not violations, H.fail_message(
        ruling=f"Ruling 1 (route-through): `{store_attr}` has exactly one writer — {owner}",
        violations=violations,
        remedy=(
            f"Do not write to `{store_attr}` directly. Emit a request to the canonical "
            f"owner ({owner}) and let it execute the write."
        ),
    )
