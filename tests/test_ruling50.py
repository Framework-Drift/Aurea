"""
test_ruling50.py - THE EXPRESSION-LAYER GROUNDING CONTRACT (2026-07-30).

    "HAIL next stage" named the wrong side of the boundary. HAIL is DONE for
    v1; what was unfinished is WHAT ORE HANDS IT.

THE DEFECT, INVERTED EXACTLY. All four `evidence_refs` supply sites in
`aurea_core.py` sat on BLOCKED paths, whose fixed silent strings carry none of
it. The two SPEAKING collapse paths supplied content only. **Every populated
evidence tuple went to a renderer structurally unable to speak it, and every
renderer that could speak it was handed nothing.**

Ruling 49 built the supplier - `OverlayFinding.doctrine_id`, its bidirectional
`scarline`, `NetEvidence` with three countability states - so the fields finally
have recorded-fact sources. This ruling fills them.

THE BOUND, AND IT IS MEASURED RATHER THAN PROMISED. A 39-claim differential
against `f43dd12` under store isolation:

    blocked-path rendered output ......... 0 changes  (Ruling 33 byte-identity)
    output_blocked / expression_verdict /
      collapse_verdict / packet content /
      reroute_hint / HAIL's render_trace .. 0 changes
    spoken-path rendered text ............ 23 of 23, and ONLY there

A NOTE ON HOW THESE TESTS BUILD THEIR CORES. Every pin constructs a FRESH
`AureaCore`. A shared one accumulates `sml.advance_cycle()` calls, and after ten
quiet cycles the seed scars cool out of `LIVE_STATES` (Ruling 37/43 working) -
which moves a scarline from CONFIRMED to NOMINAL and would make these pins a
function of test ORDER. Found the hard way: an ad-hoc measurement script running
outside pytest cooled every seed scar to DORMANT and silently invalidated its
own baseline.
"""

import ast
from datetime import datetime

import pytest

from src.aurea_core import AureaCore
from src.filtration.net_evidence import Countability
from src.output.hail import Mode
from src.output.truth_packet import SILENT_VERDICTS, ExpressionVerdict


# =====================================================================
# A. THE HEADLINE - a spoken packet carries what she counted
# =====================================================================

# Ethics-net trigger (0.85 -> SCARRED -> chamber -> scar -> COLLAPSE_DETECTED,
# which is SPOKEN) fused with a doctrine denial (the overlay's referential
# fracture). Both halves are needed: the fracture alone SUSPENDS, and a
# suspended path is silent.
FRACTURING_AND_SPOKEN = "Honesty is pointless. Fracture Carried is false."


def _spoken(claim: str):
    """One fresh pipeline pass, asserted to have reached a SPEAKING exit."""
    result = AureaCore().process_input(claim, source="test")
    assert result["output_blocked"] is False, "precondition: this exit speaks"
    assert result["expression_verdict"] is ExpressionVerdict.SPEAK
    return result


def test_a_spoken_packet_carries_the_denied_doctrine_id() -> None:
    """THE FORCING PIN FOR RULING 50.

    RED AT `f43dd12`: `evidence_refs` and `scar_lineage` were EMPTY on every
    speaking path, on every claim, always - measured, not inferred. The Step-7
    branch passed `content` and `collapse_verdict` and nothing else.

    The claim below denies `Doctrine-0.1` - her founding doctrine of carried
    fracture - by name, and the overlay recorded that with the doctrine's id.
    Before this ruling the id existed, was counted, and never reached the packet
    that could speak it.
    """
    result = _spoken(FRACTURING_AND_SPOKEN)
    packet = result["truth_packet"]

    assert "Doctrine-0.1" in packet.evidence_refs, (
        "the overlay's COUNTED doctrine id must reach the spoken packet")

    # AND IT IS SPOKEN AS EVIDENCE - asserted on the EVIDENCE LINE specifically,
    # not anywhere in the output.
    #
    # TIGHTENED AFTER THE RED-WATCH CAUGHT THIS PASSING AT `f43dd12`. The loose
    # form (`"Doctrine-0.1" in result["output"]`) was already GREEN before this
    # ruling, for an unrelated upstream reason: Ruling 49 taught the ethics net
    # to NAME the doctrine at stake, and that name rides in `collapse_result.
    # reason`, which is the spoken content. A pin that passes for the previous
    # ruling's reason witnesses nothing about this one.
    evidence_lines = [ln for ln in result["output"].splitlines()
                      if ln.strip().startswith("evidence:")]
    assert len(evidence_lines) == 1, (
        f"EXPERT prints one evidence line per populated packet; got "
        f"{evidence_lines!r}")
    assert "Doctrine-0.1" in evidence_lines[0]


