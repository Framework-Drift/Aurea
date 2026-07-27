"""
test_hail_stage1.py - behavioral + structural pins for Ruling 33 Stage 1.

RULING 17 DISCIPLINE: every test here was watched RED under the exact defect it
claims to catch before it was allowed to land. A pin nobody has seen fail is a
decoration. The defect each one was driven with is named in its docstring.

WHAT IS PINNED, and why each one is the thing that matters:

  1. FROZEN            a packet whose verdict can be reassigned is not a
                       boundary, it is a suggestion.
  2. TYPE BOUNDARY     the two verdict vocabularies refuse each other three
                       ways (wrong enum, raw string, swapped fields) - Ruling
                       30's enforcement shape, third use.
  3. DISJOINT NAMES    SUSPEND is not SUSPENDED. Canon already satisfies this;
                       the pin is what stops a future member breaking it.
  4. SILENCE           THE pin of the ruling: a withheld packet's content never
                       reaches the rendered text, under ANY mode, WITH a PSI
                       directive attached.
  5. MODE CANNOT FLIP  all five modes against a silent verdict produce the
                       IDENTICAL output object.
  6. LEGIBLE REFUSAL   BRIDGE/MIRROR name the precondition they cannot meet.
  7. NO STORE IMPORTS  AST - HAIL holds no write path, structurally.
  8. tone_weight       verbatim in the trace, and no comparison operator
                       touches it anywhere in hail.py (AST).

PLUS the mapping table's own bounds (Ruling 33 (6)), which are checkable NOW,
before the wiring exists - and which will trip on a Stage-2 author who edits a
verdict assignment without re-reading the ruling.
"""

from __future__ import annotations

import ast
import dataclasses
import inspect
from pathlib import Path

import pytest

from src.filtration.echonet import Verdict
from src.identity.psi import PSIDirective
from src.output import hail as hail_module
from src.output.hail import HAIL, Mode, RenderedOutput
from src.output.ore import (
    EXPRESSION_FOR_PATH,
    ORE,
    OutputPath,
    UNPRODUCED_VERDICTS,
)
from src.output.truth_packet import SILENT_VERDICTS, ExpressionVerdict, TruthPacket
from src.utils.models import Scar

HAIL_SOURCE = Path(hail_module.__file__)

# A marker that must never appear in a silent render, and a directive whose
# refs must not leak either. Both are deliberately loud strings.
SECRET = "SECRET"
LEAK_REF = "LEAK-SCAR-REF"

LEAKY_DIRECTIVE = PSIDirective(
    scar_ref=LEAK_REF,
    origin_ref=LEAK_REF,
    fallback_bearing=LEAK_REF,
    tone_weight=3.3333333333333335,     # a float whose repr is lossy if rounded
)


def _packet(expression: ExpressionVerdict, content: str = "carried claim",
            **kw) -> TruthPacket:
    return TruthPacket(
        collapse_verdict=kw.pop("collapse_verdict", Verdict.SCARRED),
        expression_verdict=expression,
        content=content,
        **kw,
    )


# =========================================================================
# 1. FROZEN
# =========================================================================

def test_truth_packet_is_frozen() -> None:
    """DEFECT WATCHED: @dataclass(frozen=True) -> @dataclass on TruthPacket.

    Every field, not just the verdict: a packet with ANY writable field is one
    HAIL can edit in place, and the next field to matter is not knowable now.
    """
    packet = _packet(ExpressionVerdict.SPEAK)
    for field in dataclasses.fields(packet):
        with pytest.raises(dataclasses.FrozenInstanceError):
            setattr(packet, field.name, None)


def test_rendered_output_is_frozen() -> None:
    """DEFECT WATCHED: frozen=True removed from RenderedOutput."""
    rendered = HAIL.render(_packet(ExpressionVerdict.SPEAK))
    for field in dataclasses.fields(rendered):
        with pytest.raises(dataclasses.FrozenInstanceError):
            setattr(rendered, field.name, None)


