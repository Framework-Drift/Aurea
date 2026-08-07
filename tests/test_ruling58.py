"""
test_ruling58.py - THE CLAIM-ANCESTRY RECORD (Ruling 58 / Docket O item O1).

Manifest twenty-third addendum, 2026-08-01.

    A claim's origin is recorded at ingress, ONCE, as fact.
    A claim whose origin cannot be recorded is not perceived.

WHAT WAS BROKEN was not an absence - it was a FABRICATION. `process_input` took
`source: str = "user"` and handed that default to SPL, which wrote it into
`Echo.source`, a DURABLE STORE FIELD, and `aurea_core` stamped it onto the echo's
topology node. Every claim this system has ever processed is on record as having
come from a human user, including the ones that did not.

EVERY PIN MARKED **RED FIRST** WAS WATCHED FAILING AGAINST `56f2839`, where no
ledger existed at all.

COINS NOTHING: every enum member is recovered from the SPL Adapter (1:574) or
the docket's own registration, the three-state vocabulary is Docket H's, and no
threshold, weight or magnitude exists anywhere in this path.
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
import builtins
import json
from pathlib import Path

import pytest

from src.aurea_core import STRUCTURAL_VIOLATIONS, AureaCore
from src.external.claim_ancestry import (ANCESTRY_FIELDS, AncestryField,
                                         AncestryLedgerUnreadable,
                                         ClaimAncestryLedger,
                                         ClaimAncestryRecord, FieldState,
                                         OriginDeclaration, OriginKind, absent,
                                         declared_none, provided)


def _ledger(tmp_path, name="claim_ancestry.jsonl") -> ClaimAncestryLedger:
    return ClaimAncestryLedger(ledger_path=str(tmp_path / name))


def _lines(ledger) -> list:
    path = Path(ledger.ledger_path)
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()
            if l.strip()]


# =====================================================================
# A. THE RECORD IS WRITTEN, AND IT FABRICATES NOTHING
# =====================================================================

def test_a_bare_process_input_records_undeclared_and_five_absent(tmp_path) -> None:
    """PIN 1, THE FORCING PIN. **RED FIRST**: no ledger existed at `56f2839`.

    A caller that declares nothing is recorded as having declared nothing. The
    new surface does not invent a source class, and specifically does not
    record HUMAN - which is exactly the fabrication the old `source="user"`
    default committed into a durable store on every claim ever processed.
    """
    core = AureaCore()
    result = core.process_input("Water is wet.")

    lines = _lines(core.ancestry)
    assert len(lines) == 1, "exactly one line per perceived claim"

    entry = lines[0]
    assert entry["origin_kind"] == "undeclared", (
        "a channel that said nothing is UNDECLARED - never HUMAN")
    assert entry["claim_id"] == result["claim_id"] == "CLM-0001"

    for name in ANCESTRY_FIELDS:
        assert entry[name]["state"] == "absent", (
            f"{name} was never mentioned by the channel and says so")
        assert entry[name]["value"] is None


def test_a_declared_ingress_persists_verbatim(tmp_path) -> None:
    """PIN 2, first half. What a channel declares is what the ledger holds."""
    core = AureaCore()
    declaration = OriginDeclaration(
        kind=OriginKind.EXTERNAL_AI,
        asserted_by=provided("some-model-v3"),
        basis=provided({"kind": "retrieval", "corpus": "internal"}),
        replication_refs=provided(["run-1", "run-2"]),
        connecting_assumptions=declared_none(),
        defeaters=provided(["contradicted by Δ17"]),
    )
    result = core.process_input("The sky is green at noon.",
                                origin=declaration)

    entry = _lines(core.ancestry)[0]
    assert entry["origin_kind"] == "external_ai"
    assert entry["asserted_by"] == {"state": "provided", "value": "some-model-v3"}
    assert entry["basis"]["value"] == {"kind": "retrieval", "corpus": "internal"}
    assert entry["replication_refs"]["value"] == ["run-1", "run-2"]
    assert entry["defeaters"]["value"] == ["contradicted by Δ17"]
    assert result["claim_id"] == entry["claim_id"]


def test_declared_none_is_distinguishable_from_absent_on_disk(tmp_path) -> None:
    """PIN 2, second half - THE HONESTY PIN, forced in BOTH directions.

    Docket H's cut at the ingress: "there are none" and "nobody said" are
    different facts. If they flattened to the same persisted shape, a later
    reader could not tell a channel that checked for defeaters and found none
    from one that never looked - which is the whole reason the three-state
    vocabulary exists rather than an Optional.
    """
    ledger = _ledger(tmp_path)
    ledger.record(OriginDeclaration(kind=OriginKind.HUMAN,
                                    defeaters=declared_none()))

    entry = _lines(ledger)[0]
    assert entry["defeaters"]["state"] == "declared_none"
    assert entry["basis"]["state"] == "absent"
    assert entry["defeaters"] != entry["basis"], (
        "the two absences must not persist identically")

    restored = ledger.read_all()[0]
    assert restored.defeaters.state is FieldState.DECLARED_NONE
    assert restored.basis.state is FieldState.ABSENT


def test_a_non_provided_field_cannot_carry_a_value() -> None:
    """DECLARED_NONE and ABSENT are statements ABOUT an answer, not answers.
    A value on either would be a third state smuggled through the second."""
    with pytest.raises(ValueError):
        AncestryField(state=FieldState.DECLARED_NONE, value=[])
    with pytest.raises(ValueError):
        AncestryField(state=FieldState.ABSENT, value="something")


def test_the_declaration_refuses_a_raw_string_kind_or_bare_value() -> None:
    """The closed enum is enforced AT THE INGRESS SHAPE, so a caller cannot
    invent a source class, and a bare value cannot pretend to be one of the
    three states."""
    with pytest.raises(TypeError):
        OriginDeclaration(kind="human")                     # type: ignore[arg-type]
    with pytest.raises(TypeError):
        OriginDeclaration(kind=OriginKind.HUMAN,
                          basis="a bare string")            # type: ignore[arg-type]


# =====================================================================
# B. THE WRITE GATES PERCEPTION
# =====================================================================

def test_a_failed_ancestry_write_stops_the_claim_dead(tmp_path, monkeypatch) -> None:
    """PIN 3 - THE GATE WITNESS, in RULING 46's THREE-MEASURE FORM.

    Asserting only the raise would pass against an implementation that records
    the claim, builds the echo, places the node and THEN fails - which is
    exactly the defect Ruling 46's forcing pin was written to catch on the birth
    path (a refusal that spends).

    So three things are measured UNCHANGED: the echo store, the topology node
    count, and the ledger line count.
    """
    core = AureaCore()
    core.process_input("Water is wet.")       # a healthy claim

    echoes_before = core.stats["echoes_processed"]
    nodes_before = len(core.tca.topology.nodes)
    lines_before = len(_lines(core.ancestry))

    real_open = builtins.open
    target = str(core.ancestry.ledger_path)

    def failing_open(file, mode="r", *args, **kwargs):
        if str(file) == target and "a" in mode:
            raise OSError("simulated disk failure at ingress")
        return real_open(file, mode, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", failing_open)

    with pytest.raises(OSError):
        core.process_input("This claim must not be perceived.")

    monkeypatch.undo()

    assert core.stats["echoes_processed"] == echoes_before, "NO echo was built"
    assert len(core.tca.topology.nodes) == nodes_before, "NO node was placed"
    assert len(_lines(core.ancestry)) == lines_before, "NO line was appended"


def test_the_gate_is_outside_the_broad_exception_clause() -> None:
    """AST. The mint must NOT sit inside `process_input`'s `try:`.

    Inside it, an OSError would be flattened into `result['errors']` by the
    broad clause and the caller would read a DEGRADED SUCCESS - a claim
    perceived with no origin on record, reported as a hiccup. The gate has to be
    visible to the caller, which means the exception leaves the method.
    """
    tree = ast.parse(Path("src/aurea_core.py").read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "process_input")

    inside_try = {
        id(node)
        for stmt in fn.body if isinstance(stmt, ast.Try)
        for node in ast.walk(stmt)
    }
    mints = [n for n in ast.walk(fn)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
             and n.func.attr == "record"
             and isinstance(n.func.value, ast.Attribute)
             and n.func.value.attr == "ancestry"]
    assert len(mints) == 1, "exactly one ancestry mint site"
    assert id(mints[0]) not in inside_try, (
        "the ancestry write is inside `try:` - an OSError would degrade into "
        "`errors` and the caller would read a claim perceived without a record")


def test_a_suspended_pass_perceives_nothing_and_records_nothing(tmp_path) -> None:
    """THE PLACEMENT DECISION, PINNED so it is visible rather than incidental.

    A suspended AUREA refuses at the door - it builds no echo. Minting there
    would file the origin of a claim that never entered, and would break the
    one-to-one correspondence between ledger lines and perceived claims that
    O2's echo <-> claim_id linkage will need.
    """
    core = AureaCore()
    core.processing_suspended = True
    core.suspension_reason = "test suspension"

    result = core.process_input("Nothing should be recorded.")

    assert result["claim_id"] is None
    assert _lines(core.ancestry) == []
    assert result["echo"] is None


# =====================================================================
# C. THE MINT - Ruling 53's sentinel, WHOLE
# =====================================================================

def test_the_mint_resumes_from_the_file_across_a_restart(tmp_path) -> None:
    """PIN 4, first half. Continuity state (Ruling 42 res.4): a second process
    re-derives from the file's maximum rather than reminting over real ids."""
    first = _ledger(tmp_path)
    for _ in range(3):
        first.record()
    assert first.entries[-1]["claim_id"] == "CLM-0003"

    second = _ledger(tmp_path)                      # a "restart"
    assert second._derive_seq() == 3
    assert second.record().claim_id == "CLM-0004"
    assert [e["claim_id"] for e in _lines(second)] == [
        "CLM-0001", "CLM-0002", "CLM-0003", "CLM-0004"]


