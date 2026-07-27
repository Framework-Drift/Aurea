"""
Ruling 35 - THE LOADER ROUTES BY STATUS.

    A fallen doctrine loads as a FOSSIL, never as live, and Ruling 18's guard
    must hold against the REAL SEED - not only against doctrines felled at
    runtime.

THE DEFECT, three layers deep. The seed `data/doctrines.json` is a FLAT LIST of
eight, carrying `⊗ Doctrine-0` (status `fallen`) and `Doctrine-0` (status
`locked`). `Codex.load_from_file`'s flat branch read `active, fossils =
(data, [])`, so both landed in `self.doctrines` and `self.fossils` loaded EMPTY.
DRPAS then iterated the whole live map with zero status checks - and its
stagnation trigger makes an unexamined doctrine a MUTATION-PRESSURE candidate,
so **the fallen doctrine could be nominated for evolution.**

The layer the outside audit missed, and the reason this is a ruling rather than
a tidy-up: **Ruling 18's re-fossilization guard checks `if doctrine.id in
self.fossils`, and fossils was empty.** A commit over `⊗ Doctrine-0` did not
raise. Ruling 18 was structurally VACUOUS against the actual seed - it protected
doctrines felled at runtime and had never once protected the founding fossil it
was written about.

WHY NO TEST CAUGHT IT: every test loads the seed through the same loader, so the
misrouting WAS the fixture's baseline. That is Ruling 32's lesson in a third
position - **a defect in the load path is invisible to every test that loads.**
These pins therefore assert against the REAL seed file, not a synthetic one.

THE FIX IS ENTIRELY IN HOW THE SEED IS READ. The seed is read-only input
(Ruling 32) and stays byte-identical; no migration, no new status vocabulary.
"""

from __future__ import annotations

import json
from datetime import datetime

import pytest

from src.doctrine.codex import Codex, CodexWriteViolation
from src.doctrine.dee import DRPAS
from src.expansion.sae import SAE, MutationClass
from src.utils.models import Doctrine

# Written as an escape rather than the literal glyph: this id is U+2297 CIRCLED
# TIMES, and a pin that silently stopped matching because an editor normalised a
# character would be worse than no pin.
FALLEN_ID = "⊗ Doctrine-0"
LOCKED_ID = "Doctrine-0"

# The real seed's composition, asserted so the routing is pinned to the ACTUAL
# file rather than to a fixture's idea of it.
SEED_LIVE = 6
SEED_FOSSIL = 1
SEED_LOCKED = 1


@pytest.fixture
def seeded():
    """A Codex over the REAL seed.

    No `filepath=`: that is the explicit single-path form. The default
    constructor reads the tracked seed and writes only to `runtime_path`, which
    `conftest.py` has already redirected into tmp.
    """
    return Codex()


# =========================================================================
# RESOLUTION 1 - THE FLAT BRANCH ROUTES BY STATUS
# =========================================================================

def test_the_fallen_doctrine_loads_as_a_fossil(seeded):
    """DEFECT WATCHED: `active, fossils = (data, [])`.

    `⊗ Doctrine-0` is the founding fossil. Loading it live is not a cosmetic
    misfiling - it is a fallen belief presented to every reader as a current one.
    """
    assert FALLEN_ID in seeded.fossils, (
        f"{FALLEN_ID!r} did not load as a fossil - the flat branch is still "
        "routing the whole seed into the live map")
    assert FALLEN_ID not in seeded.doctrines, (
        f"{FALLEN_ID!r} is LIVE. A fallen doctrine is readable as history, "
        "never as belief")
    assert seeded.get(FALLEN_ID) is None, "the live accessor returns a fallen doctrine"
    assert seeded.get_fossil(FALLEN_ID) is not None, "the fossil accessor cannot see it"


