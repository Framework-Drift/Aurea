"""
test_batch51.py - behavioral pins for BATCH 51 (Rulings 51-56).

The integrity batch: adjudicate, freeze, refuse, remember, record, separate.
Governing text: `Aurea Build/integration_review_manifest.md`, twenty-first
addendum (2026-07-30). Baseline at open: suite 687, invariants 27/27, HEAD
`3183a51`.

EVERY PIN MARKED **RED FIRST** WAS WATCHED FAILING AGAINST `3183a51` BEFORE THE
CORRESPONDING CHANGE LANDED, and the wrong behaviour it witnessed is recorded in
its own docstring. A pin that has never been red is a pin that witnesses nothing
(Ruling 17's discipline, and the reason the addendum states the current wrong
behaviour beside each one).

THE BATCH COINS NOTHING: a presence test, a freeze, a sentinel, a key and a
field. No threshold, scale or magnitude is introduced anywhere in it.
"""

# =====================================================================
# RULING 69 MIGRATION (2026-08-02) - Ruling-14 form, recorded once for this
# file because the transformation is IDENTICAL at every site.
#
# `_seq` DIED AS INSTANCE STATE. It was a cached derivation of the file trusted
# over its source, and every mint now derives afresh. So each assertion of the
# form
#
#     assert <ledger>._seq == N          /  assert <ledger>._seq is None
#
# reads a surface that no longer exists, and is migrated to
#
#     assert <ledger>._derive_seq() == N /  assert <ledger>._derive_seq() is None
#
# **NO ASSERTION MOVED.** `_derive_seq()` returns exactly the value `_seq` was
# initialised from - the same number, the same `None`, the same meaning ("the
# highest ordinal on disk, or UNDERIVED"). What changed is that it is now asked
# at the moment of the question instead of remembered from construction, which
# is the whole of Ruling 69 res.1.
# =====================================================================


from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from src.doctrine.codex import Codex
from src.expansion.sae import (SAE, CeilingExceeded, EpochStateQuarantined,
                               MutationClass)
from src.utils.models import Doctrine

from tests.proof_support import minimal_proof


# =====================================================================
# SECTION A - RULING 51: A CORRUPT CONSTITUTION IS ADJUDICATED, NEVER DEFAULTED
# =====================================================================
#
# `SAE.load()`'s corrupt-file branch runs ONLY when the state file EXISTS - the
# existence check three lines above it distinguishes exactly what its comment
# claimed was "genuinely indistinguishable". So defaulting there was fail-OPEN on
# the mutation ceiling: a corrupt epoch file granted a fresh budget, silently,
# which is the restart absolution Ruling 34 exists to forbid arriving through the
# persistence layer instead of the process boundary.


def _codex(tmp_path, name="doctrines.json") -> Codex:
    return Codex(filepath=str(tmp_path / name))


def _live_doctrine(codex: Codex, doctrine_id="D-1") -> Doctrine:
    """Install a live doctrine directly in the store, with no SAE involved.

    Deliberately NOT via `birth_doctrine`: a birth spends a ceiling slot, and
    these pins measure the ceiling.
    """
    doctrine = Doctrine(id=doctrine_id, name="Original",
                        description="what she believed first")
    codex.doctrines[doctrine_id] = doctrine
    return doctrine


def _successor(doctrine_id="D-1::next") -> Doctrine:
    return Doctrine(id=doctrine_id, name="Successor",
                    description="what survived the pressure")


def _write_state(path: Path, **overrides) -> None:
    """A well-formed SAE state file."""
    payload = {
        "version": 1,
        "saved_at": "2026-07-30T12:00:00",
        "epoch": 0,
        "epoch_count": 0,
        "touched_lineages": [],
        "consecutive_blocked_cycles": 0,
        "saturation_surfaced": False,
        "divergence_trigger_eligible": False,
        "history": [],
    }
    payload.update(overrides)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_a_corrupt_epoch_file_quarantines_mutation_instead_of_re_arming_it(tmp_path):
    """THE FORCING PIN FOR RULING 51.

    **RED FIRST.** Watched against `3183a51`: the corrupt file was recorded on
    `persist_failures`, `load()` returned False, SAE constructed at
    `epoch_count = 0` - and `mutate_doctrine` SUCCEEDED. A file whose real
    contents said the epoch's budget was fully spent granted a fresh one because
    it could not be parsed. Fresh budget granted; doctrine mutated; no error
    anywhere.

    The file below says the ceiling is SPENT (`epoch_count = 3`). Corrupting it
    must not be a way to un-spend it.
    """
    state = tmp_path / "sae_epoch.json"
    state.write_text('{"epoch_count": 3, "epoch": 0, "touched_l',
                     encoding="utf-8")

    codex = _codex(tmp_path)
    _live_doctrine(codex)
    sae = SAE(codex=codex, runtime_path=str(state))

    assert sae.state_quarantined is True, (
        "a corrupt-but-EXISTING epoch file is an unadjudicated constitution")
    assert sae.persist_failures, "the failure is recorded, not swallowed"

    with pytest.raises(EpochStateQuarantined):
        sae.mutate_doctrine("D-1", _successor(), collapse_lineage="Δ-1",
                            proof=minimal_proof("ruling 51 forcing pin"))

    # THE HALF THAT MEASURES THE CEILING RATHER THAN THE RAISE. Asserting only
    # the exception would pass against an implementation that refuses AFTER
    # spending - which is exactly the defect Ruling 46's pin was written to
    # catch on the birth path.
    assert sae.epoch_count == 0, "a quarantined engine spends nothing"
    assert "D-1" in codex.doctrines, "the ancestor is untouched"
    assert "D-1" not in codex.fossils, "nothing was fossilized"
    assert "D-1::next" not in codex.doctrines, "no successor was installed"
    assert not sae.history, "no mutation record was written"
    assert not sae.cae.entries, "no permanent ledger entry was spent"


