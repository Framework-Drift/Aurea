"""
Docket H, Stage 1 - NetEvidence: the standard evidence payload a collapse net
emits alongside its verdict.

WHAT THESE PINS ARE FOR
-----------------------
Two things, and they pull in opposite directions:

  1. The counts must be LEGIBLE. One-of-one and one-thousand-of-one-thousand
     must not look alike, and neither must "I looked and found nothing" and
     "I have no way to look".
  2. The counts must never GATE. Section 9 standing bar 5, refused four times
     already (Symbolic Heat Index, betweenness cutoff, `tone_weight` gating,
     TCAML tier scoring). A count reports. It never decides.

Ruling 17 governs the construction: these are BEHAVIORAL, each watched RED
under its exact defect before it was allowed to go green. The one structural
pin (section D) is structural for the reason the `tone_weight` pin is - a
behavioral test can only show that whatever threshold someone wrote did not
fire on the inputs someone picked, and the bar forbids the cutoff EXISTING.
That pin is itself pinned: `test_the_cutoff_scanner_actually_fires` feeds the
scanner the forbidden code, so it cannot rot into a scanner that finds nothing
because it looks for nothing (Ruling 32's precedent).
"""

from __future__ import annotations

import ast
import dataclasses
from datetime import datetime

import pytest

from src.filtration.echonet import (
    SUSTAINED_STRAIN,
    EchoNet,
    NetResult,
    Verdict,
)
from src.filtration.net_evidence import (
    EVIDENCE_UNREPORTED,
    Countability,
    EvidenceRef,
    NetEvidence,
)
from src.utils.models import Echo, Scar
from tests.invariants import _ast as H


# =========================================================================
# FIXTURES
# =========================================================================

def _echo(content: str) -> Echo:
    return Echo(id="echo-h", content=content,
                resonance_score=0.0, created_at=datetime.now())


def _scar(scar_id: str, origin: str, text: str = "mirror shattered",
          weight: float = 1.0) -> Scar:
    return Scar(id=scar_id, name=text, origin=origin, weight=weight,
                description=text)


class _FakeScarCore:
    """Minimal stand-in for the scar OWNER. Returns copies, like the real one."""

    def __init__(self, scars):
        self._scars = list(scars)

    def get_active_scars(self):
        return [dataclasses.replace(s) for s in self._scars]


class _ScarCoreWithoutAccessor:
    """A scar core that exposes no `get_active_scars` - an ABSENT instrument."""


# A claim that lexically overlaps `_scar`'s default text on two non-stop words
# ("mirror", "shattered"), which is what `EchoNet._overlaps` requires.
RESONANT_CLAIM = "the mirror shattered when I looked"
QUIET_CLAIM = "the kettle boiled quietly"


def _net(name: str, pressure: float, evidence: NetEvidence) -> NetResult:
    return NetResult(name, True, pressure, "", evidence)


_UNCOUNTABLE = NetEvidence.not_countable("no instrument at this depth")
_GROUNDED = NetEvidence.counted((EvidenceRef("scar-1", "collapse-A"),))


# =========================================================================
# A. THE TYPE - counts are derived, and two zeroes are not the same zero
# =========================================================================

def test_counts_are_derived_never_asserted() -> None:
    """DEFECT WATCHED: `evidence_count: int` stored as a FIELD.

    An int field is an int somebody types. `NetEvidence(evidence_count=5)` with
    no evidence would be a count with nothing behind it - Ruling 12 G1's
    fabricated pressure and Ruling 15's fabricated magnitude, one layer down.
    The fields do not exist, so passing them is a TypeError rather than a
    convention nobody enforces.
    """
    field_names = {f.name for f in dataclasses.fields(NetEvidence)}
    assert "evidence_count" not in field_names
    assert "independent_source_count" not in field_names

    with pytest.raises(TypeError):
        NetEvidence(Countability.COUNTED,
                    (EvidenceRef("a", "src-1"),),
                    evidence_count=99)          # type: ignore[call-arg]

    evidence = NetEvidence.counted((EvidenceRef("a", "src-1"),
                                    EvidenceRef("b", "src-1")))
    assert evidence.evidence_count == 2
    assert evidence.independent_source_count == 1