def test_the_locked_doctrine_stays_live_and_readable(seeded):
    """RESOLUTION 2's other half, and the one it would be easy to overshoot.

    `locked` is NOT `fallen`. Doctrine-0 "Collapse-Bearing Truth" is live
    doctrine that may not be MUTATED - excluding it from a mutation scan is the
    whole ask, and deleting it from the live map would be a different bug
    wearing this ruling's authority.
    """
    doctrine = seeded.get(LOCKED_ID)
    assert doctrine is not None, "the locked doctrine vanished from the live store"
    assert doctrine.status == "locked"
    assert LOCKED_ID not in seeded.fossils, "locked is not fallen - do not fossilize it"


def test_the_real_seed_routes_six_live_one_fossil_one_locked(seeded):
    """REGRESSION, against the REAL file.

    Pinned to the actual seed so a future edit to `data/doctrines.json` that
    changes the mix has to come past this test rather than silently through it.
    """
    assert len(seeded.fossils) == SEED_FOSSIL
    assert len(seeded.doctrines) == SEED_LIVE + SEED_LOCKED
    assert len(seeded.active()) == SEED_LIVE, (
        "active() must count only status=='active' - locked is live but not active")

    statuses = sorted(d.status for d in seeded.doctrines.values())
    assert statuses.count("locked") == SEED_LOCKED
    assert "fallen" not in statuses, "a fallen doctrine is still in the live map"


def test_the_seed_file_itself_is_not_migrated():
    """RESOLUTION 3. The fix is in the READ, not the file.

    DEFECT WATCHED: "fixing" this by rewriting the seed into the nested format.
    The seed is READ-ONLY INPUT (Ruling 32) and has no writer; migrating it
    would put a write path back on a tracked identity store.
    """
    raw = json.loads((Codex().seed_path).read_text(encoding="utf-8"))
    assert isinstance(raw, list), (
        "the seed was migrated to the nested format - Ruling 32 gives it no writer")
    assert any(d["status"] == "fallen" for d in raw), (
        "the fallen entry was edited out of the seed instead of routed on read")


# =========================================================================
# THE LAYER THE AUDIT MISSED - RULING 18 ARMED AGAINST THE REAL SEED
# =========================================================================

def test_committing_over_the_founding_fossil_raises(seeded, tmp_path):
    """THE PIN THAT PROVES THE HAZARD.

    Ruling 18: a ⊗-fossilized id can never be re-committed. The guard reads
    `if doctrine.id in self.fossils` - and against the real seed `fossils` was
    EMPTY, so this commit SUCCEEDED. The guard had never once protected the
    founding fossil it was written about.

    Watched RED against pre-fix code, where the write lands silently.
    """
    sae = SAE(codex=seeded)
    auth = sae.authorize(MutationClass.MUTATE_DOCTRINE, "scar-1", FALLEN_ID)

    with pytest.raises(CodexWriteViolation):
        seeded.commit(
            Doctrine(id=FALLEN_ID, name="resurrected", created_at=datetime.now()),
            auth,
        )

    assert seeded.get(FALLEN_ID) is None, (
        "a fallen doctrine came back to life through a commit over its own id")


# =========================================================================
# RESOLUTION 2 - THE MUTATION SCAN EXCLUDES NON-ACTIVE
# =========================================================================

def _forcing_signals():
    """Signals that WOULD flag both doctrines if they were scanned.

    THIS IS LOAD-BEARING. With no signals the real seed produces flags only for
    the two doctrines carrying >=3 scar links, and every seed entry has
    `is_seed=True` so the stagnation trigger never fires - so a no-signal
    version of these pins would pass VACUOUSLY, before and after the fix.
    """
    return {FALLEN_ID: {"drpe": True, "pressure": 0.9},
            LOCKED_ID: {"drpe": True, "pressure": 0.9}}


def test_drpas_does_not_flag_the_fallen_doctrine(seeded):
    """DEFECT WATCHED: DRPAS nominating a FALLEN doctrine for evolution.

    Its stagnation trigger treats an unexamined doctrine as mutation pressure,
    so an unscanned-status map does not merely mis-report - it feeds a fallen
    belief into the doctrine-evolution path.
    """
    flags = DRPAS().scan(seeded, _forcing_signals())
    flagged = {f.doctrine_id for f in flags}

    assert FALLEN_ID not in flagged, (
        f"DRPAS flagged {FALLEN_ID!r} for mutation pressure - it is FALLEN")


