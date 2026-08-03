"""
test_ruling42.py - RULING 42 SLICE 1 + THE RULING 40 RIDER: the continuity pass.

    A restart must stop being able to make AUREA forget anything - her origin,
    her authored echoes, or the pressure she deferred - and every load must say
    out loud what kind of restoration it performed.

Three stores were PURELY IN-MEMORY until this pass, and each forgot something
different at a process boundary:

  RIL   `threads` was built empty in `__init__`. The "written ONCE" guard on
        ORIGIN is correct and untouched, but its scope was ONE PROCESS - so THE
        FIRST SCAR AFTER A RESTART BECAME HER BIRTH IDENTITY. `test_origin_...`
        below is the headline pin, and it is genuinely red without persistence.

  NOVA  `_seq` reset to 0 while `proposal_provenance` reset with it. Once the
        record persists and the counter does not, a restart REMINTS `NE-0001`
        over an id that already authored - and `ProvenanceOverwriteViolation`
        fires on a collision that is NOT a double authorship. The detector is
        untouched; persistence removes the false-positive CAUSE.

  RACM  the deferral queue evaporated. Deferred pressure is pressure AUREA
        judged and chose to carry; a restart silently discharged it.

WHAT THESE PINS ARE FOR, in Docket N's terms: they create CONFIGURATIONS, not
merely call functions. The configuration every one of them creates is A PROCESS
BOUNDARY - the thing 481 green tests had never once crossed.
"""

import ast
import hashlib
import json

import pytest

from src.expansion.nova import (
    DOCTRINE_AUTHORSHIP_ORIGIN, FermentationStatus, NovaEngine, StoreFragment,
    ProvenanceOverwriteViolation,
)
from src.filtration.scar_logic_core import ScarLogicCore
from src.filtration.scar_management import DecayState, SML, normalize
from src.identity.ril import RIL, IdentityThread
from src.reflex.racm import QUEUE_MAX, RACM, ReflexClaim, Scope
from src.utils.continuity import RestorationOutcome
from src.utils.models import Doctrine, Scar

from tests.invariants import _ast as H


def _ids(entries):
    return [e["record_id"] for e in entries]


class _StubScarCore:
    """A scar owner's READ face, with a controllable seed-tag answer."""

    def __init__(self, scars):
        self._scars = {s.id: s for s in scars}

    def get_scar(self, scar_id):
        return self._scars.get(scar_id)

    def seed_scars_tagged(self, tag):
        return [s for s in self._scars.values()
                if s.is_seed and tag in (s.tca_tags or [])]


def _seed_scar(sid, tags):
    return Scar(id=sid, name=sid, origin="seed", is_seed=True, tca_tags=list(tags))


# =====================================================================
# PIN 1 - THE HEADLINE. A restart cannot rewrite her birth identity.
# =====================================================================

def test_origin_survives_a_restart_and_the_next_scar_does_not_claim_it():
    """RULING 42 res.1+2 - THE PIN THIS WHOLE PASS EXISTS FOR.

    Ingest A, tear the process down, rebuild from disk, ingest B. ORIGIN IS
    STILL A.

    RED BEFORE THIS PASS, for the plainest possible reason: `RIL.__init__` built
    `threads` empty and there was no `load()`, so the rebuilt RIL saw an empty
    ORIGIN and B claimed it. The `is_root and not ORIGIN` guard was doing its job
    perfectly and guarding a fact that had already been erased.

    NO SCAR OWNER HERE, DELIBERATELY. That keeps res.4's bare-construction
    semantics in play (the constitutional derivation needs an owner to ask), so
    this pin watches the RESTART, not the constitution. The constitution has its
    own pins below.
    """
    a = Scar(id="Scar-A", name="a", origin="test")
    b = Scar(id="Scar-B", name="b", origin="test")

    first = RIL()
    first.ingest_scar(a)
    assert _ids(first.threads[IdentityThread.ORIGIN]) == ["Scar-A"]

    del first                                    # the process boundary
    resumed = RIL()                              # rebuilt from disk alone

    assert resumed.load_report is not None, "a resumed store must report itself"
    assert resumed.load_report.outcome is RestorationOutcome.RESTORED
    assert resumed.load_report.resumed is True
    assert _ids(resumed.threads[IdentityThread.SCARLINE]) == ["Scar-A"]

    resumed.ingest_scar(b)

    assert _ids(resumed.threads[IdentityThread.ORIGIN]) == ["Scar-A"], (
        "a restart must not let the next scar become her birth identity")
    assert _ids(resumed.threads[IdentityThread.SCARLINE]) == ["Scar-A", "Scar-B"]


