"""
test_ruling69.py - RULING 69: WRITER OWNERSHIP, the last verification finding.

**The mint derives from the record at the moment of minting, because a counter
is a cached derivation and this house has refused that structure twice already**
(Ruling 63 at the projection, Ruling 65 at the topology, this at the mint).

WHERE THE REST OF THIS RULING'S PINS LIVE:
`tests/test_verification_pass.py` carries the three collected witnesses this
ruling closes - the last three of the original nineteen. They were written
against the DEFECT at `0b2072c`, carry its measured values (four lines, two
distinct ids, on each ledger), and Ruling 69 retired them in place.

THE HOISTED HELPER GETS ITS OWN PINS HERE, per Ruling 63's mandate: a shared
helper guarded only through its consumers is guarded by accident - that ruling
shipped a `deep_freeze` whose dict rebuild and sequence rebuild could each be
deleted without a single test in its own file noticing.
"""

from __future__ import annotations

import ast
import builtins
import threading
from pathlib import Path

import pytest

from src.doctrine.cae import CAE, LedgerUnreadable
from src.external.claim_ancestry import (AncestryLedgerUnreadable,
                                         ClaimAncestryLedger, OriginDeclaration,
                                         OriginKind)
from src.external.prediction_ledger import (PredictionLedger,
                                            PredictionLedgerUnreadable,
                                            provided)
from src.goals.goal_ledger import (GoalKind, GoalLedger, GoalLedgerUnreadable,
                                   GoalLevel, GoalProvenance)
from src.utils.ledger_mint import (derive_max_ordinal, mint_lock,
                                   ordinal_pattern)

REPO = Path(__file__).resolve().parents[1]

# One row per ledger: build, mint-one, prefix, first id, typed refusal.
LEDGERS = [
    ("cae", lambda p: CAE(ledger_path=str(p)),
     lambda L: L.record(event="e", target="T"),
     "CAE-", "CAE-001", LedgerUnreadable),
    ("ancestry", lambda p: ClaimAncestryLedger(ledger_path=str(p)),
     lambda L: L.record(OriginDeclaration(kind=OriginKind.HUMAN)).claim_id,
     "CLM-", "CLM-0001", AncestryLedgerUnreadable),
    ("prediction", lambda p: PredictionLedger(ledger_path=str(p)),
     lambda L: L.commit(expected_result="x",
                        success_criteria=provided("s")).prediction_id,
     "PRD-", "PRD-0001", PredictionLedgerUnreadable),
    # RULING 72 MIGRATION (2026-08-03), Ruling-14 form. NO ASSERTION MOVED -
    # one row added, so every parametrized claim in this file now also binds
    # the goal ledger. It is the shared mint's SECOND consumer (Ruling 69
    # res.5), so the interleave, the absent counter, the typed refusal and the
    # torn-line property are its properties too, inherited rather than
    # re-argued at a new prefix.
    #
    # `ensure_genesis` is deliberately NOT called here: genesis is a separate
    # act, and these rows measure the MINT. A constructor that seeded would
    # have made this row impossible to write, which is one of the reasons
    # genesis is not in `__init__`.
    ("goal", lambda p: GoalLedger(ledger_path=str(p)),
     lambda L: L.commit(desired_state="x", kind=GoalKind.RESEARCH,
                        level=GoalLevel.PROJECT,
                        provenance=GoalProvenance.EXTERNAL_PROPOSAL,
                        asserter="tester").goal_id,
     "GLC-", "GLC-0001", GoalLedgerUnreadable),
]
IDS = [row[0] for row in LEDGERS]


# =====================================================================
# (b) INTERLEAVED TWO-INSTANCE MINTS
# =====================================================================