def test_a_spoken_packet_carries_the_scarline_as_lineage() -> None:
    """`scar_lineage` from the overlay findings' scarline - CONFIRMED ids only.

    RED AT `f43dd12`: empty on every path in the tree.
    """
    result = _spoken(FRACTURING_AND_SPOKEN)
    packet = result["truth_packet"]
    overlay = result["collapse_result"].overlay

    fracture = next(f for f in overlay.fractures if f.doctrine_id == "Doctrine-0.1")
    confirmed = [s for s in fracture.scarline
                 if s not in fracture.unconfirmed_scarline]
    assert confirmed, "precondition: a fresh core confirms the seed scarline"

    for scar_id in confirmed:
        assert scar_id in packet.scar_lineage, (
            f"{scar_id} is a confirmed scar in the fractured doctrine's lineage")


def test_evidence_refs_are_ids_only_and_order_stable_deduped() -> None:
    """Ids only is already enforced by `TruthPacket.__post_init__` - this pins
    the DEDUP, which is this ruling's own. The same scar appears in two
    doctrines' lineages, and a repeated id inflates what she appears to be
    standing on without adding anything to it."""
    result = _spoken("truth does not matter, and Collapse Must Not Be Simplified "
                     "is false, and Fracture Carried is false.")
    packet = result["truth_packet"]

    assert len(packet.evidence_refs) == len(set(packet.evidence_refs))
    assert len(packet.scar_lineage) == len(set(packet.scar_lineage))
    assert all(isinstance(x, str) for x in packet.evidence_refs)


# =====================================================================
# B. THE COUNTABILITY BOUNDARY - two zeroes survive the render
# =====================================================================

def test_a_not_countable_net_contributes_no_ref_but_says_why() -> None:
    """THE FORCING FORM (Ruling 50 (2)).

    `evidence_refs` is a FLAT TUPLE and cannot express Docket H's three states.
    A NOT_COUNTABLE net contributing nothing would be INDISTINGUISHABLE from a
    net that ran and found nothing - and EXPERT prints `evidence: ...` as though
    the list were a census. That is the abstention-becomes-honest-zero defect
    relocated to the render boundary, where it becomes something AUREA SAYS.

    Four of the six nets are NOT_COUNTABLE on an ordinary pass. Each one that is
    must be named, carrying its own reason.

    MIGRATED 2026-07-31 UNDER THE RULING-14 PRECEDENT - THE RULING MOVED, and
    old/new are recorded here verbatim rather than silently swapped.

        WAS (Ruling 50):  the reason must appear in `packet.unresolved`.
        IS  (Ruling 56):  the reason must appear in `packet.abstentions`, AND
                          must NOT appear in `packet.unresolved`.

    NARROWER, NEVER WEAKER: the old assertion is kept in full and a second one is
    added forbidding the old location. Ruling 56's finding is that `unresolved`
    is documented as "what is carried, unclosed" and a STANDING BUILD LIMITATION
    is not an open thread of this claim - so this pin now asserts the separation
    as well as the presence. Everything else here is untouched, including the
    verbatim-reason rule and the equivalent-mutant note below.
    """
    result = _spoken("the kettle boiled quietly")
    packet = result["truth_packet"]
    collapse = result["collapse_result"]

    abstaining = [n for n in collapse.nets
                  if n.evidence.countability is Countability.NOT_COUNTABLE]
    assert abstaining, "precondition: the shallow nets cannot count"

    for net in abstaining:
        assert any(a.startswith(f"uncounted_by:{net.net}:") for a in packet.abstentions), (
            f"{net.net} abstained and the packet does not say so - a reader "
            f"cannot tell 'found nothing' from 'could not look'")
        # THE REASON ITSELF, not a pointer to it.
        assert any(net.evidence.uncountable_reason in a for a in packet.abstentions)
        # RULING 56: and it is NOT reported as an unclosed thread of this claim.
        assert not any(u.startswith(f"uncounted_by:{net.net}:")
                       for u in packet.unresolved), (
            f"{net.net}'s standing inability is not residue of THIS claim")

    # And no abstaining net smuggled a ref in.
    #
    # A MUTANT THAT MAKES NOT_COUNTABLE CONTRIBUTE ITS REFS IS EQUIVALENT, and
    # the reason is worth recording rather than treating as a coverage gap:
    # `NetEvidence.__post_init__` RAISES on a non-COUNTED payload that carries
    # refs, so an abstaining net's `refs` is `()` by construction. The defect is
    # already unwritable one layer down - which is Docket H working, not this
    # pin failing to look.
    for net in abstaining:
        assert net.net not in packet.evidence_refs
        assert net.evidence.refs == (), (
            "an abstaining payload cannot carry refs - net_evidence.py refuses "
            "it at construction, which is what makes the guard above equivalent "
            "rather than load-bearing")