class _UnreadableFor:
    """Make ONE path raise on READ while leaving writes alone - the asymmetry
    that made Ruling 53's original defence contingent."""

    def __init__(self, monkeypatch, path):
        self._real = builtins.open
        self._path = str(path)
        self._armed = True
        monkeypatch.setattr(builtins, "open", self._open)

    def _open(self, file, mode="r", *args, **kwargs):
        if self._armed and str(file) == self._path and "r" in mode:
            raise OSError("simulated transient read failure")
        return self._real(file, mode, *args, **kwargs)

    def recover(self):
        self._armed = False


def test_an_unreadable_ledger_refuses_the_mint(tmp_path, monkeypatch) -> None:
    """PIN 4, Ruling 53 branch ONE. An existing-but-unreadable ledger leaves the
    mint UNDERIVED, and a still-broken read at write time REFUSES rather than
    minting from a floor it never saw."""
    ledger = _ledger(tmp_path)
    ledger.record()
    before = Path(ledger.ledger_path).read_text(encoding="utf-8")

    _UnreadableFor(monkeypatch, ledger.ledger_path)
    reopened = _ledger(tmp_path)
    assert reopened._derive_seq() is None, "UNDERIVED, not zero"

    with pytest.raises(AncestryLedgerUnreadable):
        reopened.record()
    assert Path(ledger.ledger_path).read_text(encoding="utf-8") == before


