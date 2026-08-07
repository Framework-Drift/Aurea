"""
test_ruling68.py - RULING 68: the perception lifecycle.

A claim-ancestry record records A CLAIM: a non-`str` arrival is refused at the
door - no CLM line, no echo, no node - and the one-to-one sentence becomes
unqualifiedly true instead of carefully qualified. The manufactured `source`
dies as SHAPE: parameter, field and tag deleted.

WHERE THE REST OF THIS RULING'S PINS LIVE, AND WHY THEY ARE NOT COPIED HERE:
`tests/test_verification_pass.py` carries the six collected witnesses this
ruling closes - five orphan shapes and the manufactured-source witness. They
were written against the DEFECT at `0b2072c`, they carry its measured values,
and Ruling 68 retired them in place (markers deleted, assertions kept, each
marker recorded verbatim). Pin (c), the one-to-one property across a mixed
batch, is `test_one_to_one_holds_across_a_mixed_batch`; pin (d), the
empty/whitespace control, is
`test_an_empty_or_whitespace_claim_is_perceived_and_is_not_an_orphan`.

This file carries what those cannot: the gate at the LEDGER (b), the deletions
as SHAPE (e), and the suspended door's byte-identity (f).
"""

from __future__ import annotations

import ast
import inspect
from dataclasses import fields
from pathlib import Path

import pytest

from src.aurea_core import AureaCore
from src.perception.spl import SPL
from src.utils.models import Echo

REPO = Path(__file__).resolve().parents[1]

NON_STR = [None, 12345, ["a"], {"k": "v"}, object(), bytearray(b"x"), 3.5, True]


def _ledger_bytes(core) -> bytes:
    path = core.ancestry.ledger_path
    return path.read_bytes() if path.exists() else b""


# =====================================================================
# (b) THE TYPE GATE, WITNESSED AT THE LEDGER
# =====================================================================

@pytest.mark.parametrize("bad", NON_STR, ids=lambda v: type(v).__name__)
def test_a_non_str_arrival_leaves_the_ledger_byte_identical(bad):
    """RULING 68 res.1, measured at the FILE rather than at a line count.

    A line count would pass against an implementation that wrote a line and
    truncated it back off; byte-identity is the property the ruling actually
    states. The ledger is primed with a real claim first, so this is not the
    vacuous "an empty file stayed empty".

    `bool` is in the table deliberately: it is not a `str`, and `True` reaching
    SPL would be a claim nobody made.
    """
    core = AureaCore()
    core.process_input("A real claim, so the ledger is not empty.")
    before = _ledger_bytes(core)
    assert before, "precondition: the ledger holds a real line"

    result = core.process_input(bad)

    assert _ledger_bytes(core) == before, (
        f"a {type(bad).__name__} arrival changed the permanent ancestry record")
    assert result["claim_id"] is None
    assert result["echo"] is None
    assert result["errors"], "the refusal must be caller-visible in the result"
    assert type(bad).__name__ in result["errors"][0], (
        f"the refusal must name what arrived; got {result['errors']!r}")


def test_the_refusal_is_an_ordinary_rejection_not_a_structural_violation():
    """DOCKET N'S FORM, and Ruling 68 res.1 says so in terms.

    Nothing here is one of AUREA's own guards firing - a caller passed the wrong
    type. Reporting it as a structural violation would suppress output, write a
    durable violation record, and read a caller's mistake as a breach of the
    architecture (Ruling 25's taxonomy, inverted).
    """
    core = AureaCore()
    result = core.process_input(None)

    assert result.get("structural_violation") is None
    assert result["output_blocked"] is False
    assert result["output"], "an ordinary rejection still speaks"