def test_one_of_one_and_many_of_many_do_not_look_alike() -> None:
    """The whole reason both fields exist.

    DEFECT WATCHED: `independent_source_count` derived from `len(refs)` rather
    than from the DISTINCT source keys - which would make a thousand pieces
    from one origin indistinguishable from a thousand independent ones.
    """
    one_of_one = NetEvidence.counted((EvidenceRef("a", "src-1"),))
    many_of_many = NetEvidence.counted(
        tuple(EvidenceRef(f"item-{i}", f"src-{i}") for i in range(1000)))
    many_of_one = NetEvidence.counted(
        tuple(EvidenceRef(f"item-{i}", "src-1") for i in range(1000)))

    shapes = {
        (e.evidence_count, e.independent_source_count)
        for e in (one_of_one, many_of_many, many_of_one)
    }
    assert shapes == {(1, 1), (1000, 1000), (1000, 1)}, (
        f"the three cases collapsed into {shapes}. A thousand pieces of "
        "evidence from a single origin is not a thousand confirmations, and a "
        "reader who sees only a total cannot tell them apart."
    )


def test_none_found_and_not_countable_are_not_the_same_zero() -> None:
    """DEFECT WATCHED: one zero-state instead of two, or a bare `countable: bool`.

    "I ran a real instrument and found nothing" and "I have no instrument"
    produce the identical integer 0 and mean opposite things. Only the second
    carries a reason; only the first is a search.
    """
    honest_zero = NetEvidence.none_found()
    no_instrument = NetEvidence.not_countable("there is no evidence base to read")

    assert honest_zero.evidence_count == no_instrument.evidence_count == 0
    assert honest_zero.independent_source_count == 0
    assert no_instrument.independent_source_count == 0

    assert honest_zero.countability is not no_instrument.countability
    assert honest_zero.uncountable_reason == ""
    assert no_instrument.uncountable_reason.strip(), (
        "NOT_COUNTABLE must NAME what is missing - the reason is what a later "
        "pass reads to know what to build.")


@pytest.mark.parametrize("kwargs, why", [
    (dict(countability=Countability.COUNTED, refs=()),
     "COUNTED with nothing enumerated is a claim of evidence with no evidence"),
    (dict(countability=Countability.NOT_COUNTABLE, uncountable_reason="   "),
     "an unexplained abstention is indistinguishable from an unfinished one"),
    (dict(countability=Countability.NONE_FOUND,
          refs=(EvidenceRef("a", "src-1"),)),
     "a zero-state holding evidence is a payload disagreeing with itself"),
    (dict(countability=Countability.NOT_COUNTABLE,
          uncountable_reason="none", refs=(EvidenceRef("a", "src-1"),)),
     "NOT_COUNTABLE holding refs counted after saying it could not"),
    (dict(countability=Countability.NONE_FOUND, uncountable_reason="why"),
     "a net that counted does not also explain why it could not"),
])
def test_a_payload_that_disagrees_with_itself_is_refused(kwargs, why) -> None:
    """Every state's requirements bind on EVERY construction path.

    DEFECT WATCHED: validation living in the classmethods only, so the plain
    constructor stays a way around it. `__post_init__` is the gate; the
    classmethods are legibility. CLAUDE.md section 3 - unexecutable, not
    discouraged.
    """
    with pytest.raises(ValueError):
        NetEvidence(**kwargs)


def test_a_list_of_refs_is_refused() -> None:
    """DEFECT WATCHED: `refs: List[...]` inside a frozen dataclass.

    The shell freezes and the interior does not, so `evidence.refs.append(...)`
    would succeed on an "immutable" payload and the DERIVED counts would change
    under a reader already holding it. That is the pre-Ruling-22 scar store.
    """
    with pytest.raises(TypeError):
        NetEvidence(Countability.COUNTED, [EvidenceRef("a", "src-1")])  # type: ignore[arg-type]


def test_an_unnamed_source_is_refused_rather_than_silently_merged() -> None:
    """DEFECT WATCHED: `source_id=""` permitted.

    Several empty keys collapse into ONE set member, so five unattributed
    pieces would report `independent_source_count == 1` - silently understating
    independence while looking like a real finding.
    """
    with pytest.raises(ValueError):
        EvidenceRef("scar-1", "")
    with pytest.raises(ValueError):
        EvidenceRef("", "collapse-A")
    with pytest.raises(TypeError):
        EvidenceRef("scar-1", None)      # type: ignore[arg-type]