@pytest.mark.parametrize("name,build,mint,prefix,first,err", LEDGERS, ids=IDS)
def test_interleaved_two_instance_mints_are_all_distinct(
        name, build, mint, prefix, first, err, tmp_path):
    """RULING 69 res.1, the headline property, FILE-VERIFIED.

    Two live instances over one path, alternating, N mints. Under the cached
    counter each instance derived once and then counted in its own head, so the
    second reissued everything the first had already written - measured as four
    lines carrying two ids.

    THE FILE IS THE ORACLE, not the returned values: an implementation could
    return distinct strings and still write colliding ones. Both are asserted,
    and the line count is asserted too, because "all distinct" is trivially true
    of a file with one line in it.
    """
    path = tmp_path / f"{name}.jsonl"
    a, b = build(path), build(path)

    returned = []
    for _ in range(6):
        returned.append(mint(a))
        returned.append(mint(b))

    assert len(set(returned)) == len(returned), f"duplicate ids: {returned}"

    text = path.read_text(encoding="utf-8")
    on_disk = ordinal_pattern(prefix).findall(text)
    assert len(on_disk) == 12, f"expected 12 records, found {len(on_disk)}"
    assert len(set(on_disk)) == 12, f"duplicate ids ON DISK: {on_disk}"
    assert sorted(int(o) for o in on_disk) == list(range(1, 13)), (
        "the ordinals must be the dense sequence 1..12, no gaps and no repeats")


@pytest.mark.parametrize("name,build,mint,prefix,first,err", LEDGERS, ids=IDS)
def test_a_single_instance_still_mints_the_identical_sequence(
        name, build, mint, prefix, first, err, tmp_path):
    """THE CONTROL, and the differential's own claim in miniature.

    Ruling 69 changes behaviour ONLY where two writers previously collided. One
    instance minting sequentially must derive exactly the sequence the counter
    produced - otherwise every recorded id in every store would have shifted.
    """
    ledger = build(tmp_path / f"{name}.jsonl")
    minted = [mint(ledger) for _ in range(5)]
    width = len(first) - len(prefix)
    assert minted == [f"{prefix}{n:0{width}d}" for n in range(1, 6)]


# =====================================================================
# (d) DERIVE-AT-MINT
# =====================================================================

@pytest.mark.parametrize("name,build,mint,prefix,first,err", LEDGERS, ids=IDS)
def test_an_instance_built_before_anothers_append_mints_after_it(
        name, build, mint, prefix, first, err, tmp_path):
    """RULING 69 res.1 - **THE LATE READER SEES THE EARLY WRITER'S LINE.**

    This is the defect's exact shape: `late` is constructed BEFORE `early`
    writes anything, so under the cached counter it had already derived 0 and
    would mint the same first id. The construction ORDER is the whole test.
    """
    path = tmp_path / f"{name}.jsonl"
    late = build(path)          # derives nothing now - there is nothing to cache
    early = build(path)

    first_id = mint(early)
    second_id = mint(late)

    assert first_id == first
    assert second_id != first_id, (
        "an instance constructed before the append reissued the id - the mint "
        "is remembering instead of reading")


# =====================================================================
# (e) THE TORN-LINE PROPERTY
# =====================================================================

@pytest.mark.parametrize("name,build,mint,prefix,first,err", LEDGERS, ids=IDS)
def test_an_ordinal_on_an_unparseable_line_is_never_reissued(
        name, build, mint, prefix, first, err, tmp_path):
    """RULING 69 res.2 - **THE REASON THE SCAN READS RAW TEXT.**

    Every previous derivation did `json.loads(line).get(key)`, so an ordinal on
    a TORN OR UNPARSEABLE LINE WAS INVISIBLE and the next mint would reissue it -
    into an append-only record where nothing can ever disambiguate the two
    (3a:112).

    The planted line is deliberately BOTH: it carries a high ordinal AND cannot
    be parsed. A derivation that parses sees nothing; one that reads bytes sees
    the ordinal.
    """
    path = tmp_path / f"{name}.jsonl"
    ledger = build(path)
    mint(ledger)

    with open(path, "a", encoding="utf-8") as handle:
        handle.write('{"id": "%s0042", "torn' % prefix)      # no close, no newline

    nxt = mint(build(path))
    ordinal = int(ordinal_pattern(prefix).search(nxt).group(1))
    assert ordinal == 43, (
        f"minted {nxt} - the ordinal on the torn line was invisible, so a live "
        f"id would be reissued")


# =====================================================================
# (f) THE MUTEX
# =====================================================================