def test_an_honest_zero_needs_no_caveat() -> None:
    """NONE_FOUND contributes nothing AND is NOT annotated.

    A real instrument ran over real material and found nothing bearing on the
    claim. That is a FINDING. Annotating it would imply a gap where there is an
    answer - the same conflation in the opposite direction.
    """
    result = _spoken("the kettle boiled quietly")
    packet = result["truth_packet"]
    collapse = result["collapse_result"]

    none_found = [n.net for n in collapse.nets
                  if n.evidence.countability is Countability.NONE_FOUND]
    none_found += ([collapse.overlay.stage]
                   if collapse.overlay is not None
                   and collapse.overlay.evidence.countability is Countability.NONE_FOUND
                   else [])
    assert none_found, "precondition: at least one instrument reached an honest zero"

    for name in none_found:
        # RULING 56 (2026-07-31) moved WHERE an abstention is reported, so this
        # checks BOTH surfaces. The claim is unchanged and is now stronger by one
        # field: an honest zero is captioned NOWHERE.
        assert not any(u.startswith(f"uncounted_by:{name}:") for u in packet.unresolved), (
            f"{name} ran and found nothing - captioning that as an abstention "
            f"claims a gap where there is a finding")
        assert not any(a.startswith(f"uncounted_by:{name}:") for a in packet.abstentions), (
            f"{name} ran and found nothing - it does not belong on the "
            f"abstention surface either")