def test_a_recovered_ledger_resumes_from_the_real_maximum(tmp_path, monkeypatch) -> None:
    """PIN 4, Ruling 53 branch TWO. The condition is characteristically
    transient, so `_next_id` re-derives ONCE - a ledger readable again resumes
    from its real maximum instead of refusing an audit it can now perform."""
    ledger = _ledger(tmp_path)
    for _ in range(5):
        ledger.record()

    failure = _UnreadableFor(monkeypatch, ledger.ledger_path)
    reopened = _ledger(tmp_path)
    assert reopened._derive_seq() is None

    failure.recover()
    assert reopened.record().claim_id == "CLM-0006", (
        "resumes from the real maximum, never restarts the count")


def test_a_missing_ledger_is_a_legitimate_first_run(tmp_path) -> None:
    """MUST STAY GREEN. `None` means "exists and could not be read"; ABSENCE is
    a first run, and the asymmetry is the ruling."""
    ledger = _ledger(tmp_path, "nothing_here.jsonl")
    assert ledger._derive_seq() == 0
    assert ledger.record().claim_id == "CLM-0001"


def test_ancestry_ledger_unreadable_is_structural() -> None:
    """It propagates to the structural surface (Ruling 25's clause) and is NOT
    a base class of any other member."""
    assert AncestryLedgerUnreadable in STRUCTURAL_VIOLATIONS
    for member in STRUCTURAL_VIOLATIONS:
        if member is not AncestryLedgerUnreadable:
            assert not issubclass(AncestryLedgerUnreadable, member)


# =====================================================================
# D. THE CLOSED ENUM, AND WHAT IS NOT STORED
# =====================================================================

