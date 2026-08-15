"""
test_ruling78.py - RULING 78: THE DURABILITY RULING.

    What reached the record reaches the disk, and what must agree is written
    in the order that keeps it honest.

THE SUBJECT IS CROSS-STORE DIVERGENCE, NOT DATA LOSS. Every store passed its
own integrity checks; the disagreement was BETWEEN them. After a doctrine
mutation and an unclean restart, `sae_epoch.json` durably recorded a mutation
`doctrines.json` did not contain - a spent budget against a belief she does not
hold. A durable suspension's `claim_id` could join to a scar that never landed.
And a minted ledger id that escaped into fsync'd records could be REBORN naming
a different perception, because its own append line died in the page cache and
the mint's floor re-derived lower.

WHY PINS (d) AND (f) IMPORT THE NEW HELPER LAZILY, IF AT ALL
-------------------------------------------------------------
Both were run at base (`37007b75`) and watched RED before the code that closes
them existed - the ruling requires it, and their failure output is recorded in
the pass report verbatim. A module-level import of `durable_append_text` would
have turned that watch into a COLLECTION ERROR, which witnesses nothing: a file
that cannot be imported has not measured the defect, it has merely failed to
run. So the helper is imported INSIDE the pins that need it, and this module
imports only what `37007b75` already had.
"""

from __future__ import annotations

import ast
import json
import os
from datetime import datetime
from pathlib import Path

import pytest

from src.aurea_core import AureaCore
from src.doctrine.codex import Codex
from src.filtration.scar_logic_core import ScarLogicCore
from src.utils.models import Doctrine
from tests.proof_support import minimal_proof

REPO = Path(__file__).resolve().parents[1]
ATOMIC_WRITE = "src/utils/atomic_write.py"


def _tree(rel: str) -> ast.Module:
    return ast.parse((REPO / rel).read_text(encoding="utf-8"))


def _src_files():
    """Every module in `src/`, by RGLOB.

    Ruling 70's instrument lesson: a census over a hand-maintained module list
    reports a completeness that lapses the moment someone adds a file. The
    module nobody has written yet must be covered by construction.
    """
    return sorted(REPO.joinpath("src").rglob("*.py"))


def _mutate(core, ancestor_id: str, successor_id: str):
    """One real mutation through the real path. Returns the successor id."""
    core.sae.mutate_doctrine(
        ancestor_id,
        Doctrine(id=successor_id, name="Successor",
                 description="the belief after", created_at=datetime.now()),
        collapse_lineage="Scar-0",
        proof=minimal_proof("test_ruling78"))
    return successor_id


def _a_live_doctrine(core) -> str:
    """A doctrine id the Codex actually holds, read from the tree's own seed.

    Read rather than named: pinning a literal here would make this file assert
    a fact about `data/doctrines.json` that belongs to Ruling 32's seed, not to
    this ruling.
    """
    live = [d for d in core.codex.active() if not d.id.startswith("Doctrine-0")]
    assert live, "the seed must hold at least one mutable live doctrine"
    return live[0].id


# =====================================================================
# (d) THE DIVERGENCE WITNESS - the census's central finding
# =====================================================================

def test_d_a_mutation_survives_an_unclean_restart():
    """RED AT `37007b75`, GREEN AT CLOSE. The ruling's headline.

    ONE COMMAND TWICE: mutate a doctrine through a live core, construct a
    fresh one WITHOUT `save_state`, and ask whether she still believes it.

    At base she did not. `Codex.commit` installed the successor in memory and
    nothing wrote it down, so the only durable record of the event was
    `sae_epoch.json` - which HAD been made durable at the moment of spending
    (Ruling 34). The budget was spent durably against content that vanished:
    not a lost mutation but a DISAGREEMENT, and the store that survived was the
    one recording that she had already changed her mind.

    `save_state` is deliberately not called. A checkpoint that fires only when
    someone remembers is the defect, not the fix (Ruling 78 res.3, refusing
    position (a) in terms).
    """
    core = AureaCore()
    ancestor = _a_live_doctrine(core)
    successor = _mutate(core, ancestor, f"{ancestor}::r78")

    resumed = AureaCore()

    assert resumed.codex.get(successor) is not None, (
        f"'{successor}' was committed through the real mutation path and did "
        f"not survive an unclean restart. The Codex holds "
        f"{sorted(d.id for d in resumed.codex.active())}.")