# =====================================================================
# PIN 2 - the constitution, against the REAL seed
# =====================================================================

def test_constitutional_origin_resolves_to_the_real_seed_record():
    """RULING 42 res.3, pinned against the ACTUAL tracked seed - Ruling 35's
    regression-pin precedent, and for its reason: a synthetic fixture would
    prove the mechanism works on data of my own choosing, which is exactly the
    class of test that let a fallen doctrine load LIVE for months.

    `data/scars.json` carries exactly one seed record tagged `origin`: `Scar-0`.
    A fresh RIL with no state file resolves ORIGIN to it and reports MIGRATED -
    a value derived from facts the file did not carry is not a restoration.
    """
    ril = RIL(scar_core=ScarLogicCore())

    origin = ril.threads[IdentityThread.ORIGIN]
    assert _ids(origin) == ["Scar-0"]
    assert origin[0]["provenance"] == "constitutional"
    assert origin[0]["record_type"] == "scar"

    assert ril.load_report.outcome is RestorationOutcome.MIGRATED, (
        "a derivation is reported as a derivation, never as a clean restore")
    assert ril.load_report.detail["origin_record_id"] == "Scar-0"

    # NO EMBEDDED RECORD. The entry names the scar; it does not carry it.
    assert "weight" not in origin[0], "RIL must not carry SML's magnitudes"


def test_the_first_runtime_scar_no_longer_claims_a_constitutional_origin():
    """The consequence of res.3 that changes live behavior, stated as a pin.

    With an owner present, ORIGIN is settled before any collapse happens - so
    the first scar of the run lands on SCARLINE only. Before this ruling it
    became her birth identity, which made her origin a function of what she
    happened to collapse on first.
    """
    ril = RIL(scar_core=ScarLogicCore())
    ril.ingest_scar(Scar(id="Scar-RUNTIME", name="r", origin="test"))

    assert _ids(ril.threads[IdentityThread.ORIGIN]) == ["Scar-0"]
    assert _ids(ril.threads[IdentityThread.SCARLINE]) == ["Scar-RUNTIME"]


# =====================================================================
# PIN 3 - THE FORCING FORM. Without it, pin 2 passes for free.
# =====================================================================

@pytest.mark.parametrize("scars,label", [
    ([], "zero origin-tagged seed scars"),
    ([_seed_scar("S-1", ["origin"]), _seed_scar("S-2", ["origin"])], "two of them"),
])
def test_an_unresolvable_constitution_is_declared_never_guessed(scars, label):
    """RULING 42 res.3's REFUSAL HALF, in FORCING FORM.

    THE RULING 35 LESSON, APPLIED PROSPECTIVELY: pin 2 above passes because the
    real seed happens to hold exactly one `origin` record. It would go on passing
    if the "exactly one" requirement were deleted, because the fixture can never
    produce a second one. So these stores are BUILT to violate it.

    Zero or several: ORIGIN STAYS EMPTY, a VOID discontinuity records the
    question as unresolvable, and NOTHING is picked. No name match, no id match,
    no oldest-wins tiebreak - an ambiguous constitution is a fact to record, not
    a tie to break.
    """
    ril = RIL(scar_core=_StubScarCore(scars))

    assert ril.threads[IdentityThread.ORIGIN] == [], (
        f"{label}: ORIGIN must stay empty rather than claim one")

    void = ril.threads[IdentityThread.VOID]
    assert len(void) == 1
    assert void[0]["kind"] == "constitutional_origin_unresolvable"
    assert void[0]["candidate_ids"] == sorted(s.id for s in scars)
    assert str(len(scars)) in void[0]["reason"]