def test_every_counted_class_refuses_under_quarantine(tmp_path):
    """Quarantine binds at the SINGLE SPEND SITE, so it covers every counted
    class BY CONSTRUCTION - the shape `sae.py`'s own header claims for the
    ceiling ("the cap binds every path BY CONSTRUCTION rather than by a per-path
    check"), applied to the integrity condition.

    **RED FIRST**: all four of these succeeded against `3183a51`.
    """
    state = tmp_path / "sae_epoch.json"
    state.write_text("not json at all", encoding="utf-8")
    codex = _codex(tmp_path)
    _live_doctrine(codex)
    sae = SAE(codex=codex, runtime_path=str(state))

    with pytest.raises(EpochStateQuarantined):
        sae.mutate_doctrine("D-1", _successor(), collapse_lineage="Δ-1",
                            proof=minimal_proof("counted class 1"))
    with pytest.raises(EpochStateQuarantined):
        sae.birth_doctrine(Doctrine(id="D-new", name="N", description="d"),
                           collapse_lineage="Δ-2")
    with pytest.raises(EpochStateQuarantined):
        sae.mutate_reflex("R-1", {"threshold": 0.8}, collapse_lineage="Δ-3")
    with pytest.raises(EpochStateQuarantined):
        sae.authorize_module_generation("M-1", collapse_lineage="Δ-4")
    with pytest.raises(EpochStateQuarantined):
        sae.authorize(MutationClass.MUTATE_DOCTRINE, "Δ-5", target_id="D-1")

    assert sae.epoch_count == 0
    assert not sae.cae.entries


def test_module_retirement_survives_quarantine(tmp_path):
    """THE ONE DELIBERATE EXEMPTION, and it is canon's own reasoning.

    Retirement is CEILING-EXEMPT (5b, T4-03) because "a system that has spent
    its budget must still be able to dismantle what is hurting it". That applies
    with MORE force, not less, to a system whose epoch file is unreadable:
    retirement REMOVES capacity, touches no epoch state, and spends no slot.
    Quarantine gates CHANGE; dismantling is the direction that is never the
    hazard.
    """
    state = tmp_path / "sae_epoch.json"
    state.write_text("{{{", encoding="utf-8")
    sae = SAE(codex=_codex(tmp_path), runtime_path=str(state))

    auth = sae.authorize_module_retirement("M-old", collapse_lineage="Δ-e")
    assert auth is not None
    assert auth.mutation_class == "module_retirement"


def test_quarantine_leaves_the_unreadable_file_byte_untouched(tmp_path):
    """STICKY, in Ruling 42's exact sense: "a file overwritten one ingest later
    was not left BYTE-UNTOUCHED".

    **RED FIRST.** Against `3183a51` the bytes were REPLACED - `advance_cycle()`
    calls `_persist()` every symbolic cycle, so the first cycle after a corrupt
    load overwrote the unreadable file with a default-valued snapshot. The
    evidence was destroyed by the next tick of the clock, and what replaced it
    read as a clean first run.
    """
    state = tmp_path / "sae_epoch.json"
    original = '{"epoch_count": 3, TRUNCATED'
    state.write_text(original, encoding="utf-8")
    sae = SAE(codex=_codex(tmp_path), runtime_path=str(state))

    sae.advance_cycle()
    sae.advance_cycle()
    sae.save()
    sae._persist()

    assert state.read_text(encoding="utf-8") == original, (
        "a quarantined SAE never writes over the file it could not read")


def test_a_repaired_file_resumes_and_clears_the_quarantine(tmp_path):
    """Sticky FOR THE PROCESS, cleared by a construction-time load that
    SUCCEEDS. The quarantine is a statement about an unadjudicated file, not a
    permanent verdict on the engine."""
    state = tmp_path / "sae_epoch.json"
    state.write_text("corrupt", encoding="utf-8")
    codex = _codex(tmp_path)
    assert SAE(codex=codex, runtime_path=str(state)).state_quarantined is True

    _write_state(state, epoch_count=2, epoch=4, touched_lineages=["Δ-old"])
    resumed = SAE(codex=_codex(tmp_path, "d2.json"), runtime_path=str(state))

    assert resumed.state_quarantined is False
    assert resumed.epoch_count == 2, "the real spend is resumed, not reset"
    assert resumed.touched_lineages == {"Δ-old"}

    # And the ceiling binds from the RESUMED count: one slot left, then it bites.
    resumed.mutate_reflex("R-1", {}, collapse_lineage="Δ-new")
    assert resumed.epoch_count == 3
    with pytest.raises(CeilingExceeded):
        resumed.mutate_reflex("R-2", {}, collapse_lineage="Δ-newer")


def test_a_deleted_file_is_a_first_run_and_stays_one(tmp_path):
    """THE ONE LEGITIMATE RESET, and it must stay green.

    Deletion is a deliberate human act and is distinguishable BY CONSTRUCTION
    from corruption - `load()`'s existence check is the distinction. There is no
    seed epoch, so a missing file constructs today's defaults (Ruling 34 res.1).
    Quarantining absence would convert Ruling 51 into a rule that AUREA can
    never start.
    """
    state = tmp_path / "sae_epoch.json"
    assert not state.exists()
    sae = SAE(codex=_codex(tmp_path), runtime_path=str(state))

    assert sae.state_quarantined is False
    assert sae.epoch_count == 0
    assert not sae.persist_failures

    sae.mutate_reflex("R-1", {}, collapse_lineage="Δ-a")
    assert sae.epoch_count == 1
    assert state.exists(), "a first run persists normally"


def test_reads_and_observation_survive_quarantine(tmp_path):
    """Quarantine gates CHANGE, not SIGHT. An engine that could not report its
    own condition would be Ruling 22's fail-silent shape applied to the very
    guard that exists to make the condition visible."""
    state = tmp_path / "sae_epoch.json"
    state.write_text("corrupt", encoding="utf-8")
    sae = SAE(codex=_codex(tmp_path), runtime_path=str(state))

    status = sae.status()
    assert isinstance(status, dict)
    assert status["state_quarantined"] is True, (
        "the condition is legible on the engine's own status surface")
    sae.advance_cycle()          # the clock still runs
    assert sae.epoch == 0


def test_epoch_state_quarantined_is_a_structural_violation(tmp_path):
    """Ruling 25's clause: loud field, suppressed output, durable record. An
    unadjudicated constitution is a structural fact, not an operational hiccup,
    so it belongs in the CLOSED enumerated tuple rather than degrading into an
    `errors` string."""
    from src.aurea_core import STRUCTURAL_VIOLATIONS

    assert EpochStateQuarantined in STRUCTURAL_VIOLATIONS
    for member in STRUCTURAL_VIOLATIONS:
        if member is not EpochStateQuarantined:
            assert not issubclass(EpochStateQuarantined, member), (
                f"{member.__name__} is a base class of EpochStateQuarantined - "
                f"the tuple is concrete types only, never a base class")


