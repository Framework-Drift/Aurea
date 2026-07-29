"""
test_ruling45.py - DOCKET I: CAE + DoctrineMutationProof + EntrenchmentBasis.

    "No doctrine may be mutated, collapsed, or discarded without a CAE entry."
                                                                    - canon 3a:111

Before this pass that sentence appeared, VERBATIM, in the docstrings of BOTH
`SAE._audit` and `DEE._audit`. Both then read `if self.cae is None: return None`,
`aurea_core` wired neither, and no `cae.py` existed anywhere in `src/`. So the
protection canon states in absolute terms was, in every run AUREA has ever
performed, A DOCSTRING ABOVE A SOFT RETURN - and every `cae_id` on every
authorization, ruling and mutation record was `None`.

That is CLAUDE.md section 3 in its purest negative form: a comment saying "never
do X" is a request for restraint. These pins hold the structural version.
"""

import ast
import json
from datetime import datetime

import pytest

from src.aurea_core import AureaCore
from src.doctrine.cae import CAE
from src.doctrine.codex import Codex
from src.doctrine.dee import (
    CMTE, DEE, DANGER_STABLE, PRESSURE_CRITICAL, SUSTAIN_CYCLES,
    MutationTrigger, _Watched,
)
from src.doctrine.entrenchment import EntrenchmentBasis, entrenchment_basis
from src.doctrine.mutation_proof import (
    CriterionResult, DoctrineMutationProof, InvalidMutationProof, validate_proof,
)
from src.expansion.sae import SAE
from src.filtration.scar_logic_core import ScarLogicCore
from src.identity.ril import RIL, IdentityThread
from src.utils.models import Doctrine, Scar

from tests.invariants import _ast as H
from tests.proof_support import minimal_proof


# =====================================================================
# A REAL DEE -> SAE -> CAE CHAIN
# =====================================================================

def _chain(tmp_path, scar_links=("Δ-1",)):
    """Codex + SAE + DEE over ONE shared CAE - the pipeline's own wiring.

    Deliberately not a stub anywhere: the point of every pin below is that the
    audit entry is produced by the real `_approve -> mutate_doctrine ->
    authorize -> _audit -> CAE.record` chain.
    """
    codex = Codex(filepath=str(tmp_path / "doctrines.json"))
    codex.doctrines.clear()
    codex.doctrines["D-1"] = Doctrine(
        id="D-1", name="Original", description="the belief under strain",
        scar_links=list(scar_links), created_at=datetime.now())

    cae = CAE(ledger_path=str(tmp_path / "cae.jsonl"))
    sae = SAE(codex=codex, cae=cae, runtime_path=str(tmp_path / "sae.json"))
    dee = DEE(codex=codex, sae=sae, cae=cae)
    return codex, sae, dee, cae


def _drive_to_approval(dee, proposal, context=None):
    """Sustain real pressure until DMW releases the doctrine to CMTE."""
    signals = {"D-1": {"pressure": 0.95, "drpe": True, "scar_bloom": True}}
    ctx = {"D-1": dict(context or {})}
    rulings = []
    for _ in range(SUSTAIN_CYCLES + 1):
        rulings = dee.cycle(signals=signals, proposals={"D-1": proposal},
                            context=ctx)
        if any(r.executed_by == "SAE" for r in rulings):
            break
    return rulings


def _proposal(scar_links=(), tags=()):
    return Doctrine(id="D-1::nova::NE-0001", name="Successor",
                    description="the belief after strain",
                    scar_links=list(scar_links), tca_tags=list(tags),
                    created_at=datetime.now())


# =====================================================================
# PIN 1 - THE HEADLINE. An entry exists, end to end.
# =====================================================================