@pytest.mark.parametrize("name,build,mint,prefix,first,err", LEDGERS, ids=IDS)
def test_two_threads_at_a_barrier_mint_distinct_ids(
        name, build, mint, prefix, first, err, tmp_path):
    """RULING 69 res.3. Two threads released simultaneously onto one path.

    The barrier is what makes this a real race rather than two sequential calls;
    the timeout is what stops a deadlock becoming a hung suite rather than a
    failure. Bounded, deterministic, no OS machinery.
    """
    path = tmp_path / f"{name}.jsonl"
    ledgers = [build(path) for _ in range(2)]
    barrier = threading.Barrier(2, timeout=10)
    minted, errors = [], []

    def worker(ledger):
        try:
            barrier.wait()
            for _ in range(5):
                minted.append(mint(ledger))
        except BaseException as exc:      # noqa: BLE001 - reported, not swallowed
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(L,)) for L in ledgers]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=15)
        assert not t.is_alive(), "a thread did not finish - the mutex deadlocked"

    assert not errors, f"threads raised: {errors}"
    assert len(minted) == 10
    assert len(set(minted)) == 10, f"duplicate ids under contention: {minted}"


def test_the_lock_is_keyed_by_resolved_path_not_by_object():
    """RES.3's KEYING, and why it is the FILE and not the class.

    The thing protected is one file's derive -> mint -> append. Two different
    ledger classes pointing at one path must take the SAME lock; a per-class
    registry would hand them different ones - a lock that does not exclude,
    which is worse than no lock because it reads as protection.
    """
    import tempfile
    root = Path(tempfile.mkdtemp())
    direct = root / "x.jsonl"
    indirect = root / "sub" / ".." / "x.jsonl"

    assert mint_lock(direct) is mint_lock(str(direct)), "str vs Path must agree"
    assert mint_lock(direct) is mint_lock(indirect), (
        "an unresolved path took a different lock - two writers to one file "
        "would not exclude each other")
    assert mint_lock(root / "other.jsonl") is not mint_lock(direct), (
        "different files must not share a lock, or one ledger blocks another")


# =====================================================================
# (c) `_seq` ABSENT AS SHAPE
# =====================================================================

# RULING 72 MIGRATION (2026-08-03), Ruling-14 form.
#
#     OLD: ("src/doctrine/cae.py", "src/external/claim_ancestry.py",
#           "src/external/prediction_ledger.py")
#     NEW: the same three, plus "src/goals/goal_ledger.py".
#
# **NO ASSERTION MOVED.** This list backs a claim quantified over EVERY ledger
# ("no ledger carries a `_seq` attribute"), so a ledger absent from it makes the
# claim TRUE BY OMISSION - the completeness-claim defect this house has named
# repeatedly. Ruling 72's goal ledger is the shared mint's second consumer and
# inherits Ruling 69's whole property set, so it belongs to every claim this
# file makes about ledgers.
_LEDGER_MODULES = ("src/doctrine/cae.py", "src/external/claim_ancestry.py",
                   "src/external/prediction_ledger.py",
                   "src/goals/goal_ledger.py")


def _seq_assignments(tree) -> list:
    return [f"line {n.lineno}" for n in ast.walk(tree)
            if isinstance(n, (ast.Assign, ast.AnnAssign, ast.AugAssign))
            for tgt in ([n.target] if hasattr(n, "target") and n.target is not None
                        else getattr(n, "targets", []))
            if isinstance(tgt, ast.Attribute) and tgt.attr == "_seq"]


def test_no_ledger_carries_a_seq_attribute():
    """RULING 69 res.1 AS SHAPE - **the counter is GONE, not merely unused.**

    Ruling 61's form: a cached derivation that still exists is a loaded gun for
    the next `if self._seq is None` someone adds back "for efficiency". Scanned
    for ASSIGNMENT specifically, because that is what makes it STATE.
    """
    offenders = []
    for rel in _LEDGER_MODULES:
        tree = ast.parse((REPO / rel).read_text(encoding="utf-8"))
        offenders += [f"{rel}:{hit}" for hit in _seq_assignments(tree)]
    assert not offenders, "`_seq` is back as state:\n" + "\n".join(offenders)