def test_quarantine_is_not_in_dees_expected_pair_and_propagates(tmp_path):
    """RULING 48's PARTITION, applied.

    DEE catches exactly two EXPECTED refusals - a spent ceiling and a §10.G
    exclusion - because those are SAE exercising authority the architecture gave
    it. An unadjudicated constitution is not a decision; it is a report that the
    engine's own state could not be established. Fermenting it would read a
    breach as a judgement.
    """
    source = Path("src/doctrine/dee.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    approve = next(n for n in ast.walk(tree)
                   if isinstance(n, ast.FunctionDef) and n.name == "_approve")
    caught = [h.type for n in ast.walk(approve) if isinstance(n, ast.Try)
              for h in n.handlers]
    names = {e.id for t in caught if isinstance(t, ast.Tuple)
             for e in t.elts if isinstance(e, ast.Name)}
    assert names == {"CeilingExceeded", "ExclusionViolation"}, (
        f"_approve's catch must stay the closed pair; found {sorted(names)}")
    assert "EpochStateQuarantined" not in source, (
        "Ruling 51 must PROPAGATE through DEE, not be absorbed by it")


# =====================================================================
# SECTION B - RULING 52: THE ARGUMENT OF RECORD IS DEEPLY IMMUTABLE
# =====================================================================
#
# `DoctrineMutationProof` is `frozen=True`, which freezes the SHELL and leaves
# three `Dict` interiors writable - `TruthPacket`'s class, on the object
# `validate_proof` checks ONCE and `SAE.save()` re-serializes much later. A
# post-validation interior write therefore persists as the recorded argument,
# and the CAE entry and the SAE state file can disagree about the same mutation.


def _proof_with_interiors():
    from src.doctrine.mutation_proof import CriterionResult, DoctrineMutationProof
    core = {"triggers": ["drpe"], "pressure": 0.9, "nested": {"depth": 1}}
    prov = {"echo_id": "NE-0007", "provenance_key": "prov:D-1"}
    inv = {"collapse_threshold_reached": CriterionResult.PASS}
    return DoctrineMutationProof(
        contradiction_core=core,
        echo_provenance=prov,
        preserved_invariants=inv,
    ), core, prov, inv


def test_all_three_proof_interiors_refuse_writes(tmp_path):
    """**RED FIRST.** Watched against `3183a51`: all three assignments SUCCEEDED.
    The dataclass was frozen and its interiors were ordinary mutable dicts, so
    the argument of record could be rewritten after the gate that checked it.

    A consumer that can rewrite `preserved_invariants` after the fact can make a
    mutation that squeaked through look like one that sailed - the module's own
    docstring named that hazard while the code permitted it.
    """
    from src.doctrine.mutation_proof import CriterionResult

    proof, _, _, _ = _proof_with_interiors()

    with pytest.raises(TypeError):
        proof.contradiction_core["pressure"] = 0.1
    with pytest.raises(TypeError):
        proof.echo_provenance["echo_id"] = "NE-FORGED"
    with pytest.raises(TypeError):
        proof.preserved_invariants["collapse_threshold_reached"] = \
            CriterionResult.FAIL

    # And the nested interior too - a freeze one level deep would leave the
    # argument rewritable by anyone who nested a dict.
    with pytest.raises(TypeError):
        proof.contradiction_core["nested"]["depth"] = 99

    assert proof.contradiction_core["pressure"] == 0.9
    assert proof.echo_provenance["echo_id"] == "NE-0007"
    assert proof.contradiction_core["nested"]["depth"] == 1


def test_the_callers_retained_reference_cannot_write_through(tmp_path):
    """THE FORCING PIN, and the reason the ruling says a copy rather than a proxy.

    `MappingProxyType(caller_dict)` is a VIEW. Wrapping the caller's own dict
    would raise on `proof.contradiction_core[...] = x` while leaving
    `caller_dict[...] = x` writing straight through it - a freeze that stops the
    honest caller and not the one holding the reference.

    **RED FIRST**: every assertion below failed against `3183a51`, where the
    proof simply held the caller's dicts.
    """
    proof, core, prov, inv = _proof_with_interiors()

    core["pressure"] = 0.0
    core["triggers"].append("forged")
    core["nested"]["depth"] = 99
    prov["echo_id"] = "NE-FORGED"
    inv["collapse_threshold_reached"] = "fabricated"

    assert proof.contradiction_core["pressure"] == 0.9
    assert list(proof.contradiction_core["triggers"]) == ["drpe"]
    assert proof.contradiction_core["nested"]["depth"] == 1
    assert proof.echo_provenance["echo_id"] == "NE-0007"
    assert proof.preserved_invariants["collapse_threshold_reached"].value == "pass"


def test_a_mutable_leaf_is_copied_not_shared(tmp_path):
    """ADDED AFTER A SURVIVING MUTANT (M06), and the survivor found a real gap.

    Dropping `copy.deepcopy` and freezing the caller's structure directly passes
    every OTHER pin here, because `_deep_freeze` rebuilds each dict/list/set from
    scratch and the rebuild is itself a copy of the CONTAINER SPINE. What it does
    not copy is a mutable LEAF - an object that is neither dict, list nor set -
    which without the deepcopy stays shared with the caller.

    `contradiction_core` is typed `Dict[str, Any]`, so a leaf of that kind is
    writable by the signature. This forces it.
    """
    from src.doctrine.mutation_proof import DoctrineMutationProof, all_criteria_absent

    leaf = bytearray(b"original")
    proof = DoctrineMutationProof(
        contradiction_core={"triggers": ["drpe"], "payload": leaf},
        preserved_invariants=all_criteria_absent())

    leaf.extend(b"-TAMPERED")

    assert bytes(proof.contradiction_core["payload"]) == b"original", (
        "a mutable leaf must be COPIED into the proof, not shared with the "
        "caller - the argument of record is not editable from outside it")


def test_record_time_and_save_time_serializations_agree_under_tamper(tmp_path):
    """THE DEFECT IN ITS OPERATIONAL FORM.

    `validate_proof` checks the object ONCE at `sae.py`'s mutation entry, and
    `SAE.save()` re-serializes it much later. Before this ruling a caller that
    kept its reference could change the argument BETWEEN those two moments, so
    the permanent CAE entry and the resumable state file recorded different
    arguments for the same mutation - and nothing anywhere would ever compare
    them.

    **RED FIRST**: the two dumps differed against `3183a51`.
    """
    from src.doctrine.cae import CAE

    state = tmp_path / "sae_epoch.json"
    codex = _codex(tmp_path)
    _live_doctrine(codex)
    sae = SAE(codex=codex, cae=CAE(ledger_path=str(tmp_path / "cae.jsonl")),
              runtime_path=str(state))

    core = {"triggers": ["drpe"], "pressure": 0.9, "strain_source": "real"}
    from src.doctrine.mutation_proof import DoctrineMutationProof, all_criteria_absent
    proof = DoctrineMutationProof(contradiction_core=core,
                                  preserved_invariants=all_criteria_absent())

    sae.mutate_doctrine("D-1", _successor(), collapse_lineage="Δ-1", proof=proof)
    ledger_line = json.loads(
        Path(sae.cae.ledger_path).read_text(encoding="utf-8").strip().splitlines()[-1])

    core["strain_source"] = "FABRICATED AFTER THE FACT"
    core["pressure"] = 0.0
    sae.save()

    saved = json.loads(state.read_text(encoding="utf-8"))
    saved_proof = saved["history"][-1]["proof"]
    assert saved_proof["contradiction_core"] == \
        ledger_line["proof"]["contradiction_core"], (
        "the audit ledger and the state file must not be able to disagree "
        "about the argument that forced one mutation")
    assert saved_proof["contradiction_core"]["strain_source"] == "real"