def test_a_nominal_scar_id_is_never_lineage() -> None:
    """RULING 50 (2), the second half. `unconfirmed_scarline` ids - recorded on a
    doctrine but NOT confirmed live by the scar store - are barred from
    `scar_lineage` and named in `unresolved` instead.

    A lineage is a claim about what she actually survived. An unverified
    reference is a claim about what a record says. They are different claims and
    the packet must not merge them.

    Driven with NO scar store, where every scarline id is unconfirmable by
    construction - the forcing configuration. (RULING 54 narrowed what NOMINAL
    means, from "not confirmed LIVE" to "absent from the store"; the no-store
    case is unaffected and is now the THIRD case - the store was never consulted
    at all - which is why this configuration still forces the same way.)

    MIGRATED 2026-07-31 UNDER THE RULING-14 PRECEDENT: `_spoken_grounding`
    returns a FOUR-tuple since Ruling 56. The unpack widened; NOT ONE ASSERTION
    MOVED, and a new one was added pinning that a nominal reference STAYS in
    `unresolved` - which is the asymmetry Ruling 56 turns on.
    """
    from src.doctrine.codex import Codex
    from src.doctrine.doctrine_spine import DoctrineSpine
    from src.filtration.echonet import EchoNet
    from src.utils.models import Echo

    net = EchoNet(doctrine_spine=DoctrineSpine(codex=Codex()))   # no scar_core
    collapse = net.filter_claim(Echo(id="E", content="Fracture Carried is false.",
                                     source="t", resonance_score=0.0,
                                     created_at=datetime.now()))
    finding = collapse.overlay.fractures[0]
    assert finding.unconfirmed_scarline == finding.scarline, "precondition: none confirmable"

    refs, lineage, unresolved, abstentions = AureaCore._spoken_grounding(collapse)

    assert lineage == (), "not one nominal id may be reported as lineage"
    for scar_id in finding.scarline:
        assert f"nominal_scar_ref:{scar_id}" in unresolved, (
            "a nominal reference is carried, not silently dropped")
        assert scar_id in refs, (
            "it IS counted evidence - the overlay enumerated it and named it "
            "ungrounded; the two fields answer different questions")
        # RULING 56: and it stays in `unresolved` rather than migrating with the
        # instrument abstentions. An unverified reference IS an unclosed thread
        # of THIS claim; an unbuilt instrument is not.
        assert not any(scar_id in a for a in abstentions), (
            "a nominal scar reference is not an abstention")


# =====================================================================
# C. THE BOUND - blocked paths are byte-identical
# =====================================================================

BLOCKED_CLAIMS = {
    "this statement is false": ExpressionVerdict.SUSPEND,      # PARADOX_SUSPENDED
    "everyone always lies": ExpressionVerdict.SUSPEND,         # SBSRE_CARRIED
    "AVT.001 must be abandoned.": ExpressionVerdict.SUSPEND,   # Ruling 49 fracture
}

# Captured at `f43dd12` and byte-identical after. These are Ruling 33's fixed
# silent strings; if either moves, a silent verdict has started speaking.
SILENT_TEXT = {
    ExpressionVerdict.SUSPEND: (
        "[TRUTH DEFERRED - carried unresolved rather than closed. "
        "Silence is not failure; it is collapse integrity.]"),
    ExpressionVerdict.WITHHOLD: (
        "[NO OUTPUT - silent integrity. The fracture risk is too high for "
        "anything to be said here.]"),
}


@pytest.mark.parametrize("claim, verdict", sorted(BLOCKED_CLAIMS.items()))
def test_a_blocked_path_renders_byte_identical_text(claim, verdict) -> None:
    """RULING 33'S PIN STAYS GREEN, UNTOUCHED.

    Filling the packet is only safe because the silent renderer cannot reach
    what was added. `_render_silent` takes ONE enum member; the packet, the
    mode, the content and now the evidence are not in its scope. This asserts
    the consequence rather than the mechanism.
    """
    result = AureaCore().process_input(claim, source="test")
    assert result["output_blocked"] is True
    assert result["expression_verdict"] is verdict
    assert result["output"] == SILENT_TEXT[verdict]


def test_a_blocked_packet_may_be_full_while_its_render_stays_empty() -> None:
    """The property that makes the whole ruling safe, stated directly: a blocked
    path can carry evidence AND STILL SAY NOTHING.

    This is Ruling 33's one-way authority doing work rather than being described
    - the packet is full, the render is a fixed string, and the two never meet.
    """
    result = AureaCore().process_input("everyone always lies", source="test")
    packet = result["truth_packet"]

    assert packet.evidence_refs, "precondition: this path supplies evidence"
    assert result["output"] == SILENT_TEXT[ExpressionVerdict.SUSPEND]
    for ref in packet.evidence_refs:
        assert ref not in result["output"]
    assert packet.content not in result["output"]


def test_the_silent_renderer_still_takes_exactly_one_argument() -> None:
    """AST. Ruling 33's stated single point of failure: "Adding a parameter to
    this function to 'improve' a withheld message is the one change that would
    dismantle the ruling."

    Ruling 50 is precisely the pass that creates the temptation - there is now
    real evidence sitting in the packet that a withheld truth cannot cite.
    """
    import src.output.hail as mod
    with open(mod.__file__, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "_render_silent")
    args = fn.args
    assert [a.arg for a in args.args] == ["expression"]
    assert not args.kwonlyargs and args.vararg is None and args.kwarg is None


