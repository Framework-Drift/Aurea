"""
conftest.py - suite-wide I/O isolation for persistent stores.

Ruling 11 makes GLOBAL-scope reflex entries flush to disk IMMEDIATELY - which
means any test that drives GSR (cascade decomposition, disorientation lock,
type-gate) would otherwise append real lines to logs/reflex_behavior.jsonl.
A forensic log polluted with test entries is worse than a dirty tree: it is
false pressure in a permanent record.

The same hazard applies to the suspension stores. Once Nova Stage 2b wired the
proposals path, an end-to-end test drives real CSA routing (failed-collapse
decay) and real DEE fermentation (Veiled Thread suspend) - both of which
persist to data/suspension/*.json at construction-default paths. Suspended
state written by a test is the same class of false pressure in a real store.

There is deliberately no injectable no-op sink (a store you can silently
disable is not a store), so isolation is by REDIRECTION into pytest's tmp dir
for every test:
  - RBSystem resolves DEFAULT_LOG_PATH at construction time (class attr).
  - AureaCore resolves STRUCTURAL_LOG_PATH the same way (class attr).
  - GSR resolves GSR_ALERT_PATH at WRITE time (class attr) - see below.
  - CSA / VeiledThread / BlackSphere / TopologicalSpace / TetherProtocol take
    a path default argument; AureaCore builds them with no args, so the
    default is what gets used - this fixture repoints that one named default
    at tmp, leaving every other default intact.
  - Codex / ScarLogicCore / EchoMemory have a SEED path and a RUNTIME path
    (Ruling 32). Only the RUNTIME path is redirected.
Tests asserting on disk contents pass an explicit path instead and are
unaffected.

THIS FIXTURE COVERS THIRTY-THREE PATHS: six resolved from class attributes,
twenty-seven from `__init__` defaults. If you add a thirty-fourth and do not add
it here, you have reopened the hole Ruling 31 closed.

    ~~THIS FIXTURE COVERS THIRTY-TWO PATHS: six from class attributes,
    twenty-six from `__init__` defaults.~~ MIGRATED 2026-08-16 (M8-b).

    ~~THIS FIXTURE COVERS THIRTY-ONE PATHS: six from class attributes,
    twenty-five from `__init__` defaults.~~ MIGRATED 2026-08-16 (M7-c).

    ~~THIS FIXTURE COVERS THIRTY PATHS: six resolved from class attributes,
    twenty-four from `__init__` defaults.~~
    MIGRATED 2026-08-16 (M7-b): the attention selection log. The count is
    CHECKED against the tables on every run (see `test_ruling75.py::test_j`),
    which is what caught this edit rather than leaving it to be noticed.

    ~~THIS FIXTURE COVERS TWENTY-NINE PATHS: six resolved from class attributes,
    twenty-three from `__init__` defaults.~~

    ~~THIS FIXTURE COVERS TWENTY-EIGHT PATHS: six resolved from class
    attributes, twenty-two from `__init__` defaults.~~

    ~~THIS FIXTURE COVERS TWENTY-SIX PATHS: six resolved from class attributes,
    twenty from `__init__` defaults.~~

    ~~THIS FIXTURE COVERS TWENTY-FIVE PATHS: five resolved from class
    attributes, twenty from `__init__` defaults.~~

**UPDATED 2026-08-15 (M4-alpha), old text kept above verbatim.** The acquisition
ledger is the twenty-ninth, an `__init__` default, added in the SAME commit as
the store. It is the first addition since M3-A that the CORE CONSTRUCTS BY
DEFAULT and WRITES TO on every perceived arrival, so an omission here would not
have been latent - it would have appended a line to the real record of
everything AUREA has ever received, on the first test that processed an input.

**UPDATED 2026-08-13 (M3-A), old text kept above verbatim.** The obligation
ledger and the episode record are the twenty-seventh and twenty-eighth, both
`__init__` defaults, both added in the SAME commit as the stores. The mechanism
worked again: the pass that added the paths is the pass that updated the number.

**CORRECTED 2026-08-09 (Ruling 79), old text kept above verbatim.** The
divergence report (`AureaCore.DIVERGENCE_LOG_PATH`) is the twenty-sixth, and it
was added in the SAME commit as the store, which is the rule this count exists
to police. It is the sixth CLASS ATTRIBUTE, so the class/init split moves too -
a count that tracked the total while the split went stale would be the same
defect one level down. **This one did NOT drift**: the mechanism worked because
the pass that added the path was the pass that updated the number.

**THIS FILE NOW DOES TWO THINGS, AND THE COUNT ABOVE DESCRIBES ONLY THE FIRST**
(2026-08-07). It REDIRECTS those twenty-five paths, and it RESTORES three class
attributes that something ELSE redirected - `scripts/soak.py`'s `isolate()`,
which is a standalone process and has nothing to restore to. **The two halves
are separate on purpose and the count is not shared between them**: redirection
is a coverage claim that can go stale, restoration is a derived set that cannot
(it is pinned as the soak's class attributes MINUS the ones patched here). See
the block above `_restore_bare_setattr_redirection` for the whole finding -
including why a suite-wide guard was, until this change, held up by alphabetical
file order.

    ~~THIS FIXTURE COVERS TWENTY-TWO PATHS: five resolved from class
    attributes, seventeen from `__init__` defaults.~~

**CORRECTED 2026-08-05 (Ruling 74), old text kept above verbatim - AND THE
STALENESS IS THE FINDING, NOT THE TYPO.** The count read TWENTY-TWO while the
tree carried TWENTY-FOUR: Ruling 72 added the goal ledger's path and Ruling 73
the examination log's, and neither pass updated this number. Ruling 74 adds the
activation log's, bringing it to twenty-five.

That is this docstring's own mechanism half-working, and it is worth saying
plainly. The count replaced a completeness BOAST at Ruling 34 precisely because
"a count goes visibly stale and a boast does not" - and it did go visibly stale,
exactly as designed. What the design cannot do is make anyone LOOK. **A number
that drifts for two passes is still better than a claim that never drifts at
all**, because it can be checked mechanically against the tables below in a way
"every durable store" never could; but it is not self-enforcing, and reading it
as if it were is how the completeness defect gets in through the remedy.

A CORRECTION, AND IT IS THE POINT OF THIS PARAGRAPH (Ruling 34 res.7, 2026-07-27).
This docstring previously read "AS OF RULING 32 THIS FIXTURE COVERS EVERY
DURABLE STORE IN THE SYSTEM - the first time that has been true." **It was
false when written.** `AureaCore.save_state` wrote a durable artifact and
called three store saves, and its path came from a METHOD-PARAMETER default -
a THIRD shape neither mechanism below can reach, and one Ruling 31's sweep was
never specified on. The claim is defensible only if `AureaCore` is not a store,
and no reader will take it that way.

**SIXTH INSTANCE of the completeness-claim defect - this time in the file whose
docstring IS the isolation principle.** A coverage claim is exactly as dangerous
as the coverage it asserts: the appearance of completeness is what stops anyone
looking (Ruling 31's own finding, turned on its own remedy). So this docstring
now states a COUNT and a SHAPE RULE rather than a completeness claim, because a
count goes visibly stale and a boast does not.

WHY THE FIFTH PATH ESCAPED FOR SO LONG (Ruling 31, 2026-07-26)
---------------------------------------------------------------
READ THIS BEFORE ADDING A DURABLE STORE. This fixture has exactly ONE
mechanism: monkeypatching a CLASS ATTRIBUTE or an `__init__` DEFAULT. That is
not a stylistic preference - it is the fixture's entire reach.

`GSR._default_alert` wrote `data/collapse_logs/gsr_alerts.jsonl` from a BARE
LITERAL in the method body. A literal is neither of those two shapes, so this
fixture could not reach it BY CONSTRUCTION - the path was not uncovered, it
was UNREACHABLE. Every GSR-driving test run appended to the real forensic log
(10 stale entries were found on disk, one dating to 2025-08-10), while the
fixture's own docstring said isolation was handled.

That is Ruling 22's fail-silent shape relocated into the harness: an isolation
fixture covering four of five paths does not provide isolation, it provides
the APPEARANCE of it, and the appearance is what stops anyone looking. The
defect was invisible from inside the fixture, because a fixture cannot enumerate
the paths it cannot see.

SO: A NEW DURABLE WRITE PATH MUST BE A CLASS ATTRIBUTE OR AN `__init__`
DEFAULT, AND MUST BE REDIRECTED HERE IN THE SAME COMMIT. Path injectability is
part of a durable store's contract, not a testing convenience.

This fixture weakens no assertion in any test. Do not extend it into one that
does.
"""