def test_d_the_ancestor_is_durably_fossilized_by_the_same_event():
    """The other half of the same event, and it fails the same way.

    A mutation is a PAIR - the ancestor falls and the successor rises - and
    both halves live in the one file `commit` now writes. Pinning only the
    successor would leave a tree where the belief arrived and the record of
    what it replaced did not.
    """
    core = AureaCore()
    ancestor = _a_live_doctrine(core)
    _mutate(core, ancestor, f"{ancestor}::r78")

    resumed = AureaCore()

    assert ancestor in resumed.codex.fossils, (
        f"'{ancestor}' was fossilized by the mutation and came back live. "
        f"Fossils after restart: {sorted(resumed.codex.fossils)}")
    assert resumed.codex.get(ancestor) is None


# =====================================================================
# (f) SCAR FORMATION DURABLE ACROSS AN UNCLEAN RESTART
# =====================================================================

def test_f_a_formed_scar_survives_an_unclean_restart():
    """RED AT BASE. The formation window, which the census scoped correctly.

    `scars.json` IS internally checkpointed - but only by `SML.transition`,
    i.e. by a later DECAY, and by an operator `save_state`. So a formed scar
    was durable only if something else happened to it afterwards: a wound was
    remembered because it later cooled, and forgotten if nothing disturbed it.
    That is Ruling 54's erosion argument standing on its head - there, calm
    must not erode what she survived; here, calm must not ERASE it.
    """
    core = AureaCore()
    before = {s.id for s in core.scar_core.all_scars()}
    formed = core.scar_core.form_scar(
        origin="test_ruling78", type="structural", weight=1.0,
        description="a wound that must outlive the process that made it")
    assert formed.id not in before

    resumed = AureaCore()

    assert resumed.scar_core.get_scar(formed.id) is not None, (
        f"'{formed.id}' was formed through the owner's own write door and did "
        f"not survive an unclean restart.")


# =====================================================================
# (a) THE FUNNEL'S DECISION IS UPHELD - AND ITS CONDITION IS A TRIPWIRE
# =====================================================================

def test_a_the_no_directory_fsync_exemption_still_has_its_platform():
    """PIN (a). AN EXEMPTION'S STATED CONDITION IS PART OF THE EXEMPTION.

    `atomic_write.py` declines the POSIX directory fsync and gives a REASON:
    this tree's platform has no directory file descriptor to sync, so the call
    would be a platform branch that is a no-op on the machine it runs on.
    Ruling 78 res.1 UPHELD that decision rather than repairing it.

    A decision resting on a condition nobody rechecks is how a considered
    exemption becomes an unexamined one. So the condition is asserted, and if
    it ever dies this test says what is OWED rather than leaving the next
    reader to infer that the exemption still holds.
    """
    assert os.name == "nt", (
        "THE EXEMPTION'S PLATFORM CONDITION IS DEAD. `atomic_write.py` declines "
        "the directory fsync because this tree's platform has no directory fd; "
        "that premise no longer holds, so the POSIX directory-fsync question is "
        "now OWED AS ITS OWN RULING. DO NOT add the branch here to make this "
        "green - report it.")


def test_a_the_snapshot_funnel_still_declines_the_directory_fsync():
    """PIN (a), the other half: the decision is UPHELD, so the code must still
    reflect it. A pass that quietly added the branch would leave the tripwire
    above guarding a condition nothing depends on."""
    text = (REPO / ATOMIC_WRITE).read_text(encoding="utf-8")
    assert "NO DIRECTORY FSYNC" in text, (
        "the declared exemption left the docstring; res.1 upheld it, so if it "
        "was reversed that is a ruling, and this pin is where it is recorded")