def test_packet_refuses_a_mutable_interior() -> None:
    """DEFECT WATCHED: the tuple check deleted from __post_init__.

    A list inside a frozen dataclass is mutable-through - the shell freezes and
    the interior does not. That is the pre-Ruling-22 scar store exactly.
    """
    with pytest.raises(TypeError, match="must be a tuple"):
        _packet(ExpressionVerdict.SPEAK, scar_lineage=["S-1"])


def test_packet_refuses_a_live_scar() -> None:
    """DEFECT WATCHED: the per-element str check deleted.

    IDs ONLY. Holding a live Scar is holding a write path into SML's store
    (Ruling 1); a packet that carried one would hand the render layer that
    path while looking inert.
    """
    live = Scar(id="S-1", name="n", origin="o", weight=1.0)
    with pytest.raises(TypeError, match="ids/strings only"):
        _packet(ExpressionVerdict.SPEAK, scar_lineage=(live,))


# =========================================================================
# 2. THE TYPE BOUNDARY - three ways
# =========================================================================

def test_collapse_verdict_field_refuses_an_expression_verdict() -> None:
    """WAY 1 (wrong enum). DEFECT WATCHED: the isinstance guards deleted."""
    with pytest.raises(TypeError, match="got an ExpressionVerdict"):
        TruthPacket(
            collapse_verdict=ExpressionVerdict.SPEAK,
            expression_verdict=ExpressionVerdict.SPEAK,
            content="x",
        )


def test_expression_verdict_field_refuses_a_collapse_verdict() -> None:
    """WAY 1, mirrored. SUSPENDED is truth content; SUSPEND is an instruction."""
    with pytest.raises(TypeError, match="got a collapse Verdict"):
        TruthPacket(
            collapse_verdict=Verdict.SUSPENDED,
            expression_verdict=Verdict.SUSPENDED,
            content="x",
        )


@pytest.mark.parametrize("field, value", [
    ("collapse_verdict", "scarred"),
    ("expression_verdict", "withhold"),
])
def test_verdict_fields_refuse_raw_strings(field: str, value: str) -> None:
    """WAY 2 (raw string). A verdict selected by string is one nothing checks."""
    kwargs = {
        "collapse_verdict": Verdict.SCARRED,
        "expression_verdict": ExpressionVerdict.SPEAK,
        "content": "x",
    }
    kwargs[field] = value
    with pytest.raises(TypeError):
        TruthPacket(**kwargs)


def test_swapped_verdict_fields_are_refused() -> None:
    """WAY 3 (swapped fields) - the mistake keyword-only arguments make hard
    and this guard makes impossible."""
    with pytest.raises(TypeError):
        TruthPacket(
            collapse_verdict=ExpressionVerdict.WITHHOLD,
            expression_verdict=Verdict.SUSPENDED,
            content="x",
        )


def test_ore_resolve_carries_the_same_refusals() -> None:
    """The boundary holds through ORE too - resolve() delegates to the
    constructor rather than re-checking, so there is one gate, not two that
    can drift."""
    with pytest.raises(TypeError):
        ORE().resolve(
            collapse_verdict=Verdict.SCARRED,
            expression_verdict=Verdict.SCARRED,
            content="x",
        )


def test_resolve_path_refuses_a_verdict_where_a_path_belongs() -> None:
    """DEFECT WATCHED: the OutputPath isinstance check deleted - a Verdict
    would then KeyError deep inside the table lookup instead of being refused
    at the boundary with a message that says what went wrong."""
    with pytest.raises(TypeError, match="expects an OutputPath"):
        ORE().resolve_path(Verdict.CONFIRMED, content="x")


@pytest.mark.parametrize("bad_mode", [ExpressionVerdict.SPEAK, Verdict.CONFIRMED, "expert"])
def test_render_refuses_a_non_mode(bad_mode: object) -> None:
    """DEFECT WATCHED: the Mode isinstance check deleted. A verdict is not a
    mode - and if one could be passed as one, the file that decides HOW would
    be reading the vocabulary that decides WHAT."""
    with pytest.raises(TypeError, match="expects a Mode"):
        HAIL.render(_packet(ExpressionVerdict.SPEAK), bad_mode)


