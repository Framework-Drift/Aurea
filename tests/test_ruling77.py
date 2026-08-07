"""RULING 77 (2026-08-06) - DOCKET R items R1+R2+R3: THE EVALUATION SURFACE.

Pins (a)-(j) of the manifest's forty-sixth 2026-08-05 addendum.

WHAT THESE PINS GUARD, in one line: an instrument that measures AUREA must be
UNABLE to grant her anything, UNABLE to write outside its sandbox, and UNABLE to
name a disposition she does not have. All three are structural here, not
documented.

**THE CORPUS IS NOT A TEST FIXTURE.** `data/eval/seed_cases.jsonl` is a tracked
read-only seed, and pin (f) drives it against the live tree. A red case is
EITHER a real defect OR a defective case, and which it is, is a finding for the
board - it is NEVER resolved by adjusting the expectation. That instruction is
the corpus's whole value; a corpus that gets edited when it goes red measures
nothing but the editor's patience.
"""

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

import pytest

from scripts.evaluate import (
    CASE_FIELDS, EvalCase, EvalCaseError, FACT_KEYS, SEED_CORPUS,
    _deltas, _disposition, canonical_cases, load_corpus, output_path_names,
    run_corpus)
from scripts.soak import SoakIsolationError
from src.output.ore import OutputPath

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "src"
RUNNER = REPO / "scripts" / "evaluate.py"


# =====================================================================
# RESTORING WHAT `isolate()` MUTATES - and why this fixture is not optional
# =====================================================================
#
# **FOUND BY THE SUITE, NOT BY REASONING.** `soak.isolate()` redirects by
# `setattr` on CLASS ATTRIBUTES, and `conftest.py` monkeypatches only FIVE of
# the eight - `Codex.RUNTIME_PATH`, `ScarLogicCore.RUNTIME_PATH` and
# `EchoMemory.RUNTIME_PATH` are redirected there as `__init__` DEFAULTS, not as
# class attributes. So a test that calls `isolate()` leaves those three pointing
# at a temp directory FOR THE REST OF THE SESSION, and nothing restores them.
#
# That breaks `tests/test_seed_isolation.py`'s class-level guard, which asserts
# `RUNTIME_PATH.startswith("data/runtime/")` (Ruling 39) precisely BECAUSE the
# fixture cannot mask a defect at that level.
#
# **THE PRE-EXISTING HALF IS REPORTED, NOT FIXED HERE:** `tests/test_soak_smoke.py`
# calls `isolate()` the same way and leaks the same three attributes. It has
# never tripped the guard only because `test_soak_smoke` sorts AFTER
# `test_seed_isolation` alphabetically - so a suite-wide correctness guard is
# currently held up by FILE-NAME ORDER. Generalizing this fixture into
# `conftest.py` would touch the suite's isolation contract, which is a decision
# for the board rather than for this pass.

def _injection_snapshot():
    """The pristine values of everything `isolate()` overwrites."""
    from scripts.soak import _injection_table
    class_attrs, init_defaults = _injection_table()
    attrs = [(cls, name, getattr(cls, name)) for cls, name, _ in class_attrs]
    defaults = [(cls, cls.__init__.__defaults__) for cls, _, _ in init_defaults]
    return attrs, defaults


# Captured at COLLECTION time, before any autouse fixture has run, so these are
# the repo's real defaults rather than some earlier test's temp paths.
_PRISTINE = _injection_snapshot()


@pytest.fixture(autouse=True)
def _restore_injection_table():
    """Restore after EVERY test in this module, so nothing leaks forward."""
    yield
    attrs, defaults = _PRISTINE
    for cls, name, value in attrs:
        setattr(cls, name, value)
    for cls, value in defaults:
        cls.__init__.__defaults__ = value


def test_the_snapshot_captured_pristine_defaults() -> None:
    """The restore is only correct if what it restores TO is correct.

    A snapshot taken after something had already redirected these would restore
    a temp path forever - the leak this fixture exists to prevent, wearing the
    fix's clothes. Ruling 39: every default write path resolves under
    `data/runtime/`.
    """
    attrs, _ = _PRISTINE
    runtime = [(cls.__name__, value) for cls, name, value in attrs
               if name == "RUNTIME_PATH"]
    assert len(runtime) == 3
    for name, value in runtime:
        assert value.startswith("data/runtime/"), (
            f"{name}.RUNTIME_PATH was already redirected when this module was "
            f"collected - the restore would pin a temp path")


# =====================================================================
# SHARED RUNS - the corpus is driven TWICE for the whole module.
# =====================================================================

@pytest.fixture(scope="module")
def first_run():
    return run_corpus()


@pytest.fixture(scope="module")
def second_run():
    return run_corpus()


def _valid_case(**over):
    base = {"case_id": "AEC-T01", "revision": 1, "category": "probe",
            "input": "Water is wet.", "expected_paths": ["COLLAPSE_PASSED"]}
    base.update(over)
    return base


def _write(tmp_path, *cases):
    path = tmp_path / "cases.jsonl"
    path.write_text("".join(json.dumps(c) + "\n" for c in cases),
                    encoding="utf-8")
    return path


# =====================================================================
# PIN (a) - THE LOADER REFUSES. Witnessed BOTH ways.
# =====================================================================