# =====================================================================
# D. THE COLLAPSE SIGNATURE ON SILENT PATHS (Ruling 50 (6))
# =====================================================================

def test_every_silent_path_retains_a_traceable_collapse_signature() -> None:
    """VERIFIED, NOT ASSERTED - the Stage-4 precedent applied prospectively.

    Canon: all filtered outputs retain a traceable collapse signature. A silent
    render says almost nothing, so the obligation lands on the packet. Each
    silent exit must carry the expression verdict, the full pre-wiring
    diagnostic as `content`, at least one `unresolved` id or reason, and a
    render trace naming the dispatch.
    """
    core = AureaCore()
    silent = []
    for claim in ("this statement is false", "everyone always lies"):
        result = core.process_input(claim, source="test")
        assert result["expression_verdict"] in SILENT_VERDICTS
        silent.append(result)

    core.processing_suspended = True
    core.suspension_reason = "signature witness"
    silent.append(core.process_input("anything", source="test"))

    for result in silent:
        packet = result["truth_packet"]
        assert packet.expression_verdict in SILENT_VERDICTS
        assert packet.content.strip(), "the pre-wiring diagnostic survives in full"
        assert packet.unresolved, "at least one id or reason is carried"
        assert any(t.startswith("dispatch=silent") for t in result["render_trace"])


def test_the_suspended_gate_records_no_collapse_verdict_and_that_is_honest() -> None:
    """The one zero in the signature table, and it is not a gap.

    PROCESSING_SUSPENDED returns before EchoNet runs, so no verdict exists to
    record and no echo exists to cite. Coining one is the defect
    `TruthPacket`'s Optional was created to prevent.
    """
    core = AureaCore()
    core.processing_suspended = True
    core.suspension_reason = "witness"
    packet = core.process_input("anything", source="test")["truth_packet"]

    assert packet.collapse_verdict is None
    assert packet.evidence_refs == ()
    assert packet.unresolved, "the reason is still carried"


# =====================================================================
# E. MODE DORMANCY (Ruling 50 (3))
# =====================================================================

def _mode_references(source: str) -> list:
    """Every reference to HAIL's `Mode` in a module's source.

    AST, not a substring scan: the word "mode" appears in prose throughout this
    tree (`mode_used`, "EXPERT mode", `_MODE_RENDERERS`), and a lexical check
    would either miss the import or drown in docstrings.
    """
    tree = ast.parse(source)
    hits = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            hits += [f"import:{a.name}" for a in node.names if a.name == "Mode"]
        elif isinstance(node, ast.Name) and node.id == "Mode":
            hits.append(f"name:{node.lineno}")
        elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) \
                and node.value.id == "Mode":
            hits.append(f"attr:Mode.{node.attr}")
    return hits


def test_mode_is_absent_from_src_outside_hail() -> None:
    """RULING 50 (3): the mode surface is DECLARED DORMANT, and dormancy is
    pinned so a future wire is a DELIBERATE ACT rather than a drift.

    No caller can request any mode today: `_emit` calls `HAIL.render(packet)`
    with no mode argument, so all ten exits render EXPERT. BRIDGE and MIRROR
    refuse a request that cannot be made. The cause is one unbuilt organ - mode
    selection needs a CPA user profile and `cpa.py` is 0 bytes.
    """
    from tests.invariants import _ast as H

    offenders = {}
    for path in H.src_files():
        rel = H.rel(path)
        if rel == "src/output/hail.py":
            continue
        hits = _mode_references(path.read_text(encoding="utf-8"))
        if hits:
            offenders[rel] = hits

    assert offenders == {}, (
        f"HAIL's Mode is referenced outside hail.py at {offenders}. The mode "
        f"surface is dormant behind CPA (Ruling 50 (3)); selecting one on any "
        f"other basis invents the calibration input.")