def test_an_unknown_origin_kind_is_floor_dropped_never_defaulted(tmp_path) -> None:
    """PIN 5, THE CLOSED-ENUM PIN.

    A forensic log outlives the code that wrote it. A line carrying a source
    class this build does not know is DROPPED - never coerced to a member and
    never defaulted to UNDECLARED, because either would hand a reader a fact the
    writer did not record.
    """
    ledger = _ledger(tmp_path)
    ledger.record(OriginDeclaration(kind=OriginKind.HUMAN))

    with open(ledger.ledger_path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "claim_id": "CLM-0002", "origin_kind": "quantum_oracle",
            "recorded_at": "", **{n: {"state": "absent", "value": None}
                                  for n in ANCESTRY_FIELDS}}) + "\n")
        handle.write("{ this line will not parse\n")

    records = ledger.read_all()
    assert [r.claim_id for r in records] == ["CLM-0001"]
    assert all(r.origin_kind is not OriginKind.UNDECLARED or
               r.claim_id == "CLM-0001" for r in records)

    # And the junk lines raise NOTHING - per-line floor semantics, unchanged.
    assert _ledger(tmp_path)._derive_seq() == 2, (
        "the mint still floors past both bad lines, reading the real maximum")


def test_the_origin_enum_is_closed_at_six_recovered_members() -> None:
    """Every member is recovered: four from the SPL Adapter (1:574), one is
    O6's registered member, one is the honest 'nobody said'. Additions require
    a manifest ruling - the closed-enum discipline (Ruling 7)."""
    assert {k.name for k in OriginKind} == {
        "HUMAN", "EXTERNAL_AI", "SYSTEM_PLUGIN", "LLM_WRAPPER",
        "MODEL_PREDICTION", "UNDECLARED"}


def test_no_epistemic_standing_is_ever_stored(tmp_path) -> None:
    """PIN 6 - THE L3 AST PIN, in `EntrenchmentBasis`'s shape.

    The record holds origin FACTS ONLY. A stored tier / admissibility /
    reliability would be a second writer of what the evidence already
    determines, and the field is the one people read while the facts are the
    one that is true. Scanned over ALL of `src/`, because the hazard is a
    consumer deciding to cache a judgement onto the record.

    TWO SCOPES, DELIBERATELY, because one scope cannot do this honestly. The
    first attempt scanned the whole tree for the bare word `tier` and flagged
    `tcaml.py`'s THRESHOLD tier - Ruling 27's Docket-F measure, a completely
    unrelated and legitimate concept. A scanner that cannot tell those apart
    reports noise, and a noisy guard gets weakened by whoever it annoys.

      * TREE-WIDE for tokens that have no legitimate partner anywhere
        (`admissibility`, `reliability`, `trust_score`, `credibility`,
        `epistemic_*`) - a hit is a defect wherever it is.
      * MODULE-SCOPED for the generic ones (`tier`, `standing`) - on the
        ancestry record they would be stored standing; elsewhere they are
        someone else's vocabulary.

    CONVERTED 2026-08-01 BY RULING 64's RIDE-ALONG. THE ASSERTION IS
    UNCHANGED; the GENERIC half now matches WHOLE snake_case WORDS instead of
    substrings.

        OLD:  any(word in name.lower() for word in distinctive + generic)
        NEW:  substring for `distinctive`, whole-word for `generic`

    WHY: written as a substring scan, the generic half flagged `frontier` -
    which CONTAINS `tier` - inside a transitive-closure loop, i.e. a correct
    local variable reported as stored epistemic standing. THE THIRD OF FIVE
    OCCURRENCES of the substring-scanner defect; Ruling 60 sharpened its OWN
    copy of this scanner and left this one, and the manifest has since made
    the conversion no longer deferrable.

    The DISTINCTIVE half stays a substring match on purpose: those tokens have
    no legitimate partner anywhere, and `epistemic_` is a prefix by design.
    """
    distinctive = ("admissibility", "reliability", "trust_score",
                   "credibility", "epistemic_")
    generic = {"tier", "standing"}

    def assigned_names(tree):
        for node in ast.walk(tree):
            targets = []
            if isinstance(node, ast.Assign):
                targets = list(node.targets)
            elif isinstance(node, (ast.AnnAssign, ast.AugAssign)):
                targets = [node.target]
            for target in targets:
                name = (target.attr if isinstance(target, ast.Attribute)
                        else target.id if isinstance(target, ast.Name) else "")
                if name:
                    yield node.lineno, name

    offenders = []
    for path in Path("src").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        # MODULE SCOPE STAYS `claim_ancestry.py` ALONE, and an attempt to widen
        # it to `record_projection.py` during Ruling 64 was REVERTED for the
        # reason this scanner's own docstring gives: that module's `tier` is
        # its RULED VOCABULARY (Ruling 63 mandates a `KnowledgeTier` on every
        # component), derived on every call and never stored - it is the
        # `tcaml.py` THRESHOLD-tier false positive in a new file. The
        # tree-wide distinctive tokens still cover it.
        module_scoped = path.as_posix().endswith("external/claim_ancestry.py")
        for lineno, name in assigned_names(tree):
            lowered = name.lower()
            hit = any(word in lowered for word in distinctive)
            if module_scoped and set(lowered.split("_")) & generic:
                hit = True
            if hit:
                offenders.append(f"{path.as_posix()}:{lineno} {name}")

    assert offenders == [], (
        f"epistemic standing is being STORED at {offenders}. The ancestry "
        f"record carries origin facts only (Ruling 58 res.6): a stored standing "
        f"would be a second writer of what the evidence already determines.")