import inspect

import pytest

from src.aurea_core import AureaCore
from src.external.acquisition_ledger import AcquisitionLedger
from src.worldmodel.proposition_ledger import PropositionLedger
from src.doctrine.cae import CAE
from src.doctrine.codex import Codex
from src.doctrine.dee import DMW
from src.expansion.nova import NovaEngine
from src.external.claim_ancestry import ClaimAncestryLedger
from src.external.prediction_ledger import PredictionLedger
from src.goals.goal_activation import ActivationLayer
from src.goals.goal_arbitration import GoalArbiter
from src.goals.goal_ledger import GoalLedger
from src.expansion.sae import SAE
from src.identity.ril import RIL
from src.reflex.racm import RACM
from src.expansion.tether.session_governor import TetherProtocol
from src.filtration.episode_record import EpisodeRecord
from src.filtration.obligation_ledger import ObligationLedger
from src.executive.selection_log import SelectionLog
from src.executive.inquiry_log import InquiryLog
from src.executive.routing_log import RoutingLog
from src.filtration.scar_logic_core import ScarLogicCore
from src.reflex.rb_system import RBSystem
from src.reflex.reflex_grid import GSR
from src.suspension.black_sphere import BlackSphere
from src.suspension.csa import CSA
from src.suspension.veiled_thread import VeiledThread
from src.topology.tca_core import TopologicalSpace
from src.topology.tcaml import TCAML
from src.utils.echo_memory import EchoMemory