def test_a_non_str_arrival_places_no_node_and_advances_no_clock():
    """The gate sits ABOVE the three clock advances, so a non-claim ages
    nothing - Rider R2's principle in the mint comment's own grammar: a mind
    that is not running does not perceive claims, and an arrival that is not a
    claim is not perceived either."""
    core = AureaCore()
    core.process_input("A real claim.")
    nodes = len(core.tca.topology.nodes)
    cycle = core.tcaml._cycle

    result = core.process_input(12345)

    assert len(core.tca.topology.nodes) == nodes, "a non-claim placed a node"
    assert result["pass_nodes"] == ()
    assert core.tcaml._cycle == cycle, "a non-claim advanced the symbolic clock"


# =====================================================================
# (e) THE DELETIONS, AS SHAPE
# =====================================================================

def test_neither_process_input_declares_a_source_parameter():
    """RULING 68 res.3, Ruling 61's form: DELETION, NOT DEPRECATION.

    A legacy display parameter that exists but is unread is a loaded gun for the
    next caller who defaults it - which is exactly how `"user"` reached a
    durable store field for every claim AUREA ever processed.
    """
    # RULING 75 MIGRATION (2026-08-05), Ruling-14 form. NO ASSERTION MOVED -
    # the same claim, over the method that replaced the one it named.
    #     OLD: `("SPL", SPL.process_input)`
    #     NEW: `("SPL", SPL.normalize)`
    # Ruling 75 DELETED `SPL.process_input` outright: SPL stopped minting, so it
    # stopped constructing an Echo at all, and `normalize` is what remains of
    # this layer's perception verb. **The `source` claim survives the rename
    # intact** - and it is now enforced by something stronger than a signature
    # scan, since SPL no longer builds the record a `source` could land on.
    for owner, func in (("AureaCore.process_input", AureaCore.process_input),
                        ("SPL.normalize", SPL.normalize)):
        params = inspect.signature(func).parameters
        assert "source" not in params, (
            f"{owner} accepts `source` again: {list(params)}")


def test_the_echo_dataclass_has_no_source_field():
    """The field itself. `EchoMemory` serializes `__dict__` raw, so the absence
    flows through structurally rather than by anyone remembering to strip it."""
    names = {f.name for f in fields(Echo)}
    assert "source" not in names, f"Echo.source is back: {sorted(names)}"
    assert "claim_id" in names, (
        "the join key to the single origin surface must remain - deleting the "
        "display string is only safe because the real one is reachable")