@pytest.mark.parametrize("name,build,mint,prefix,first,err", LEDGERS, ids=IDS)
def test_no_ledger_instance_carries_a_seq(name, build, mint, prefix, first, err,
                                          tmp_path):
    """The runtime half of (c). A live instance holds no counter, before or
    after minting - an attribute created lazily on first mint would satisfy the
    AST pin above and still be the defect."""
    ledger = build(tmp_path / f"{name}.jsonl")
    assert not hasattr(ledger, "_seq")
    mint(ledger)
    assert not hasattr(ledger, "_seq"), "a counter appeared at mint time"


def test_the_seq_scanner_actually_fires():
    """THE SCANNER'S OWN CONTROL - Ruling 32's answer to the vacuous pin."""
    for source in ("class L:\n    def __init__(self):\n        self._seq = 0\n",
                   "class L:\n    def f(self):\n        self._seq += 1\n",
                   "class L:\n    def f(self):\n        self._seq: int = 3\n"):
        assert _seq_assignments(ast.parse(source)), f"scanner blind to:\n{source}"

    # And it must NOT flag a READ, which is not state.
    assert not _seq_assignments(ast.parse("x = self._seq\n"))


# =====================================================================
# (g) RULING 53's REFUSAL, UNCHANGED
# =====================================================================

class _ReadsFailFor:
    """Make ONE path raise on READ while leaving writes alone - the asymmetry
    Ruling 53's original defence depended on, reused here verbatim in spirit."""

    def __init__(self, monkeypatch, path):
        self._real = builtins.open
        self._path = str(path)
        monkeypatch.setattr(builtins, "open", self._open)

    def _open(self, file, mode="r", *args, **kwargs):
        if str(file) == self._path and "r" in mode:
            raise OSError("simulated read failure")
        return self._real(file, mode, *args, **kwargs)


@pytest.mark.parametrize("name,build,mint,prefix,first,err", LEDGERS, ids=IDS)
def test_an_unreadable_existing_ledger_still_raises_typed(
        name, build, mint, prefix, first, err, tmp_path, monkeypatch):
    """RULING 53 IS UNCHANGED IN SEMANTICS, and each ledger keeps ITS OWN error.

    Deriving at mint time makes this MORE reachable, not less: the read now
    happens on every mint rather than once at construction. It must still refuse
    with the typed error and NEVER fall back to a number - an id minted from an
    unknown floor is exactly the collision Ruling 53 closed.
    """
    path = tmp_path / f"{name}.jsonl"
    ledger = build(path)
    mint(ledger)
    before = path.read_bytes()

    _ReadsFailFor(monkeypatch, path)
    with pytest.raises(err):
        mint(ledger)

    monkeypatch.undo()
    assert path.read_bytes() == before, "a refused mint wrote something"


@pytest.mark.parametrize("name,build,mint,prefix,first,err", LEDGERS, ids=IDS)
def test_a_recovered_ledger_resumes_from_the_real_maximum(
        name, build, mint, prefix, first, err, tmp_path, monkeypatch):
    """RULING 53's transient-recovery property, now held BY CONSTRUCTION.

    Res.1 SUBSUMES the explicit single re-derive: there is no cached value for a
    transient failure to poison, so a recovered ledger resumes from its real
    maximum without a special case anyone has to remember.
    """
    path = tmp_path / f"{name}.jsonl"
    ledger = build(path)
    mint(ledger)
    mint(ledger)

    _ReadsFailFor(monkeypatch, path)
    with pytest.raises(err):
        mint(ledger)
    monkeypatch.undo()

    resumed = mint(ledger)
    assert int(ordinal_pattern(prefix).search(resumed).group(1)) == 3, (
        f"resumed at {resumed} - a recovered ledger must resume from the file "
        f"maximum, never from zero")


# =====================================================================
# THE HOISTED HELPER'S OWN PINS (Ruling 63's mandate)
# =====================================================================

def test_a_missing_file_is_zero_and_an_unreadable_one_is_none(tmp_path, monkeypatch):
    """RULING 53's SENTINEL at the helper's own home. **Two absences that are
    not the same absence:** a missing file is a first run and a legitimate `0`;
    an existing file that cannot be read is `None`, because "what is here is
    unknown" and answering it with `0` claims content the code never saw."""
    missing = tmp_path / "nope.jsonl"
    assert derive_max_ordinal(missing, "CAE-") == 0

    present = tmp_path / "there.jsonl"
    present.write_text('{"id": "CAE-007"}\n', encoding="utf-8")
    assert derive_max_ordinal(present, "CAE-") == 7

    _ReadsFailFor(monkeypatch, present)
    assert derive_max_ordinal(present, "CAE-") is None