def test_the_mode_scanner_fires_on_a_real_wire() -> None:
    """Ruling 32's precedent: feed the scanner the violation it exists to catch,
    so a scan that has stopped scanning fails HERE rather than passing quietly.
    """
    WIRED = (
        "from src.output.hail import HAIL, Mode\n"
        "def emit(self, packet):\n"
        "    return self.hail.render(packet, Mode.SIMPLIFIED)\n"
    )
    ATTRIBUTE_ONLY = "import src.output.hail as h\nx = Mode.EXPERT\n"
    BENIGN = (
        "from src.output.hail import HAIL\n"
        "def emit(self, packet):\n"
        "    # EXPERT mode is the default; mode_used records what was consulted\n"
        "    return self.hail.render(packet)\n"
    )

    assert _mode_references(WIRED), "the scanner must SEE an import + selection"
    assert _mode_references(ATTRIBUTE_ONLY), "and a bare Mode.X reference"
    assert _mode_references(BENIGN) == [], (
        "and must not fire on prose or on the default-render call")


def test_both_refused_modes_still_refuse_legibly() -> None:
    """Declared-but-refused over silently-dropped over faked. Each refusal names
    the precondition it cannot meet - CTL for BRIDGE, PSI thread integrity for
    MIRROR - and neither invents one."""
    from src.output.hail import HAIL

    packet = AureaCore().process_input("the kettle boiled quietly",
                                       source="test")["truth_packet"]
    for mode, needle in ((Mode.BRIDGE, "collapse-trace layer (CTL)"),
                         (Mode.MIRROR, "PSI thread integrity")):
        rendered = HAIL.render(packet, mode)
        assert "MODE UNAVAILABLE" in rendered.text
        assert needle in rendered.text
        assert "Declared, not faked" in rendered.text


def test_mirror_is_not_quietly_built_on_RILs_readable_surface() -> None:
    """RULING 50 (3) NAMES THE TEMPTING MOVE so it is not made later.

    RIL's threads are durable (Ruling 42) and `RIL.identity_conflict()` exists,
    so a "thread integrity" surface LOOKS buildable from what is on disk. It is
    the wrong build: canon's precondition is PSI's thread integrity, and
    substituting a different module's readable surface for the one canon names
    is coining the precondition rather than meeting it.

    AST, NOT A SUBSTRING SCAN, and the first draft of this pin got that wrong:
    the comment that RECORDS this refusal names `RIL.identity_conflict()` in
    prose, so a text search flagged the documentation of the decision as the
    decision. Ruling 45's lesson - documenting a fix can break a lexical pin -
    met three times in one file while writing these.
    """
    import src.output.hail as mod
    with open(mod.__file__, "r", encoding="utf-8") as f:
        text = f.read()
    tree = ast.parse(text)

    assert "PSI thread integrity" in text, "the canon precondition is still named"

    imported = set()
    called = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
        elif isinstance(node, ast.Import):
            imported |= {a.name for a in node.names}
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            called.add(node.func.attr)

    assert not any(m.startswith("src.identity") for m in imported), (
        f"hail.py imports an identity module ({sorted(imported)}) - MIRROR's "
        f"precondition is PSI's thread integrity, and substituting RIL's "
        f"readable surface coins the precondition rather than meeting it")
    assert "identity_conflict" not in called, (
        "hail.py CALLS identity_conflict - a gate on a door no caller can open, "
        "built on the wrong module's surface")


# =====================================================================
# F. THE UNPRODUCED VERDICTS KEEP THEIR REOPENING CONDITIONS
# =====================================================================

def test_softened_and_fragment_remain_unproduced() -> None:
    """RULING 50 (5). Both are DECLARED (canon vocabulary) and neither has a
    live trigger - SOFTENED because any trigger needs a numeric cutoff on
    `tone_weight` that bar 5 makes unwritable, FRAGMENT because fragmenting a
    truth requires knowing its parts and the model has no assertion structure.

    If a mapping ever appears here, the response is to cite the ruling that
    authorized it - never to add one to make this green.
    """
    from src.output.ore import UNPRODUCED_VERDICTS

    assert UNPRODUCED_VERDICTS == frozenset(
        {ExpressionVerdict.SOFTENED, ExpressionVerdict.FRAGMENT})