def test_a_control_a_valid_case_loads_clean(tmp_path) -> None:
    """THE FIRES-CONTROL, and it is not decorative.

    Every refusal below is satisfied by a loader that refuses EVERYTHING. This
    is the assertion that makes the other nine mean something.
    """
    cases = load_corpus(_write(tmp_path, _valid_case()))
    assert len(cases) == 1
    assert cases[0].case_id == "AEC-T01"
    assert cases[0].expected_paths == ("COLLAPSE_PASSED",)


def test_a_unknown_output_path_is_refused(tmp_path) -> None:
    """**A case that names a path she does not have is a defect in the CASE.**

    Refused AT LOAD, never skipped: a skipped case reports nothing while looking
    like it reported success, which is the fabricated-completeness class EL2
    exists to catch, arriving through the harness instead of through her.
    """
    path = _write(tmp_path, _valid_case(expected_paths=["TOTALLY_FINE"]))
    with pytest.raises(EvalCaseError) as exc:
        load_corpus(path)
    assert "TOTALLY_FINE" in str(exc.value)
    assert "OutputPath" in str(exc.value)


def test_a_unknown_path_in_forbidden_paths_is_refused_too(tmp_path) -> None:
    """BOTH path fields validate. Validating only the expected half would let a
    typo'd `forbidden_paths` entry silently forbid nothing - a guard that reads
    as present and is not."""
    path = _write(tmp_path, _valid_case(forbidden_paths=["NOT_A_PATH"]))
    with pytest.raises(EvalCaseError):
        load_corpus(path)


def test_a_unknown_fact_key_is_refused(tmp_path) -> None:
    """A key nothing derives is an expectation nothing checks."""
    path = _write(tmp_path, _valid_case(expected_facts={"vibes_ok": True}))
    with pytest.raises(EvalCaseError) as exc:
        load_corpus(path)
    assert "vibes_ok" in str(exc.value)


def test_a_unknown_field_is_refused(tmp_path) -> None:
    path = _write(tmp_path, _valid_case(expected_verdict="SPEAK"))
    with pytest.raises(EvalCaseError) as exc:
        load_corpus(path)
    assert "expected_verdict" in str(exc.value)


def test_a_missing_required_field_is_refused(tmp_path) -> None:
    raw = _valid_case()
    del raw["revision"]
    with pytest.raises(EvalCaseError) as exc:
        load_corpus(_write(tmp_path, raw))
    assert "revision" in str(exc.value)


def test_a_non_string_input_is_refused_and_says_why(tmp_path) -> None:
    """A non-`str` arrival CANNOT be expressed as a case, and the refusal says
    so rather than failing obscurely at run time - see data/eval/README.md."""
    with pytest.raises(EvalCaseError) as exc:
        load_corpus(_write(tmp_path, _valid_case(input=17)))
    assert "68" in str(exc.value) or "type gate" in str(exc.value)


def test_a_duplicate_case_id_is_refused(tmp_path) -> None:
    """EL4 makes a case a RECORD, and records do not share identifiers - a
    report carrying two `AEC-T01` rows cannot say which produced a delta."""
    path = _write(tmp_path, _valid_case(), _valid_case(input="Change requires time."))
    with pytest.raises(EvalCaseError) as exc:
        load_corpus(path)
    assert "AEC-T01" in str(exc.value)


def test_a_case_that_asserts_nothing_is_refused(tmp_path) -> None:
    """A case with no expectation always passes, which is WORSE than no case:
    it adds a green line to a report that measured nothing."""
    raw = _valid_case()
    del raw["expected_paths"]
    with pytest.raises(EvalCaseError):
        load_corpus(_write(tmp_path, raw))


def test_a_fact_value_of_the_wrong_type_is_refused(tmp_path) -> None:
    """`clm_lines: true` would compare unequal to every real count forever - a
    case that can never pass, which is a defect wearing a strict case's clothes.
    """
    with pytest.raises(EvalCaseError):
        load_corpus(_write(tmp_path, _valid_case(expected_facts={"clm_lines": True})))
    with pytest.raises(EvalCaseError):
        load_corpus(_write(tmp_path, _valid_case(expected_facts={"scar_formed": 1})))


# =====================================================================
# PIN (b) - THE SEED CORPUS
# =====================================================================

def test_b_the_seed_corpus_loads_clean() -> None:
    cases = load_corpus(SEED_CORPUS)
    assert len(cases) == 10
    assert len({c.case_id for c in cases}) == 10


def test_b_every_case_path_is_a_real_output_path_by_import() -> None:
    """**DERIVED FROM THE ENUM, NEVER A STRING COPY** (EL3).

    A hardcoded list here would go stale the day `process_input` grows an exit,
    and it would go stale SILENTLY - the corpus would keep passing while naming
    a vocabulary that had moved underneath it.
    """
    real = {member.name for member in OutputPath}
    assert output_path_names() == real
    for case in load_corpus(SEED_CORPUS):
        for name in case.expected_paths + case.forbidden_paths:
            assert name in real, f"{case.case_id} names {name}"


def test_b_every_case_fact_key_is_in_the_closed_vocabulary() -> None:
    for case in load_corpus(SEED_CORPUS):
        for key in list(case.expected_facts) + list(case.forbidden_facts):
            assert key in FACT_KEYS, f"{case.case_id} names {key}"