def test_an_ungrounded_contributor_must_be_in_the_tally() -> None:
    """DEFECT WATCHED: `uncounted_contributors` free to name anything.

    The caveat exists so a reader can SUBTRACT the nominally-attributed items
    from the tally. Naming something absent from `refs` makes it unsubtractable
    and turns the caveat into decoration.
    """
    with pytest.raises(ValueError):
        NetEvidence.counted((EvidenceRef("scar-1", "collapse-A"),),
                            uncounted_contributors=("scar-99",))

    ok = NetEvidence.counted((EvidenceRef("scar-1", "scar-1"),),
                             uncounted_contributors=("scar-1",))
    assert ok.uncounted_contributors == ("scar-1",)


def test_evidence_is_frozen() -> None:
    """A tally is a statement about verdict time, not a channel to top up later."""
    evidence = NetEvidence.none_found()
    with pytest.raises(dataclasses.FrozenInstanceError):
        evidence.countability = Countability.COUNTED   # type: ignore[misc]


# =========================================================================
# B. THE HONEST-TALLY INVENTORY - four of six nets cannot count
# =========================================================================

@pytest.mark.parametrize("net_name, claim", [
    ("logic", "this statement is false"),
    ("logic", QUIET_CLAIM),
    ("empirical", "everyone always lies"),
    ("empirical", QUIET_CLAIM),
    ("ethics", "truth does not matter"),
    ("ethics", QUIET_CLAIM),
    ("intuition", QUIET_CLAIM),
])
def test_the_shallow_nets_cannot_count_and_each_names_why(net_name, claim) -> None:
    """DEFECT WATCHED: filling these with `none_found()` - or with a tally of
    how many COINED regexes matched.

    Neither is evidence. A regex count tallies this module's own guesses, and
    an honest zero would imply AUREA searched an evidence base she does not
    have. Both are checked in the SAME parametrisation whether the net fires or
    not: the payload must not change shape with the verdict, because the count
    does not participate in the verdict.
    """
    net = EchoNet()
    result = getattr(net, f"_net_{net_name}")(claim)

    assert result.evidence.countability is Countability.NOT_COUNTABLE, (
        f"_net_{net_name} claims it counted something on {claim!r}. It reads "
        "the claim's own wording and has no evidence base behind it."
    )
    assert result.evidence.evidence_count == 0
    assert result.evidence.independent_source_count == 0
    assert result.evidence.uncountable_reason.strip(), (
        f"_net_{net_name} abstains without saying what is missing")


def test_each_abstaining_net_gives_its_own_reason() -> None:
    """DEFECT WATCHED: one shared "not implemented" string across four nets.

    The four abstain for four DIFFERENT reasons - no external sources, no
    evidence base, no doctrine read, no instrument at all - and the reason is
    the input a later pass reads to know what to build. A single string erases
    that.
    """
    net = EchoNet()
    reasons = {
        net._net_logic(QUIET_CLAIM).evidence.uncountable_reason,
        net._net_empirical(QUIET_CLAIM).evidence.uncountable_reason,
        net._net_ethics(QUIET_CLAIM).evidence.uncountable_reason,
        net._net_intuition(QUIET_CLAIM).evidence.uncountable_reason,
    }
    assert len(reasons) == 4, f"abstention reasons collapsed: {reasons}"


def test_resonance_counts_real_scars_and_attributes_them_to_origins() -> None:
    """The one net with a real store behind it."""
    core = _FakeScarCore([
        _scar("scar-1", "collapse-A"),
        _scar("scar-2", "collapse-B"),
    ])
    result = EchoNet(scar_core=core)._net_resonance(RESONANT_CLAIM)

    assert result.evidence.countability is Countability.COUNTED
    assert result.evidence.evidence_count == 2
    assert result.evidence.independent_source_count == 2
    assert {r.item_id for r in result.evidence.refs} == {"scar-1", "scar-2"}
    assert result.evidence.uncounted_contributors == ()