# =====================================================================
# (b) THE HELPER'S OWN BATTERY
# =====================================================================

def test_b_every_append_is_fsynced(tmp_path, monkeypatch):
    """PIN (b). THE WHOLE POINT, WITNESSED.

    `flush` moves Python's buffer into the OS; only `fsync` moves the OS's
    buffer onto the device. An append that returns after the first leaves the
    caller believing a record was made while the bytes sit in the page cache -
    the mechanism behind the reborn-id hazard: the id escaped into fsync'd
    records, its own line did not, and the mint's floor re-derived lower.

    THE FD IS ASSERTED, NOT MERELY THE CALL COUNT: an `os.fsync` on some OTHER
    descriptor would satisfy a bare counter while syncing nothing that matters.
    """
    from src.utils.atomic_write import durable_append_text

    synced = []
    real = os.fsync

    def spy(fd):
        synced.append(fd)
        return real(fd)

    monkeypatch.setattr(os, "fsync", spy)

    target = tmp_path / "ledger.jsonl"
    durable_append_text(target, chr(123) + '"id": "A"' + chr(125) + "\n")
    durable_append_text(target, chr(123) + '"id": "B"' + chr(125) + "\n")

    assert len(synced) == 2, "one fsync per append; got " + repr(synced)
    assert all(isinstance(fd, int) for fd in synced)
    assert target.read_text(encoding="utf-8").count("\n") == 2


def test_b_the_caller_supplies_the_newline(tmp_path):
    """PIN (b) / res.2. THE RULED CHOICE, PINNED AS BYTES.

    The helper writes what it is given and not one byte more. A separator is
    part of a ledger's FORMAT, which belongs to the ledger's owner - the same
    boundary `atomic_write_text` draws when it writes `text` verbatim. It is
    also what makes every routed site a pure substitution, so the bytes on disk
    are identical to what the raw `open` produced.

    CHANGED BY A RULING, 2026-08-15 (M4-δ) - the Ruling-14 precedent, and the
    one that needs its reasoning read rather than skimmed. Recorded verbatim:

        OLD (Ruling 78, 2026-08-09):
            durable_append_text(target, "one")
            durable_append_text(target, "two")
            assert target.read_text(encoding="utf-8") == "onetwo"
        NEW (M4-δ):
            ... the same two appends now produce "one\\ntwo", and the pin's own
            claim is asserted on a WELL-FORMED sequence instead.

    **RES.2 IS NOT WEAKENED AND ITS CLAIM IS RE-ASSERTED BELOW, HARDER.** What
    the old body measured was the funnel writing no separator - but it measured
    it by appending TWO LINES THAT WERE NOT LINES, i.e. by driving the exact
    torn-boundary state M4-δ exists to repair. The property res.2 actually
    rules is that **the funnel adds nothing to the CALLER'S CONTENT**, and that
    is now pinned where it means something: across well-formed appends the bytes
    are unchanged, and the prefix can never fire.

    THE LINE M4-δ DRAWS: the caller still owns the FORMAT (its own trailing
    newline, never added here); the funnel owns the BOUNDARY (an append begins
    at column 0). A prefix that fires only when the previous write was TORN is
    filesystem integrity of the same standing as the `fsync` beside it - it
    chooses nothing about any record's bytes. The torn fragment is still refused
    by floor semantics; it simply stops taking the next record down with it.
    """
    from src.utils.atomic_write import durable_append_text

    # THE CLAIM RES.2 ACTUALLY MAKES: no separator is added to the caller's
    # content. Driven on WELL-FORMED lines, which is what every routed site
    # writes, and asserted as exact bytes.
    target = tmp_path / "raw.log"
    durable_append_text(target, "one\n")
    durable_append_text(target, "two\n")
    assert target.read_text(encoding="utf-8") == "one\ntwo\n", (
        "the helper appended a separator it was not given - the line format is "
        "the owner's decision, not this primitive's")

    # AND WITHOUT A TRAILING NEWLINE THE CONTENT IS STILL VERBATIM: a single
    # append to an empty file takes no prefix, so the caller's bytes are the
    # file's bytes.
    bare = tmp_path / "bare.log"
    durable_append_text(bare, "no newline here")
    assert bare.read_text(encoding="utf-8") == "no newline here"