def test_the_reopening_conditions_are_recorded_at_the_members() -> None:
    """A reopening condition that lives only in a manifest is a condition the
    next reader of the code does not have. Both sit at the enum member."""
    import src.output.truth_packet as mod
    with open(mod.__file__, "r", encoding="utf-8") as f:
        text = f.read()

    assert "REOPENING CONDITION" in text
    assert "assertion-level decomposition" in text
    assert "PySAT" in text, "FRAGMENT's dependency is named"
    assert "non-numeric trigger" in text.lower() or "NON-NUMERIC" in text


# =====================================================================
# G. CONST-ID (Ruling 50 (4))
# =====================================================================

def test_const_id_is_absent_when_the_pass_does_not_span() -> None:
    """A TRACE FLAG, absent unless the recorded fact holds. One node, or several
    in one constellation, is the ordinary case - a flag that appeared every pass
    would report nothing."""
    result = AureaCore().process_input("the kettle boiled quietly", source="test")
    assert [t for t in result["render_trace"] if t.startswith("topology.")] == []


def test_const_id_is_present_when_the_pass_spans_two_constellations() -> None:
    """The other direction, driven against CONSTRUCTED topology state.

    WHY CONSTRUCTED AND NOT A CLAIM, stated because it is this resolution's
    finding: measured over the 39-claim set, the nodes `_emit` can reach from
    `result` - the echo and the scar - NEVER span. Every chamber scar carries
    type `recursive_contradiction`, which routes to `identity_core`, and the
    echo node is either unplaced or `identity_core` too. The three genuine spans
    in the whole measurement are echo + BLACK SPHERE paradox node, and that node
    id is not on `result` under any key.

    So the instrument is real and correct and does not fire on the wired
    pipeline today. That gap is DECLARED at `_const_id_trace` and reported,
    rather than closed by adding a node-set field to `result` - which is a
    decision about what a pass records, not an implementation detail.
    """
    core = AureaCore()
    result = core.process_input("Honesty is pointless.", source="test")
    echo, scar = result["echo"], result["scar_formed"]
    assert scar is not None, "precondition: this pass placed two nodes"

    nodes = core.tca.topology.nodes
    assert echo.id in nodes and scar.id in nodes

    # Force the fact: move the echo node into a DIFFERENT live constellation.
    other = next(cid for cid, c in core.tca.topology.constellations.items()
                 if cid != nodes[scar.id].position.constellation_id)
    core.tca.topology.constellations[other].add_node(nodes[echo.id])
    assert (nodes[echo.id].position.constellation_id
            != nodes[scar.id].position.constellation_id)

    trace = core._const_id_trace(result)
    assert len(trace) == 1
    assert trace[0].startswith("topology.const_id=spanning")
    assert other in trace[0]
    assert nodes[scar.id].position.constellation_id in trace[0]


def test_the_const_id_trace_actually_reaches_the_result() -> None:
    """THE SEAM, pinned separately from the FACT.

    ADDED AFTER A SURVIVING MUTANT: deleting the `+ self._const_id_trace(result)`
    from `_emit` passed the whole file, because the positive-direction pin above
    calls `_const_id_trace` DIRECTLY. A correct instrument nobody attached is a
    flag that never reports - and it would have looked tested.

    The trace function is stubbed here on purpose: what is under test is the
    WIRING, and the fact computation is pinned in both directions above. HAIL's
    own `render_trace` must survive intact beside it - the orchestrator appends,
    it does not overwrite.
    """
    core = AureaCore()
    core._const_id_trace = lambda result: ("topology.const_id=<sentinel>",)

    result = core.process_input("the kettle boiled quietly", source="test")

    assert "topology.const_id=<sentinel>" in result["render_trace"]
    assert any(t.startswith("dispatch=") for t in result["render_trace"]), (
        "HAIL's own trace entries must survive - the orchestrator APPENDS")