# =====================================================================
# THE RESTORE HALF (2026-08-07) - redirection this fixture does NOT own
# =====================================================================
#
# **THE HAZARD, AND IT WAS REAL RATHER THAN THEORETICAL.** `scripts/soak.py`'s
# `isolate()` redirects by BARE `setattr` on CLASS ATTRIBUTES - it is a
# standalone process and has nothing to restore to. Three of those attributes,
# `Codex.RUNTIME_PATH` / `ScarLogicCore.RUNTIME_PATH` / `EchoMemory.RUNTIME_PATH`,
# are redirected BELOW as `__init__` DEFAULTS instead, so this fixture never
# monkeypatches the class attributes and therefore never restores them.
#
# Any test that calls `isolate()` (the soak smoke test, the evaluation
# instrument's tests) therefore left those three pointing at a temp directory
# FOR THE REST OF THE SESSION. That breaks `tests/test_seed_isolation.py`'s
# class-level guard, which asserts `RUNTIME_PATH.startswith("data/runtime/")`
# (Ruling 39) precisely BECAUSE a class-level defect is one this fixture cannot
# mask.
#
# **IT HAD NEVER FIRED FOR ONE REASON ONLY: `test_soak_smoke` SORTS AFTER
# `test_seed_isolation` ALPHABETICALLY.** A suite-wide correctness guard was
# being held up by FILE-NAME ORDER - which is the "discouraged, not
# unexecutable" shape (CLAUDE.md section 3) sitting underneath the guard that
# enforces Ruling 39. Ruling 77's pass hit it, restored the table LOCALLY in its
# own file, and reported the general case as the board's. This is that
# generalization: **ONE implementation, in the fixture that owns isolation.**
#
# WHY SNAPSHOT/RESTORE RATHER THAN ANOTHER `monkeypatch.setattr`: monkeypatch
# restores the value it recorded AT PATCH TIME, so patching these here would
# work - but it would also REDIRECT them, and this fixture deliberately moves
# the `__init__` default rather than the class attribute for these three (see
# the comment at the loop below: the SEED path must stay reachable). Snapshot
# and restore leaves the redirection policy exactly as it is and only undoes
# what someone else did.
#
# CAPTURED AT IMPORT, before any fixture has run, so these are the repo's real
# defaults rather than some earlier test's temp paths.
_ISOLATE_MUTATED_CLASS_ATTRS = (
    (Codex, "RUNTIME_PATH"),
    (ScarLogicCore, "RUNTIME_PATH"),
    (EchoMemory, "RUNTIME_PATH"),
)
_PRISTINE_CLASS_ATTRS = tuple(
    (cls, name, getattr(cls, name)) for cls, name in _ISOLATE_MUTATED_CLASS_ATTRS
)