def test_b_the_helper_creates_its_parent_directory(tmp_path):
    """PIN (b). Complete as a primitive, for the site nobody has written yet."""
    from src.utils.atomic_write import durable_append_text

    target = tmp_path / "deep" / "deeper" / "ledger.jsonl"
    durable_append_text(target, "line\n")
    assert target.read_text(encoding="utf-8") == "line\n"


def test_b_a_write_failure_raises_and_the_site_decides(tmp_path, monkeypatch):
    """PIN (b) / res.2. THE HELPER RAISES; IT DOES NOT CHOOSE.

    Whether a failed append is fatal is the SITE's ruling and always was: the
    ledgers whose write GATES the thing recorded (Rulings 58/61) refuse, and
    the best-effort forensic writers catch and record (Ruling 11 - the observer
    never gates the observed). A helper that swallowed the error would take
    that decision away from all twelve of them at once.
    """
    from src.utils.atomic_write import durable_append_text

    def boom(fd):
        raise OSError("device is gone")

    monkeypatch.setattr(os, "fsync", boom)
    with pytest.raises(OSError):
        durable_append_text(tmp_path / "x.jsonl", "line\n")


def test_b_the_never_raise_wrappers_still_hold(monkeypatch):
    """PIN (b) / res.2, THE OTHER SIDE OF THE SAME CONTRACT, DRIVEN FOR REAL.

    Ruling 11: a logging failure must not disable a safety suppression. The
    helper raises, so the never-raise wrappers now cover one more failure mode -
    and this drives the REAL structural-violation path with the fsync broken,
    rather than asserting the wrapper's shape.
    """
    def boom(fd):
        raise OSError("device is gone")

    core = AureaCore()
    monkeypatch.setattr(os, "fsync", boom)

    core._flush_structural_violation({"type": "CodexWriteViolation",
                                      "message": "a guard fired"})

    assert core.structural_log_failures, (
        "an fsync failure must land on the failure ledger, exactly as an open "
        "failure already did")
    assert "OSError" in core.structural_log_failures[-1]["error"], (
        "and the recorded failure must be the real one, not a swallowed shrug")


# =====================================================================
# (c) THE ROUTING IS UNEXECUTABLE-BY-OMISSION
# =====================================================================