def test_no_module_in_src_writes_a_source_tag_or_reads_an_echo_source():
    """RULING 68 res.3 AS SHAPE, scanned across ALL of `src/`.

    TWO patterns, because the ruling deleted two different things: the node tag
    that COPIED a fabricated origin onto the topology, and any read of the
    deleted field. Origin is reached from a node the way Ruling 58 ruled it
    single - `node_id == echo.id -> echo.claim_id -> the ledger`.
    """
    tag_writes, field_reads = [], []
    for path in sorted((REPO / "src").rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        rel = path.relative_to(REPO).as_posix()
        for node in ast.walk(tree):
            if isinstance(node, ast.JoinedStr):
                rendered = ast.unparse(node)
                if rendered.startswith(("f'source:", 'f"source:')):
                    tag_writes.append(f"{rel}:{node.lineno} {rendered}")
            if (isinstance(node, ast.Attribute) and node.attr == "source"
                    and isinstance(node.value, ast.Name)
                    and node.value.id in ("echo", "e", "probe")):
                field_reads.append(f"{rel}:{node.lineno} {ast.unparse(node)}")
    assert not tag_writes, "a `source:` node tag is back:\n" + "\n".join(tag_writes)
    assert not field_reads, "something reads a deleted field:\n" + "\n".join(field_reads)


def test_the_source_scanner_actually_fires():
    """THE SCANNER'S OWN CONTROL - Ruling 32's answer to the vacuous pin.

    A scan that passes because it cannot see is worth nothing, so the same two
    patterns are fed to the same logic and must both be caught.
    """
    for source, kind in (
        ('echo_node.tags.add(f"source:{source}")\n', "tag"),
        ("x = echo.source\n", "read"),
    ):
        tree = ast.parse(source)
        hits = []
        for node in ast.walk(tree):
            if isinstance(node, ast.JoinedStr):
                rendered = ast.unparse(node)
                if rendered.startswith(("f'source:", 'f"source:')):
                    hits.append(node)
            if (isinstance(node, ast.Attribute) and node.attr == "source"
                    and isinstance(node.value, ast.Name)
                    and node.value.id in ("echo", "e", "probe")):
                hits.append(node)
        assert hits, f"the scanner is blind to a {kind} violation"

    # And it must NOT flag `SuspensionEntry.source`, a DIFFERENT class that
    # Ruling 68 does not touch - the two-file census called this out by name.
    tree = ast.parse("x = entry.source\n")
    assert not [n for n in ast.walk(tree)
                if isinstance(n, ast.Attribute) and n.attr == "source"
                and isinstance(n.value, ast.Name)
                and n.value.id in ("echo", "e", "probe")]


def test_an_echo_node_carries_its_claim_id_reachable_origin():
    """THE POSITIVE HALF, and why deleting the tag loses nothing.

    The ruling's claim is that origin is REACHABLE, not merely that the
    fabricated copy is gone. Walked end to end: node id -> echo id -> claim_id
    -> the ledger line that records the origin.
    """
    import json

    core = AureaCore()
    result = core.process_input("A claim whose origin must stay reachable.")

    node_id = result["pass_nodes"][0]
    echo = result["echo"]
    assert node_id == echo.id, "the echo node is keyed by the echo id"
    assert echo.claim_id == result["claim_id"]

    lines = core.ancestry.ledger_path.read_text(encoding="utf-8").splitlines()
    record = json.loads(lines[-1])
    assert record["claim_id"] == echo.claim_id, (
        "the ledger line for this claim is reachable from the node, which is "
        "the whole reason the tag was redundant")


# =====================================================================
# (f) THE SUSPENDED DOOR IS UNCHANGED
# =====================================================================

def test_a_suspended_pass_still_refuses_before_the_mint():
    """RULING 68 res.1: the suspension gate keeps its position and behaviour
    EXACTLY. The type gate went BELOW it, so the suspended surface is untouched.

    Pinned for both a valid and an invalid arrival: under suspension the type
    gate must never be reached, so a `bytearray` and a real claim are refused
    identically - by the door, not by the type check.
    """
    for arrival in ("A real claim.", bytearray(b"not even a claim")):
        core = AureaCore()
        core.processing_suspended = True
        core.suspension_reason = "test suspension"
        before = _ledger_bytes(core)

        result = core.process_input(arrival)

        assert result["claim_id"] is None
        assert result["echo"] is None
        assert _ledger_bytes(core) == before
        # READ THE PACKET, NOT THE RENDERED OUTPUT. Ruling 33 Stage 2 renders
        # every blocked exit to one of two FIXED silent strings, and the
        # pre-wiring diagnostic survives verbatim as `truth_packet.content` -
        # so `result['output']` cannot distinguish these two paths and asserting
        # on it would pin the renderer instead of the gate order.
        assert "SUSPENDED" in (result["truth_packet"].content or ""), (
            f"{type(arrival).__name__} was refused by the type gate rather "
            f"than the suspended door - the gate must sit BELOW suspension; "
            f"packet said {result['truth_packet'].content!r}")


def test_the_type_gate_sits_between_the_suspension_gate_and_the_mint():
    """THE ORDER, AS SHAPE - res.1 rules the position, so a pin reads it.

    Behaviourally the two are distinguishable only through the output string
    above; structurally the ordering is exact, and a refactor that hoisted the
    type gate above suspension would change what a suspended AUREA reports
    without failing any behavioural pin that did not think to check.
    """
    src = inspect.getsource(AureaCore.process_input)
    suspension = src.index("if self.processing_suspended:")
    type_gate = src.index("if not isinstance(raw_input, str):")
    mint = src.index("self.ancestry.record(origin)")
    assert suspension < type_gate < mint, (
        "res.1 rules the order: suspension gate, then type gate, then mint")