@pytest.mark.parametrize("text,expected,why", [
    ('{"id": "CLM-0001"}\n{"id": "CLM-0009"}\n', 9, "the maximum, not the last"),
    ('{"id": "CLM-0009"}\n{"id": "CLM-0001"}\n', 9, "order must not matter"),
    ("", 0, "an empty file has no ordinals"),
    ("total nonsense, no ids here\n", 0, "no match is zero, not a crash"),
    ('{"id": "CLM-00010"}\n', 10, "the FULL digit run - stopping early would "
                                 "reissue a live id"),
    ("aCLM-0099\n", 0, "a leading identifier char blocks the match"),
    ("CLM-0099x\n", 0, "a trailing identifier char blocks the match"),
    ("X-CLM-0099\n", 0, "`-` is a non-word char, so `\\b` would NOT block this"),
    ('{"claim_id": "CLM-0003", "asserted_by": "CLM-0011"}\n', 11,
     "a raw scan sees every id on the line - over-counting BURNS an ordinal, "
     "which is the conservative direction"),
])
def test_the_anchored_scan_reads_exactly_what_it_should(text, expected, why,
                                                        tmp_path):
    """RES.2's SCAN DISCIPLINE, at its own home.

    The `X-CLM-0099` row is the one that matters most: Ruling 60 res.3 said
    "anchored" and the code was bare, and Ruling 64's rider had to fix it -
    `\\b` is INSUFFICIENT because `-` is itself a non-word character. The
    `CLM-00010` row is its twin in the other direction: a scan that stopped at
    the first four digits would read a live `CLM-00010` as `CLM-0001` and
    REISSUE it.
    """
    path = tmp_path / "l.jsonl"
    path.write_text(text, encoding="utf-8")
    assert derive_max_ordinal(path, "CLM-") == expected, why


def test_prefixes_do_not_bleed_between_ledgers(tmp_path):
    """Three ledgers, one convention, and the scan must not confuse them - a
    `PRD-0500` in a file also holding `CAE-` ids must not raise the CAE floor."""
    path = tmp_path / "mixed.jsonl"
    path.write_text('{"id": "CAE-003", "ref": "PRD-0500", "c": "CLM-0777"}\n',
                    encoding="utf-8")
    assert derive_max_ordinal(path, "CAE-") == 3
    assert derive_max_ordinal(path, "PRD-") == 500
    assert derive_max_ordinal(path, "CLM-") == 777


def test_the_helper_holds_no_module_level_mutable_state_but_the_lock_registry():
    """The helper is a PURE derivation plus a lock registry - nothing else.

    A cached maximum here would be the very defect this ruling deleted, one
    level further out and harder to see, so its absence is pinned rather than
    trusted.
    """
    import src.utils.ledger_mint as module

    cachey = [name for name, value in vars(module).items()
              if isinstance(value, dict) and not name.startswith("__")
              and name != "_LOCKS"]
    assert not cachey, f"module-level mutable state appeared: {cachey}"
    # Dunders excluded: `__cached__` is Python's own bytecode-path attribute on
    # every module, not this one's state.
    assert not [n for n in dir(module)
                if "cache" in n.lower() and not n.startswith("__")]


def test_no_ledger_reimplements_the_scan():
    """RES.5: ONE derivation, three callers. A fourth copy is the drift this
    hoist exists to prevent - and the AST check that justified the hoist found
    the three had ALREADY drifted by a variable name."""
    offenders = []
    for rel in _LEDGER_MODULES:
        tree = ast.parse((REPO / rel).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_derive_seq":
                calls = [ast.unparse(n.func) for n in ast.walk(node)
                         if isinstance(n, ast.Call)]
                if "derive_max_ordinal" not in calls:
                    offenders.append(f"{rel}:{node.lineno}")
    assert not offenders, (
        "a ledger re-implements the scan instead of calling the helper:\n"
        + "\n".join(offenders))