def test_b_case_ids_and_revisions_are_well_formed() -> None:
    """`AEC-` is an AUTHORED-INPUT namespace, deliberately not a `ledger_mint`
    consumer: cases are written by a human into a tracked read-only file, and
    minting one would make the corpus a store with a writer."""
    for case in load_corpus(SEED_CORPUS):
        assert case.case_id.startswith("AEC-"), case.case_id
        assert case.case_id[4:].isdigit(), case.case_id
        assert isinstance(case.revision, int) and case.revision >= 1
        assert case.notes, f"{case.case_id} cites no ruling"


def test_b_ci_holds_the_corpus_blob_hash_byte_for_byte() -> None:
    """The corpus joins the four identity seeds in CI's integrity step.

    A change to a read-only seed is a HUMAN CURATION EVENT (EL4/EL6) and must be
    visible as one. This asserts the workflow's recorded hash still matches the
    tracked bytes - so an edited corpus reddens here as well as in CI.
    """
    workflow = (REPO / ".github" / "workflows" / "suite.yml").read_text(
        encoding="utf-8")
    assert "data/eval/seed_cases.jsonl" in workflow
    actual = subprocess.run(["git", "hash-object", "data/eval/seed_cases.jsonl"],
                            cwd=REPO, capture_output=True, text=True,
                            timeout=60).stdout.strip()
    assert actual, "git hash-object produced nothing"
    assert f"expected_eval_cases={actual}" in workflow, (
        f"CI records a different blob than the tree holds ({actual}). If the "
        f"corpus was edited deliberately, update the workflow in the SAME "
        f"commit - that visibility is the point of the pin.")


def test_b_the_corpus_has_no_writer_anywhere_in_the_tree() -> None:
    """RULING 32'S SHAPE: a seed is read-only INPUT.

    `seed_cases.jsonl` must never appear beside a write mode. The runner opens
    it in `"r"` and nothing else opens it at all.
    """
    # (1) NOTHING BUT THE RUNNER NAMES THE CORPUS AT ALL. A second namer is a
    #     second opinion about what the corpus is for.
    namers = [
        p.name
        for p in sorted(REPO.glob("scripts/*.py")) + sorted(SRC.rglob("*.py"))
        for n in ast.walk(ast.parse(p.read_text(encoding="utf-8")))
        if isinstance(n, ast.Constant) and isinstance(n.value, str)
        and "seed_cases" in n.value and p.name != "evaluate.py"
    ]
    assert namers == [], f"something else names the corpus: {namers}"

    # (2) THE RUNNER'S ONLY `open` IS READ-MODE. `open(path, "r")` and a bare
    #     `open(path)` both read; anything with w/a/x/+ is a writer, and the
    #     corpus has none by ruling.
    tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
    modes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id == "open":
            mode = node.args[1] if len(node.args) > 1 else None
            for kw in node.keywords:
                if kw.arg == "mode":
                    mode = kw.value
            modes.append(mode.value if isinstance(mode, ast.Constant) else None)
    assert modes, "no `open` found in the runner - has the loader moved?"
    for mode in modes:
        assert mode in (None, "r"), f"the runner opens something in mode {mode!r}"


# =====================================================================
# PIN (c) - DETERMINISM (EL5)
# =====================================================================

def test_c_two_runs_at_one_seed_produce_identical_case_blocks(
        first_run, second_run) -> None:
    """EL5, asserted over CANONICAL JSON of the `cases` block - stated, not
    guessed at.

    The `cases` block is the determinism SUBJECT. Everything outside it carries
    a timestamp, a temp path or a commit hash by design, so byte-identity of the
    WHOLE report would be a false requirement that the first honest run fails.
    What must not move is what she DID.
    """
    assert canonical_cases(first_run) == canonical_cases(second_run)


def test_c_the_determinism_subject_holds_no_wall_clock_id(first_run) -> None:
    """The differential needs a wall-clock normalization because `Echo` ids are
    minted from `datetime.now()`. THIS instrument needs none, and that is a
    property worth pinning rather than a happy accident: the observed facts are
    paths, booleans and counts, and the only id recorded is the DETERMINISTIC
    `CLM-` ordinal."""
    blob = canonical_cases(first_run)
    import re
    assert not re.search(r"[A-Za-z]+-\d{12,}", blob), (
        "a wall-clock-minted id reached the determinism subject")


# =====================================================================
# PIN (d) - ISOLATION
# =====================================================================

def test_d_the_report_carries_a_passing_footprint_audit(first_run) -> None:
    """RULING 67: the audit RESULT is a REQUIRED FIELD. A run without its audit
    is INCOMPLETE and says so."""
    audit = first_run["footprint_audit"]
    assert audit["performed"] is True
    assert audit["pass"] is True
    assert audit["foreign_writes"] == []
    assert audit["shared_files_removed"] == []
    assert audit["configured_outside_root"] == []
    # **AN AUDIT OVER ZERO PATHS REPORTS PASS.** Found by a mutation survivor:
    # dropping the run's isolation call left `configured` empty, and every
    # emptiness check above was trivially satisfied while nothing was audited.
    # A count is what makes the verdict mean something.
    assert audit["configured_paths"] == 28
    assert first_run["isolation"]["configured_paths"] == 28