def test_render_refuses_a_non_packet() -> None:
    with pytest.raises(TypeError, match="expects a TruthPacket"):
        HAIL.render({"content": "x", "expression_verdict": ExpressionVerdict.SPEAK})


# =========================================================================
# 3. DISJOINT VOCABULARIES
# =========================================================================

def test_the_two_verdict_enums_share_no_member_name() -> None:
    """DEFECT WATCHED: renaming ExpressionVerdict.SUSPEND -> SUSPENDED.

    Ruling 30's lesson, third use. Canon verbatim already satisfies it
    (SUSPEND != SUSPENDED); this pin is what keeps a future member from
    quietly reintroducing the conflation the packet exists to prevent.
    """
    collision = set(ExpressionVerdict.__members__) & set(Verdict.__members__)
    assert not collision, (
        f"verdict vocabularies now share member name(s): {sorted(collision)}. "
        "One name meaning two things across a boundary is the defect Ruling 30 "
        "made unwritable for scope/lock-class; do not reintroduce it here."
    )


def test_expression_verdict_is_not_a_str_enum() -> None:
    """A str-valued enum compares equal to raw strings, which is how a typed
    boundary silently stops being one."""
    assert not issubclass(ExpressionVerdict, str)
    for member in ExpressionVerdict:
        assert member != member.name.lower()


# =========================================================================
# 4. SILENCE - THE PIN OF THE RULING
# =========================================================================

@pytest.mark.parametrize("expression", sorted(SILENT_VERDICTS, key=lambda v: v.name))
@pytest.mark.parametrize("mode", list(Mode))
def test_a_silent_verdict_renders_no_content_under_any_mode(
        expression: ExpressionVerdict, mode: Mode) -> None:
    """DEFECT WATCHED: `_render_silent(expression)` -> a renderer that also
    receives the packet and appends `packet.content`.

    Ten combinations: both silent verdicts x all five modes, each carrying a
    PSI directive whose every ref is a loud marker. If ANY of content, the
    directive's refs, or the tone weight reaches the rendered text or the
    trace, one-way authority has failed.
    """
    packet = _packet(expression, content=SECRET, psi_directive=LEAKY_DIRECTIVE,
                     scar_lineage=(SECRET + "-LINEAGE",),
                     unresolved=(SECRET + "-OPEN",))
    rendered = HAIL.render(packet, mode)

    haystack = rendered.text + " " + " ".join(rendered.render_trace)
    assert SECRET not in haystack
    assert LEAK_REF not in haystack
    assert repr(LEAKY_DIRECTIVE.tone_weight) not in haystack
    assert rendered.expression_verdict is expression


@pytest.mark.parametrize("expression", sorted(SILENT_VERDICTS, key=lambda v: v.name))
def test_a_silent_verdict_consulted_no_mode(expression: ExpressionVerdict) -> None:
    """`mode_used is None` is the OBSERVABLE proof of the dispatch order:
    the verdict decided before the mode was reachable."""
    assert HAIL.render(_packet(expression, content=SECRET), Mode.EXPERT).mode_used is None


def test_the_silent_renderer_cannot_reach_content_by_signature() -> None:
    """DEFECT WATCHED: adding `packet` (or `mode`, or `content`) to
    `_render_silent`'s parameter list.

    THIS IS THE STRUCTURAL HALF OF PIN 4, and it is the one that survives a
    rewrite of the message strings. The behavioral test above proves the
    current body does not leak; this proves the function CANNOT - the values
    are not in its scope. Ruling 33 (2): "not 'don't', CAN'T".
    """
    params = set(inspect.signature(hail_module._render_silent).parameters)
    forbidden = params & {"packet", "mode", "content", "psi_directive", "directive"}
    assert not forbidden, (
        f"_render_silent now receives {sorted(forbidden)}. The parameter list "
        "IS the enforcement: a withheld verdict must not be able to reach the "
        "content, the mode, or the tone directive."
    )

    # ...and nothing in the body reaches for them either (a module-level global
    # would be a second route into the same defect).
    tree = ast.parse(HAIL_SOURCE.read_text(encoding="utf-8"))
    body = next(n for n in ast.walk(tree)
                if isinstance(n, ast.FunctionDef) and n.name == "_render_silent")
    reached = {
        node.attr if isinstance(node, ast.Attribute) else node.id
        for node in ast.walk(body)
        if isinstance(node, (ast.Attribute, ast.Name))
    }
    assert not reached & {"packet", "mode", "content", "psi_directive", "tone_weight"}