def test_a_real_mutation_writes_a_cae_entry_and_carries_its_id(tmp_path):
    """RED AT `eb11b1e`: `self.cae` was None on every path, `_audit` returned
    None, and the ledger did not exist. The mutation happened anyway.
    """
    codex, sae, dee, cae = _chain(tmp_path)
    rulings = _drive_to_approval(dee, _proposal())

    executed = [r for r in rulings if r.executed_by == "SAE"]
    assert executed, "precondition: the real chain performed a mutation"

    record = sae.history[-1]
    assert record.cae_id is not None, (
        "3a:111 - no doctrine may be mutated without a CAE entry")
    assert record.cae_id.startswith("CAE-")

    # The entry is ON DISK, not merely in memory.
    entries = cae.read_all()
    assert any(e["id"] == record.cae_id for e in entries)
    written = next(e for e in entries if e["id"] == record.cae_id)
    assert written["event"] == "mutate_doctrine"
    assert written["target"] == "D-1"
    assert written["proof"]["contradiction_core"]["doctrine_id"] == "D-1"


def test_aurea_core_shares_exactly_one_ledger_between_its_two_writers():
    """ONE ledger, two writers of entries, zero writers of each other's entries.
    Two CAEs would mint colliding ids into two files and neither would be the
    record."""
    aurea = AureaCore()
    assert aurea.cae is aurea.sae.cae
    assert aurea.cae is aurea.dee.cae


def test_a_bare_sae_still_audits(tmp_path):
    """DEFAULT-BY-CONSTRUCTION (the Ruling 27 `tcaml or TCAML()` shape). There is
    no "CAE absent" state left, which is what let the soft branch be DELETED
    rather than softened."""
    codex = Codex(filepath=str(tmp_path / "d.json"))
    codex.doctrines.clear()
    codex.doctrines["D-1"] = Doctrine(id="D-1", name="x", created_at=datetime.now())
    sae = SAE(codex=codex, runtime_path=str(tmp_path / "sae.json"))   # no cae=

    assert sae.cae is not None
    out = sae.mutate_doctrine(
        "D-1", Doctrine(id="D-1::nova::NE-0001", name="y", created_at=datetime.now()),
        collapse_lineage="Δ-1", proof=minimal_proof("bare-SAE audit probe"))

    assert out is not None
    assert sae.history[-1].cae_id is not None


def _cae_soft_guards(tree):
    """Code that lets a missing/incomplete CAE be routed around.

    AST, NOT A SUBSTRING SEARCH, and the first draft of this pin got that wrong
    in the way this codebase has already learned about once: it matched the
    DOCSTRINGS in which both modules now describe the deleted branch, so
    documenting the fix made the pin fail. That is the scanner-cries-wolf-on-
    prose defect the Ruling 39 sweep's `_pathish` excludes spaces for, and a
    scanner that fires on its own epitaph gets narrowed by whoever it annoys.
    """
    found = []
    for node in ast.walk(tree):
        # `self.cae is None` / `self.cae is not None` in any comparison
        if isinstance(node, ast.Compare):
            left = node.left
            if (isinstance(left, ast.Attribute) and left.attr == "cae"
                    and isinstance(left.value, ast.Name) and left.value.id == "self"
                    and any(isinstance(op, (ast.Is, ast.IsNot)) for op in node.ops)):
                found.append(f"line {node.lineno}: compares self.cae to None")
        # `hasattr(self.cae, ...)` - the capability check that degrades to a no-op
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "hasattr" and node.args
                and isinstance(node.args[0], ast.Attribute)
                and node.args[0].attr == "cae"):
            found.append(f"line {node.lineno}: hasattr(self.cae, ...)")
    return found


@pytest.mark.parametrize("module", ["src/expansion/sae.py", "src/doctrine/dee.py"])
def test_no_soft_none_branch_survives_in_either_audit(module):
    """STRUCTURAL. The defect was not that the ledger was missing - it was that
    both modules were WRITTEN TO CONTINUE WITHOUT ONE. A future `if self.cae is
    None` would restore exactly that, so it is refused here rather than trusted
    not to come back.

    DEE's `hasattr(self.cae, "record")` half is covered by the same scan: that is
    the `hasattr(scar_core, "form_scar")` shape which silently dropped every
    SBSRE scar request (CLAUDE.md section 3).
    """
    tree = H.parse(H.repo_root() / module)
    assert _cae_soft_guards(tree) == []