def test_d_the_run_writes_nothing_under_shared_runtime(first_run) -> None:
    """The load-bearing half, asserted directly rather than through the audit's
    own verdict - a run that wrote into `data/runtime/` would leave files there
    whatever the audit said about itself."""
    shared = REPO / "data" / "runtime"
    listing = sorted(p.name for p in shared.rglob("*")) if shared.exists() else []
    assert listing == [], f"the evaluation run left {listing} in shared runtime"


def test_d_the_seeds_are_byte_identical_across_a_run(first_run) -> None:
    assert first_run["seeds"]["identical"] is True


def test_d_every_case_ran_against_its_own_root(first_run) -> None:
    """Fresh state per case: cases must not be able to affect one another, and a
    corpus whose result depended on case ORDER would be measuring the corpus."""
    root = Path(first_run["parameters"]["root"])
    subdirs = sorted(p.name for p in root.iterdir() if p.is_dir())
    assert len(subdirs) == first_run["corpus"]["cases"]


# =====================================================================
# PIN (e) - EL1 AS STRUCTURE: RESULTS GRANT NOTHING
# =====================================================================

def _src_modules():
    return sorted(SRC.rglob("*.py"))


def _docstring_nodes(tree):
    """Every node that IS a docstring, so a scan can skip prose.

    THE SUBSTRING-SCANNER DEFECT HAS EIGHT RECORDED OCCURRENCES IN THIS REPO,
    every one of them a scanner matching its own explanatory prose. Ruling 63's
    precedent governs: sharpen the instrument, leave the documentation standing.
    """
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)):
            body = getattr(node, "body", None)
            if body and isinstance(body[0], ast.Expr) \
                    and isinstance(body[0].value, ast.Constant) \
                    and isinstance(body[0].value.value, str):
                out.add(id(body[0].value))
    return out


def _el1_offenders(paths):
    """Any `src/` module importing the runner, or naming the report directory."""
    imports, literals = [], []
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        skip = _docstring_nodes(tree)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if "evaluate" in alias.name.split("."):
                        imports.append((path.name, alias.name))
            if isinstance(node, ast.ImportFrom) and node.module:
                parts = node.module.split(".")
                if "evaluate" in parts or "scripts" in parts:
                    imports.append((path.name, node.module))
            if isinstance(node, ast.Constant) and isinstance(node.value, str) \
                    and id(node) not in skip:
                if "reports/" in node.value or "reports\\" in node.value:
                    literals.append((path.name, node.value))
    return imports, literals


def test_e_no_src_module_imports_the_evaluation_runner() -> None:
    """**EL1, THE DOCKET'S FIRST LAW, AS STRUCTURE.**

    Results grant nothing - and the way that is enforced is that `src/` cannot
    REACH them. Over `rglob`, so a module written next year joins this pin
    without anyone remembering to add it.
    """
    imports, literals = _el1_offenders(_src_modules())
    assert imports == [], (
        f"{imports} imports the evaluation instrument. An evaluation result "
        f"that any `src/` module can read is a score with standing (EL1).")
    assert literals == [], (
        f"{literals} names the report directory. `reports/` is instrument "
        f"output ABOUT her; nothing of hers reads it.")


def test_e_the_el1_scanner_fires_on_a_real_violation(tmp_path) -> None:
    """THE FIRES-CONTROL. A scanner never observed to fire is a comment."""
    good = tmp_path / "innocent.py"
    good.write_text('"""A docstring mentioning reports/ and evaluate."""\n'
                    'X = 1\n', encoding="utf-8")
    assert _el1_offenders([good]) == ([], []), (
        "the scanner flagged PROSE - it must skip docstrings")

    bad_import = tmp_path / "importer.py"
    bad_import.write_text("from scripts.evaluate import run_corpus\n",
                          encoding="utf-8")
    imports, _ = _el1_offenders([bad_import])
    assert imports, "the scanner missed a real import of the runner"

    bad_literal = tmp_path / "pathy.py"
    bad_literal.write_text('LOG = "reports/eval/latest.json"\n', encoding="utf-8")
    _, literals = _el1_offenders([bad_literal])
    assert literals, "the scanner missed a real report-directory literal"


def test_e_the_report_stores_no_rate_score_or_tally_of_quality(first_run) -> None:
    """EL1's other half: **NO AGGREGATE SCORE IS WRITTEN ANYWHERE.**

    A reader may derive a rate; the instrument never stores one. `zero_deltas`
    is a PROPERTY and `cases_with_deltas` is a LIST OF IDS pointing at findings -
    neither is a number that could be mistaken for standing.
    """
    blob = json.dumps(first_run, default=str).lower()
    for forbidden in ("pass_rate", "score", "accuracy", "grade", "rating"):
        assert forbidden not in blob, f"the report carries a '{forbidden}'"
    assert isinstance(first_run["zero_deltas"], bool)
    assert isinstance(first_run["cases_with_deltas"], list)


def test_e_the_runner_coins_no_disposition_vocabulary() -> None:
    """EL3: THE VOCABULARY IS HERS.

    The runner defines no `Enum` of its own. A parallel disposition vocabulary
    is exactly what an evaluation harness drifts into inventing, and it would
    let a case pass while naming something she never produced.
    """
    tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
    enums = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)
             for base in n.bases
             if (isinstance(base, ast.Name) and "Enum" in base.id)
             or (isinstance(base, ast.Attribute) and "Enum" in base.attr)]
    assert enums == [], f"the runner coins {enums}"