def _append_opens():
    """Every mode-`"a"` `open` in `src/`, by AST, tagged with its scope.

    RE-DERIVED BY INSTRUMENT, NEVER INHERITED FROM THE HANDOFF. The census's
    enumeration is a CLAIM; this is the measurement, and the ruling makes a
    disagreement between them a STOP rather than something to reconcile.

    RGLOB, so a module added next year is covered by construction rather than
    by someone remembering to extend a list (Ruling 70's instrument lesson).
    """
    found = []
    for path in _src_files():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        funcs = [(n.lineno, n.end_lineno, n.name) for n in ast.walk(tree)
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = (getattr(node.func, "id", None)
                    or getattr(node.func, "attr", None))
            if name != "open":
                continue
            modes = [a.value for a in node.args[1:]
                     if isinstance(a, ast.Constant)]
            modes += [k.value.value for k in node.keywords
                      if k.arg == "mode" and isinstance(k.value, ast.Constant)]
            if any("a" in str(m) for m in modes):
                scope = [f for f in funcs if f[0] <= node.lineno <= f[1]]
                scope = (sorted(scope, key=lambda f: f[1] - f[0])[0][2]
                         if scope else "<module>")
                found.append((path.relative_to(REPO).as_posix(), node.lineno,
                              scope))
    return found


def test_c_the_only_append_open_in_src_is_the_funnels_own():
    """PIN (c). THE ROUTING IS A PROPERTY, NOT A DISCIPLINE.

    Twelve disciplined sites are twelve chances to forget; one funnel is a
    property, and it stays true for the thirteenth site nobody has written yet -
    `atomic_write_json`'s own argument for putting `allow_nan=False` at the
    funnel, applied one guarantee over.
    """
    offenders = [site for site in _append_opens() if site[0] != ATOMIC_WRITE]
    assert offenders == [], (
        "an append bypassed the durability funnel: " + repr(offenders) +
        ". Route it through `durable_append_text` - a raw append returns "
        "before the bytes are on the device.")


def test_c_the_funnel_itself_still_appends():
    """PIN (c), THE CONTROL. The scan above is satisfied by a tree with NO
    appends at all, so the one legitimate site is asserted PRESENT - otherwise
    deleting the helper's own `open` would pass the census."""
    own = [site for site in _append_opens() if site[0] == ATOMIC_WRITE]
    assert len(own) == 1, "expected exactly one, the helper's: " + repr(own)
    assert own[0][2] == "durable_append_text"


def test_c_every_routed_site_is_still_a_site():
    """PIN (c). THE COUNT, so a silently DELETED append is not read as a
    successfully routed one.

    Twelve modules held an append when this ruling opened and twelve held a
    call to the funnel at its close. A census that only FORBIDS raw appends is
    equally satisfied by a store that stopped recording altogether.

    **SIXTEEN AS OF M6-α (2026-08-15).** The proposition ledger is the
    sixteenth - the World Model domain's first member. Same branch of the
    message below, taken as written: the count moved because a record started
    being kept.

    ~~**FIFTEEN AS OF M4-alpha (2026-08-15), old counts kept above.** The
    acquisition ledger is the fifteenth - the boundary record, and the first
    store whose append is on the pipeline's own hot path since the ancestry
    ledger's. Same branch of the message below, taken exactly as written: the
    count moved because a record started being kept.~~

    ~~**FOURTEEN AS OF M3-A (2026-08-13), old count kept in the sentence
    above.** The obligation ledger and the episode record are the thirteenth and
    fourteenth - the two Kernel stores of the pivot's first construction. This
    is the "A NEW one is fine and welcome" branch of the message below, taken
    exactly as written: the count moved because two records started being kept,
    not because one stopped.~~
    """
    callers = set()
    for path in _src_files():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call)
                    and getattr(node.func, "id", None) == "durable_append_text"):
                callers.add(path.relative_to(REPO).as_posix())
    assert len(callers) == 16, (
        "sixteen append sites are routed through Ruling 78's funnel; the tree "
        "now has " + str(len(callers)) + ": " + repr(sorted(callers)) + ". A "
        "NEW one is fine and welcome - update this count. A MISSING one means a "
        "record stopped being kept.")


# =====================================================================
# (e) THE TWO STORES TELL THE SAME STORY ACROSS AN UNCLEAN RESTART
# =====================================================================