def test_the_soft_guard_scanner_actually_fires():
    """Fed the exact pre-Ruling-45 code, both halves must be caught - and the
    prose that describes them must NOT be."""
    assert _cae_soft_guards(ast.parse(
        "class S:\n    def a(self):\n        if self.cae is None:\n            return None\n"))
    assert _cae_soft_guards(ast.parse(
        "class D:\n    def a(self):\n"
        "        if self.cae is None or not hasattr(self.cae, 'record'):\n"
        "            return None\n"))
    assert _cae_soft_guards(ast.parse(
        '"""The `if self.cae is None` branch is GONE."""\n'
        "class S:\n    def a(self):\n        return self.cae.record()\n")) == []


# =====================================================================
# PIN 4 - the proof is required, and it is not a formality
# =====================================================================

def test_a_mutation_without_a_proof_is_unwritable(tmp_path):
    """The enforcement is the ABSENCE OF A DEFAULT. A default proof would be a
    fabricated argument: every mutation would carry one, so carrying one would
    mean nothing."""
    _codex, sae, _dee, _cae = _chain(tmp_path)
    with pytest.raises(TypeError):
        sae.mutate_doctrine(                                    # type: ignore[call-arg]
            "D-1", _proposal(), collapse_lineage="Δ-1")


@pytest.mark.parametrize("bad,why", [
    (None, "not a proof at all"),
    ("a good reason", "a sentence is not an argument"),
    (DoctrineMutationProof(), "empty - nothing is stated to have forced it"),
    (DoctrineMutationProof(contradiction_core={"triggers": ["drpe"]}),
     "no criteria reported as evaluated"),
    # THE MIRROR CASE, ADDED AFTER A SURVIVING MUTANT (M13). Without it, a proof
    # with an empty `contradiction_core` was still refused - but by the
    # `preserved_invariants` check underneath it, so deleting the
    # contradiction_core guard changed nothing observable. Each guard needs a
    # case only IT can catch, or the suite is pinning their conjunction and
    # calling it two pins.
    (DoctrineMutationProof(preserved_invariants={
        "collapse_threshold_reached": CriterionResult.PASS}),
     "criteria reported, but nothing stated to have forced the mutation"),
])
def test_a_structurally_invalid_proof_refuses(bad, why, tmp_path):
    """A proof that carries no argument is refused BEFORE any write, beside the
    other Ruling 24 preflight checks - so it costs no ceiling slot and no CAE
    entry."""
    _codex, sae, _dee, _cae = _chain(tmp_path)
    with pytest.raises(InvalidMutationProof):
        sae.mutate_doctrine("D-1", _proposal(), collapse_lineage="Δ-1", proof=bad)

    assert sae.history == [], why
    assert sae.epoch_count == 0, "a refused proof spends no ceiling slot"


def test_the_proof_carries_the_FULL_scar_lineage_not_the_first_element(tmp_path):
    """THE FORCING FORM, and the one that is RED at `eb11b1e` for a reason that
    is not "the field did not exist".

    `_approve` hands SAE `doctrine.scar_links[0]` - the FIRST element - because
    `mutate_doctrine` took one string. That single string SURVIVES on the call
    and on the record (AVT.017 refuses "" and that guard is untouched), but it
    was never the lineage: it was the head of it.

    A doctrine strained by TWO scars must put BOTH in the proof. With one scar
    this pin would pass on the truncated value and witness nothing.
    """
    _codex, sae, dee, _cae = _chain(tmp_path, scar_links=("Δ-1", "Δ-2"))
    _drive_to_approval(dee, _proposal(scar_links=("Δ-3",)))

    record = sae.history[-1]
    assert record.collapse_lineage == "Δ-1", "the singular survives, unchanged"
    assert record.proof.scar_lineage == ("Δ-1", "Δ-2", "Δ-3"), (
        "BOTH criterion-2 sources, in full and ordered: the doctrine's own scars "
        "first, then the proposal's")