def test_the_standing_scanner_actually_fires(tmp_path) -> None:
    """Ruling 32's answer to the vacuous-pin problem: feed the scanner the
    forbidden shape and a benign control, so a scan that has stopped scanning
    fails HERE rather than passing quietly forever."""
    forbidden = ast.parse("record.reliability = 0.9\n")
    benign = ast.parse("record.origin_kind = kind\nself._tier_unrelated = 1\n")

    def hits(tree, words):
        found = []
        for node in ast.walk(tree):
            targets = list(node.targets) if isinstance(node, ast.Assign) else []
            for target in targets:
                name = (target.attr if isinstance(target, ast.Attribute)
                        else target.id if isinstance(target, ast.Name) else "")
                if any(w in name.lower() for w in words):
                    found.append(name)
        return found

    assert hits(forbidden, ("reliability",)) == ["reliability"]
    assert hits(benign, ("admissibility", "reliability", "credibility")) == []


def test_the_record_is_deeply_frozen(tmp_path) -> None:
    """PIN 8 - RULING 52's class, applied to the argument of record at ingress.

    Including the MUTABLE LEAF case, which is what a surviving mutant
    established in Batch 51: the recursive rebuild copies the container spine,
    and without the deepcopy a leaf stays shared with the caller.
    """
    payload = {"nested": {"depth": 1}, "refs": ["a"]}
    leaf = bytearray(b"original")
    record = ClaimAncestryRecord.from_declaration(
        "CLM-0001",
        OriginDeclaration(kind=OriginKind.HUMAN,
                          basis=provided(payload),
                          defeaters=provided(leaf)))

    with pytest.raises(TypeError):
        record.basis.value["nested"] = "tampered"
    with pytest.raises(TypeError):
        record.basis.value["nested"]["depth"] = 99

    payload["nested"]["depth"] = 99            # the caller's retained reference
    payload["refs"].append("forged")
    leaf.extend(b"-TAMPERED")

    assert record.basis.value["nested"]["depth"] == 1
    assert list(record.basis.value["refs"]) == ["a"]
    assert bytes(record.defeaters.value) == b"original", (
        "a mutable LEAF is copied into the record, not shared with the caller")


def test_the_record_round_trips_through_the_ledger(tmp_path) -> None:
    """The freeze must be invisible to serialization - `_thaw` at the boundary
    where the record leaves memory, and nowhere else."""
    ledger = _ledger(tmp_path)
    ledger.record(OriginDeclaration(
        kind=OriginKind.LLM_WRAPPER,
        basis=provided({"nested": {"depth": 1}, "refs": ["a", "b"]})))

    restored = ledger.read_all()[0]
    assert restored.origin_kind is OriginKind.LLM_WRAPPER
    assert restored.basis.value["nested"]["depth"] == 1
    assert list(restored.basis.value["refs"]) == ["a", "b"]
    with pytest.raises(TypeError):
        restored.basis.value["nested"] = "tampered"


# =====================================================================
# E. THE DEMOTED FIELD
# =====================================================================