def test_five_scars_from_one_collapse_are_not_five_independent_sources() -> None:
    """DEFECT WATCHED: `source_id=scar.id` for every scar.

    That is the natural, wrong choice - it makes the two counts identical by
    construction and destroys the distinction the fields exist for. Five scars
    left by ONE collapse are five pieces of evidence from ONE source.
    """
    core = _FakeScarCore([_scar(f"scar-{i}", "collapse-A") for i in range(5)])
    evidence = EchoNet(scar_core=core)._net_resonance(RESONANT_CLAIM).evidence

    assert evidence.evidence_count == 5
    assert evidence.independent_source_count == 1, (
        "five scars sharing an origin reported as five independent sources")


def test_resonance_with_no_scar_store_cannot_count_it_did_not_find_zero() -> None:
    """DEFECT WATCHED: `none_found()` when `scar_core is None`.

    That is the whole docket in one line. No store means the net COULD NOT
    LOOK; reporting an honest zero would assert a search that never ran.
    """
    evidence = EchoNet(scar_core=None)._net_resonance(RESONANT_CLAIM).evidence
    assert evidence.countability is Countability.NOT_COUNTABLE
    assert evidence.uncountable_reason.strip()


def test_resonance_with_a_store_but_no_accessor_still_cannot_look() -> None:
    """DEFECT WATCHED: relying on the pre-existing `getattr(..., lambda: [])`.

    That fallback iterates an empty list and would render an ABSENT INSTRUMENT
    as an honest zero - the same fail-silent shape Ruling 22 closed, in the
    evidence layer.
    """
    evidence = (EchoNet(scar_core=_ScarCoreWithoutAccessor())
                ._net_resonance(RESONANT_CLAIM).evidence)
    assert evidence.countability is Countability.NOT_COUNTABLE


def test_resonance_that_read_the_scars_and_found_nothing_is_an_honest_zero() -> None:
    """The other side of the same line: a real instrument ran, nothing resonated."""
    core = _FakeScarCore([_scar("scar-1", "collapse-A")])
    evidence = EchoNet(scar_core=core)._net_resonance(QUIET_CLAIM).evidence

    assert evidence.countability is Countability.NONE_FOUND
    assert evidence.evidence_count == 0
    assert evidence.uncountable_reason == ""


def test_a_scar_with_no_recorded_origin_is_named_not_silently_self_attributed() -> None:
    """DEFECT WATCHED: silently using `scar.id` as the source key for an
    unattributed scar - which OVERSTATES independence - or silently merging all
    such scars under one sentinel, which UNDERSTATES it.

    Neither silence is acceptable. The item is kept in the tally, attributed to
    itself, and NAMED, so a reader can subtract.
    """
    core = _FakeScarCore([
        _scar("scar-1", "collapse-A"),
        _scar("scar-2", ""),
        _scar("scar-3", "   "),
    ])
    evidence = EchoNet(scar_core=core)._net_resonance(RESONANT_CLAIM).evidence

    assert evidence.evidence_count == 3
    assert set(evidence.uncounted_contributors) == {"scar-2", "scar-3"}, (
        "ungrounded scars were absorbed into the tally without being named")


# =========================================================================
# C. CONVERGENT ELIMINATION - the count reports below the line too
# =========================================================================

def test_convergent_elimination_reports_strain_below_the_convergence_line() -> None:
    """DEFECT WATCHED: populating evidence only inside the `>= 3` branch.

    One strain and two strains are real findings this net does not act on. A
    payload that appeared only when the net FIRED would make the tally look
    like the trigger - which is precisely what it must never be.
    """
    net = EchoNet()
    nets = [
        _net("logic", 0.0, _UNCOUNTABLE),
        _net("empirical", SUSTAINED_STRAIN, _UNCOUNTABLE),
        _net("ethics", 0.0, _UNCOUNTABLE),
        _net("resonance", SUSTAINED_STRAIN, _GROUNDED),
        _net("intuition", 0.0, _UNCOUNTABLE),
    ]
    result = net._net_convergent_elimination(nets)

    assert result.survived is True, "two strains must not cross the canon >=3 line"
    assert result.evidence.countability is Countability.COUNTED
    assert result.evidence.evidence_count == 2, (
        "strain below the convergence line went unreported")