def test_the_proof_records_the_echo_that_authored_the_proposal(tmp_path):
    """`echo_provenance` reads the `prov:` tags Nova stamps at emission. None
    where no echo authored - the ordinary case, and not a gap."""
    _codex, sae, dee, _cae = _chain(tmp_path)
    _drive_to_approval(dee, _proposal(tags=("prov:nova_echo_index:NE-0007",)))

    assert sae.history[-1].proof.echo_provenance == {
        "echo_id": "NE-0007", "provenance_key": "D-1::nova::NE-0001"}


def test_the_proof_records_the_content_delta_at_the_level_the_store_has(tmp_path):
    """Name/description level. Assertion-level decomposition is DEFERRED to the
    PySAT experiment tier - `Doctrine` has no assertion structure, and a regex
    over prose would be invented structure."""
    _codex, sae, dee, _cae = _chain(tmp_path)
    _drive_to_approval(dee, _proposal())

    delta = sae.history[-1].proof.content_delta
    assert delta.ancestor_id == "D-1"
    assert delta.name_before == "Original" and delta.name_after == "Successor"
    assert delta.description_before == "the belief under strain"


# =====================================================================
# PIN 6 - ABSENT IS NOT PASS
# =====================================================================

def test_a_criterion_that_passed_by_absence_records_ABSENT_not_PASS():
    """THE FORCING FORM. Criteria 3, 4 and 5 are read with `context.get(...)`, so
    an unsupplied key does not fail them - that absent-reads-as-pass semantics is
    DELIBERATE and unchanged. Recording it as PASS would claim an instrument ran.

    Docket H's `NONE_FOUND` / `NOT_COUNTABLE` cut, applied to a gate instead of a
    tally: two silences are not the same silence.
    """
    doctrine = Doctrine(id="D-1", name="x", scar_links=["Δ-1"])
    watched = _Watched(doctrine_id="D-1", pressure=0.95,
                       sustained_cycles=SUSTAIN_CYCLES,
                       triggers=[MutationTrigger.DRPE])

    absent = CMTE().evaluate(doctrine, watched, {})
    assert absent["echo_resonance_aligned"] is CriterionResult.ABSENT
    assert absent["identity_continuity_maintained"] is CriterionResult.ABSENT
    assert absent["no_distortion_flags"] is CriterionResult.ABSENT
    # ...while the two that are always readable are never ABSENT.
    assert absent["collapse_threshold_reached"] is CriterionResult.PASS
    assert absent["scar_lineage_present"] is CriterionResult.PASS

    # SAME doctrine, SAME watched slot - only the context differs. An instrument
    # that RAN and found nothing wrong reports PASS, and the two are distinct.
    supplied = CMTE().evaluate(doctrine, watched, {
        "echo_resonance": True,
        "ril_identity_conflict": False,
        "distortion_detected": False,
    })
    assert supplied["echo_resonance_aligned"] is CriterionResult.PASS
    assert supplied["identity_continuity_maintained"] is CriterionResult.PASS
    assert supplied["no_distortion_flags"] is CriterionResult.PASS

    # And the VERDICT is identical either way - the distinction is in the RECORD,
    # not in the gate. Absent-reads-as-pass is unchanged behaviour.
    assert CMTE().validate(doctrine, watched, {}) == []
    assert CMTE().validate(doctrine, watched, {"echo_resonance": True}) == []