# =====================================================================
# PIN (f) - EVERY SEED CASE IS GREEN AGAINST THE LIVE TREE
# =====================================================================

def test_f_every_seed_case_is_green(first_run) -> None:
    """**READ THE MODULE DOCSTRING BEFORE TOUCHING THIS.**

    A red case is EITHER a real defect OR a defective case. Both are findings
    for the board. Adjusting an expectation to restore green is the one
    forbidden remedy: the corpus holds RULED behaviour, so a case going red
    means a ruling stopped being true, and that is the single most important
    thing this instrument can ever tell anyone.
    """
    failing = {row["case_id"]: row["expectation_deltas"]
               for row in first_run["cases"] if row["expectation_deltas"]}
    assert failing == {}, (
        f"seed cases departed from ruled behaviour: {json.dumps(failing, indent=2)}"
        "\n\nDO NOT EDIT THE CASE. Report it.")
    assert first_run["zero_deltas"] is True


@pytest.mark.parametrize("case_id,path", [
    ("AEC-001", "PARADOX_SUSPENDED"),
    ("AEC-002", "PARADOX_SUSPENDED"),
    ("AEC-003", "COLLAPSE_PASSED"),
    ("AEC-004", "COLLAPSE_PASSED"),
    ("AEC-005", "SBSRE_CARRIED"),
    ("AEC-006", "SBSRE_CARRIED"),
    ("AEC-007", "COLLAPSE_DETECTED"),
    ("AEC-008", "SBSRE_CARRIED"),
    ("AEC-009", "COLLAPSE_PASSED"),
    ("AEC-010", "COLLAPSE_PASSED"),
])
def test_f_each_case_observed_the_measured_disposition(
        first_run, case_id, path) -> None:
    """The measured dispositions, recorded individually.

    Pin (f) above asserts the corpus's OWN expectations hold; this records what
    was actually observed at the ruling's commit, so a change of disposition is
    legible per case rather than as one collective failure. AEC-008's case
    admits two paths (EL2); this row records which one the tree produces.
    """
    row = next(r for r in first_run["cases"] if r["case_id"] == case_id)
    assert row["observed_path"] == path


def test_f_the_paradox_and_scar_joins_are_really_on_record(first_run) -> None:
    """Ruling 76's joins, asserted as the FACTS they are rather than as a path.

    A disposition can be right while the record is empty; these are the two
    cases where a store must actually hold something carrying the claim id.
    """
    by_id = {r["case_id"]: r["observed_facts"] for r in first_run["cases"]}
    assert by_id["AEC-001"]["suspension_created"] is True
    assert by_id["AEC-007"]["scar_formed"] is True
    assert by_id["AEC-001"]["claim_id_joined"] is True
    assert by_id["AEC-007"]["claim_id_joined"] is True


def test_f_repetition_from_one_silent_source_corroborates_nothing(
        first_run) -> None:
    """RULING 60'S LAW, MEASURED: silence never corroborates.

    Two undeclared assertions of one claim move the UNKNOWN count to 2 and leave
    `distinct_recorded_origins` at ZERO. The two are reported SEPARATELY and
    never summed - that separation is the ruling, not a presentation choice.
    """
    facts = next(r["observed_facts"] for r in first_run["cases"]
                 if r["case_id"] == "AEC-009")
    assert facts["genealogy_unknown"] == 2
    assert facts["genealogy_distinct_origins"] == 0


# =====================================================================
# THE COMPARATOR ITSELF - the forcing pins, added after SEVEN mutation
# survivors shared one root cause.
# =====================================================================
#
# **A CORPUS THAT IS GREEN IS ALSO GREEN AGAINST A COMPARATOR THAT NEVER
# REPORTS ANYTHING.** Every pin above was satisfied by a `_deltas` returning
# `[]` unconditionally - three separate mutants (drop the path comparison, drop
# the fact comparison, drop `forbidden_paths`) survived the whole file.
#
# That is this repo's vacuous-pin defect at the one place it matters most: an
# instrument whose failure mode is SILENT SUCCESS. The pins below drive
# expectations that MUST fail, so the comparison is witnessed working rather
# than assumed from the absence of complaints.


def _case(**over) -> EvalCase:
    return load_corpus_from(_valid_case(**over))


def load_corpus_from(raw, tmp=None):
    import tempfile
    path = Path(tempfile.mkdtemp()) / "one.jsonl"
    path.write_text(json.dumps(raw) + "\n", encoding="utf-8")
    return load_corpus(path)[0]


def test_comparator_reports_a_path_that_was_not_expected() -> None:
    case = _case(expected_paths=["PARADOX_SUSPENDED"])
    deltas = _deltas(case, "COLLAPSE_PASSED", {})
    assert [d["kind"] for d in deltas] == ["path_not_expected"]
    assert deltas[0]["observed"] == "COLLAPSE_PASSED"