def test_convergent_elimination_names_contributors_it_cannot_ground() -> None:
    """DEFECT WATCHED: three strains reported as three corroborating sources.

    Four of the six nets cannot enumerate what their strain rests on. Left
    silent, a nominal source is indistinguishable from a grounded one.
    """
    net = EchoNet()
    nets = [
        _net("logic", 0.9, _UNCOUNTABLE),
        _net("empirical", 0.6, _UNCOUNTABLE),
        _net("resonance", 0.5, _GROUNDED),
    ]
    result = net._net_convergent_elimination(nets)

    assert result.survived is False, "three strains cross the canon convergence line"
    assert result.evidence.evidence_count == 3
    assert set(result.evidence.uncounted_contributors) == {"logic", "empirical"}
    assert "resonance" not in result.evidence.uncounted_contributors, (
        "a net with grounded evidence was flagged as ungrounded")


def test_convergent_elimination_with_no_strain_is_an_honest_zero() -> None:
    """It read five real NetResults and none strained. A search that ran."""
    net = EchoNet()
    nets = [_net(n, 0.0, _UNCOUNTABLE) for n in ("a", "b", "c", "d", "e")]
    evidence = net._net_convergent_elimination(nets).evidence

    assert evidence.countability is Countability.NONE_FOUND


# =========================================================================
# D. THE BAR - a count reports, it never gates
# =========================================================================

COUNT_FIELDS = {"evidence_count", "independent_source_count"}
BINNING_CALLS = {"round", "min", "max", "int", "abs", "bool"}


def _is_count_expr(node: ast.AST) -> bool:
    """The count referenced DIRECTLY, not merely somewhere inside."""
    return ((isinstance(node, ast.Attribute) and node.attr in COUNT_FIELDS)
            or (isinstance(node, ast.Name) and node.id in COUNT_FIELDS))


def _touches_count(node: ast.AST) -> bool:
    return any(_is_count_expr(n) for n in ast.walk(node))


def find_count_cutoffs(tree: ast.AST) -> list[tuple[int, str]]:
    """Every place a cutoff is applied to either tally.

    A BIN IS A CUTOFF WITHOUT AN OPERATOR, so refusing only `>` would leave the
    coined magnitude one function call away. Truthiness is included because
    `if evidence_count:` is a threshold at zero - and the COUNTED /
    NONE_FOUND / NOT_COUNTABLE enum exists precisely so nobody has to ask that
    question of the integer.
    """
    found: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare) and _touches_count(node):
            found.append((node.lineno, "compared"))
        elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id in BINNING_CALLS
                and any(_touches_count(a) for a in node.args)):
            found.append((node.lineno, f"binned via {node.func.id}()"))
        elif (isinstance(node, ast.BinOp)
                and isinstance(node.op, (ast.FloorDiv, ast.Mod))
                and _touches_count(node)):
            found.append((node.lineno, "binned via // or %"))
        elif isinstance(node, (ast.If, ast.While)) and _is_count_expr(node.test):
            found.append((node.lineno, "used as a truth test (a cutoff at zero)"))
        elif (isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not)
                and _is_count_expr(node.operand)):
            found.append((node.lineno, "negated (a cutoff at zero)"))
        elif isinstance(node, ast.BoolOp) and any(_is_count_expr(v) for v in node.values):
            found.append((node.lineno, "used in a boolean operator (a cutoff at zero)"))
    return found


def test_no_cutoff_operates_on_either_count_anywhere_in_src() -> None:
    """Section 9 standing bar 5, fifth application.

    STRUCTURAL, and deliberately so - the `tone_weight` pin's reasoning
    verbatim: a behavioral test can only show that whatever threshold someone
    wrote did not fire on the inputs someone picked. The bar forbids the cutoff
    EXISTING.

    Scoped to the WHOLE of `src/`, not to `echonet.py`, because four consumers
    are already named for this shape and a threshold would most naturally land
    in one of them rather than at the source.
    """
    violations: list[H.Violation] = []
    for path in H.src_files():
        tree = H.parse(path)
        if tree is None:
            continue
        for lineno, detail in find_count_cutoffs(tree):
            violations.append(H.Violation(path, lineno, detail))

    assert not violations, (
        "\n".join(str(v) for v in violations) + "\n\n"
        "  A COUNT REPORTS. IT NEVER GATES. Either tally under a comparison, a\n"
        "  bin, or a truth test is a COINED MAGNITUDE at the evidence layer -\n"
        "  section 9 standing bar 5, already refused for the Symbolic Heat\n"
        "  Index, the betweenness cutoff, tone_weight gating, and TCAML tier\n"
        "  scoring. The answer is to report the raw tally.\n\n"
        "  If you need to know WHETHER anything was counted, read\n"
        "  `countability` - that enum exists so the question never has to be\n"
        "  asked of the integer.\n\n"
        "  Reopen only on a cutoff RECOVERED from corpus or demonstrated by\n"
        "  operational correlation (Ruling 28's condition, neither half\n"
        "  optional) - NEVER an invented one."
    )