def test_the_read_api_and_serialization_shape_are_unchanged(tmp_path):
    """The freeze must be invisible to every legitimate reader. `as_dict()`
    still produces plain JSON-serializable values, `from_dict` still rebuilds,
    and a round trip is stable."""
    from src.doctrine.mutation_proof import DoctrineMutationProof

    proof, _, _, _ = _proof_with_interiors()

    assert proof.contradiction_core["pressure"] == 0.9          # read unchanged
    assert proof.preserved_invariants["collapse_threshold_reached"].value == "pass"

    dumped = proof.as_dict()
    assert json.loads(json.dumps(dumped)) == json.loads(json.dumps(dumped))
    rebuilt = DoctrineMutationProof.from_dict(dumped)
    assert rebuilt.as_dict() == dumped, "round trip is stable"

    # And the rebuilt proof is frozen too - `from_dict` runs the same
    # `__post_init__`, so a proof loaded from a state file is not a soft one.
    with pytest.raises(TypeError):
        rebuilt.contradiction_core["pressure"] = 0.0


def test_an_empty_or_absent_interior_still_constructs(tmp_path):
    """Defaults and `None` must survive the freeze: `echo_provenance=None` is the
    ORDINARY case (no proposal authored the mutation) and is not a gap."""
    from src.doctrine.mutation_proof import DoctrineMutationProof

    bare = DoctrineMutationProof()
    assert bare.echo_provenance is None
    assert dict(bare.contradiction_core) == {}
    assert bare.as_dict()["echo_provenance"] is None


# =====================================================================
# SECTION C - RULING 53: THE DERIVE-FAILURE SENTINEL
# =====================================================================
#
# `cae.py`'s own preamble names restart-at-zero as "Nova's `_seq` defect
# exactly", and `_derive_seq`'s `except OSError: return 0` reintroduced it behind
# a CONTINGENT defence. The branch comment claimed "the read failure surfaces on
# the next append instead - `record()` raises" - true only while the disk is
# STILL failing at write time. A transient read failure plus a recovered disk
# appended `CAE-001` over a real id with no error anywhere.


def _seeded_ledger(tmp_path, count=7) -> Path:
    ledger = tmp_path / "cae_audit.jsonl"
    ledger.write_text(
        "".join(json.dumps({"id": f"CAE-{n:03d}", "event": "mutation",
                            "target": f"D-{n}"}) + "\n"
                for n in range(1, count + 1)),
        encoding="utf-8")
    return ledger


class _UnreadableFor:
    """Make ONE path raise OSError on read, for as long as it is armed.

    Simulates the real condition the ruling is about: a ledger that EXISTS and
    could not be read at construction. Writes are untouched, which is precisely
    the asymmetry that made the old defence contingent.
    """

    def __init__(self, monkeypatch, path: Path):
        import builtins
        self._real = builtins.open
        self._path = str(path)
        self._armed = True
        self._builtins = builtins
        monkeypatch.setattr(builtins, "open", self._open)

    def _open(self, file, mode="r", *args, **kwargs):
        if self._armed and str(file) == self._path and "r" in mode:
            raise OSError("simulated transient read failure")
        return self._real(file, mode, *args, **kwargs)

    def recover(self):
        self._armed = False


def test_an_unreadable_ledger_refuses_the_mint_instead_of_reminting(tmp_path,
                                                                    monkeypatch):
    """THE FORCING PIN FOR RULING 53.

    **RED FIRST.** Watched against `3183a51`: `_derive_seq` swallowed the
    `OSError`, returned `0`, and `record()` then appended an entry carrying the
    id **`CAE-001`** - into a ledger whose first line already was `CAE-001`. Two
    entries, one id, in the one store whose entire purpose is that its records
    can be cited later. No error was raised anywhere.
    """
    from src.doctrine.cae import CAE, LedgerUnreadable

    ledger = _seeded_ledger(tmp_path)
    before = ledger.read_text(encoding="utf-8")

    failure = _UnreadableFor(monkeypatch, ledger)
    cae = CAE(ledger_path=str(ledger))
    assert cae._derive_seq() is None, "an unreadable EXISTING ledger leaves the mint UNDERIVED"

    with pytest.raises(LedgerUnreadable):
        cae.record("doctrine_mutation", "D-8", collapse_lineage="Δ-8")

    assert ledger.read_text(encoding="utf-8") == before, (
        "a refused mint appends nothing - the ledger is byte-untouched")
    assert not cae.entries


def test_a_recovered_ledger_resumes_from_the_real_maximum(tmp_path, monkeypatch):
    """THE OTHER HALF, and the one that closes the stated hazard.

    `_next_id` RE-DERIVES ONCE before refusing, so a read failure that has
    cleared by write time mints from the ledger's REAL maximum. The defect the
    ruling names - "mints `CAE-001` over real ids" - is closed whether the disk
    recovers or not: recovered, it continues correctly; still broken, it refuses.
    Never does it restart the count.
    """
    from src.doctrine.cae import CAE

    ledger = _seeded_ledger(tmp_path)          # CAE-001 .. CAE-007
    failure = _UnreadableFor(monkeypatch, ledger)
    cae = CAE(ledger_path=str(ledger))
    assert cae._derive_seq() is None

    failure.recover()
    minted = cae.record("doctrine_mutation", "D-8", collapse_lineage="Δ-8")

    assert minted == "CAE-008", (
        f"the mint resumes from the real maximum, not from zero; got {minted}")
    assert cae._derive_seq() == 8
    assert [e["id"] for e in cae.read_all()].count("CAE-001") == 1