def test_the_verdict_and_the_record_come_from_one_evaluation(tmp_path):
    """`validate()` DERIVES from `evaluate()`, so what the gate decided and what
    the proof records cannot drift. A second evaluation could disagree with the
    first the moment anything in context became time-dependent."""
    _codex, sae, dee, _cae = _chain(tmp_path)
    _drive_to_approval(dee, _proposal(), context={"ril_identity_conflict": False})

    invariants = sae.history[-1].proof.preserved_invariants
    assert invariants["identity_continuity_maintained"] is CriterionResult.PASS
    assert invariants["no_distortion_flags"] is CriterionResult.ABSENT
    assert len(invariants) == 5, "all five criteria are reported, always"


# =====================================================================
# PIN 5 - the ledger is append-only and its mint is continuity state
# =====================================================================

def test_the_ledger_is_append_only_across_a_restart_and_never_remints(tmp_path):
    """RULING 42 res.4 applied to the one store whose whole purpose is that its
    records can be CITED later. A counter restarting at zero would remint
    `CAE-001` over an id that already names a recorded mutation."""
    path = str(tmp_path / "cae.jsonl")

    first = CAE(ledger_path=path)
    a = first.record(event="mutate_doctrine", target="D-1")
    b = first.record(event="dee_rejection", target="D-2")
    assert (a, b) == ("CAE-001", "CAE-002")

    del first
    resumed = CAE(ledger_path=path)
    c = resumed.record(event="override", target="D-3")

    assert c == "CAE-003", "the mint resumed rather than restarting"
    entries = resumed.read_all()
    assert [e["id"] for e in entries] == ["CAE-001", "CAE-002", "CAE-003"], (
        "and nothing earlier was overwritten - the ledger only grows")
    assert entries[0]["event"] == "mutate_doctrine", "3a:112 - never rewritten"


def test_an_unparseable_line_contributes_nothing_rather_than_raising(tmp_path):
    """FLOOR SEMANTICS (Nova's `_derive_seq` shape). A forensic log outlives the
    code that wrote it, and a build that refuses to start because it met a line
    it does not understand has turned an append-only record into a liability."""
    path = tmp_path / "cae.jsonl"
    path.write_text('{"id": "CAE-004", "event": "x"}\n'
                    'this line is not json at all\n'
                    '{"id": "not-an-id"}\n', encoding="utf-8")

    cae = CAE(ledger_path=str(path))
    assert cae.record(event="mutate_doctrine", target="D-1") == "CAE-005"


def test_the_id_format_grows_past_999_rather_than_wrapping(tmp_path):
    """`{n:03d}` matches canon's three-digit examples and keeps counting.
    `CAE-1000` is what the format produces; it is not an overflow."""
    path = tmp_path / "cae.jsonl"
    path.write_text('{"id": "CAE-999"}\n', encoding="utf-8")
    assert CAE(ledger_path=str(path)).record(event="e", target="t") == "CAE-1000"


def test_the_proof_round_trips_through_saes_state_file(tmp_path):
    """ADDED AFTER TWO SURVIVING MUTANTS (M28/M29: dropping the proof from
    `_record_to_dict` and from `_record_from_dict` each left all 582 green).

    THE QUESTION THEY GOT: what path would have to run? A restart. Nothing in the
    suite round-tripped a `MutationRecord`'s proof through `save()`/`load()`, so
    the argument that forced a mutation was durable in theory and untested in
    fact - which is how Ruling 42 found three stores that forgot.
    """
    _codex, sae, dee, _cae = _chain(tmp_path, scar_links=("Δ-1", "Δ-2"))
    _drive_to_approval(dee, _proposal(tags=("prov:nova_echo_index:NE-0007",)))
    sae.save()

    resumed = SAE(codex=Codex(filepath=str(tmp_path / "doctrines.json")),
                  runtime_path=str(tmp_path / "sae.json"))
    record = resumed.history[-1]

    assert record.proof is not None, "the argument must survive the boundary"
    assert record.proof.scar_lineage == ("Δ-1", "Δ-2")
    assert record.proof.echo_provenance["echo_id"] == "NE-0007"
    assert record.proof.content_delta.name_after == "Successor"
    assert record.proof.preserved_invariants["no_distortion_flags"] \
        is CriterionResult.ABSENT, "ABSENT survives as ABSENT, not as PASS"