def test_e_the_epoch_record_and_the_doctrine_store_agree_after_restart():
    """PIN (e). THE RULING'S SUBJECT, STATED AS AGREEMENT RATHER THAN LOSS.

    `sae_epoch.json` has been durable at the moment of SPENDING since Ruling 34.
    So at base the durable record said "a mutation of X was executed" while the
    durable Codex said "X is alive and has never fallen" - two stores, each
    internally consistent, disagreeing about whether an event happened.

    THIS IS NOT PIN (d) TWICE. (d) asks whether the successor survived; this
    asks whether the two files can be read TOGETHER without contradiction, which
    is the thing that was actually broken and the thing a future divergence
    detector (registered by res.4.iii) would be built to notice.
    """
    core = AureaCore()
    ancestor = _a_live_doctrine(core)
    successor = _mutate(core, ancestor, ancestor + "::r78")

    resumed = AureaCore()

    assert resumed.sae.history, "the epoch record did not survive at all"
    record = resumed.sae.history[-1]
    assert record.target_id == ancestor

    # THE AGREEMENT: what the epoch file says was spent, the doctrine file must
    # show as having happened - the ancestor fallen AND the successor standing.
    assert ancestor in resumed.codex.fossils, (
        "the durable epoch record says '" + ancestor + "' was mutated; the "
        "durable Codex still holds it live. The two stores disagree, which is "
        "the whole subject of Ruling 78.")
    assert resumed.codex.get(successor) is not None
    assert resumed.sae.epoch_count >= 1, (
        "a spent slot that does not survive would be the DIVERGENCE POINTING "
        "THE OTHER WAY - content held against an unspent budget, i.e. a free "
        "mutation (res.4.i names this as the direction that must never happen)")


# =====================================================================
# (g) RULING 76'S JOINS, AND THE REBORN-ID HAZARD
# =====================================================================

def _clm_ids_in_durable_records(core):
    """Every `CLM-` id reachable from a DURABLE record, after a restart.

    Scars and suspensions both carry Ruling 76's `claim_id`, and both stores
    are durable - so these are exactly the ids that could still be pointed at
    by something on disk when the mint next runs.
    """
    ids = {getattr(s, "claim_id", None) for s in core.scar_core.all_scars()}
    for entry in getattr(core.black_sphere, "entries", {}).values():
        ids.add(getattr(entry, "claim_id", None))
    return {i for i in ids if i}


def test_g_a_joined_claim_survives_and_its_id_is_never_reborn():
    """PIN (g). THE SHARPEST CONSEQUENCE IN THE RULING, WITNESSED DEAD.

    A minted id escapes into records that ARE fsync'd - a suspension snapshot,
    one of Ruling 76's `claim_id` joins. Its own ledger line dies in the page
    cache. The mint's floor re-derives LOWER at restart, and the id is REBORN
    naming a DIFFERENT perception while the durable joins still point at it.
    Ruling 69's letter holds - the line never reached disk - and its intent
    does not.

    BOTH HALVES ARE MEASURED, because either alone is satisfiable by a broken
    tree: that the durable joins still RESOLVE, and that the next mint sits
    strictly ABOVE every id any durable record carries.
    """
    core = AureaCore()
    for claim in ("Honesty is pointless.",
                  "This statement is false.",
                  "Fracture Carried is false."):
        core.process_input(claim)

    joined = _clm_ids_in_durable_records(core)
    assert joined, "precondition: the cycles produced at least one durable join"

    resumed = AureaCore()

    # HALF ONE: the joins survived the restart with their referents.
    surviving = _clm_ids_in_durable_records(resumed)
    assert joined <= surviving, (
        "a durable join lost its record across a restart: " +
        repr(sorted(joined - surviving)))

    # HALF TWO: the next perception may not wear an id a durable record already
    # names. Driven through the REAL door, so the real mint answers.
    result = resumed.process_input("A claim after the restart.")
    minted = result["claim_id"]
    assert minted not in surviving, (
        "the mint REBORN '" + minted + "', an id a durable record already "
        "names - so a join now points at a different perception than the one "
        "it recorded")
    ordinal = int(minted.rsplit("-", 1)[1])
    assert all(ordinal > int(i.rsplit("-", 1)[1]) for i in surviving), (
        "the new ordinal must sit strictly above every id on disk; got " +
        minted + " against " + repr(sorted(surviving)))


# =====================================================================
# (h) THE TWO DELIBERATE ABSENCES
# =====================================================================

