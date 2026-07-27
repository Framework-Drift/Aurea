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
    # SCANNED, not just asserted. It was registered while Nova was unwired and
    # was trivially green then; NOVA HAS BEEN WIRED SINCE 2026-07-24, so this
    # is now LOAD-BEARING - `aurea_core` holds a Nova handle and must reach the
    # index only through `erupt()`.
    "echo_index": "src/expansion/nova.py",
    # Ruling 27 / TCAML Stage 1 (2026-07-26). CLAUDE.md 2 has named TCAML the
    # sole writer of compass anchor state since before TCAML existed; the organ
    # now exists, so the claim becomes SCANNED rather than merely asserted.
    # CSE calls `anchor_feedback_update` / `trigger_anchor_realignment` - it
    # REPORTS what it measured and ASKS; it never reaches into the store and
    # straightens the needle itself. Registered while TCAML was still unwired,
    # the same way `echo_index` was registered before Nova Stage 2 - and, like
    # that one, NOW LOAD-BEARING: TCAML has been wired since 2026-07-26 and
    # both RACM and CSE hold a handle to it.
    "anchor_state": "src/topology/tcaml.py",
    # Ruling 34 (2026-07-27) made SAE's epoch state DURABLE, which is what
    # turns it into a store rather than a counter. `touched_lineages` is the
    # load-bearing half - sae.py's own annotation calls it "what must settle to
    # close the epoch" - and the Self-Mutation Ceiling is downstream of it, so a
    # foreign write here is a write to AUREA's mutation budget.
    #
    # REGISTERED AS A PAIR with CLAUDE.md §2's ownership table (both-or-neither):
    # the previous pass declined to add the table row alone, because a claim of
    # ownership in prose with no scanner behind it is the completeness-claim
    # defect in its purest form.
    #
    # `epoch`/`epoch_count`/`history` are deliberately NOT registered: `history`
    # collides with EchoNet's and CSE's own `self.history` (three modules, one
    # name), so registering it would flag correct code. Ruling 1's own warning -
    # do not name a local collection after a canonical store - cuts both ways,
    # and the honest move is to register the name that IS unique.
    "touched_lineages": "src/expansion/sae.py",
    # RULING 40 (2026-07-27). CLAUDE.md section 2 has named SML the owner of
    # "Scar weight / decay" since before `scar_management.py` existed, and
    # `scar_logic_core.py` carried an in-file flag saying it was the ONE
    # remaining writer of `decay_state` outside SML - "Reported, not repaired"
    # since Ruling 37. Two writers of one field is what Ruling 1 exists to
    # prevent, and this is the scanner behind the claim.
    #
    # REGISTERED AS A PAIR with CLAUDE.md section 2's ownership table
    # (both-or-neither), the `touched_lineages` precedent directly above: an
    # ownership claim in prose with no scanner behind it is the completeness-claim
    # defect, and a scanner with no prose behind it is an unexplained tripwire.
    #
    # THE FIELD, NOT A COLLECTION - and that is what makes it registrable here.
    # `find_store_mutations` flags `<anything>.decay_state = ...`, and after the
    # delegation exactly one module in `src/` does that. `srg.py` COMPARES it,
    # which is a read and is free.
    "decay_state": "src/filtration/scar_management.py",
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