def test_a_record_written_before_proofs_existed_loads_as_None(tmp_path):
    """ADDITIVE AND OPTIONAL, so `STATE_VERSION` does NOT move. An older file has
    no `proof` key and its records load with `proof=None` - a TRUTHFUL statement
    about mutations performed before proofs existed, not an error and not a value
    to backfill.

    Bumping the version instead would REFUSE those files outright (Ruling 42's
    version gate is a refusal), discarding real epoch state to record the absence
    of a field that was never owed.
    """
    path = tmp_path / "sae.json"
    path.write_text(json.dumps({
        "version": 1, "epoch": 0, "epoch_count": 1, "touched_lineages": [],
        "consecutive_blocked_cycles": 0, "saturation_surfaced": False,
        "divergence_trigger_eligible": False,
        "history": [{
            "authorization_id": "AUTH-old", "mutation_class": "mutate_doctrine",
            "target_id": "D-1", "collapse_lineage": "Δ-1", "pre_state": None,
            "epoch": 0, "cae_id": None,
            "executed_at": datetime.now().isoformat(), "reverted": False,
        }],
    }), encoding="utf-8")

    sae = SAE(codex=Codex(filepath=str(tmp_path / "d.json")),
              runtime_path=str(path))

    assert sae.history[-1].proof is None
    assert sae.history[-1].cae_id is None, (
        "and its missing audit entry stays missing - the era is recorded, not "
        "retroactively repaired")


# =====================================================================
# PIN 7 - EntrenchmentBasis: derived, never stored
# =====================================================================

@pytest.mark.parametrize("doctrine,expected", [
    (Doctrine(id="d", name="n", is_seed=True), EntrenchmentBasis.SEED),
    (Doctrine(id="d", name="n", scar_links=["Δ-1"]), EntrenchmentBasis.SCAR_SURVIVED),
    (Doctrine(id="d", name="n", mutation_lineage=["a"]), EntrenchmentBasis.DERIVED),
    (Doctrine(id="d", name="n"), EntrenchmentBasis.PROVISIONAL),
])
def test_all_four_entrenchment_classes(doctrine, expected):
    assert entrenchment_basis(doctrine) is expected


def test_precedence_is_ordered_not_scored():
    """A seed doctrine that later acquires scars is STILL what she was founded
    on. Nothing outranks SEED, and there is no blend - the classes are DISCRETE
    STRUCTURAL FACTS, checkable without a magnitude (section 9 bar #5)."""
    loaded = Doctrine(id="d", name="n", is_seed=True, scar_links=["Δ-1"],
                      mutation_lineage=["a"])
    assert entrenchment_basis(loaded) is EntrenchmentBasis.SEED

    scarred_descendant = Doctrine(id="d", name="n", scar_links=["Δ-1"],
                                  mutation_lineage=["a"])
    assert entrenchment_basis(scarred_descendant) is EntrenchmentBasis.SCAR_SURVIVED


def test_the_real_seed_doctrines_classify_as_seed():
    """Against the ACTUAL tracked seed (Ruling 35's regression-pin precedent),
    because a synthetic doctrine would prove only that the getattr works."""
    codex = Codex()
    seeds = [d for d in codex.view().values() if d.is_seed]
    assert seeds, "precondition: the tracked seed holds doctrines"
    assert all(entrenchment_basis(d) is EntrenchmentBasis.SEED for d in seeds)