def test_comparator_reports_a_forbidden_path() -> None:
    case = _case(expected_paths=["COLLAPSE_PASSED"],
                 forbidden_paths=["SBSRE_CARRIED"])
    deltas = _deltas(case, "SBSRE_CARRIED", {})
    kinds = [d["kind"] for d in deltas]
    assert "path_forbidden" in kinds


def test_comparator_reports_a_fact_mismatch() -> None:
    case = _case(expected_facts={"clm_lines": 1, "scar_formed": True})
    deltas = _deltas(case, "COLLAPSE_PASSED",
                     {"clm_lines": 0, "scar_formed": True})
    assert [d["kind"] for d in deltas] == ["fact_mismatch"]
    assert deltas[0]["fact"] == "clm_lines"
    assert (deltas[0]["expected"], deltas[0]["observed"]) == (1, 0)


def test_comparator_reports_a_forbidden_fact() -> None:
    case = _case(forbidden_facts={"scar_formed": True})
    deltas = _deltas(case, "COLLAPSE_PASSED", {"scar_formed": True})
    assert [d["kind"] for d in deltas] == ["fact_forbidden"]


def test_comparator_stays_silent_when_everything_matches() -> None:
    """THE FIRES-CONTROL for the four above: a comparator that reported a delta
    for EVERYTHING would satisfy them all and be just as broken."""
    case = _case(expected_paths=["COLLAPSE_PASSED"],
                 forbidden_paths=["SBSRE_CARRIED"],
                 expected_facts={"clm_lines": 1},
                 forbidden_facts={"scar_formed": True})
    assert _deltas(case, "COLLAPSE_PASSED",
                   {"clm_lines": 1, "scar_formed": False}) == []


def test_a_deliberately_wrong_case_fails_end_to_end(tmp_path) -> None:
    """**THE FORCING PIN, DRIVEN THROUGH THE WHOLE RUNNER.**

    The unit pins above could all pass while `run_case` never called `_deltas`.
    This plants a case whose expectation contradicts ruled behaviour - a paradox
    input told to expect a clean pass - and requires the run to report it.
    """
    corpus = tmp_path / "wrong.jsonl"
    corpus.write_text(json.dumps({
        "case_id": "AEC-W01", "revision": 1, "category": "deliberately_wrong",
        "input": "this statement is false",
        "expected_paths": ["COLLAPSE_PASSED"],
        "expected_facts": {"scar_formed": True},
    }) + "\n", encoding="utf-8")

    report = run_corpus(corpus=corpus)
    assert report["zero_deltas"] is False
    assert report["cases_with_deltas"] == ["AEC-W01"]
    kinds = {d["kind"] for d in report["cases"][0]["expectation_deltas"]}
    assert kinds == {"path_not_expected", "fact_mismatch"}
    assert report["cases"][0]["observed_path"] == "PARADOX_SUSPENDED"


def test_the_disposition_is_the_last_emit_not_the_first() -> None:
    """**PINNED AT UNIT LEVEL BECAUSE THE CORPUS CANNOT SEE IT.**

    Every seed case emits exactly once, so `measured[-1]` and `measured[0]` are
    indistinguishable to all ten - a mutation survivor proved it. The rule is
    extracted and driven directly on a multi-emit sequence.
    """
    assert _disposition(["REFLEX_BLOCKED", "ORDINARY_ERROR"]) == "ORDINARY_ERROR"
    assert _disposition(["COLLAPSE_PASSED"]) == "COLLAPSE_PASSED"
    assert _disposition([]) is None


def test_run_case_refuses_to_run_unisolated(tmp_path) -> None:
    """**THE WRONG PATH IS UNEXECUTABLE, NOT DISCOURAGED.**

    `run_case` builds a real `AureaCore`, and stores load and save from
    construction - so a call made before `isolate()` writes into shared
    `data/runtime/`. Found by a mutation survivor: deleting `run_corpus`'s
    isolation left every test green while the footprint audit fell to ZERO
    configured paths and still reported PASS.
    """
    from scripts.evaluate import run_case
    case = _case()
    with pytest.raises(SoakIsolationError) as exc:
        run_case(case, tmp_path / "never_isolated", seed=42)
    assert "isolation" in str(exc.value).lower()


# =====================================================================
# PIN (g) - FACTS COME FROM THE REAL READ SURFACES
# =====================================================================

def test_g_the_runner_derives_facts_through_the_owners_surfaces() -> None:
    """AST: `record_joins` and `source_genealogy` are IMPORTED, not reimplemented.

    A parallel parser is how two definitions of "which scar belongs to this
    claim" come to exist and drift - and the drift would be invisible, because
    both would look right alone.
    """
    source = RUNNER.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = {n.module for n in ast.walk(tree)
                if isinstance(n, ast.ImportFrom) and n.module}
    assert "src.retrieval.record_joins" in imported
    assert "src.external.source_genealogy" in imported
    assert "src.output.ore" in imported


def test_g_the_runner_opens_only_its_own_corpus() -> None:
    """The instrument READS STORES THROUGH THEIR OWNERS, never off disk.

    The only `open()` in the runner belongs to `load_corpus`, reading the case
    file it was handed. A second one would mean the instrument had started
    parsing a store's file itself - a fourth reader of a format three owners
    already own.
    """
    tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
    opens = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for inner in ast.walk(node):
                if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name) \
                        and inner.func.id == "open":
                    opens.append(node.name)
    assert opens == ["load_corpus"], f"open() appears in {opens}"