def test_drpas_does_not_flag_the_locked_doctrine(seeded):
    """§10.G's principle one layer down: a locked doctrine is not a mutation
    candidate. It stays readable; it is simply not scanned."""
    flags = DRPAS().scan(seeded, _forcing_signals())
    flagged = {f.doctrine_id for f in flags}

    assert LOCKED_ID not in flagged, (
        f"DRPAS flagged {LOCKED_ID!r} - locked doctrine is excluded from "
        "mutation scanning")


# =========================================================================
# THE SECOND VACUOUS GUARD - exposed, not created, by this ruling
# =========================================================================

def test_a_seed_fossil_is_not_a_live_anchor_collapse():
    """RULING 35 CONSEQUENCE. FLAGGED - architect-approved in session, owed a
    manifest ruling of its own.

    `compass._north()` appended EVERY fossil to `collapsed`, and any non-empty
    `collapsed` becomes an `anchor_collapse` trigger at pressure 1.0, which GSR
    cascades into a total output block. That was harmless ONLY because
    `fossils` was always empty - the very defect Ruling 35 closes.

    THE DEFECT PREDATES THIS RULING: the first time SAE fossilized a doctrine
    at runtime - the first time AUREA successfully EVOLVED - she would have
    gone permanently mute. Ruling 35 moves the trigger from first-mutation to
    BOOT, which is how it surfaced.

    A seed fossil is founding history, not ground collapsing underneath her.
    """
    from src.aurea_core import AureaCore

    core = AureaCore()
    north = core.compass._north()

    assert north.collapsed == [], (
        f"the founding fossil {north.collapsed} reads as a live anchor "
        "collapse - AUREA is permanently mute from boot")

    result = core.process_input("A claim that should reach an ordinary answer.")
    assert result["output_blocked"] is False, (
        "output is blocked on a clean pipeline pass - she cannot speak at all")


def test_a_runtime_fossil_IS_still_an_anchor_collapse(tmp_path):
    """THE OTHER HALF, AND THE ONE THAT MATTERS MOST.

    DEFECT WATCHED: "fixing" the above by disabling anchor collapse. A doctrine
    that falls UNDER her is exactly the event the compass exists to catch, and
    a narrowing that swallowed it would be far worse than the bug it replaced -
    it would silently remove a safety trigger while looking like a bug fix.
    """
    from src.expansion.sae import SAE, MutationClass
    from src.identity.compass import CompassStabilityEngine

    codex = Codex(filepath=str(tmp_path / "doctrines.json"))
    sae = SAE(codex=codex)

    live = Doctrine(id="D-live", name="ground", scar_links=["scar-1"],
                    created_at=datetime.now())
    codex.commit(live, sae.authorize(MutationClass.MUTATE_DOCTRINE, "scar-1", "D-live"))
    codex.fossilize("D-live",
                    sae.authorize(MutationClass.MUTATE_DOCTRINE, "scar-1", "D-live"),
                    reason="fell under her")

    assert "D-live" in codex.fossils
    north = CompassStabilityEngine(codex=codex)._north()
    assert north.collapsed == ["D-live"], (
        "a doctrine fossilized AT RUNTIME no longer registers as an anchor "
        "collapse - the narrowing swallowed the real trigger")


def test_drpas_still_scans_every_active_doctrine(seeded):
    """The exclusion is surgical, not a blanket narrowing.

    DEFECT WATCHED: excluding so much that the scan stops working. Every ACTIVE
    doctrine must still be reachable by pressure.
    """
    signals = {d.id: {"drpe": True, "pressure": 0.9} for d in seeded.active()}
    flagged = {f.doctrine_id for f in DRPAS().scan(seeded, signals)}

    assert flagged == {d.id for d in seeded.active()}, (
        "DRPAS stopped seeing active doctrines")
    assert len(flagged) == SEED_LIVE