def _codex_method(name):
    tree = _tree("src/doctrine/codex.py")
    cls = next(n for n in ast.walk(tree)
               if isinstance(n, ast.ClassDef) and n.name == "Codex")
    return next(n for n in cls.body
                if isinstance(n, ast.FunctionDef) and n.name == name)


def _saves_in(method):
    return [n for n in ast.walk(method)
            if isinstance(n, ast.Call)
            and getattr(n.func, "attr", None) == "save_to_file"]


def test_h_fossilize_deliberately_does_not_save():
    """PIN (h). THE HONEST UNIT OF DURABILITY IS THE EVENT, NOT THE METHOD.

    Fossilization is ALWAYS the mid-event half of a pair: `mutate_doctrine`
    fossilizes the ancestor and then commits the successor. A save here would
    publish that intermediate state - ancestor fallen, successor absent - as a
    perfectly well-formed file, so a crash between the two writes would leave a
    durable record of a doctrine that fell and was replaced by nothing.

    Nothing is lost by waiting: `save_to_file` snapshots fossils and active
    doctrines TOGETHER, so `commit`'s save carries this write too.
    """
    assert _saves_in(_codex_method("fossilize")) == [], (
        "`fossilize` must not checkpoint - it is the mid-event half of a pair, "
        "and a save here publishes a torn mutation as a well-formed file")


def test_h_seed_deliberately_does_not_save():
    """PIN (h). THE TRACKED SEED IS ALREADY THIS WRITE'S DURABLE RECORD.

    Ruling 32 split the seed away from the write path; a runtime snapshot at
    genesis would record nothing that was not already on disk and would put a
    WRITER back on the genesis path. A first run that has never mutated must
    leave `data/runtime/doctrines.json` ABSENT - the difference between "no
    runtime state" and "runtime state identical to the seed" is one a loader
    can read, and it must stay readable.
    """
    assert _saves_in(_codex_method("seed")) == [], (
        "`seed` must not checkpoint - the tracked seed IS the durable record "
        "of genesis (Ruling 32)")


def test_h_a_fresh_core_that_never_mutated_writes_no_doctrine_snapshot():
    """PIN (h), THE BEHAVIOURAL HALF - the absence above, observable.

    Without this, a save added to `seed` would be caught by an AST pin alone,
    and an AST pin is exactly what someone edits when it is in the way. This
    one fails on the consequence instead.
    """
    core = AureaCore()
    assert not Path(core.codex.runtime_path).exists(), (
        "construction alone wrote a runtime doctrine snapshot; genesis has no "
        "writer (Ruling 32) and this ruling did not give it one")


def test_h_commit_is_the_one_that_saves():
    """PIN (h), THE CONTROL. The two absences above are satisfied by a Codex
    that saves NOWHERE - which is precisely the tree Ruling 78 found. The
    terminal write must be present, and present exactly once."""
    saves = _saves_in(_codex_method("commit"))
    assert len(saves) == 1, (
        "`commit` is the terminal write of every doctrine event - mutation, "
        "birth and reversion all end there - so it saves, once")


# =====================================================================
# (i) THE ORDERING LAW
# =====================================================================