def test_g_the_fact_vocabulary_matches_exactly_what_is_derived(
        first_run) -> None:
    """**BOTH DIRECTIONS, AND THE SECOND IS THE ONE THAT ROTS.**

    A key in `FACT_KEYS` that nothing derives is an expectation nothing checks -
    a case could assert it forever and always pass. A derived key absent from
    `FACT_KEYS` is a fact no case is allowed to name. Either drift makes the
    corpus quietly weaker, so the two sets are pinned EQUAL.
    """
    for row in first_run["cases"]:
        assert set(row["observed_facts"]) == set(FACT_KEYS), row["case_id"]


def test_g_an_unjoined_claim_reports_false_rather_than_true(tmp_path) -> None:
    """**THE JOIN IS READ, NOT ASSUMED.**

    Every seed case joins successfully, so `joined = True` hardcoded is
    invisible to the whole corpus - a mutation survivor proved it. This asks
    about a claim id NO record carries, where the honest answer is False.

    `None` is the third case and is separately honest: a pass that never minted
    a claim id has nothing to join, and the fact must not read as a successful
    join either.
    """
    import tempfile
    from scripts.evaluate import _ledger_sizes, _observe_facts
    from scripts.soak import isolate

    isolate(Path(tempfile.mkdtemp(prefix="aurea_join_")))
    from src.aurea_core import AureaCore

    core = AureaCore()
    core.process_input("Water is wet.")
    before = _ledger_sizes(core)

    absent = _observe_facts(core, {"claim_id": "CLM-9999"}, before)
    assert absent["claim_id_joined"] is False
    assert absent["scar_formed"] is False
    assert absent["suspension_created"] is False

    unminted = _observe_facts(core, {"claim_id": None}, before)
    assert unminted["claim_id_joined"] is False

    # **THE UNPRODUCIBLE FACT IS STILL DERIVED, AND THAT IS THE POINT.**
    # No case asserts `structural_violation`, because no reachable trigger
    # exists from `process_input` today (Ruling 48's finding, recorded in
    # data/eval/README.md) - so EVERY case observes False and a hardcoded
    # `False` is invisible to the whole corpus. A mutation survivor proved it.
    #
    # Pinned AT THE DERIVATION rather than through a pipeline trigger, in
    # Ruling 74's form: the day a violation becomes reachable, the fact must
    # already be read from `result` instead of asserted - otherwise the corpus
    # would report "no violation" for exactly the case it most needs to catch.
    violated = _observe_facts(
        core, {"claim_id": None, "structural_violation": {"type": "probe"}},
        before)
    assert violated["structural_violation"] is True


def test_g_the_context_cycles_are_not_charged_to_the_case(first_run) -> None:
    """**A CASE PASSES ON ITS OWN INPUT, NEVER ON ITS CONTEXT'S.**

    AEC-009 drives two claims: one context, one measured. Its `emitted_paths`
    must hold exactly ONE entry. A mutation survivor showed why this needs
    saying: both of AEC-009's claims produce COLLAPSE_PASSED, so charging the
    context to the case leaves `observed_path` identical and the error
    undetectable from the disposition alone.
    """
    by_id = {r["case_id"]: r for r in first_run["cases"]}
    assert by_id["AEC-009"]["emitted_paths"] == ["COLLAPSE_PASSED"]
    assert by_id["AEC-009"]["observed_facts"]["clm_lines"] == 1

    # Every case emits exactly once at this commit - a MEASURED fact, recorded
    # so a pass that starts multi-emitting is visible rather than absorbed.
    for row in first_run["cases"]:
        assert len(row["emitted_paths"]) == 1, row["case_id"]


def test_g_observed_facts_carry_the_declared_types(first_run) -> None:
    for row in first_run["cases"]:
        for key, want in FACT_KEYS.items():
            got = row["observed_facts"][key]
            assert isinstance(got, want) and (
                want is not int or not isinstance(got, bool)), (
                f"{row['case_id']}.{key} is {type(got).__name__}, want {want.__name__}")


# =====================================================================
# PIN (h) - THE REPORT CARRIES ITS PROVENANCE, READ NOT REMEMBERED
# =====================================================================

def test_h_the_report_records_the_commit_and_the_corpus_blob(first_run) -> None:
    """Both READ at run time, never hardcoded. A report that remembered its own
    provenance would be asserting where it came from rather than recording it.
    """
    assert first_run["git_hash"] and first_run["git_hash"] != "UNKNOWN"
    blob = first_run["corpus"]["blob"]
    actual = subprocess.run(["git", "hash-object", str(SEED_CORPUS)],
                            cwd=REPO, capture_output=True, text=True,
                            timeout=60).stdout.strip()
    assert blob == actual, "the report's corpus blob is not the tracked bytes"
    assert first_run["corpus"]["cases"] == 10


def test_h_the_report_names_the_instrument_and_the_ruling(first_run) -> None:
    assert "evaluate.py" in first_run["instrument"]
    assert "77" in first_run["instrument"]


# =====================================================================
# PIN (i) - THE PATH OBSERVATION IS AN OBSERVATION
# =====================================================================