def test_entrenchment_is_never_stored_anywhere_in_src():
    """THE DOCKET'S SECOND-WRITER ARGUMENT, MADE STRUCTURAL.

    A stored `entrenchment` attribute would be a second writer of something the
    Codex already determines, and the two could disagree - with the FIELD being
    the one people read and the FACTS being the one that is true. Ruling 1's
    argument arriving through a side door, with Ruling 22's fail-silent shape as
    the consequence.
    """
    offenders = []
    for path in H.src_files():
        tree = H.parse(path)
        if tree is None:
            continue
        for node in ast.walk(tree):
            targets = []
            if isinstance(node, ast.Assign):
                targets = list(node.targets)
            elif isinstance(node, (ast.AugAssign, ast.AnnAssign)):
                targets = [node.target]
            for t in targets:
                name = (t.attr if isinstance(t, ast.Attribute)
                        else t.id if isinstance(t, ast.Name) else "")
                if name.startswith("entrenchment"):
                    offenders.append(f"{H.rel(path)}:{node.lineno} assigns {name}")

    assert not offenders, (
        "\n".join(offenders) + "\n\n"
        "  Entrenchment is DERIVED from (is_seed, scar_links, mutation_lineage),\n"
        "  never stored. Call `entrenchment_basis(doctrine)`.\n")


def test_that_scanner_actually_fires():
    """The pin above is pinned (Ruling 32's scanner-fires precedent) - otherwise
    it is green because it sees nothing, which is indistinguishable from green
    because it found nothing."""
    for source in ("class D:\n    def f(self):\n        self.entrenchment = 3\n",
                   "class D:\n    entrenchment_level: int = 0\n",
                   "def f(d):\n    entrenchment = 1\n    return entrenchment\n"):
        tree = ast.parse(source)
        found = [n for n in ast.walk(tree)
                 if isinstance(n, (ast.Assign, ast.AugAssign, ast.AnnAssign))]
        names = []
        for n in found:
            tg = list(n.targets) if isinstance(n, ast.Assign) else [n.target]
            for t in tg:
                names.append(t.attr if isinstance(t, ast.Attribute)
                             else getattr(t, "id", ""))
        assert any(x.startswith("entrenchment") for x in names), source


# =====================================================================
# PIN 8 - criterion 4 finally has a supplier
# =====================================================================

def _ril_with_fracture(tmp_path, doctrine_id):
    ril = RIL(runtime_path=str(tmp_path / "ril.json"))
    ril.threads[IdentityThread.VOID].append({
        "doctrine_id": "D-successor",
        "fallen_ancestor": doctrine_id,
        "ruling_reason": "an identity-anchoring belief fell",
    })
    return ril


def test_ril_flags_a_grounded_identity_conflict(tmp_path):
    """RED AT `eb11b1e`: `ril_identity_conflict` was READ by CMTE and WRITTEN BY
    NOTHING. `aurea_core`'s context builder supplied `echo_origin` and nothing
    else, so criterion 4 passed by absence in every run AUREA ever performed.
    """
    ril = _ril_with_fracture(tmp_path, "D-1")
    assert ril.identity_conflict("D-1") is True

    doctrine = Doctrine(id="D-1", name="x", scar_links=["Δ-1"])
    watched = _Watched(doctrine_id="D-1", pressure=0.95,
                       sustained_cycles=SUSTAIN_CYCLES,
                       triggers=[MutationTrigger.DRPE])

    failed = CMTE().validate(doctrine, watched,
                             {"ril_identity_conflict": ril.identity_conflict("D-1")})
    assert "identity_discontinuity" in failed


def test_an_ungrounded_doctrine_is_abstained_on_not_cleared(tmp_path):
    """GROUND IT OR ABSTAIN. No fracture record naming it → no flag; and the
    proof records that as ABSENT rather than PASS, because silence is not a
    clean bill of health."""
    ril = _ril_with_fracture(tmp_path, "D-1")
    assert ril.identity_conflict("D-2") is False
    assert RIL(runtime_path=str(tmp_path / "bare.json")).identity_conflict("D-1") is False