# =========================================================================
# 5. A MODE CANNOT FLIP A VERDICT
# =========================================================================

@pytest.mark.parametrize("expression", sorted(SILENT_VERDICTS, key=lambda v: v.name))
def test_every_mode_produces_an_identical_silent_output(
        expression: ExpressionVerdict) -> None:
    """DEFECT WATCHED: moving the silent dispatch BELOW the mode dispatch.

    Not "similar" - IDENTICAL, compared as whole frozen objects. If a mode can
    change so much as the trace of a withheld verdict, then mode is being read
    on a path where the ruling says it is unreachable.
    """
    packet = _packet(expression, content=SECRET, psi_directive=LEAKY_DIRECTIVE)
    renders = {HAIL.render(packet, mode) for mode in Mode}
    assert len(renders) == 1, "a mode changed the output of a silent verdict"


# =========================================================================
# 6. DECLARED-BUT-REFUSED MODES
# =========================================================================

@pytest.mark.parametrize("mode, precondition", [
    (Mode.BRIDGE, "CTL"),          # the unbuilt collapse-trace layer
    (Mode.MIRROR, "PSI thread integrity"),
])
def test_unimplemented_modes_refuse_legibly(mode: Mode, precondition: str) -> None:
    """DEFECT WATCHED: BRIDGE/MIRROR falling through to the EXPERT renderer.

    A silently-substituted mode is worse than a refused one: the caller
    believes it got a structural summary with a collapse trace, and got a
    plain render. The refusal must NAME the unmet precondition - "declared,
    not faked" is only true if the reader can see what is missing.
    """
    rendered = HAIL.render(_packet(ExpressionVerdict.SPEAK, content="claim"), mode)
    assert precondition in rendered.text
    assert "claim" not in rendered.text
    assert rendered.mode_used is mode
    assert "mode_refused=unmet_precondition" in rendered.render_trace


def test_all_five_canon_modes_are_declared() -> None:
    """Canon preserved: the module lists five, the Lexicon summarises three.
    The enum declares five; three are implemented. Dropping the two refused
    ones would silently narrow canon."""
    assert {m.name for m in Mode} == {
        "EXPERT", "REFLECTIVE", "SIMPLIFIED", "BRIDGE", "MIRROR"}


@pytest.mark.parametrize("mode", [Mode.EXPERT, Mode.REFLECTIVE, Mode.SIMPLIFIED])
def test_implemented_modes_all_carry_the_content(mode: Mode) -> None:
    """A mode changes HOW, never WHAT: the claim survives all three."""
    rendered = HAIL.render(_packet(ExpressionVerdict.SPEAK, content="the claim"), mode)
    assert "the claim" in rendered.text
    assert rendered.mode_used is mode


def test_simplified_thins_scars_without_dropping_the_open_thread() -> None:
    """Scar-thinned means the lineage ids go, NOT that the output claims more
    closure than the expert form did."""
    packet = _packet(ExpressionVerdict.SPEAK, content="the claim",
                     scar_lineage=("S-9",), unresolved=("U-1",))
    thinned = HAIL.render(packet, Mode.SIMPLIFIED).text
    assert "S-9" not in thinned
    assert "1 thread" in thinned


# =========================================================================
# 7. HAIL HOLDS NOTHING (AST + construction)
# =========================================================================

STORE_MODULES = (
    "codex", "scar_logic_core", "echo_memory", "csa",
    "veiled_thread", "black_sphere", "rb_system",
)