def test_a_runtime_scar_tagged_origin_can_never_become_her_constitution():
    """CASE PIN ADDED AFTER A SURVIVING MUTANT (M06: dropping `is_seed` from
    `seed_scars_tagged` left the whole suite green).

    THE QUESTION THE SURVIVOR GOT: what execution path would have to run for this
    to matter? One where a scar formed at RUNTIME carries the `origin` tag. The
    tracked seed has exactly one `origin` record and it is `is_seed=True`, so no
    fixture in the tree could ever produce that configuration - the filter was
    correct and completely unwitnessed. That is Ruling 35's lesson exactly: a
    guard is invisible to every test whose data cannot violate it.

    SO THIS TEST BUILDS THE CONFIGURATION. With `is_seed` in the filter, the
    constitution resolves to `Scar-0` and the runtime scar is simply not a
    candidate. Without it, there are TWO candidates, the constitution becomes
    unresolvable, and ORIGIN goes empty - which is how a runtime fact would have
    been able to erase her birth identity.

    It uses the REAL owner deliberately: the stub above re-implements the filter,
    so it would answer for the owner and witness nothing.
    """
    scars = ScarLogicCore()
    scars.add_scar(Scar(id="Scar-RUNTIME-ORIGIN", name="r", origin="runtime",
                        is_seed=False, tca_tags=["origin"]))

    ril = RIL(scar_core=scars)

    assert _ids(ril.threads[IdentityThread.ORIGIN]) == ["Scar-0"], (
        "her constitution is what she was BORN with - a runtime scar carrying "
        "the same tag is a runtime fact and must not be a candidate")
    assert ril.threads[IdentityThread.VOID] == [], (
        "and the runtime scar must not make the constitution ambiguous either")


def test_no_scar_owner_declares_nothing_at_all():
    """THE THIRD CASE, and it is not the same as the second.

    No owner means NO INSTRUMENT RAN - Docket H's `NOT_COUNTABLE` vs
    `NONE_FOUND` cut, which is that two zeroes are not the same zero. A bare
    RIL has asked nobody, so it has learned nothing to declare, and writing a
    discontinuity here would be reporting a failed lookup that never happened.
    """
    ril = RIL()
    assert ril.threads[IdentityThread.ORIGIN] == []
    assert ril.threads[IdentityThread.VOID] == [], (
        "an absent instrument is not a negative result")


# =====================================================================
# PIN 4 + 5 - the Nova mint, and the detector that survives it
# =====================================================================

def _mutated_echo(nova, doctrine_id, scar="Scar-1"):
    echo = nova.erupt(origin_kind=DOCTRINE_AUTHORSHIP_ORIGIN,
                      origin_id=doctrine_id, scar_links=[scar])
    echo.status = FermentationStatus.MUTATED
    return echo


def _frags(doctrine_id):
    return {doctrine_id: [StoreFragment(store="doctrines", record_id=doctrine_id,
                                        content="material")]}


def test_the_nova_mint_restores_and_ids_never_repeat_across_a_restart():
    """RULING 42 res.4 - THE MINT IS PART OF THE RECORD.

    RED BEFORE THIS PASS: `_seq` was rebuilt to 0 on every construction. With the
    record durable and the counter not, the second process remints `NE-0001` over
    an id that has already authored, and `_append_provenance` raises
    ProvenanceOverwriteViolation on a collision that is NOT a double authorship -
    a true detector firing on a false positive, which is how a detector gets
    weakened by whoever it annoys.
    """
    first = NovaEngine()
    _mutated_echo(first, "D-1")
    emitted = first.proposals(_frags("D-1"))
    assert emitted, "the echo should have authored"
    minted_before = sorted(first.echo_index)

    del first
    resumed = NovaEngine()

    assert resumed.load_report.outcome is RestorationOutcome.RESTORED
    assert sorted(resumed.echo_index) == minted_before
    assert resumed.proposal_provenance, "authorship must survive the boundary"

    # The second era mints, and it does NOT collide.
    _mutated_echo(resumed, "D-2")
    assert resumed.proposals(_frags("D-2")), "the new echo should author"

    ordinals = [int(i[3:]) for i in sorted(resumed.echo_index)]
    assert ordinals == sorted(set(ordinals)), "no id was reminted"
    assert ordinals == list(range(1, len(ordinals) + 1)), (
        "the counter resumed rather than restarting")


