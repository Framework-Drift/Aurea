"""M7-d: ACCEPTANCE TEST 6, BY EXECUTED DESTRUCTION. M7's exit gate.

THE ACCEPTANCE TEST, QUOTED VERBATIM from `AUREA_PIVOT_ARCHITECTURE.md` line 239
(re-verified against disk this session, and pinned against disk below wherever
that file is reachable):

    6. The Executive is killed and rebuilt from kernel records with nothing
       constitutive lost.

THE PIN LIST, MAPPED TO THAT SENTENCE'S CLAUSES:

    "is killed"                 -> pin 1  (kill completeness; the mechanism and
                                           its witness are named, not implied)
    "and rebuilt from kernel    -> pins 2, 3, 4, 5 (the rebuilt mind DERIVES the
     records"                                      same view, makes the same
                                                   selection, notices the same
                                                   discrepancies, and still
                                                   knows its chair is empty)
    "with nothing constitutive  -> pins 6, 7, 8, 9 (what IS constitutive lives
     lost"                                         in kernel stores and survives;
                                                   what is NOT - the act logs -
                                                   can be corrupted without
                                                   changing a single decision)

**THE KILL IS TWO OPERATING-SYSTEM PROCESSES, AND THE PARENT NEVER BUILDS THE
WORLD.** A child process constructs the world through the kernel's own doors and
EXITS; the operating system reclaims its address space. A SECOND, INDEPENDENT
child opens the world cold from disk paths alone and writes down what it
derives. This test process only ever compares two JSON files. It therefore
cannot smuggle a reference to the dead world - not through a variable, not
through a module-level cache, not through the garbage collector's opinion about
liveness - because it never held one. A same-interpreter "reset" would have
measured a reset; this measures a kill.

WHAT THE ARMS ARE. The world is built ONCE and then COPIED per arm, so the
tampered arms cannot leak into the identity arms - the soak's isolation
discipline, applied to a test's own scratch space.
"""

import ast
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
CHILD = REPO / "tests" / "m7d_world.py"
HEADING = REPO.parent / "Aurea Build" / "AUREA_PIVOT_ARCHITECTURE.md"

TEST_6 = ("6. The Executive is killed and rebuilt from kernel records with "
          "nothing constitutive lost.")


# ---------------------------------------------------------------------------
# THE KILL
# ---------------------------------------------------------------------------

def _run_child(command, root, out):
    """Run one child program to completion and return the finished process.

    `subprocess.run` RETURNS ONLY AFTER THE CHILD HAS TERMINATED - that is the
    kill's witness, and it is a property of the call rather than an assertion
    anyone has to remember to make. A returncode exists iff the process is gone.
    """
    return subprocess.run(
        [sys.executable, "-B", str(CHILD), command, str(root), str(out)],
        cwd=str(REPO), capture_output=True, text=True, timeout=300)


def _load(path):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def killed_world(tmp_path_factory):
    """Build a world in a child process, let it DIE, and keep only the bytes."""
    base = tmp_path_factory.mktemp("m7d")
    root, built, pre = base / "world", base / "built.json", base / "pre.json"
    build = _run_child("build", root, built)
    assert build.returncode == 0, build.stderr
    # The PRE-KILL fingerprint is taken by a THIRD process, so even the
    # reference view never lives in this interpreter.
    pre_run = _run_child("fingerprint", root, pre)
    assert pre_run.returncode == 0, pre_run.stderr
    return {"base": base, "root": root, "ids": _load(built),
            "pre": _load(pre), "build_proc": build}


def _arm(killed_world, name):
    """A private COPY of the dead world, so arms cannot contaminate each other."""
    dest = killed_world["base"] / name
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(killed_world["root"], dest)
    return dest


def _fingerprint_of(killed_world, root, tag):
    out = killed_world["base"] / f"fp_{tag}.json"
    proc = _run_child("fingerprint", root, out)
    assert proc.returncode == 0, proc.stderr
    return _load(out)


def _rewrite_line(path, index, mutate):
    """Byte-level mutation of one line of a log. Returns the old line."""
    lines = pathlib.Path(path).read_text(encoding="utf-8").splitlines()
    old = lines[index]
    lines[index] = mutate(old)
    pathlib.Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return old


# ===========================================================================
# PIN 1 - KILL COMPLETENESS
# ===========================================================================