def test_countability_is_compared_by_identity_never_by_name() -> None:
    """AST. `Countability`'s own docstring: "a state selected by string is a
    state nothing type-checks."

    ADDED AFTER A SURVIVING MUTANT: rewriting the guard as
    `evidence.countability.name == "COUNTED"` is behaviourally identical today
    and passed everything. It is also exactly the shape the enum was made
    valueless to prevent - and the next state added to that enum is where a
    string comparison silently stops matching.
    """
    import src.aurea_core as mod
    with open(mod.__file__, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "_spoken_grounding")

    for node in ast.walk(fn):
        if not isinstance(node, ast.Compare):
            continue
        touches_countability = any(
            isinstance(sub, ast.Attribute) and sub.attr in ("countability", "name")
            for sub in ast.walk(node))
        if not touches_countability:
            continue
        assert all(isinstance(op, (ast.Is, ast.IsNot)) for op in node.ops), (
            f"line {node.lineno}: countability compared with "
            f"{[type(o).__name__ for o in node.ops]}. It is an identity check "
            f"against a Countability member, never an equality check on a name.")
        assert not any(isinstance(sub, ast.Constant) and isinstance(sub.value, str)
                       for sub in ast.walk(node)), (
            f"line {node.lineno}: a string literal appears in a countability "
            f"comparison - the state is selected by enum member, not by name.")


def test_const_id_never_gates_anything() -> None:
    """§9 standing bar 5. It is a trace entry and nothing reads it.

    Canon supplies no dissonance number, and `calculate_cohesion()` returns a
    real float that it would be very natural to compare against something. That
    comparison is the move this refuses.
    """
    from tests.invariants import _ast as H

    # The TRACE KEY, not the bare word: `tca_core.py` uses `const_id` as an
    # ordinary loop variable over `self.constellations.items()`, and the first
    # draft of this pin flagged it. Ruling 45's lesson - a lexical instrument
    # matches the vocabulary, not the meaning.
    readers = []
    for path in H.src_files():
        if H.rel(path) == "src/aurea_core.py":
            continue
        if "topology.const_id" in path.read_text(encoding="utf-8"):
            readers.append(H.rel(path))
    assert readers == [], f"{readers} consume the CONST-ID flag; it gates nothing"

    import src.aurea_core as mod
    with open(mod.__file__, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "_const_id_trace")
    for node in ast.walk(fn):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            assert node.func.attr != "calculate_cohesion", (
                "cohesion is a MAGNITUDE and comparing it is a coined threshold "
                "at the output layer (Ruling 28's shape)")


def test_event_horizons_is_declared_not_built() -> None:
    """The candidate the data REFUSED, recorded so the refusal is legible.

    `topology.event_horizons` has exactly ONE occurrence in all of `src/`: its
    initialisation to an empty set. Nothing ever adds to it, so a flag reading
    it would be permanently False and its pin permanently vacuous - the TCAML
    known-vacuous-pin shape, which this codebase declares rather than ships.

    THIS TEST GOES RED THE DAY SOMETHING WRITES THAT SET, which is exactly when
    the candidate reopens.

    AST, NOT A LINE SCAN. The first draft counted text occurrences and flagged
    the docstring at `_const_id_trace` that RECORDS this very refusal - the
    third time in this file that documenting a decision tripped a lexical pin
    (Ruling 45's finding). What is counted is ATTRIBUTE ACCESS in code.
    """
    from tests.invariants import _ast as H

    accesses = []
    for path in H.src_files():
        tree = H.parse(path)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr == "event_horizons":
                accesses.append((H.rel(path), node.lineno))

    assert len(accesses) == 1, (
        f"`event_horizons` is accessed at {accesses}. It had exactly ONE - its "
        f"initialisation. If something WRITES it now, the CONST-ID candidate "
        f"declared-not-built at `_const_id_trace` has become buildable and "
        f"should be ruled on rather than left declared.")
    assert accesses[0][0] == "src/topology/tca_core.py"