def test_a_discontinuity_record_is_not_a_fracture(tmp_path):
    """Ruling 42's constitutional-origin VOID entry records that a QUESTION was
    unresolvable. It names no doctrine and is not an identity fracture; reading
    it as one would flag every doctrine in a store whose constitution was
    ambiguous."""
    ril = RIL(runtime_path=str(tmp_path / "ril.json"))
    ril.threads[IdentityThread.VOID].append({
        "record_type": "discontinuity",
        "kind": "constitutional_origin_unresolvable",
        "candidate_ids": ["D-1"],
    })
    assert ril.identity_conflict("D-1") is False

    # STRENGTHENED AFTER A SURVIVING MUTANT (M25). Ruling 42's discontinuity
    # record happens to carry NEITHER `doctrine_id` NOR `fallen_ancestor`, so
    # deleting the record_type skip changed nothing for the entry above and the
    # mutant was undetectable. The skip is guarding the KIND of record, not the
    # keys this one happens to have - so the pin now uses a discontinuity that
    # DOES name a doctrine, which is the shape a future one could easily take.
    ril.threads[IdentityThread.VOID].append({
        "record_type": "discontinuity",
        "kind": "some_future_unresolvable_question",
        "doctrine_id": "D-2",
    })
    assert ril.identity_conflict("D-2") is False, (
        "a question RIL could not resolve is not a fracture RIL detected")


def test_the_live_context_builder_supplies_criterion_4():
    """The wire, not just the surface: `aurea_core` must actually put the key in
    the context it hands DEE. A read surface nothing calls is Ruling 8's
    caller-less directive all over again."""
    import inspect
    source = inspect.getsource(AureaCore._evolve_doctrine)
    assert "ril_identity_conflict" in source
    assert "self.ril.identity_conflict" in source


# =====================================================================
# PIN 9 - the override path's entry (3a:728) is real at last
# =====================================================================

def test_the_override_path_writes_a_cae_entry(tmp_path):
    """3a:728 - the override routes through CTL *and* CAE, and `dee.override`'s
    own docstring says the record is a PRECONDITION for the override, not a side
    effect of it. The CAE half is now real.

    FLAGGED, NOT BUILT: CTL remains unbuilt (out of scope for this docket), so
    the other half of that pair is still absent. `override` guards its CTL call
    with `if self.ctl is not None`, so this pin is not blocked by it - but the
    pair is not yet whole, and saying so is the point.
    """
    codex = Codex(filepath=str(tmp_path / "d.json"))
    cae = CAE(ledger_path=str(tmp_path / "cae.jsonl"))
    dee = DEE(codex=codex, cae=cae)

    ruling = dee.override("D-1", actor="operator", decision="force",
                          danger_index=DANGER_STABLE)

    assert ruling.cae_id is not None, "an UNLOGGED override is out of scope (3a:728)"
    entry = cae.get(ruling.cae_id)
    assert entry["event"] == "override"
    assert entry["target"] == "D-1"
    assert "operator" in entry["collapse_lineage"]


def test_a_rejection_and_a_fermentation_are_recorded_too(tmp_path):
    """3a:111 says mutated, collapsed, OR DISCARDED. A refusal is a decision
    about doctrine and it lands in the ledger like any other."""
    _codex, _sae, dee, cae = _chain(tmp_path)
    dee.cycle(signals={"D-1": {"pressure": 0.95, "drpe": True}},
              proposals={}, context={"D-1": {}})
    for _ in range(SUSTAIN_CYCLES + 1):
        dee.cycle(signals={"D-1": {"pressure": 0.95, "drpe": True}},
                  proposals={}, context={"D-1": {}})

    events = {e["event"] for e in cae.read_all()}
    assert events, "a pass that decided things wrote entries"
    assert events & {"dee_ferment", "dee_rejection", "dee_eligibility"}