def test_a_genuine_double_authorship_still_raises():
    """RULING 42's FORCING FORM for pin 4: the detector SURVIVES, AIMED.

    Persistence removes a false-positive cause. It must not remove the guard. A
    real collision - the same proposal id written twice - still raises, and the
    raise still refuses to be softened to a merge or a skip.
    """
    nova = NovaEngine()
    nova._append_provenance("D-1::nova::NE-0001", [{"store": "doctrines",
                                                    "record_id": "D-1"}])
    with pytest.raises(ProvenanceOverwriteViolation):
        nova._append_provenance("D-1::nova::NE-0001", [{"store": "doctrines",
                                                        "record_id": "D-1"}])


def test_a_spent_echo_is_still_spent_after_a_restart():
    """RULING 13 ACROSS THE BOUNDARY. One echo backs one proposal, EVER - and
    "ever" now means what it says. Before persistence, a restart restored the
    echo unspent and it could author a second time: Ruling 13 undone by a
    power cut."""
    first = NovaEngine()
    echo = _mutated_echo(first, "D-1")
    first.proposals(_frags("D-1"))
    assert first.echo_index[echo.id].is_spent

    del first
    resumed = NovaEngine()

    assert resumed.echo_index[echo.id].is_spent, "spentness must cross the boundary"
    assert resumed.proposals(_frags("D-1")) == {}, (
        "a spent echo may never author again, restart or no restart")


def test_a_migrated_mint_is_reported_as_a_derivation():
    """RULING 42 res.4's MIGRATED half: `seq` absent, minted ids present.

    Those ids are RECORDED FACTS - `NE-0003` on disk is proof three ids were
    issued - so the counter is DERIVED from them rather than restarted. Reported
    as MIGRATED, never as RESTORED: the file did not carry it.
    """
    nova = NovaEngine()
    for i in range(3):
        nova.erupt(origin_kind=DOCTRINE_AUTHORSHIP_ORIGIN, origin_id=f"D-{i}")
    path = nova.runtime_path

    payload = json.loads(path.read_text(encoding="utf-8"))
    del payload["seq"]                                   # a pre-contract file
    path.write_text(json.dumps(payload), encoding="utf-8")

    resumed = NovaEngine()
    assert resumed.load_report.outcome is RestorationOutcome.MIGRATED
    assert resumed._seq == 3, "derived from the highest recorded NE- ordinal"

    resumed.erupt(origin_kind=DOCTRINE_AUTHORSHIP_ORIGIN, origin_id="D-new")
    assert "NE-0004" in resumed.echo_index, "the derived mint continues, not repeats"


def test_an_echo_whose_scar_vanished_is_quarantined_not_dropped():
    """RULING 42's QUARANTINED outcome. A dangling reference is a reason to stop
    trusting the LINK, not a reason to destroy the record of the eruption - and
    not a reason to silently relink it to something else either."""
    nova = NovaEngine(scar_core=_StubScarCore([Scar(id="Scar-live", name="l",
                                                    origin="t")]))
    nova.erupt(origin_kind=DOCTRINE_AUTHORSHIP_ORIGIN, origin_id="D-1",
               scar_links=["Scar-live"])
    nova.erupt(origin_kind=DOCTRINE_AUTHORSHIP_ORIGIN, origin_id="D-2",
               scar_links=["Scar-GONE"])

    resumed = NovaEngine(scar_core=_StubScarCore([Scar(id="Scar-live", name="l",
                                                       origin="t")]),
                         runtime_path=str(nova.runtime_path))

    assert resumed.load_report.outcome is RestorationOutcome.PARTIALLY_RESTORED
    assert "NE-0001" in resumed.echo_index
    assert "NE-0002" not in resumed.echo_index, "a dangling echo is HELD OUT"
    assert [q["echo_id"] for q in resumed.quarantined_echoes] == ["NE-0002"]
    assert resumed.quarantined_echoes[0]["missing_scar_links"] == ["Scar-GONE"]