@pytest.mark.parametrize("source", [
    "if ev.evidence_count >= 3:\n    pass\n",
    "tier = min(ev.independent_source_count, 5)\n",
    "band = ev.evidence_count // 10\n",
    "if ev.evidence_count:\n    pass\n",
    "flag = not ev.independent_source_count\n",
    "x = round(ev.evidence_count)\n",
    "ok = ev.evidence_count and other\n",
    "weight = abs(ev.independent_source_count)\n",
    "while ev.evidence_count:\n    pass\n",
])
def test_the_cutoff_scanner_actually_fires(source: str) -> None:
    """The pin above is pinned.

    DEFECT WATCHED: a scanner that finds nothing because it LOOKS for nothing.
    `test_no_cutoff_operates_on_either_count_anywhere_in_src` is green today
    for the honest reason - no cutoff exists - which is exactly how a broken
    scanner hides. Ruling 3's invariant passed vacuously against a 0-byte
    `hail.py` for months; Ruling 32's answer was to feed the scanner the
    forbidden code, and this is that.
    """
    assert find_count_cutoffs(ast.parse(source)), (
        f"the scanner missed a cutoff in: {source!r}")


def test_the_cutoff_scanner_does_not_fire_on_reporting() -> None:
    """A scanner that flags everything is as useless as one that flags nothing."""
    benign = (
        "trace.append(f'evidence={ev.evidence_count} "
        "sources={ev.independent_source_count}')\n"
        "record = {'n': ev.evidence_count}\n"
        "total = ev.evidence_count + other.evidence_count\n"
    )
    assert find_count_cutoffs(ast.parse(benign)) == []


# =========================================================================
# E. STAGE 1 IS ORGAN-LOCAL, AND NO VERDICT MOVED
# =========================================================================

@pytest.mark.parametrize("claim, expected", [
    ("the kettle boiled quietly", Verdict.CONFIRMED),
    ("this statement is false", Verdict.PARADOX),
    ("everyone always lies", Verdict.SUSPENDED),
    ("truth does not matter", Verdict.SCARRED),
])
def test_evidence_did_not_move_a_single_verdict(claim, expected) -> None:
    """DEFECT WATCHED: the evidence tally leaking into the verdict.

    The whole docket rides ALONGSIDE the verdict. If any of these four move,
    a count has started deciding something.
    """
    result = EchoNet().filter_claim(_echo(claim))
    assert result.verdict is expected


def test_every_net_reports_evidence_on_a_live_pass() -> None:
    """All six nets populate the payload - none silently keeps the default."""
    core = _FakeScarCore([_scar("scar-1", "collapse-A")])
    result = EchoNet(scar_core=core).filter_claim(_echo(RESONANT_CLAIM))

    assert len(result.nets) == 6
    for net_result in result.nets:
        assert net_result.evidence is not EVIDENCE_UNREPORTED, (
            f"{net_result.net} left the abstaining default in place - which "
            "reads as 'did not report', not as anything it actually found")


def test_the_default_is_abstention_not_an_honest_zero() -> None:
    """DEFECT WATCHED: defaulting `NetResult.evidence` to `none_found()`.

    A net that was never taught to report must not read as a net that looked
    and found nothing. `echonet.py` fails toward SUSPENSION rather than false
    collapse; this default fails toward ABSTENTION rather than a false zero.
    """
    bare = NetResult("some_future_net", True, 0.0)
    assert bare.evidence.countability is Countability.NOT_COUNTABLE
    assert bare.evidence.uncountable_reason.strip()