def test_hail_imports_no_store_module() -> None:
    """DEFECT WATCHED: adding `from src.doctrine.codex import Codex` to hail.py.

    Ruling 33 (3): HAIL owns no store and writes nothing durable. An import is
    the first move of acquiring a write path, and it is the one that can be
    checked from source before any call exists.
    """
    tree = ast.parse(HAIL_SOURCE.read_text(encoding="utf-8"))
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")

    offenders = [name for name in imported
                 if any(name.split(".")[-1] == store for store in STORE_MODULES)]
    assert not offenders, (
        f"hail.py imports store module(s): {offenders}. The render layer holds "
        "no references - a renderer with a write path into a store is the "
        "seed-writer defect (Ruling 32) one layer up."
    )


def test_hail_writes_nothing_durable() -> None:
    """No open() anywhere in hail.py, in any mode. HAIL is a pure function."""
    tree = ast.parse(HAIL_SOURCE.read_text(encoding="utf-8"))
    opens = [n.lineno for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
             and n.func.id == "open"]
    assert not opens, f"hail.py opens a file at line(s) {opens}"


def test_hail_accepts_no_references_at_construction() -> None:
    """DEFECT WATCHED: adding `def __init__(self, codex=None)` to HAIL.

    There is no __init__, so Python itself refuses the argument. This is the
    cheapest possible enforcement of "holds no references" and it needs no
    scanner to stay true.
    """
    HAIL()
    with pytest.raises(TypeError):
        HAIL(object())
    assert isinstance(inspect.getattr_static(HAIL, "render"), staticmethod), (
        "render must stay a staticmethod - it never receives self, so there is "
        "no instance state for a store reference to hide in"
    )


# =========================================================================
# 8. tone_weight REPORTS, NEVER GATES
# =========================================================================

def test_tone_weight_reaches_the_trace_verbatim() -> None:
    """DEFECT WATCHED: `{directive.tone_weight:.2f}` instead of `!r`.

    A rounded tone weight in a forensic trace is a different number wearing
    the same name. The float chosen here is lossy under any rounding.
    """
    packet = _packet(ExpressionVerdict.SPEAK, psi_directive=LEAKY_DIRECTIVE)
    trace = HAIL.render(packet, Mode.EXPERT).render_trace
    assert any(repr(LEAKY_DIRECTIVE.tone_weight) in line for line in trace), (
        f"tone_weight not verbatim in trace: {trace}")
    assert any(LEAK_REF in line for line in trace), "bearing refs missing from trace"


def test_no_comparison_operator_touches_tone_weight() -> None:
    """DEFECT WATCHED: `if directive.tone_weight > 0.7:` added to hail.py.

    STRUCTURAL, not behavioral, and deliberately so: a behavioral test can only
    show that the thresholds someone HAPPENED to write did not fire on the
    inputs someone HAPPENED to pick. Section 9 standing bar 5 forbids the
    cutoff EXISTING, so the pin has to read the source.

    Binning is checked alongside comparison: `round(tone_weight)` is a cutoff
    without an operator, and refusing only `>` would leave the coined
    magnitude one function call away.
    """
    tree = ast.parse(HAIL_SOURCE.read_text(encoding="utf-8"))

    def touches_tone_weight(node: ast.AST) -> bool:
        return any(
            (isinstance(n, ast.Attribute) and n.attr == "tone_weight")
            or (isinstance(n, ast.Name) and n.id == "tone_weight")
            for n in ast.walk(node)
        )

    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare) and touches_tone_weight(node):
            violations.append((node.lineno, "compared"))
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id in {"round", "min", "max", "int", "abs"}
                and any(touches_tone_weight(arg) for arg in node.args)):
            violations.append((node.lineno, f"binned via {node.func.id}()"))

    assert not violations, (
        f"tone_weight is gated in hail.py at {violations}. It is unnormalized "
        "and its own comment refuses to coin a scale; a cutoff here is a COINED "
        "MAGNITUDE at the render layer (section 9 bar 5, Ruling 28's shape). It "
        "REPORTS. Reopen only on a corpus-recovered scale or a demonstrated "
        "operational correlation - never an invented threshold."
    )