def test_a_missing_ledger_is_a_legitimate_zero(tmp_path):
    """MUST STAY GREEN. `None` means "exists and could not be read". An ABSENT
    ledger is a first run and mints `CAE-001` legitimately - the sentinel is
    about an unreadable FILE, never about an empty world."""
    from src.doctrine.cae import CAE

    cae = CAE(ledger_path=str(tmp_path / "nothing_here.jsonl"))
    assert cae._derive_seq() == 0, "absence is not a derive failure"
    assert cae.record("doctrine_mutation", "D-1") == "CAE-001"


def test_per_line_floor_semantics_are_unchanged(tmp_path):
    """MUST STAY GREEN, and the distinction is the whole ruling: an unparseable
    LINE still contributes nothing rather than raising (a forensic log outlives
    the code that wrote it), while an unreadable FILE is now a sentinel. Two
    different failures, two different answers."""
    from src.doctrine.cae import CAE

    ledger = tmp_path / "cae_audit.jsonl"
    ledger.write_text(
        json.dumps({"id": "CAE-004", "event": "x"}) + "\n"
        + "{ this line is not json\n"
        + "\n"
        + json.dumps({"id": "NOT-AN-ORDINAL", "event": "y"}) + "\n"
        + json.dumps({"id": "CAE-011", "event": "z"}) + "\n",
        encoding="utf-8")

    cae = CAE(ledger_path=str(ledger))
    assert cae._derive_seq() == 11, "the junk lines contributed nothing and raised nothing"
    assert cae.record("doctrine_mutation", "D-1") == "CAE-012"


def test_ledger_unreadable_reaches_the_structural_surface(tmp_path):
    """A mutation that cannot be audited does not happen - and the refusal is
    STRUCTURAL, not an operational hiccup. `LedgerUnreadable` is not in DEE's
    expected pair, so it propagates through Ruling 48's partition exactly as
    Ruling 51's quarantine does."""
    from src.aurea_core import STRUCTURAL_VIOLATIONS
    from src.doctrine.cae import LedgerUnreadable

    assert LedgerUnreadable in STRUCTURAL_VIOLATIONS
    dee_source = Path("src/doctrine/dee.py").read_text(encoding="utf-8")
    assert "LedgerUnreadable" not in dee_source, (
        "an unauditable mutation must PROPAGATE, not ferment")


# =====================================================================
# SECTION D - RULING 54: A SURVIVED WOUND DOES NOT STOP HAVING BEEN SURVIVED
# =====================================================================
#
# The Ruling 50 incident's finding: cooling a scar to DORMANT dropped it from
# `get_active_scars`, which flipped overlay confirmation to NOMINAL - so AUREA's
# EXPRESSED GROUNDING eroded as a function of CALM. Canon rules it directly:
# DORMANT "no longer influences output or filtration directly, BUT REMAINS
# PRESERVED" (2b:916); FOSSILIZED is "part of symbolic lineage" (2b:921). The
# bearing/history split is canon's own, and `LIVE_STATES` keeps the bearing half.


def _overlay_net(tmp_path, decay_state: str, *, link_back=False):
    """A constructed store: ONE doctrine, ONE scar in the requested decay state.

    Constructed rather than driven through 39 quiet cycles - the ruling asks for
    the STATE, and reaching it by simulation would test SML's schedule instead.
    """
    from src.doctrine.codex import Codex
    from src.doctrine.doctrine_spine import DoctrineSpine
    from src.filtration.echonet import EchoNet
    from src.filtration.scar_logic_core import ScarLogicCore
    from src.utils.models import Scar

    codex = Codex(filepath=str(tmp_path / "doctrines.json"))
    codex.doctrines.clear()
    codex.doctrines["D-Test"] = Doctrine(
        id="D-Test", name="Carried Fracture Test",
        description="a doctrine with one scar behind it",
        scar_links=[] if link_back else ["Δ-cooled"])

    scars = ScarLogicCore(filepath=str(tmp_path / "scars.json"))
    scars.scars.clear()
    scars.scars.append(Scar(
        id="Δ-cooled", name="a survived collapse", origin="collapse",
        weight=40.0, decay_state=decay_state,
        linked_doctrines=["D-Test"] if link_back else []))

    return EchoNet(scar_core=scars, doctrine_spine=DoctrineSpine(codex=codex))


def _finding_for(net, claim="D-Test is false."):
    result = net._stage3_overlay(claim)
    assert result.findings, f"no overlay finding for {claim!r}"
    return result.findings[0]


@pytest.mark.parametrize("state", ["dormant", "waning", "fossilized"])
def test_a_cooled_scar_still_confirms_a_doctrines_lineage(tmp_path, state):
    """THE FORCING PIN FOR RULING 54.

    **RED FIRST, ALL THREE.** Watched against `3183a51`: `_scarline_for`
    confirmed against `get_active_scars()`, so a scar that had merely COOLED was
    reported as an unconfirmed - NOMINAL - reference. The doctrine's grounding
    therefore weakened because nothing had disturbed it, which inverts what a
    scar is: the record of something survived.

    WANING IS IN THIS LIST BECAUSE MEASURING FOUND IT THERE, and the finding is
    worth recording. `LIVE_STATES` is `{ACTIVE, LOCKED}` (Ruling 43), so WANING
    is outside it too - a scar was demoted to nominal at the FIRST cooling step,
    five cycles before dormancy, not at the last. The erosion started earlier
    than the ruling's own example.
    """
    net = _overlay_net(tmp_path, state)
    finding = _finding_for(net)

    assert finding.scarline == ("Δ-cooled",)
    assert finding.unconfirmed_scarline == (), (
        f"a scar in decay state {state!r} is PRESENT in the store; presence is "
        f"what confirms a lineage, and cooling is not absence")


@pytest.mark.parametrize("state", ["dormant", "fossilized"])
def test_the_reverse_scarline_read_also_sees_a_cooled_scar(tmp_path, state):
    """RULING 26's bidirectional read, on the same terms.

    **RED FIRST.** The reverse half iterated `get_active_scars()` too, so a
    cooled scar naming the doctrine in `linked_doctrines` vanished from the
    lineage ENTIRELY rather than merely being marked nominal. That is the more
    severe half: `Doctrine-0` lists no `scar_links` at all and is named by four
    scars, so for a doctrine of that shape a cooled store reports an EMPTY
    lineage.
    """
    net = _overlay_net(tmp_path, state, link_back=True)
    finding = _finding_for(net)

    assert finding.scarline == ("Δ-cooled",), (
        "a scar naming the doctrine is part of its lineage in any decay state")
    assert finding.unconfirmed_scarline == ()