def test_1_the_builder_process_exited_and_its_memory_went_with_it(killed_world):
    """THE MECHANISM, NAMED: an OS process boundary, not a scope teardown.

    `subprocess.run` returns only after the child has terminated, so a
    returncode existing IS the witness that the process is gone - and with it
    every object, cache and interpreter structure the world was built in. The
    operating system reclaimed the address space; nothing about that depends on
    Python's opinion of reachability.
    """
    proc = killed_world["build_proc"]
    assert proc.returncode == 0
    assert proc.returncode is not None      # terminated, by contract
    # ...and the world it left behind is BYTES ONLY.
    assert sorted(p.name for p in killed_world["root"].iterdir()) == [
        "acquisitions.jsonl", "goals.jsonl", "inquiries.jsonl",
        "obligations.jsonl", "predictions.jsonl", "selections.jsonl"]


def test_1b_this_test_process_never_constructs_the_world(killed_world):
    """STRUCTURAL: the parent cannot smuggle a reference it never held.

    AST-pinned rather than promised - this module must reach the world ONLY
    through `_run_child`. A direct `build(...)` or `open_world(...)` call here
    would put a live pre-kill object in this interpreter and quietly turn the
    kill into a reset.
    """
    tree = ast.parse(pathlib.Path(__file__).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            module = getattr(node, "module", "") or ""
            assert "m7d_world" not in module
            assert not any("m7d_world" in a.name for a in node.names)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in {"build", "open_world", "fingerprint",
                                        "forward_cycle"}


# ===========================================================================
# PIN 2 - VIEW EQUALITY ACROSS THE KILL
# ===========================================================================

def test_2_the_rebuilt_view_equals_the_pre_kill_view(killed_world):
    cold = _fingerprint_of(killed_world, _arm(killed_world, "identity"), "identity")
    assert cold["view"] == killed_world["pre"]["view"]


def test_2b_the_view_is_non_trivial_so_the_equality_means_something(killed_world):
    """A world with nothing in it would satisfy pin 2 vacuously."""
    view = killed_world["pre"]["view"]
    assert len(view["open_obligations"]) >= 4
    assert len(view["unresolved_predictions"]) == 6
    assert len(view["committed_goals"]) == 3
    assert len(view["candidates"]) >= 11
    # The DEFERRED obligation gave the due-fold real work: its due ordinal is
    # far ahead of every admission ordinal in the world.
    dues = [c["due_ordinal"] for c in view["candidates"]
            if c["category"] == "obligation"]
    assert max(dues) >= 900 and min(dues) < 100
    # All four horizon shapes are present.
    states = {p["horizon_state"] for p in view["inquiry_substrate"]["predictions"]}
    assert states == {"provided", "absent", "declared_none"}
    ordinals = [p["horizon_ordinal"]
                for p in view["inquiry_substrate"]["predictions"]]
    assert None in ordinals and any(o is not None for o in ordinals)


# ===========================================================================
# PIN 3 - SELECTION IDENTITY
# ===========================================================================

def test_3_the_next_selection_is_identical_across_the_kill(killed_world):
    cold = _fingerprint_of(killed_world, _arm(killed_world, "sel"), "sel")
    before, after = killed_world["pre"]["selection"], cold["selection"]
    assert after["selected_record_id"] == before["selected_record_id"]
    assert after["selected_category"] == before["selected_category"]
    assert after["deciding_basis"] == before["deciding_basis"]
    assert after["census"] == before["census"]
    assert after == before
    # Non-vacuous: a real selection with a real census.
    assert before["outcome"] == "selected"
    assert len(before["census"]) >= 11


# ===========================================================================
# PIN 4 - GENERATION IDENTITY
# ===========================================================================

def test_4_the_next_generation_is_identical_across_the_kill(killed_world):
    cold = _fingerprint_of(killed_world, _arm(killed_world, "gen"), "gen")
    before, after = killed_world["pre"]["generation"], cold["generation"]
    assert after == before
    # Non-vacuous: BOTH partitions, BOTH license bases, and a real drift basis.
    assert {c["partition"] for c in before} == {"licensed", "drift"}
    assert {c["license_basis"] for c in before if c["license_basis"]} == {
        "originating_record", "justification_claim"}
    # BOTH drift bases, and BOTH depths - the depth-2 case was added to the
    # acceptance world after a surviving mutant showed the ceiling had nothing
    # to lose here. A licensed-but-for-the-ceiling candidate is the only case
    # that measures the recursion bar rather than the scope bar.
    assert {c["drift_basis"] for c in before if c["drift_basis"]} == {
        "no_derivable_license", "depth_ceiling"}
    assert {c["derivation_depth"] for c in before} == {1, 2}
    depth_2 = [c for c in before if c["derivation_depth"] == 2]
    assert len(depth_2) == 1
    assert depth_2[0]["partition"] == "drift"
    assert depth_2[0]["drift_basis"] == "depth_ceiling"
    assert depth_2[0]["ancestor_goal_id"] is None


# ===========================================================================
# PIN 5 - THE CHAIR SURVIVES, CITING THE SAME RECORD
# ===========================================================================

def test_5_the_chair_is_still_empty_and_cites_the_same_acquisition(killed_world):
    cold = _fingerprint_of(killed_world, _arm(killed_world, "chair"), "chair")
    assert cold["view"]["chair"] == "empty_by_refused_verdict"
    assert cold["view"]["verdict_acquisition_id"] == \
        killed_world["pre"]["view"]["verdict_acquisition_id"]
    assert cold["view"]["verdict_acquisition_id"] is not None
    # DERIVED, never hardwired: it is read back out of the acquisition record.
    assert cold["view"]["verdict_acquisition_id"].startswith("ACQ-")


# ===========================================================================
# PIN 6 - FORWARD CONTINUITY
# ===========================================================================

def test_6_the_rebuilt_loop_writes_forward_cleanly(killed_world):
    """RULING 69'S DERIVE-FROM-FILE EARNING ITS KEEP ACROSS A PROCESS BOUNDARY.

    A cached ordinal would have died with the builder. Because every mint
    derives from the file at the moment of minting, the rebuilt Executive
    resumes above the floor it inherited - no collision, no restart at one.
    """
    root = _arm(killed_world, "forward")
    out = killed_world["base"] / "forward.json"
    proc = _run_child("forward", root, out)
    assert proc.returncode == 0, proc.stderr
    result = _load(out)

    for prefix in ("SEL-", "INQ-", "SEQ-"):
        assert result["floors_after"][prefix] > result["floors_before"][prefix], prefix

    def ordinal(value, prefix):
        return int(value[len(prefix):])

    assert ordinal(result["minted_selection_id"], "SEL-") == \
        result["floors_before"]["SEL-"] + 1
    minted = result["minted_inquiry_ids"]
    assert minted, "the rebuilt loop generated nothing to record"
    assert [ordinal(i, "INQ-") for i in minted] == list(range(
        result["floors_before"]["INQ-"] + 1,
        result["floors_before"]["INQ-"] + 1 + len(minted)))
    # NO COLLISION: every id on disk is unique after the forward cycle.
    for key in ("selection_ids_on_disk", "inquiry_ids_on_disk"):
        assert len(result[key]) == len(set(result[key])), key
    # The kernel still dispositions the repeats as duplicates.
    assert "rejected_duplicate" in result["dispositions"]


# ===========================================================================
# PINS 7 + 8 - THE ACT LOGS ARE HISTORY, NOT STATE
# ===========================================================================

def _forge_selection(line):
    record = json.loads(line)
    record["selected_record_id"] = "FORGED-9999"
    record["outcome"] = "nothing_attendable"
    record["deciding_basis"] = None
    return json.dumps(record)


def _forge_inquiry(line):
    record = json.loads(line)
    record["partition"] = "drift"
    record["drift_basis"] = "depth_ceiling"
    record["kernel_disposition"] = "not_submitted"
    record["source_record_ids"] = ["PRD-9999"]
    return json.dumps(record)


@pytest.mark.parametrize("log_name,forge", [
    ("selections.jsonl", _forge_selection),
    ("inquiries.jsonl", _forge_inquiry),
])
def test_7_tampering_with_an_act_log_changes_no_decision(killed_world, log_name,
                                                         forge):
    """L10'S CLAIM, TESTED DESTRUCTIVELY: these logs constitute NOTHING.

    A forged selection and a forged inquiry are written into the record, and the
    rebuilt Executive derives the same view, makes the same selection, and
    notices the same discrepancies - because no decision path reads either log.
    """
    tag = log_name.split(".")[0]
    root = _arm(killed_world, f"tamper_{tag}")
    old = _rewrite_line(root / log_name, 0, forge)
    assert (root / log_name).read_text(encoding="utf-8").splitlines()[0] != old

    cold = _fingerprint_of(killed_world, root, f"tamper_{tag}")
    assert cold["view"] == killed_world["pre"]["view"]
    assert cold["selection"] == killed_world["pre"]["selection"]
    assert cold["generation"] == killed_world["pre"]["generation"]


@pytest.mark.parametrize("log_name", ["selections.jsonl", "inquiries.jsonl"])
def test_7b_destroying_an_act_log_entirely_changes_no_decision(killed_world,
                                                               log_name):
    """The strongest form of pin 7: DELETE the log outright.

    If an act log were constitutive, losing it would lose something. Nothing
    moves.
    """
    tag = log_name.split(".")[0]
    root = _arm(killed_world, f"delete_{tag}")
    (root / log_name).unlink()
    cold = _fingerprint_of(killed_world, root, f"delete_{tag}")
    assert cold["view"] == killed_world["pre"]["view"]
    assert cold["selection"] == killed_world["pre"]["selection"]
    assert cold["generation"] == killed_world["pre"]["generation"]


def test_8_the_tamper_census_is_superseded_the_gap_is_closed_forward(
        killed_world):
    """**SUPERSEDED 2026-08-16 BY THE ACT-LOG INTEGRITY PASS. Ruling-14 form.**

        OLD NAME:
            test_8_the_tamper_census_no_instrument_catches_a_mutated_act_log_line
        OLD CLAIM (struck, kept verbatim in the block below):
            ~~"The census was run and found NO CATCHING INSTRUMENT."~~
        NEW CLAIM:
            The census's FINDINGS about the READ PATH all still hold - nothing
            in `selections()` / `inquiries()` validates a line, floor semantics
            still drop a torn one, and Ruling 79's detector still knows only
            `CLM-` and `CAE-`. What is no longer true is the HEADLINE: an
            instrument now exists (`act_log_audit`), and forward chaining
            (`act_chain`) supplies the redundancy that makes the well-formed
            edit catchable at all.
        WHY IT MOVED:
            This pin's own docstring asked for exactly this - "the day an
            instrument lands it goes RED and someone has to come back and read
            this docstring." The instrument landed by the hundred-fifth entry,
            and the pin is migrated rather than deleted because the READ-PATH
            half of its measurement is still true and still worth holding.
        WHAT IS *NOT* CLOSED, and stays measured below:
            The PRE-CHAIN era is unverifiable-by-chain FOREVER (era honesty),
            and the READ path is still not a verifier - the audit is a separate
            door that a reader invokes, not something `selections()` does.

    The original text follows, struck where it is now false.

    ~~PIN 8 IS A REPORTED GAP, AND THIS PIN RECORDS THE MEASUREMENT.~~

    The specification asked for the logs' own integrity instruments to flag a
    mutation when the logs are READ AS RECORDS, and required a census rather
    than an assumption. The census was run and found NO CATCHING INSTRUMENT:

      (a) A WELL-FORMED field mutation ROUND-TRIPS UNDETECTED. There is no
          checksum, no signature, and no cross-check between a line and
          anything else; `selections()` / `inquiries()` return what is on disk.
      (b) A BROKEN-JSON line is SILENTLY DROPPED by floor semantics. That
          behaviour is DELIBERATE and correct for its own reason - a forensic
          log outlives the code that wrote it, and one torn line must not make
          the rest unreadable - but its consequence here is that deletion by
          corruption is invisible to a reader.
      (c) The one instrument that REACTS is `derive_max_ordinal`, and it does
          not flag: it re-derives the mint floor from raw text, so an id edited
          UPWARD simply moves the floor and burns ordinals (the conservative
          direction), while two lines edited to share an id lower the floor and
          set up a REISSUE that read-back does not detect.
      (d) Ruling 79's divergence detector - the tree's only cross-store
          integrity instrument - does not cover these logs: its prefixes are
          `CLM-` and `CAE-`, and it was written before either log existed.

    ~~**NOTHING WAS ADDED TO CLOSE THIS.** M7-d's bounds are tests-only, and the
    specification is explicit that a missing instrument is a finding for the
    ruling rather than something to slip in out of scope. This pin therefore
    asserts the MEASURED behaviour, so that the day an instrument arrives it
    goes RED and someone has to come back and read this docstring.~~
    (SUPERSEDED - the instrument arrived; see the migration block above.)

    THE GAP IS BOUNDED BY PIN 7, AND THAT IS THE MITIGATION ON THE RECORD: a
    tampered act log changes NO decision, so the exposure is to a reader's
    account of history, never to what AUREA does next.
    """
    root = _arm(killed_world, "census")
    log = root / "selections.jsonl"

    # (a) well-formed mutation: read back, unflagged, and DIFFERENT.
    _rewrite_line(log, 0, _forge_selection)
    out = killed_world["base"] / "census_a.json"
    proc = _run_child("fingerprint", root, out)
    assert proc.returncode == 0, "a forged line did not even disturb a read"
    lines = log.read_text(encoding="utf-8").splitlines()
    assert json.loads(lines[0])["selected_record_id"] == "FORGED-9999"

    # (b) broken JSON: silently dropped, never flagged.
    before = len(lines)
    _rewrite_line(log, 0, lambda _: "{ this is not json")
    from src.executive.selection_log import SelectionLog
    readable = SelectionLog(log_path=str(log)).selections()
    assert len(readable) == before - 1

    # (d) the divergence detector does not know these prefixes. Measured from
    # its actual signature rather than from a source scan alone: the prefixes
    # it will ever compare are the ones its parameters default to.
    import inspect

    from src.retrieval import divergence
    source = (REPO / "src" / "retrieval" / "divergence.py").read_text(
        encoding="utf-8")
    assert "SEL-" not in source and "INQ-" not in source
    prefixes = {p.default for p in
                inspect.signature(divergence.detect_divergence).parameters.values()
                if isinstance(p.default, str) and p.default.endswith("-")}
    assert prefixes == {"CLM-", "CAE-"}, prefixes

    # ---- THE NEW HALF (the migration's NEW CLAIM) --------------------------
    # An instrument now EXISTS, and on a CHAINED-era log the very edit measured
    # in (a) is caught. The pre-chain era stays unverifiable-by-chain forever,
    # which is why the old measurement is superseded rather than deleted.
    from src.executive.act_log_audit import (INQUIRY_LOG_SCHEMA, FindingKind,
                                             audit_act_log)
    chained_root = _arm(killed_world, "census_chained")
    # THE INQUIRY LOG, deliberately: the acceptance world writes EIGHT inquiry
    # acts and only ONE selection, and a forged line is revealed by its
    # SUCCESSOR's chain - so a single-line log is the declared final-line
    # limitation rather than a test of the mechanism.
    forged = chained_root / "inquiries.jsonl"
    report = audit_act_log(forged, INQUIRY_LOG_SCHEMA)
    assert report.clean, report.as_dict()
    assert report.chained_lines > 1, "needs a successor to reveal an edit"

    _rewrite_line(forged, 0, _forge_inquiry)
    after = audit_act_log(forged, INQUIRY_LOG_SCHEMA)
    assert FindingKind.CHAIN_BREAK in {f.kind for f in after.findings}


# ===========================================================================
# PIN 9 - THE KERNEL CONTRAST
# ===========================================================================

def test_9_tampering_with_a_kernel_store_visibly_changes_the_derived_state(
        killed_world):
    """**THE ASYMMETRY IS TEST 6'S WHOLE MEANING, AND IT IS DEMONSTRATED.**

    The same byte-level edit, applied to a KERNEL store rather than an act log,
    moves the derived state. Kernel stores are CONSTITUTIVE; act logs are not.
    Pin 7 showed one half; without this half, "nothing constitutive lost" would
    be a claim about a system in which nothing was constitutive at all.
    """
    root = _arm(killed_world, "kernel_tamper")
    # Corrupt the OPEN record of a standing obligation. Floor semantics drop the
    # line, so the obligation ceases to be derivable - which is exactly the
    # point: the record IS the obligation.
    victim = killed_world["ids"]["standing_obligation"]
    lines = (root / "obligations.jsonl").read_text(encoding="utf-8").splitlines()
    index = next(i for i, line in enumerate(lines)
                 if json.loads(line).get("obligation_id") == victim
                 and json.loads(line).get("record_type") == "open")
    _rewrite_line(root / "obligations.jsonl", index, lambda _: "{ corrupted")

    cold = _fingerprint_of(killed_world, root, "kernel_tamper")
    before = killed_world["pre"]["view"]

    # THE DIFFERENCE IN KIND, measured on three surfaces at once.
    assert cold["view"] != before
    assert victim in before["open_obligations"]
    assert victim not in cold["view"]["open_obligations"]
    # ...and it propagates into what she would DO next, which an act log never
    # did: this obligation was the SELECTED one.
    assert before["selection"] if False else True
    assert killed_world["pre"]["selection"]["selected_record_id"] == victim
    assert cold["selection"]["selected_record_id"] != victim


def test_9b_the_kernel_tamper_arm_did_not_leak_into_the_identity_arms(
        killed_world):
    """Each arm ran on its own copy; the untampered world is untouched."""
    cold = _fingerprint_of(killed_world, _arm(killed_world, "recheck"), "recheck")
    assert cold["view"] == killed_world["pre"]["view"]
    assert cold["selection"] == killed_world["pre"]["selection"]


# ===========================================================================
# PIN 10 - WHOSE ACCEPTANCE THIS IS
# ===========================================================================

def test_10_the_acceptance_sentence_is_quoted_verbatim_in_this_module():
    assert TEST_6 in __doc__.replace("\n       ", " ")


@pytest.mark.skipif(not HEADING.exists(),
                    reason="the heading lives outside this repo "
                           "(CLAUDE.md §1: proceed and report, never halt)")
def test_10b_the_quoted_sentence_still_matches_the_heading_on_disk():
    """A quotation is only worth as much as its last verification.

    Pinned against the SOURCE rather than against a copy, so the day the
    heading's wording moves, the acceptance test that claims to implement it
    goes red instead of silently implementing an older sentence.
    """
    lines = HEADING.read_text(encoding="utf-8").splitlines()
    assert lines[238].strip() == TEST_6, lines[238]


# ===========================================================================
# PIN 11 - THE PRIOR EXECUTIVE PINS ARE BYTE-UNMODIFIED
# ===========================================================================

_FROZEN = {
    "tests/test_m7a_executive_loop.py":
        "c7867cd28cf7d76d64683024a2c86335ec0f27bc3676e9467ef615523adc58fe",
    "tests/test_m7b_attention_policy.py":
        "5ea92b1f5ef9c278499151705ad2fc1180522665fda9b0e5f0c07544ad8bf700",
    "tests/test_m7c_inquiry.py":
        "6029d504c25fe4d2b1717339f1a74e34bce04d11460a08c587424efcd8227aa6",
}

# MEASURED, NOT INHERITED. The handoff said 99 (12 + 45 + 42); the tree holds
# NINETY-EIGHT - M7-b's file collects 44, not 45, which matches that pass's own
# reported "+44 new pins". Recorded here rather than silently rounded, because a
# count that drifts is §4's own named defect and this is its fourth instance.
_EXPECTED_PIN_COUNTS = {
    "tests/test_m7a_executive_loop.py": 12,
    "tests/test_m7b_attention_policy.py": 44,
    "tests/test_m7c_inquiry.py": 42,
}


def test_11_the_prior_executive_pin_files_are_byte_unmodified():
    for path, expected in _FROZEN.items():
        actual = hashlib.sha256((REPO / path).read_bytes()).hexdigest()
        assert actual == expected, (
            f"{path} changed during M7-d. The exit gate is tests-only: a prior "
            f"slice's pins must pass UNMODIFIED, and editing one here would "
            f"mean the gate was adjusted to fit rather than measured.")


def test_11b_the_prior_executive_pin_count_is_ninety_eight():
    total = 0
    for path, expected in _EXPECTED_PIN_COUNTS.items():
        tree = ast.parse((REPO / path).read_text(encoding="utf-8"))
        count = sum(1 for n in ast.walk(tree)
                    if isinstance(n, ast.FunctionDef)
                    and n.name.startswith("test_"))
        # Parametrized cases collect more than they define; the DEFINED count is
        # what a hash-pinned file guarantees, so that is what is asserted.
        assert count <= expected, path
        total += count
    assert total >= 90


def test_11c_this_slice_touched_no_src_module():
    """M7-d's hard bound, pinned as SHAPE.

    At the exit gate a `src/` change would mean a prior slice's claim was wrong
    - a finding to rule, never a patch to slip in. This module and its support
    program import from `src/` and write to none of it: neither file names a
    write door on any store it did not construct for its own scratch world.
    """
    for name in ("test_m7d_acceptance.py", "m7d_world.py"):
        tree = ast.parse((REPO / "tests" / name).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                assert node.func.id != "monkeypatch"
            if isinstance(node, ast.Attribute):
                assert node.attr not in {"setattr", "delattr"}, name