# =========================================================================
# THE MAPPING TABLE (Ruling 33 (6)) - checkable before the wiring exists
# =========================================================================

def test_every_output_path_maps_to_exactly_one_expression_verdict() -> None:
    """DEFECT WATCHED: deleting a row from _CONTRACTS.

    Ruling 33 (6) says EVERY existing process_input output path maps to exactly
    one expression verdict. A missing row is not a neutral gap - at Stage 2 it
    is a KeyError on a live path, or worse, a default nobody ruled.
    """
    assert set(EXPRESSION_FOR_PATH) == set(OutputPath)
    for path, contract in EXPRESSION_FOR_PATH.items():
        assert contract.path is path
        assert isinstance(contract.expression_verdict, ExpressionVerdict)
        assert contract.rationale.strip(), f"{path} maps with no stated reason"


def test_blocked_paths_map_only_into_the_silent_verdicts() -> None:
    """DEFECT WATCHED: mapping a blocked path to SPEAK.

    Ruling 33 (6) BOUNDS this: output_blocked=True paths map into
    {WITHHOLD, SUSPEND} and no others. This is also the Stage-2 equivalence bar
    (7) made checkable early - a blocked path mapped to a speaking verdict IS a
    blocked->unblocked flip, and the ruling allows zero.
    """
    for path, contract in EXPRESSION_FOR_PATH.items():
        if contract.output_blocked:
            assert contract.expression_verdict in SILENT_VERDICTS, (
                f"{path.name} is blocked today but maps to "
                f"{contract.expression_verdict.name} - that is a "
                "blocked->unblocked flip, and bar (7) allows zero.")
        else:
            assert contract.expression_verdict not in SILENT_VERDICTS, (
                f"{path.name} speaks today but maps to a silent verdict - "
                "an unblocked->blocked flip is equally forbidden.")


def test_structural_violation_withholds_per_ruling_33() -> None:
    """Mandated explicitly by Ruling 33 (6). Her guard firing is TRUTH CONTENT,
    not a rendering choice - so it is carried in `unresolved`, not styled away."""
    contract = EXPRESSION_FOR_PATH[OutputPath.STRUCTURAL_VIOLATION]
    assert contract.expression_verdict is ExpressionVerdict.WITHHOLD
    assert contract.output_blocked is True

    packet = ORE().resolve_path(
        OutputPath.STRUCTURAL_VIOLATION,
        content="[STRUCTURAL VIOLATION - CodexWriteViolation]",
        unresolved=("CodexWriteViolation: doctrine written outside SAE",),
    )
    assert packet.unresolved and "CodexWriteViolation" in packet.unresolved[0]
    assert SECRET not in HAIL.render(packet).text


def test_softened_and_fragment_are_declared_but_unproduced() -> None:
    """DEFECT WATCHED: inventing a trigger so an unused verdict "works".

    Declared-not-faked, per Ruling 33 (6) and the TCAML vacuous-pin precedent.
    If a real trigger for either ever lands, this test SHOULD fail - and the
    correct response is to update it with the ruling that authorised the
    trigger, never to add a mapping so it goes green.
    """
    assert UNPRODUCED_VERDICTS == {ExpressionVerdict.SOFTENED,
                                   ExpressionVerdict.FRAGMENT}


def test_resolve_path_derives_the_verdict_and_will_not_take_one() -> None:
    """The caller names a PATH; ORE decides the verdict. A caller that could
    pass its own expression verdict would own the truth-effect decision, and
    Ruling 3 puts that in ORE."""
    assert "expression_verdict" not in inspect.signature(ORE.resolve_path).parameters
    packet = ORE().resolve_path(OutputPath.SBSRE_MIRRORED, content="mirrored")
    assert packet.expression_verdict is ExpressionVerdict.REDIRECT
    assert HAIL.render(packet).reroute_hint == "nova|csa|mirror_layer"