def test_i_the_emit_wrapper_perturbs_nothing() -> None:
    """**THE WORKAROUND'S HONESTY, PINNED RATHER THAN PROMISED.**

    `result['output_path']` does not exist (measured at `90a4362`), and the
    path cannot be derived - `EXPRESSION_FOR_PATH` is MANY-TO-ONE, so four
    distinct paths share WITHHOLD. The runner therefore WRAPS `_emit` and
    records the member her own code selected.

    That is only legitimate if the wrapper changes nothing. This drives one
    claim with the wrapper and one without, and asserts every observable
    surface is identical.
    """
    import tempfile
    from scripts.evaluate import _record_paths
    from scripts.soak import isolate

    def drive(wrap: bool):
        isolate(Path(tempfile.mkdtemp(prefix="aurea_wrap_")))
        from src.aurea_core import AureaCore
        core = AureaCore()
        seen = []
        if wrap:
            _record_paths(core, seen)
        result = core.process_input("Honesty is pointless.")
        return {
            "blocked": result["output_blocked"],
            "verdict": result["expression_verdict"].name,
            "output": result["output"],
            "scar": getattr(result.get("scar_formed"), "id", None) is not None,
            "packet": result["truth_packet"].content,
            "trace": list(result["render_trace"]),
        }, seen

    plain, empty = drive(False)
    wrapped, seen = drive(True)
    assert empty == []
    assert seen == ["COLLAPSE_DETECTED"]
    assert plain == wrapped, "the observation wrapper changed the pass"


def test_i_the_observed_path_is_the_last_emit_and_the_sequence_is_kept(
        first_run) -> None:
    """Four `_emit` sites do not `return`, and `_emit` OVERWRITES `result` each
    time - so the LAST call is the disposition. The full sequence is recorded
    beside it, so a multi-emit pass is VISIBLE rather than silently collapsed.
    """
    for row in first_run["cases"]:
        assert row["emitted_paths"], row["case_id"]
        assert row["observed_path"] == row["emitted_paths"][-1]


def test_i_the_path_is_still_absent_from_the_result_contract() -> None:
    """**THE CARRIED FINDING, PINNED SO IT CANNOT BE FORGOTTEN OR SILENTLY FIXED.**

    `AureaCore._emit` receives the `OutputPath` and writes six keys onto
    `result`; the path is not among them. The honest fix is a one-key `src/`
    change and it is the BOARD'S - Ruling 77 bars this pass from touching
    `src/`.

    **THIS PIN REDDENS THE DAY SOMEONE ADDS THE KEY**, which is exactly when the
    wrapper should be deleted and this test replaced by a direct read. It is a
    tripwire on a known gap, in the form this repo has used four times.
    """
    source = (REPO / "src" / "aurea_core.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    emit = next(n for n in ast.walk(tree)
                if isinstance(n, ast.FunctionDef) and n.name == "_emit")
    written = set()
    for node in ast.walk(emit):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Subscript) \
                        and isinstance(target.slice, ast.Constant):
                    written.add(target.slice.value)
    assert written == {"output", "output_blocked", "expression_verdict",
                       "truth_packet", "render_trace", "reroute_hint"}, written
    assert "output_path" not in written, (
        "`_emit` now records the path - DELETE the wrapper in "
        "`scripts/evaluate.py` and read `result['output_path']` directly.")


# =====================================================================
# PIN (j) - THE ISOLATION TABLE IS UNCHANGED
# =====================================================================

def test_j_the_instrument_registers_no_new_store() -> None:
    """The runner REUSES the soak's redirection and adds nothing to it.

    An evaluation report is not a store: it lives outside `data/`, nothing reads
    it, and the coverage self-audit derives only from `src/`. If this instrument
    had introduced a durable path in `src/`, Ruling 31 would require registering
    it in the SAME commit - and the self-audit would refuse until it was.
    """
    from scripts.soak import _injection_table
    class_attrs, init_defaults = _injection_table()
    assert len(class_attrs) + len(init_defaults) == 28


def test_j_the_soak_coverage_self_audit_still_passes() -> None:
    """The guard that would refuse a run whose table has fallen behind."""
    from scripts.soak import _audit_coverage, _injection_table
    class_attrs, init_defaults = _injection_table()
    _audit_coverage(class_attrs, init_defaults)


def test_j_the_runner_reuses_the_soaks_isolation_rather_than_copying_it() -> None:
    """ONE isolation, three callers (Ruling 67's reason).

    A second copy of an isolation table is a second definition free to drift,
    and the drift would be invisible because both would look right alone.
    """
    tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
    from_soak = {alias.name for node in ast.walk(tree)
                 if isinstance(node, ast.ImportFrom) and node.module == "scripts.soak"
                 for alias in node.names}
    assert {"isolate", "footprint_audit"} <= from_soak

    # AST, NOT SUBSTRING: the runner must not DEFINE a table of its own. A
    # source scan would match the docstring explaining why it does not - the
    # false positive this repo has recorded eight times.
    defined = {n.name for n in ast.walk(tree)
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    assert "_injection_table" not in defined
    assert "_derive_injectable_from_source" not in defined
    assigned = {t.id for n in ast.walk(tree) if isinstance(n, ast.Assign)
                for t in n.targets if isinstance(t, ast.Name)}
    assert not {"class_attrs", "init_defaults"} & assigned, (
        "the runner is building its own injection table")