def test_i_authority_then_content_then_record(monkeypatch):
    """PIN (i) / res.4.i. THE ORDER IS THE GUARANTEE, SO IT IS PINNED AS ORDER.

        A crash may lose CONTENT against a durably spent budget - conservative,
        detectable, and recoverable by re-deciding. It may NEVER hold content
        against an UNSPENT budget, which is a free mutation: the ceiling
        silently refunded by a well-timed process death.

    Ruling 34 made the spend durable at the moment of spending; Ruling 47 made
    the record durable at the moment of the mutation; this ruling slots the
    CONTENT save between them. The existing code needed no reordering - what it
    needed was for the order to become a pinned law rather than an accident of
    where three unrelated rulings happened to land their writes.

    INSTRUMENTED RATHER THAN READ FROM SOURCE: the three writes live in two
    different modules and the sequence is a runtime fact, so an AST reading of
    `mutate_doctrine` alone would miss the save that happens one frame down
    inside `Codex.commit`.
    """
    core = AureaCore()
    ancestor = _a_live_doctrine(core)

    events = []
    real_persist = type(core.sae)._persist
    real_save = Codex.save_to_file

    def persist_spy(self):
        events.append(("epoch_persist", len(self.history)))
        return real_persist(self)

    def save_spy(self):
        events.append(("codex_save", None))
        return real_save(self)

    monkeypatch.setattr(type(core.sae), "_persist", persist_spy)
    monkeypatch.setattr(Codex, "save_to_file", save_spy)

    _mutate(core, ancestor, ancestor + "::r78")

    names = [name for name, _ in events]
    assert "codex_save" in names, "the content save did not happen at all"
    assert names.count("codex_save") == 1, (
        "one save per EVENT is the whole of res.3; got " + repr(names))

    save_at = names.index("codex_save")

    # AUTHORITY BEFORE CONTENT: every persist before the save is a SPEND - it
    # happens while the history record does not yet exist.
    assert save_at > 0, (
        "the content was written before the budget was durably spent - a crash "
        "here holds a mutation against an unspent ceiling, which is a free "
        "mutation and the one direction res.4.i forbids")
    assert all(depth == 0 for _, depth in events[:save_at]), (
        "a pre-save persist already carried a history record: " + repr(events))

    # CONTENT BEFORE RECORD.
    after = events[save_at + 1:]
    assert after, "the mutation record was never persisted after the content"
    assert after[0][0] == "epoch_persist" and after[0][1] == 1, (
        "the first write after the content save must be the RECORD of it: " +
        repr(events))


# =====================================================================
# (j) THE add_scar CALLER CENSUS
# =====================================================================

def test_j_add_scar_has_exactly_one_caller_and_it_is_the_owner():
    """PIN (j). THE CENSUS THE RULING REQUIRED BEFORE THE SAVE WAS ADDED, KEPT
    AS A STANDING GUARD.

    `add_scar` now checkpoints, so every caller pays a snapshot. That is correct
    for the ONE caller the tree has - `form_scar`, the owner-side execution of
    every scar REQUEST in the system (Ruling 1), which is what makes the save
    cover every requester BY CONSTRUCTION rather than by each one remembering.

    A SECOND CALLER IS A STOP, NOT A MERGE CONFLICT. A bulk or loading path
    calling `add_scar` per record would snapshot the whole store per scar, and
    the honest answer to that is a ruling about where the checkpoint belongs -
    not a quiet edit to this number.
    """
    callers = []
    for path in _src_files():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        funcs = [(n.lineno, n.end_lineno, n.name) for n in ast.walk(tree)
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call)
                    and getattr(node.func, "attr", None) == "add_scar"):
                scope = [f for f in funcs if f[0] <= node.lineno <= f[1]]
                scope = (sorted(scope, key=lambda f: f[1] - f[0])[0][2]
                         if scope else "<module>")
                callers.append((path.relative_to(REPO).as_posix(), scope))

    assert callers == [("src/filtration/scar_logic_core.py", "form_scar")], (
        "the `add_scar` caller census changed: " + repr(callers) + ". Ruling "
        "78 res.3 makes an unenumerated caller a STOP - report it rather than "
        "adjusting this pin.")


def test_j_form_scar_is_durable_through_the_owners_door(tmp_path):
    """PIN (j), the behavioural half: the census exists to justify the save, so
    the save is witnessed at the door the census names."""
    store = ScarLogicCore(filepath=str(tmp_path / "scars.json"))
    store.scars.clear()
    formed = store.form_scar(origin="test_ruling78", description="a wound")

    reopened = ScarLogicCore(filepath=str(tmp_path / "scars.json"))
    assert [s.id for s in reopened.all_scars()] == [formed.id]