# =====================================================================
# PIN 6 - RACM: deferred pressure survives the boundary
# =====================================================================

def _claim(rid, pressure, scope=Scope.LOCAL):
    return ReflexClaim(reflex_id=rid, pressure_level=pressure, scope=scope,
                       source_module="test", trigger_conditions={"p": pressure})


def _age_to(racm, arbitrations):
    """Drive REAL arbitration `arbitrations` times.

    ACR is declared GLOBAL-scope so the compatibility partition (Overflow Policy
    2) forces a genuine contention rather than letting both claims co-execute -
    a queue reached by hand-inserting a slot would pin the serializer and not the
    thing being serialized. ICA wins on canonical rank; ACR is the one that ages.
    """
    for _ in range(arbitrations):
        racm.arbitrate([_claim("ACR", 0.9, Scope.GLOBAL), _claim("ICA", 0.8)])


def test_a_deferred_claim_resumes_at_its_own_age_and_keeps_ageing():
    """RULING 42 res.3. Deferred pressure is pressure AUREA JUDGED AND CHOSE TO
    CARRY. A restart used to discharge it silently.

    `deferred_cycles` and `ttl_remaining` are RELATIVE counters, so `cycle` is
    written in the SAME snapshot - the age is still measured against the clock it
    was counted against. No global symbolic ordinal exists, and none is invented.
    """
    first = RACM()
    _age_to(first, 3)
    slot = first._queue["ACR"]
    assert slot.deferred_cycles == 2, "precondition: the loser has aged twice"
    saved_cycle, saved_ttl = first.cycle, slot.ttl_remaining

    del first
    resumed = RACM()

    assert resumed.load_report.outcome is RestorationOutcome.RESTORED
    assert resumed.cycle == saved_cycle, "the clock crosses with the ages"
    assert "ACR" in resumed._queue, "deferred pressure must not evaporate"
    assert resumed._queue["ACR"].deferred_cycles == 2
    assert resumed._queue["ACR"].ttl_remaining == saved_ttl
    assert resumed._queue["ACR"].claim.trigger_conditions == {"p": 0.9}, (
        "the claim's own payload rides with it (Ruling 9: a queue winner "
        "executes against its OWN stored trigger, never the live cycle's)")

    # And it CONTINUES ageing - it resumed as live state, not as a frozen record.
    resumed.arbitrate([_claim("ICA", 0.8)])
    assert resumed._queue["ACR"].deferred_cycles == 3


def test_a_restored_queue_over_the_bound_is_refused_not_truncated():
    """RULING 42 res.3 + Ruling 23's bound. TRUNCATION IS A SILENT DRAIN: it
    would discard real deferred pressure and report a healthy queue. The 32-slot
    reasoning applies to this bound too - the cap does not move, and overflowing
    it is a REFUSAL that gets RECORDED."""
    racm = RACM()
    payload = {
        "version": RACM.STATE_VERSION,
        "cycle": 5,
        "queue": [{"claim": RACM._claim_to_dict(_claim(f"R-{i}", 0.5)),
                   "deferred_cycles": 1, "ttl_remaining": 4}
                  for i in range(QUEUE_MAX + 1)],
    }
    racm.runtime_path.write_text(json.dumps(payload), encoding="utf-8")

    resumed = RACM(runtime_path=str(racm.runtime_path))

    assert resumed.load_report.outcome is RestorationOutcome.REFUSED
    assert resumed._queue == {}
    assert len(resumed.declared_losses) == 1, (
        "unresolved pressure never leaves silently (Ruling 23)")
    assert resumed.declared_losses[0]["slots_lost"] == QUEUE_MAX + 1


def test_an_unreadable_queue_declares_its_loss_on_the_durable_channel():
    """The declared loss reaches the RB channel, not just an in-memory list.
    A loss recorded only in memory would evaporate at the NEXT restart, which is
    this ruling's own defect one level up."""
    racm = RACM()
    racm.runtime_path.write_text("{ this is not json", encoding="utf-8")

    resumed = RACM(runtime_path=str(racm.runtime_path))

    assert resumed.load_report.outcome is RestorationOutcome.REFUSED
    assert resumed.declared_losses
    logged = [e for e in resumed.rb.entries
              if e.trigger_conditions.get("restore_refused")]
    assert logged, "the loss must reach the durable forensic channel"