def test_the_evidence_vocabulary_has_exactly_ONE_ruled_consumer() -> None:
    """CHANGED BY A RULING, 2026-07-30 - the one legitimate reason a pinned test
    moves (the Ruling-14 precedent), and this test NAMED ITS OWN CONDITION.
    Recorded verbatim:

        OLD (Docket H Stage 1, 2026-07-27):
            def test_stage_1_populates_no_downstream_surface() -> None:
                '''DEFECT WATCHED: wiring `TruthPacket.evidence_refs` /
                `scar_lineage` now.

                That surface was deliberately deferred at HAIL Stage 2 and is a
                separate, unruled decision. Stage 1 is ORGAN-LOCAL: the shape
                exists, the nets populate it, nothing consumes it.
                '''
                ...
                assert importers == [], (
                    f"{importers} already consume NetEvidence. Stage 1 is
                    organ-local - a consumer is Stage 2 and needs its own
                    ruling, particularly for TruthPacket.evidence_refs /
                    scar_lineage.")

        NEW (Ruling 50, 2026-07-30):
            the allowed set gains `src/aurea_core.py`, and NOTHING ELSE.

    WHY: the old assertion said a consumer "needs its own ruling, particularly
    for TruthPacket.evidence_refs / scar_lineage". Ruling 50 IS that ruling, and
    it is that exact surface. The deferral was discharged, not overruled.

    NOTHING WAS WEAKENED - THE PIN IS NARROWER NOW THAN IT WAS BROAD BEFORE. It
    no longer asks "is there a consumer" (a question with one permanent answer
    once any consumer lands); it asks "is the consumer set exactly the ruled
    one". A SECOND unruled consumer still fails here, which is the property the
    original was protecting.
    """
    RULED_CONSUMERS = {
        # Ruling 50 (1)+(2): the spoken packet's grounding. `_spoken_grounding`
        # reads Countability to keep NOT_COUNTABLE out of `evidence_refs` and
        # into `unresolved` - the two zeroes surviving the render boundary.
        "src/aurea_core.py",
    }
    OWNERS = {"src/filtration/net_evidence.py", "src/filtration/echonet.py"}

    # CONVERTED 2026-08-01 BY RULING 64's RIDE-ALONG, under the Ruling-14
    # precedent. THE ASSERTIONS BELOW ARE UNCHANGED; the INSTRUMENT is strictly
    # narrower and now says what it always meant.
    #
    #     OLD:  "net_evidence" in p.read_text(...)      # source-text substring
    #     NEW:  an AST scan for an actual IMPORT of the module
    #
    # WHY IT MOVED: the substring form matched PROSE. It registered
    # `claim_ancestry.py` as a consumer of the evidence vocabulary because that
    # file's docstring MENTIONED the module - twice, in Batch 51 and again at
    # Ruling 58 - and both times the remedy was to word the prose around the
    # scanner rather than fix it. THE FIRST TWO OF FIVE OCCURRENCES OF THIS
    # DEFECT; Ruling 63 produced the fourth and fifth, and the manifest made
    # the conversion no longer deferrable.
    #
    # A guard that misfires on correct documentation teaches its readers to
    # route around it, and two files already had.
    importers = set()
    for path in H.src_files():
        if H.rel(path) in OWNERS:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = set()
            if isinstance(node, ast.Import):
                names = {a.name for a in node.names}
            elif isinstance(node, ast.ImportFrom):
                names = {node.module or ""} | {a.name for a in node.names}
            if any("net_evidence" in name for name in names):
                importers.add(H.rel(path))
                break

    unruled = importers - RULED_CONSUMERS
    assert unruled == set(), (
        f"{sorted(unruled)} consume NetEvidence without a ruling. Each consumer "
        f"of the evidence vocabulary is a DECISION about where a countability "
        f"state is allowed to be flattened - Ruling 50 made exactly one.")

    assert RULED_CONSUMERS <= importers, (
        f"{sorted(RULED_CONSUMERS - importers)} is ruled as a consumer but no "
        f"longer imports the vocabulary. If the spoken packet stopped reading "
        f"Countability, a NOT_COUNTABLE net is being flattened into "
        f"`evidence_refs` as though it were an honest zero.")