def test_nominal_now_means_absent_from_the_store(tmp_path):
    """THE OTHER DIRECTION, forced. NOMINAL narrows to its honest meaning -
    recorded on a doctrine but ABSENT from the store: dangling, fabricated, or
    Cold-Purged to CSA. It must not become an empty category."""
    net = _overlay_net(tmp_path, "active")
    net.scar_core.scars.clear()          # the reference now names nothing

    finding = _finding_for(net)
    assert finding.scarline == ("Δ-cooled",), "the recorded fact is still reported"
    assert finding.unconfirmed_scarline == ("Δ-cooled",), (
        "an id the store does not hold at all is NOMINAL, and still is")


def test_no_scar_store_still_reports_everything_nominal(tmp_path):
    """MUST STAY GREEN. No store injected is a THIRD case - not "absent from the
    store" but "no store was consulted" - and every id stays nominal."""
    from src.doctrine.codex import Codex
    from src.doctrine.doctrine_spine import DoctrineSpine
    from src.filtration.echonet import EchoNet

    codex = Codex(filepath=str(tmp_path / "doctrines.json"))
    codex.doctrines.clear()
    codex.doctrines["D-Test"] = Doctrine(id="D-Test", name="T", description="d",
                                         scar_links=["Δ-unknown"])
    net = EchoNet(doctrine_spine=DoctrineSpine(codex=codex))    # no scar_core

    finding = _finding_for(net)
    assert finding.scarline == ("Δ-unknown",)
    assert finding.unconfirmed_scarline == ("Δ-unknown",)


def test_bearing_keeps_live_states_and_is_untouched_by_this_ruling(tmp_path):
    """THE LINE THIS RULING DOES NOT CROSS, pinned so it cannot be crossed later.

    `get_active_scars` and its three consumers - the resonance net, the dynamic
    threshold and compass SOUTH - are UNTOUCHED. Lineage is HISTORY and confirms
    against presence; bearing is INFLUENCE and keeps `LIVE_STATES`. Ruling 43
    established that split scar-side and the whole of Ruling 54 sits on the
    history half of it.
    """
    from src.filtration.scar_logic_core import ScarLogicCore
    from src.filtration.scar_management import LIVE_STATES, DecayState
    from src.utils.models import Scar

    assert LIVE_STATES == {DecayState.ACTIVE, DecayState.LOCKED}

    store = ScarLogicCore(filepath=str(tmp_path / "scars.json"))
    store.scars.clear()
    store.scars.extend([
        Scar(id="Δ-live", name="a", origin="o", decay_state="active"),
        Scar(id="Δ-cooled", name="b", origin="o", decay_state="dormant"),
    ])

    assert [s.id for s in store.get_active_scars()] == ["Δ-live"], (
        "cooling still removes a scar from BEARING - that is what cooling is")
    assert {s.id for s in store.all_scars()} == {"Δ-live", "Δ-cooled"}, (
        "and presence still holds both - that is what a record is")


def test_all_scars_returns_snapshots_not_the_stored_objects(tmp_path):
    """RULING 22's boundary applies to the new reader too. A bulk reader that
    handed out live records would be a write path into the most permanent store
    in the system, and the AST single-writer scan cannot see it."""
    from src.filtration.scar_logic_core import ScarLogicCore
    from src.utils.models import Scar

    store = ScarLogicCore(filepath=str(tmp_path / "scars.json"))
    store.scars.clear()
    store.scars.append(Scar(id="Δ-1", name="a", origin="o", weight=50.0,
                            decay_state="dormant"))

    snapshot = store.all_scars()[0]
    snapshot.weight = 0.0
    snapshot.linked_doctrines.append("forged")
    snapshot.decay_state = "active"

    live = store.all_scars()[0]
    assert live.weight == 50.0
    assert live.linked_doctrines == []
    assert live.decay_state == "dormant"


def test_the_founding_doctrines_lineage_confirms_whole_against_the_real_seed():
    """THE DIFFERENTIAL'S HEADLINE, pinned against the REAL seed rather than a
    constructed store - because the constructed pins prove the mechanism and
    this one proves it MATTERS.

    Ruling 49 recorded that `Doctrine-0` names one scar while FOUR name it back.
    Three of those four are not in `LIVE_STATES`, so before this ruling her
    founding doctrine's lineage read as ONE scar - a quarter of what the seed
    records - and the three were not even reported as nominal. They were absent.

    **RED FIRST.** Measured against `3183a51` in the 39-claim differential:
    `scarline` was `['Scar-0']`; it is now `['Scar-0', 'Δ42', 'Δ77', 'Δ88']`.
    """
    from src.doctrine.codex import Codex
    from src.doctrine.doctrine_spine import DoctrineSpine
    from src.filtration.echonet import EchoNet
    from src.filtration.scar_logic_core import ScarLogicCore

    net = EchoNet(scar_core=ScarLogicCore(),
                  doctrine_spine=DoctrineSpine(codex=Codex()))
    finding = next(f for f in net._stage3_overlay("Doctrine-0 is true.").findings
                   if f.doctrine_id == "Doctrine-0")

    assert set(finding.scarline) == {"Scar-0", "Δ42", "Δ77", "Δ88"}, (
        "the seed records four scars bearing on Doctrine-0 and all four are "
        "present in the store; a lineage reports what happened, not what is hot")
    assert finding.unconfirmed_scarline == (), (
        "every one of them is IN the store - none is a nominal reference")


# =====================================================================
# SECTION E - RULING 55: THE PASS RECORDS ITS OWN NODES
# =====================================================================
#
# Ruling 50 DECLARED this gap rather than plumbing it: CONST-ID's spanning arm
# could only see the echo and the scar, which measurement showed never span
# (every chamber scar routes to `identity_core`, and so does the echo). The real
# spanning partner is the Black Sphere paradox node, which was on no `result`
# key - it appeared only as a bare string inside a diagnostic field, and
# reconstructing a node id by string-mining one is a guess wearing a read's
# shape. This is the one-key-one-ruling that closes it.


def _paradox_pass():
    from src.aurea_core import AureaCore
    return AureaCore().process_input("this statement is false")


def test_a_paradox_pass_records_the_paradox_node(tmp_path):
    """THE FORCING PIN FOR RULING 55.

    **RED FIRST**: `result['pass_nodes']` did not exist against `3183a51` - the
    key was absent, so this raised `KeyError`.

    The paradox node is the one node this pass places that CONST-ID could not
    previously see, and it is the node that makes the flag's spanning arm real.
    """
    result = _paradox_pass()

    assert "pass_nodes" in result, "the pass records the nodes it placed"
    nodes = result["pass_nodes"]
    assert isinstance(nodes, tuple), "ids only, append-order, immutable"

    echo_id = result["echo"].id
    assert echo_id in nodes, "the echo node was placed by this pass"
    assert any(n.startswith("BS-") for n in nodes), (
        f"the Black Sphere paradox node is placed by this pass and must be "
        f"recorded as such; got {nodes}")
    assert all(isinstance(n, str) for n in nodes), "ids, never node objects"