@pytest.fixture(autouse=True)
def _restore_bare_setattr_redirection():
    """Undo, after every test, any bare `setattr` redirection of the three.

    Runs for EVERY test rather than only the ones that call `isolate()`,
    deliberately: a fixture that had to be requested is a fixture someone
    forgets, and the whole finding here is that correctness was resting on
    something nobody had to remember. This costs three attribute writes.
    """
    yield
    for cls, name, value in _PRISTINE_CLASS_ATTRS:
        setattr(cls, name, value)


@pytest.fixture(autouse=True)
def _persist_to_tmp(tmp_path, monkeypatch):
    monkeypatch.setattr(
        RBSystem, "DEFAULT_LOG_PATH",
        str(tmp_path / "reflex_behavior.jsonl"),
    )
    # Ruling 25 (Docket N): structural violations get a durable record too, and
    # a test driving a guard on purpose must not append to the real forensic
    # log. Same shape as RBSystem's - resolved at construction from a class
    # attribute, so redirecting the attribute is the whole isolation.
    monkeypatch.setattr(
        AureaCore, "STRUCTURAL_LOG_PATH",
        str(tmp_path / "structural_violations.jsonl"),
    )
    # Ruling 31 (Docket 6d): the fifth path, and the one this fixture could not
    # reach until it stopped being a literal. GSR resolves it at WRITE time, so
    # this redirect binds even for a GSR the Grid already constructed.
    monkeypatch.setattr(
        GSR, "GSR_ALERT_PATH",
        str(tmp_path / "gsr_alerts.jsonl"),
    )
    # Ruling 34 res.7: `AureaCore.save_state` resolved its path from a METHOD-
    # PARAMETER default, the one shape neither mechanism below can reach, and
    # wrote outside `data/runtime/`. Now a class attribute, so it is reachable.
    monkeypatch.setattr(
        AureaCore, "STATE_PATH",
        str(tmp_path / "aurea_state.json"),
    )
    # Ruling 34 res.4: SAE's restart record. Class attribute resolved at WRITE
    # time (the GSR shape), so it binds even for an already-constructed SAE.
    monkeypatch.setattr(
        SAE, "RESTART_LOG_PATH",
        str(tmp_path / "sae_restarts.jsonl"),
    )
    # Ruling 79: the divergence report. The detector runs at EVERY `AureaCore`
    # construction, so an unredirected path here would append a real finding to
    # shared forensics from any test that happens to build a store pair that
    # disagrees - and hand-built test worlds disagree routinely. Redirected in
    # the SAME commit that adds the store, per Ruling 31's standing rule.
    #
    # PATCHED HERE RATHER THAN LEFT TO THE RESTORE SET ABOVE: `_PRISTINE_CLASS_
    # ATTRS` only UNDOES a bare `setattr` someone else performed, which protects
    # the next test and does nothing for this one. Redirection and restoration
    # answer different questions, and this path needs the first.
    monkeypatch.setattr(
        AureaCore, "DIVERGENCE_LOG_PATH",
        str(tmp_path / "divergence.jsonl"),
    )
    # Repoint each remaining store's path default at tmp.
    #
    # A SEVENTH COMPLETENESS-CLAIM INSTANCE, REMOVED 2026-07-27 (Ruling 42). This
    # comment read "THE FIXTURE NOW COVERS EVERY DURABLE STORE IN THE SYSTEM - the
    # first time that has been true." The docstring's version of that boast was
    # replaced by a COUNT at Ruling 34; this copy survived the edit and went on
    # asserting it - and it was FALSE AGAIN, because RIL, Nova and RACM held state
    # no file has ever carried. A claim that outlives the fix it described is the
    # completeness defect in its most durable form: it reads as verified history.
    # The count lives in the docstring, once, where it can go visibly stale.
    #
    # For Codex / ScarLogicCore / EchoMemory it is the RUNTIME path that moves.
    # The SEED path deliberately does NOT: a test still reads AUREA's real
    # founding doctrine and scars, exactly as the pipeline does, and writes
    # land in tmp. Redirecting the seed too would silently give every test an
    # empty identity store and change what the whole suite is testing.
    for cls, param, fname in (
        (CSA, "filepath", "csa.json"),
        (VeiledThread, "filepath", "veiled_thread.json"),
        (BlackSphere, "filepath", "black_sphere.json"),
        (Codex, "runtime_path", "doctrines.json"),
        (ScarLogicCore, "runtime_path", "scars.json"),
        (EchoMemory, "runtime_path", "echoes.jsonl"),
        (TopologicalSpace, "filepath", "tca_map.json"),
        (TetherProtocol, "telemetry_path", "tether_telemetry.jsonl"),
        # Ruling 34 res.1: SAE's epoch state. An `__init__` default (resolved by
        # NAME below), and it MUST be redirected before anything constructs an
        # SAE - `SAE.__init__` calls `load()`, and `AureaCore.__init__`
        # constructs one. There is NO seed counterpart: a missing file is a
        # first run, and an epoch is accumulated rather than issued.
        (SAE, "runtime_path", "sae_epoch.json"),
        # Ruling 42 (2026-07-27) - THE CONTINUITY PASS. Three stores that were
        # purely in-memory until now, so a restart could make AUREA forget her
        # origin, her authored echoes, or the pressure she deferred. Each is an
        # `__init__` default under `data/runtime/`, resolved BY NAME below.
        #
        # RIL MUST be redirected before anything constructs one - `RIL.__init__`
        # calls `load()`, exactly as `SAE.__init__` does. Same for Nova and RACM.
        (RIL, "runtime_path", "ril_threads.json"),
        (NovaEngine, "runtime_path", "nova_record.json"),
        (RACM, "runtime_path", "racm_queue.json"),
        # Ruling 42 SLICE 2 (2026-07-28). TCAML's GLOBAL lock and DEE's doctrine
        # watch queue - the last two in-memory stores from Ruling 42's register.
        # Both call `load()` from `__init__`, so both MUST be redirected before
        # anything constructs one (the SAE/RIL/Nova precedent).
        #
        # TCA's topology map is NOT in this addition: it has had a `filepath`
        # default and been redirected here since before Ruling 42. Slice 2 gave
        # it the CONTRACT (version gate, reported outcome, reference validation),
        # not persistence - see `tca_core.load_from_file`.
        (TCAML, "runtime_path", "tcaml_lock.json"),
        (DMW, "runtime_path", "dmw_queue.json"),
        # Ruling 45: the CAE audit ledger. Append-only forensics (Ruling 31's
        # semantics), so a test driving a mutation on purpose must not append to
        # the real record of what AUREA actually changed about herself. SAE and
        # DEE both construct one by DEFAULT when none is injected, so this MUST
        # be redirected before anything constructs either.
        (CAE, "ledger_path", "cae_audit.jsonl"),
        # Ruling 58: the claim-ancestry ledger. Append-only forensics recording
        # where every claim came from, and `AureaCore` constructs one BY DEFAULT
        # when none is injected - so this MUST be redirected before anything
        # constructs a core, or a test run appends to the real record of what
        # AUREA has been asked.
        (ClaimAncestryLedger, "ledger_path", "claim_ancestry.jsonl"),
        # M4-alpha: the acquisition ledger. THE ANCESTRY LEDGER'S SITUATION
        # EXACTLY, not the prediction ledger's - `AureaCore` constructs one BY
        # DEFAULT and `process_input` writes to it on every perceived arrival,
        # so this MUST be redirected before anything constructs a core or a test
        # run appends to the real record of everything AUREA has ever received.
        (AcquisitionLedger, "ledger_path", "acquisitions.jsonl"),
        # M6-α: the proposition ledger - the World Model domain's first
        # member. NOTHING in the pipeline constructs one (zero writers,
        # pinned), so like the prediction and goal ledgers this redirect
        # protects tests that build one DIRECTLY - and it lands in the
        # SAME COMMIT as the store, per Ruling 31's standing rule.
        (PropositionLedger, "ledger_path", "propositions.jsonl"),
        # Ruling 61: the prediction ledger. Append-only forensics recording what
        # AUREA committed to BEFORE an outcome, which is the one record whose
        # value depends entirely on not having been written afterwards. NOTHING
        # in the pipeline constructs one today, so unlike the ancestry ledger
        # this redirect protects tests that build a ledger DIRECTLY - and it is
        # here in the SAME COMMIT as the store, per Ruling 31's rule, rather
        # than waiting for a consumer that would make it urgent.
        (PredictionLedger, "ledger_path", "prediction_ledger.jsonl"),
        # Ruling 72 (Docket Q item Q1): the goal commitment ledger. Append-only
        # forensics recording what AUREA committed to pursue BEFORE pursuing it.
        # NOTHING in the pipeline constructs one - the ledger is substrate and
        # is deliberately unwired this pass - so like the prediction ledger this
        # redirect protects tests that build one DIRECTLY, and it lands in the
        # SAME COMMIT as the store per Ruling 31's rule.
        #
        # `seed_path` is DELIBERATELY NOT REDIRECTED, exactly as the three seed
        # paths are not: it is READ-ONLY INPUT with no writer (Ruling 32), and
        # redirecting it would hand every test an empty roots document and
        # quietly stop genesis from being measured against the real seed.
        (GoalLedger, "ledger_path", "goal_ledger.jsonl"),
        # Ruling 73 (Docket Q item Q2): the examination log. The arbiter is
        # unwired this pass - nothing in `src/` consumes it - so like the two
        # ledgers above this redirect protects tests that build one DIRECTLY,
        # and it lands in the SAME COMMIT as the store per Ruling 31's rule.
        (GoalArbiter, "log_path", "goal_examinations.jsonl"),
        # Ruling 74 (Docket Q item Q3): the activation log - bounded episodes of
        # directed attention, opened and closed as SEPARATE appends.
        #
        # **THIS ONE IS DIFFERENT FROM THE TWO ABOVE, AND THE DIFFERENCE IS WHY
        # IT MATTERS MOST.** Ruling 74 res.6 composes all three goal stores in
        # `AureaCore.__init__`, so from this commit onward EVERY test that
        # builds a core constructs an `ActivationLayer` - the ancestry ledger's
        # situation rather than the prediction ledger's. Without this redirect a
        # bare `AureaCore()` would point at the real `data/runtime/` log.
        #
        # Composing a layer is NOT invoking one: no verb here has an internal
        # caller, so a core that is merely constructed writes nothing. The
        # redirect protects against the day that stops being true, and against
        # tests that build a layer DIRECTLY.
        (ActivationLayer, "log_path", "goal_activations.jsonl"),
        # M3-A (kernels K2/K3/K11): the obligation ledger and the episode
        # record - the pivot's first two Kernel stores. Both are SUBSTRATE and
        # deliberately unwired this pass (zero internal callers anywhere in
        # `src/`), so like the prediction and goal ledgers these redirects
        # protect tests that build one DIRECTLY, and they land in the SAME
        # COMMIT as the stores per Ruling 31's standing rule.
        #
        # `peer_paths` is NOT redirected and needs no entry: it defaults to
        # EMPTY rather than to a path, so an unredirected instance reads only
        # its own file. That is deliberate - a peer default pointing at the
        # real `data/runtime/` would make the shared clock read shared state
        # from inside an isolated test.
        (ObligationLedger, "ledger_path", "obligations.jsonl"),
        (EpisodeRecord, "log_path", "episodes.jsonl"),
        # M7-b: the attention selection log. **THIS ONE IS THE ACTIVATION
        # LAYER'S SITUATION, NOT THE ARBITER'S**, and the difference is why it
        # matters: `ExecutiveLoop.__init__` composes a `SelectionLog` BY
        # DEFAULT (Ruling 45's `cae or CAE()` idiom), so from this commit every
        # loop that is merely CONSTRUCTED holds one. Composing a log is not
        # writing to it - no verb here has an internal caller, so a constructed
        # loop writes nothing - but without this redirect a bare
        # `ExecutiveLoop(...)` would point at the real `data/runtime/` log.
        (SelectionLog, "log_path", "attention_selections.jsonl"),
        # M7-c: the inquiry act log. Same situation as the selection log -
        # `ExecutiveLoop.__init__` composes one BY DEFAULT, so every
        # constructed loop holds one. Composing is not writing (no verb here
        # has an internal caller), but without this redirect a bare
        # `ExecutiveLoop(...)` would point at the real `data/runtime/` log.
        (InquiryLog, "log_path", "inquiry_acts.jsonl"),
        # M8-b: the routing act log. Same situation as its two siblings -
        # `ExecutiveLoop.__init__` composes one BY DEFAULT, so every
        # constructed loop holds one; composing is not writing, but without
        # this redirect a bare `ExecutiveLoop(...)` would point at the real
        # `data/runtime/` log.
        (RoutingLog, "log_path", "routing_acts.jsonl"),
    ):
        _redirect_default(monkeypatch, cls, param, str(tmp_path / fname))