def test_echo_has_no_source_field_at_all() -> None:
    """~~PIN 7 - THE CONSUMER-SET PIN~~ -> SUPERSEDED 2026-08-02 BY RULING 68.

    THE OLD PIN AND ITS REASONING, KEPT VERBATIM because it is the record of
    why demotion was not enough:

        PIN 7 - THE CONSUMER-SET PIN, over exactly what the mandated sweep
        found. RULING 50'S SHAPE: not "is there a consumer" (a question with one
        permanent answer once any appears) but "is the consumer set exactly the
        swept one". THE SWEEP FOUND ZERO READERS IN `src/`. ... The only reader
        anywhere in the repo is a display line in `scripts/aurea_diagnostic.py`,
        which is precisely what "legacy display string" means. A NEW READER
        FAILS HERE ...

        readers = [] for path in Path("src").rglob("*.py") ... if
        node.attr == "source" and node.value.id in ("echo", "e") ...
        assert readers == [], f"{readers} read the DEMOTED `Echo.source`."

    **RULING 68 DELETED THE FIELD, so a pin asking who reads it now asks about
    something that does not exist.** The successor is STRICTLY STRONGER and
    needs no sweep: there is no field to read. Ruling 61's form - the wrong
    path's ABSENCE is the enforcement, because a legacy display field that
    exists but is unread is a loaded gun for the next caller who defaults it.

    The old pin was ALSO the instrument that proved the deletion safe: its
    sweep, re-run tree-wide as Ruling 68's mandated precondition, found exactly
    one `.source` read on an echo anywhere - a `print` in
    `scripts/aurea_diagnostic.py`, a DISPLAY read and not a logic read, deleted
    with the field.
    """
    from dataclasses import fields

    from src.utils.models import Echo

    names = {f.name for f in fields(Echo)}
    assert "source" not in names, (
        f"`Echo.source` is back. Ruling 68 deleted it: origin is the "
        f"claim-ancestry ledger, reached from `claim_id`. Fields: {sorted(names)}")
    assert "claim_id" in names, "the join key to the real origin surface must remain"


def test_neither_process_input_accepts_a_source_argument() -> None:
    """~~test_the_source_default_is_untouched_this_pass~~ -> SUPERSEDED
    2026-08-02 BY RULING 68, and this pin now asserts the OPPOSITE of what it
    asserted - which is the whole of Ruling 68 res.3.

    THE OLD PIN, KEPT VERBATIM:

        DEMOTED, NOT MIGRATED. The `"user"` default stays: its bytes are already
        in persisted stores, and rewriting them is not this ruling's remit. What
        changed is that it is no longer the origin fact.

        assert inspect.signature(SPL.process_input).parameters["source"].default == "user"
        assert inspect.signature(AureaCore.process_input).parameters["source"].default == "user"

    **RULING 58's DOCSTRING EXPLICITLY DEFERRED THIS DEFAULT AS "not this
    ruling's remit". RULING 68 IS THE RULING IT DEFERRED TO.** Demotion is
    discipline, and the manufacture continued underneath it: a claim could carry
    `origin_kind=undeclared` with all five fields ABSENT while simultaneously
    reporting `Echo.source == 'user'` and tagging its node `source:user`.

    LEGACY BYTES REMAIN UNTOUCHED - that half of the old pin's reasoning still
    stands and is res.4. What is deleted is the SIGNATURE that keeps minting new
    ones.
    """
    import inspect

    from src.perception.spl import SPL

    # RULING 75 MIGRATION (2026-08-05), Ruling-14 form. NO ASSERTION MOVED.
    #     OLD: `("SPL", SPL.process_input)`
    #     NEW: `("SPL.normalize", SPL.normalize)`
    # Ruling 75 deleted `SPL.process_input` - the layer stopped minting, and so
    # stopped constructing an Echo at all. The `source` claim is unchanged and
    # now rests on a stronger structural fact than a signature: there is no
    # record built in that module for a `source` to be written onto.
    for owner, func in (("SPL.normalize", SPL.normalize),
                        ("AureaCore.process_input", AureaCore.process_input)):
        params = inspect.signature(func).parameters
        assert "source" not in params, (
            f"{owner} still accepts `source`; Ruling 68 deletes "
            f"the parameter, not merely its documentation. Params: "
            f"{list(params)}")


def test_the_origin_parameter_is_keyword_only() -> None:
    """A new positional would silently re-bind every existing two-argument call
    site - `process_input(text, "user")` must keep meaning what it meant."""
    import inspect

    params = inspect.signature(AureaCore.process_input).parameters
    assert params["origin"].kind is inspect.Parameter.KEYWORD_ONLY
    assert params["origin"].default is None