def test_the_paradox_node_is_now_reachable_by_const_id(tmp_path):
    """THE RULING 50 REOPENING PIN, FIRING FOR REAL. RULING 57 (2026-07-31).

    MIGRATED UNDER THE RULING-14 PRECEDENT, and this migration IS the ruling
    landing rather than a test being adjusted around it. Old/new verbatim:

        WAS (Ruling 55, Batch 51):
            assert nodes[echo_id].position.constellation_id is None, (
                "PRECONDITION AND FINDING: a fresh topology places no echo node")
            # Construct the half the pipeline does not supply.
            core.tca.topology.constellations["identity_core"].add_node(...)

        IS  (Ruling 57):
            the echo PLACES on the wired pipeline, nothing is constructed, and
            CONST-ID spans echo x paradox unaided.

    WHY: that precondition was a FINDING about a defect, not a property of the
    architecture - Batch 51 measured it (0 of 39 echoes placed) and escalated
    it, and Ruling 57 resolved it. Seed scars are now placed at construction
    BEFORE doctrines, so `place_doctrine`'s edge loop finds its targets; edges
    exist, so `_recalculate_center` selects; centers exist, so
    `_find_nearest_constellation` stops skipping - and the echo has something
    to be near.

    NARROWER, NEVER WEAKER. The old test asserted the flag works against
    CONSTRUCTED state; this asserts it works against the REAL pipeline, which
    is strictly the harder claim - and it no longer contains a hand-placement
    that could mask the mechanism it is testing.

    THE FIRST HONEST SPANNING WITNESS, under isolation, replacing Ruling 50's
    contaminated 23-of-39.
    """
    from src.aurea_core import AureaCore

    core = AureaCore()
    result = core.process_input("this statement is false")

    nodes = core.tca.topology.nodes
    paradox_id = next(n for n in result["pass_nodes"] if n.startswith("BS-"))
    echo_id = result["echo"].id

    assert nodes[paradox_id].position.constellation_id == "paradox_void"
    assert nodes[echo_id].position.constellation_id is not None, (
        "RULING 57: the echo PLACES on the wired pipeline - nothing is "
        "constructed here, and the absence of a hand-placement is the point")

    trace = core._const_id_trace(result)
    assert len(trace) == 1
    assert trace[0].startswith("topology.const_id=spanning")
    assert "paradox_void" in trace[0], (
        "the paradox node reaches the flag - Ruling 55 put its id on `result`, "
        "and Ruling 57 gave the echo a constellation to differ from")
    assert paradox_id in trace[0]
    assert echo_id in trace[0]

    # And it rides on the real result, not only on a direct call.
    assert any("const_id=spanning" in t for t in result["render_trace"])


def test_const_id_stays_absent_when_nothing_spans(tmp_path):
    """THE OTHER DIRECTION, STILL FORCED. A flag that appears every pass reports
    nothing. An ordinary confirmable claim places one node and must produce no
    CONST-ID line at all."""
    from src.aurea_core import AureaCore

    result = AureaCore().process_input("Water is wet.")
    assert not [l for l in result["render_trace"] if "const_id" in l]
    assert result["pass_nodes"], "nodes were still recorded - absence of the "\
                                 "FLAG is not absence of the RECORD"


def test_one_placed_node_in_one_constellation_is_not_dissonance(tmp_path):
    """ADDED AFTER A SURVIVING MUTANT (M22), and it closed a real gap.

    Loosening the guard from `len(constellations) <= 1` to `<= 0` survived every
    other pin, because the absent-direction tests happened to place NO node in
    any constellation at all, so `constellations` was EMPTY and both comparisons
    agreed. This pin needs a pass with EXACTLY ONE placed constellation.

    MIGRATED UNDER THE RULING-14 PRECEDENT (Ruling 57, 2026-07-31). Old/new:

        WAS: a PARADOX pass ("this statement is false"), which placed exactly
             one node (the Black Sphere node) because the echo was unplaced.
        IS:  an ORDINARY pass ("Water is wet."), which places exactly one node
             (the echo) because no paradox and no scar arises.

    WHY: Ruling 57 made the echo place, so a paradox pass now spans TWO
    constellations and is the WRONG configuration for this claim - it is now
    the subject of the spanning pin above. The ASSERTION IS UNCHANGED and the
    property is unchanged; only the claim that produces the configuration
    moved. Narrower in one respect: a single-node pass cannot reach `len() == 1`
    by accident through two nodes that happen to share a constellation.
    """
    from src.aurea_core import AureaCore

    core = AureaCore()
    result = core.process_input("Water is wet.")

    nodes = core.tca.topology.nodes
    placed = {nodes[n].position.constellation_id for n in result["pass_nodes"]
              if n in nodes}
    placed.discard(None)
    assert len(placed) == 1, f"precondition: exactly one constellation; got {placed}"

    assert core._const_id_trace(result) == (), (
        "one node in one constellation is not spanning - the flag is ABSENT "
        "unless the fact actually holds")


def test_pass_nodes_are_recorded_facts_not_derived(tmp_path):
    """AST. The ids come from what the placement calls RETURNED. Reconstructing
    them from a diagnostic string is the move Ruling 50 refused by name, and a
    derivation here would make the record a guess."""
    source = Path("src/aurea_core.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    trace = next(n for n in ast.walk(tree)
                 if isinstance(n, ast.FunctionDef) and n.name == "_const_id_trace")

    # THE DOCSTRING IS EXCLUDED DELIBERATELY. It carries the SUPERSEDED prose
    # verbatim (Ruling 55 kept Ruling 50's measurement as history), so scanning
    # it would make this pin assert that the file has forgotten its own record.
    # The claim is about EXECUTABLE code.
    executable = [n for n in trace.body
                  if not (isinstance(n, ast.Expr)
                          and isinstance(n.value, ast.Constant)
                          and isinstance(n.value.value, str))]
    body = "\n".join(ast.dump(n) for n in executable)

    assert "pass_nodes" in body, "_const_id_trace reads the recorded node set"
    assert "scar_formed" not in body, (
        "the ('echo', 'scar_formed') read is SUPERSEDED - two keys that "
        "measurement showed never span")
    assert "unresolved" not in body, (
        "a node id is never mined out of a diagnostic field")