def _redirect_default(monkeypatch, cls, param: str, value: str) -> None:
    """Repoint ONE named `__init__` default, located BY NAME.

    The older form of this loop assumed the path was the LAST defaulted
    parameter (`defaults[:-1] + (value,)`). That happens to be true for the
    suspension stores and is FALSE for `TetherProtocol`, whose
    `telemetry_path` is followed by three callback parameters - patching the
    last default there would have silently rebound `on_abort` to a string and
    left the telemetry path pointing at the real forensic directory. Found
    while extending the loop, not by a failing test.

    A positional assumption that is true for the cases you happen to have is
    the same class of defect Ruling 31 closed: a mechanism that appears to
    cover a store while structurally missing it. Resolve by name instead.
    """
    spec = inspect.signature(cls.__init__)
    names = [n for n, p in spec.parameters.items()
             if p.default is not inspect.Parameter.empty]
    assert param in names, (
        f"{cls.__name__}.__init__ has no defaulted parameter '{param}' - the "
        f"redirect would silently do nothing"
    )
    defaults = list(cls.__init__.__defaults__ or ())
    assert len(defaults) == len(names), (
        f"{cls.__name__}: keyword-only defaults are not in __defaults__; "
        f"this helper would patch the wrong parameter"
    )
    defaults[names.index(param)] = value
    monkeypatch.setattr(cls.__init__, "__defaults__", tuple(defaults))