def test_both_scope_axes_round_trip_without_collapsing_into_each_other():
    """RULING 30 ACROSS SERIALIZATION. `scope` is the durability/breadth axis;
    `lock_class` is the ACTION's structural class. They share neither type nor
    member names by construction, and writing either as the other would rebuild
    the exact conflation Ruling 30 made unwritable."""
    from src.topology.tcaml import LockClass

    claim = ReflexClaim(reflex_id="GSR", scope=Scope.GLOBAL,
                        lock_class=LockClass.STRUCTURAL, pressure_level=0.9,
                        affected_systems=frozenset({"all"}))
    back = RACM._claim_from_dict(RACM._claim_to_dict(claim))

    assert back.scope is Scope.GLOBAL
    assert back.lock_class is LockClass.STRUCTURAL
    assert back.affected_systems == frozenset({"all"})


# =====================================================================
# PIN 7 + 10 - the taxonomy, and REFUSED means BYTE-UNTOUCHED
# =====================================================================

@pytest.mark.parametrize("build", [
    lambda p: RIL(runtime_path=str(p)),
    lambda p: NovaEngine(runtime_path=str(p)),
    lambda p: RACM(runtime_path=str(p)),
], ids=["ril", "nova", "racm"])
def test_an_unknown_version_is_refused_and_the_file_is_left_byte_untouched(build, tmp_path):
    """RULING 42 res.1's GOVERNING SENTENCE, pinned on all three stores:

        When AUREA cannot prove a budget is unused, she does not assume it is
        unused.

    An unknown `version` is exactly that condition. The store constructs EMPTY
    and the file is NOT rewritten, migrated or truncated - she does not overwrite
    what she could not read.
    """
    path = tmp_path / "future.json"
    body = json.dumps({"version": 999, "payload": "from a build that does not exist yet"})
    path.write_text(body, encoding="utf-8")
    before = hashlib.sha256(path.read_bytes()).hexdigest()

    store = build(path)

    assert store.load_report.outcome is RestorationOutcome.REFUSED
    assert "999" in store.load_report.detail["reason"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == before, (
        "a refused file must be left BYTE-UNTOUCHED")


def test_a_refusal_is_sticky_for_the_life_of_the_process():
    """"BYTE-UNTOUCHED" IS NOT A STATEMENT ABOUT THE INSTANT OF THE REFUSAL.

    A file overwritten one ingest later was not left untouched. So a store that
    refused its file does not write to it again - and the lost durability is
    RECORDED on `load_report` rather than being silent, which is the difference
    between an honest degradation and a fail-silent one.
    """
    ril = RIL()
    ril.runtime_path.write_text(json.dumps({"version": 999}), encoding="utf-8")

    resumed = RIL(runtime_path=str(ril.runtime_path))
    before = hashlib.sha256(resumed.runtime_path.read_bytes()).hexdigest()

    resumed.ingest_scar(Scar(id="Scar-X", name="x", origin="t"))

    assert hashlib.sha256(resumed.runtime_path.read_bytes()).hexdigest() == before
    assert resumed.load_report.outcome is RestorationOutcome.REFUSED


def test_a_first_run_reports_nothing_because_it_restored_nothing():
    """There is no sixth enum member for "nothing happened". A first run performs
    no restoration, so `load_report` stays None - absence is not an event.

    NOVA AND RACM ONLY: a first-run RIL WITH an owner does perform a derivation
    (the constitutional origin), and a derivation is `MIGRATED`. Absence of a
    file and absence of a restoration are two different absences."""
    assert NovaEngine().load_report is None
    assert RACM().load_report is None
    assert RIL().load_report is None            # bare: no owner, so no derivation


# =====================================================================
# PIN 8 - STRUCTURAL. No identity thread may hold a record OBJECT.
# =====================================================================

def test_no_identity_thread_entry_is_ever_an_embedded_record_object():
    """RULING 42 res.2, RUNTIME HALF, through the REAL pipeline.

    An embedded `Scar` in an identity thread is a WRITE PATH INTO THE SCAR STORE
    that the Ruling 1 scanner structurally cannot see, because nothing assigns to
    `scar_core.scars`. psi.py had already named the hazard in words - "a held
    Scar reference is a held write path" - while RIL held one per scar.
    """
    from src.aurea_core import AureaCore

    aurea = AureaCore()
    aurea.process_input("Honesty is pointless.")

    for thread, entries in aurea.ril.threads.items():
        for entry in entries:
            assert not isinstance(entry, (Scar, Doctrine)), (
                f"{thread.value} holds an embedded record object: {entry!r}")
            assert isinstance(entry, dict), f"{thread.value} entry is not a reference"


def _thread_append_offenders(tree, exempt=frozenset()):
    """Appends into `self.threads[...]` whose value is not built at the site.

    A dict literal or a `_scar_entry(...)` call is a reference BUILT HERE. A bare
    name is whatever the caller handed in - which is exactly how the live `Scar`
    objects got onto the threads in the first place.
    """
    offenders = []
    for fn in ast.walk(tree):
        if not isinstance(fn, ast.FunctionDef) or fn.name in exempt:
            continue
        for node in ast.walk(fn):
            if not (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "append"):
                continue
            target = node.func.value
            if not (isinstance(target, ast.Subscript)
                    and isinstance(target.value, ast.Attribute)
                    and target.value.attr == "threads"):
                continue
            arg = node.args[0] if node.args else None
            ok = isinstance(arg, ast.Dict) or (
                isinstance(arg, ast.Call) and isinstance(arg.func, ast.Attribute)
                and arg.func.attr == "_scar_entry")
            if not ok:
                offenders.append(
                    f"ril.py:{node.lineno} ({fn.name}) appends "
                    f"{ast.dump(arg)[:60] if arg else 'nothing'}")
    return offenders


def test_ril_never_appends_a_bare_object_to_a_thread():
    """RULING 42 res.2, STRUCTURAL HALF - the runtime pin above only sees the
    paths this pass happens to drive.

    Every append into `self.threads[...]` in `ril.py` must build its entry
    inline (a dict literal) or through `_scar_entry`. A bare name would be
    whatever the caller handed in, which is how the live objects got there.

    `request_thread_write` is EXEMPT BY NAME and that is deliberate, not a hole:
    it is the SPECULATIVE requester surface for TCAML/MSSL, neither of which
    exists, and its entry is the requester's own record rather than a scar
    reference. When a real requester arrives, its shape is a ruling.
    """
    tree = H.parse(H.repo_root() / "src" / "identity" / "ril.py")
    offenders = _thread_append_offenders(tree, exempt={"request_thread_write"})

    assert not offenders, (
        "\n".join(offenders) + "\n\n"
        "  An identity thread entry must be a BY-ID REFERENCE built here\n"
        "  (Ruling 42 res.2), never an object handed in by a caller.\n")


def test_that_scanner_actually_fires():
    """The pin above is pinned (Ruling 32's scanner-fires precedent). Fed the
    exact pre-Ruling-42 code, it must go red - otherwise it is green because it
    sees nothing, which is indistinguishable from green because it found nothing.
    """
    offending = ("class R:\n"
                 "    def ingest(self, scar):\n"
                 "        self.threads[T.SCARLINE].append(scar)\n")
    assert _thread_append_offenders(ast.parse(offending)), (
        "the scanner would not have caught the original defect")

    # ... and it does NOT fire on the shapes that are correct, or it would be
    # demanding the wrong fix (the `find_default_paths` benign-control precedent).
    benign = ("class R:\n"
              "    def ingest(self, scar):\n"
              "        self.threads[T.SCARLINE].append(self._scar_entry(scar, 'i'))\n"
              "    def note(self):\n"
              "        self.threads[T.VOID].append({'kind': 'x'})\n"
              "    def elsewhere(self, x):\n"
              "        self.refusals.append(x)\n")
    assert _thread_append_offenders(ast.parse(benign)) == []


# =====================================================================
# PIN 9 - THE RULING 40 RIDER: one writer for `decay_state`
# =====================================================================

def test_only_sml_assigns_decay_state_anywhere_in_src():
    """RULING 40. `scar_logic_core.decay_scar` wrote `decay_state` directly - the
    ONE remaining writer outside SML, flagged in-file as "Reported, not repaired"
    since Ruling 37.

    This is an AST pin over the WHOLE of `src/`, not just the two modules that
    happened to be involved: the invariant suite registers `decay_state` in
    STORE_OWNERS as well, and a rule enforced in one place is a rule with one
    place left to break it.
    """
    owner = "src/filtration/scar_management.py"
    offenders = []
    for path in H.src_files():
        if H.rel(path) == owner:
            continue
        tree = H.parse(path)
        if tree is None:
            continue
        for lineno, detail in H.find_store_mutations(tree, "decay_state"):
            offenders.append(f"{H.rel(path)}:{lineno} {detail}")

    assert not offenders, (
        "\n".join(offenders) + f"\n\n  Only {owner} writes `decay_state`.\n")


def test_decay_scar_still_retires_and_does_so_through_the_owner():
    """RULING 40, BEHAVIORAL HALF. The public surface is unchanged - same name,
    same argument, same True/False contract - and the WRITE moved to SML.

    The record shows it was MANUAL, not scheduled (Ruling 29's shape: one event
    type covering two causes is a defect one level down).
    """
    scars = ScarLogicCore()
    target = scars.scars[0].id

    assert scars.decay_scar(target) is True
    assert normalize(scars.get_scar(target).decay_state) is DecayState.DORMANT
    assert scars.decay_scar("no-such-scar") is False, (
        "an unknown id answers False; it does not raise")

    record = scars._decay_owner().transitions[-1]
    assert record["scar_id"] == target
    assert record["trigger"] == "manual"
    assert record["to"] == DecayState.DORMANT.value


def test_a_manual_retire_never_closes_an_epoch():
    """THE LOAD-BEARING HALF OF THE RIDER, and the reason the jump past WANING is
    safe.

    Ruling 37 makes fermentation complete when a scar leaves ACTIVE **by decay** -
    `_emit_fermentation` is reachable ONLY from `ACTIVE -> WANING`. A manual
    retire goes straight to DORMANT, so it cannot reach it EVEN BY ACCIDENT.

    If it could, an operator calling `decay_scar` would restore AUREA's mutation
    budget - restart-absolution (Ruling 34) wearing a different hat, and a guard
    pointed the wrong way for the second time.
    """
    class _SAEStub:
        def __init__(self):
            self.touched_lineages = {"Scar-M"}
            self.epoch = 0
            self.calls = []

        def stabilization_event(self, kind, lineage=""):
            self.calls.append((kind, lineage))
            return True

    scar = Scar(id="Scar-M", name="m", origin="t", decay_state="active")
    core = ScarLogicCore()
    core.scars = [scar]
    sae = _SAEStub()
    core.attach_decay_owner(SML(scar_core=core, sae=sae))

    assert core.decay_scar("Scar-M") is True
    assert normalize(scar.decay_state) is DecayState.DORMANT
    assert sae.calls == [], (
        "a manual retire is not cooling - it must not discharge an epoch debt")


def test_the_scheduled_path_still_emits_its_settle_event():
    """The rider's non-weakening argument, as a pin: Ruling 37's settle sender
    is UNTOUCHED. Scheduled `ACTIVE -> WANING` still emits, or the rider would
    have closed the only way an epoch can close."""
    class _SAEStub:
        def __init__(self):
            self.touched_lineages = {"Scar-S"}
            self.epoch = 0
            self.calls = []

        def stabilization_event(self, kind, lineage=""):
            self.calls.append((kind, lineage))
            return True

    scar = Scar(id="Scar-S", name="s", origin="t", decay_state="active")
    core = ScarLogicCore()
    core.scars = [scar]
    sae = _SAEStub()
    sml = SML(scar_core=core, sae=sae)

    sml.transition("Scar-S", DecayState.WANING)

    assert sae.calls == [("scar_fermentation", "Scar-S")]
    assert sml.transitions[-1]["trigger"] == "scheduled"