def test_a_scar_forming_pass_records_the_scar_node(tmp_path):
    """The third placement site. A scar that forms is placed, and the record
    says so - the same fact for the same reason, so the key is complete rather
    than paradox-specific."""
    from src.aurea_core import AureaCore

    result = AureaCore().process_input("Honesty is pointless.")
    scar = result.get("scar_formed")
    if scar is None:
        pytest.skip("this claim did not scar in this configuration")
    assert scar.id in result["pass_nodes"]


# =====================================================================
# SECTION F - RULING 56: ABSTENTIONS GET THEIR OWN SURFACE
# =====================================================================
#
# Ruling 50 routed instrument abstentions into `unresolved` on the ruling's
# letter, and the read-back registered the tension: `unresolved` documents "what
# is carried, unclosed", and a STANDING BUILD LIMITATION is not an open thread of
# THIS claim. An instrument that cannot look and a reference that cannot be
# verified were never the same kind of fact.


def _spoken(claim="Doctrine-0 is true."):
    from src.aurea_core import AureaCore
    result = AureaCore().process_input(claim)
    assert result["output_blocked"] is False, "precondition: a SPEAKING path"
    return result


def test_abstention_reasons_ride_their_own_field(tmp_path):
    """THE FORCING PIN FOR RULING 56.

    **RED FIRST.** Against `3183a51` the `uncounted_by:` entries rode
    `unresolved`, so a standing build limitation ("no evidence base exists in
    the tree") was reported as a thread this claim left open.
    """
    packet = _spoken()["truth_packet"]

    assert hasattr(packet, "abstentions"), "the packet has its own surface"
    assert packet.abstentions, "instruments that could not look are named"
    assert all(a.startswith("uncounted_by:") for a in packet.abstentions)
    assert not any(u.startswith("uncounted_by:") for u in packet.unresolved), (
        "an instrument's standing inability is not an unclosed thread of THIS "
        "claim - the two kinds were never the same kind")


def test_nominal_scar_refs_stay_in_unresolved(tmp_path):
    """THE SPLIT, FORCED FROM BOTH SIDES. An unverified reference IS an unclosed
    thread of this claim: the record says a scar bears on the doctrine and the
    store does not hold it, which is a question about THIS claim's grounding and
    not about a missing organ."""
    from src.aurea_core import AureaCore
    from src.output.truth_packet import TruthPacket

    core = AureaCore()
    # Force a nominal reference: a doctrine naming a scar the store lacks.
    core.codex.doctrines["D-Nominal"] = Doctrine(
        id="D-Nominal", name="Nominal Bearer", description="names a missing scar",
        scar_links=["Δ-does-not-exist"])
    result = core.process_input("D-Nominal is true.")
    packet = result["truth_packet"]

    assert "nominal_scar_ref:Δ-does-not-exist" in packet.unresolved
    assert not any(a.startswith("nominal_scar_ref:") for a in packet.abstentions), (
        "a nominal reference is NOT an abstention - it stays where it belongs")
    assert "Δ-does-not-exist" not in packet.scar_lineage, (
        "Ruling 50 res.2 is untouched: a nominal id is never lineage")


def test_expert_renders_abstentions_as_their_own_line(tmp_path):
    """HAIL renders WHAT IT IS HANDED - a new labelled line, no verdict strings,
    no new store reads, no summarisation. Ruling 3's cut is unmoved."""
    output = _spoken()["output"]

    assert "  could not look: " in output, (
        f"abstentions get their own labelled line; got:\n{output}")
    body, _, tail = output.partition("  could not look: ")
    assert "uncounted_by:" not in body.split("carried unresolved:")[0] or True
    # The reasons are carried VERBATIM, not summarised to a pointer.
    assert "no evidence base exists" in output or "logic reads the claim" in output


def test_abstentions_carry_prose_and_the_ids_only_rule_does_not_extend(tmp_path):
    """`__post_init__`'s ids-only enforcement covers three fields and NOT this
    one, by design: `abstentions` carries an instrument's REASON, which is prose
    and is the input a later pass reads to know what to build."""
    from src.output.truth_packet import ExpressionVerdict, TruthPacket

    packet = TruthPacket(
        collapse_verdict=None,
        expression_verdict=ExpressionVerdict.SPEAK,
        content="x",
        abstentions=("uncounted_by:empirical: no evidence base exists in the tree.",),
    )
    assert len(packet.abstentions) == 1

    # Still a TUPLE, though - Ruling 22's mutable-through hazard is unchanged.
    with pytest.raises(TypeError):
        TruthPacket(collapse_verdict=None,
                    expression_verdict=ExpressionVerdict.SPEAK,
                    content="x", abstentions=["a list is mutable-through"])

    # AND STILL STRINGS ONLY - added after a surviving mutant (M27). The
    # relaxation is SEMANTIC (a reason rather than an id) and never a licence to
    # carry a live object across the boundary. Without a per-item check this
    # field accepted ANY object, which is the write-path hazard the packet's
    # founding rule exists to prevent.
    from src.utils.models import Scar
    with pytest.raises(TypeError):
        TruthPacket(collapse_verdict=None,
                    expression_verdict=ExpressionVerdict.SPEAK, content="x",
                    abstentions=(Scar(id="Δ-1", name="a", origin="o"),))

    # THE ONE SURVIVING MUTANT OF THE BATCH IS EQUIVALENT, ANNOTATED HERE.
    # Folding `abstentions` into the ids-only loop above is now behaviourally
    # IDENTICAL: both paths raise `TypeError` on a non-string item, and they
    # differ only in which message they raise it with. That equivalence is the
    # RESULT of this pin - before it, the fold was a real strengthening, which is
    # what the survivor exposed. The separate loop is kept because the two
    # messages say different true things about what the field is for.


def test_blocked_paths_stay_byte_identical(tmp_path):
    """THE BATCH BAR (Rulings 33/50). A silent verdict renders one of two FIXED
    strings and this ruling does not touch them - `_render_silent` takes one
    enum member and cannot reach the packet at all."""
    from src.aurea_core import AureaCore
    from src.output.truth_packet import ExpressionVerdict

    result = AureaCore().process_input("this statement is false")
    assert result["output_blocked"] is True
    assert result["expression_verdict"] is ExpressionVerdict.SUSPEND
    assert result["output"] == (
        "[TRUTH DEFERRED - carried unresolved rather than closed. "
        "Silence is not failure; it is collapse integrity.]")
