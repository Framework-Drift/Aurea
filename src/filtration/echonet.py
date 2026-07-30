"""
echonet.py - EchoNet: AUREA's front-line collapse filtration system.

Canon: AUREA_Lexicon_v4.0 §I.3 - "Filters all input claims to determine if they survive
collapse, enter suspension, or are rejected/scarred. Uses SIX COLLAPSE NETS (logic,
intuition, empirical, resonance, ethics, convergent elimination) and adjusts thresholds
dynamically based on scar weighting, doctrine pressure, and compass drift."

    Verdict classes:  Confirmed → Codex
                      Suspended → Veiled Thread
                      Scarred   → Collapse Archive
                      Paradox   → Black Sphere

WHY THIS FILE EXISTED AS 0 BYTES
--------------------------------
`echonet.py` was an empty stub with a stale `.pyc` beside it - it once had content and was
emptied. Because `aurea_core` imports EchoNet at module level, **AureaCore could not be
constructed at all**. The pipeline was unrunnable, and had been for some time.

⚠ SPECULATION FLAG - READ BEFORE TRUSTING THIS MODULE
------------------------------------------------------
The SIX NETS and the four verdict classes are CANON. The detection heuristics inside each
net are **COINED** - the corpus names the nets and never says how any of them decides.
What is implemented here is a deterministic, legible first pass: pattern and structure
checks, no model, no guessing.

They are deliberately CONSERVATIVE about claiming to have found a contradiction. A filter
that over-reports collapse manufactures scars, and a scar is supposed to be the mark of
something AUREA actually survived - not something a regex disliked. Real filtration needs
EchoTrace (distortion detection) and CPA (context/intent), both still stubs. Until then,
this net set is a scaffold that fails toward SUSPENSION, not toward false collapse.

    A claim that is merely UNCERTAIN must not be scarred. Uncertainty is suspended.
    Only a claim that cannot be held without contradiction gets to leave a mark.

DOCKET H (Stage 1, 2026-07-27) - EVERY NET NOW STATES WHAT IT COUNTED
----------------------------------------------------------------------
Each `NetResult` carries a `NetEvidence` (see `net_evidence.py`): a tally of how
many pieces of evidence bore on the net and how many DISTINCT sources they came
from. The fields exist so that one-of-one and one-thousand-of-one-thousand do
not look alike - a LEGIBILITY requirement, never a scoring one.

    A COUNT REPORTS. IT NEVER GATES. No threshold, no combination rule, no
    weighting, no derived scalar - here or in any consumer (section 9 bar 5).

The nets are keyword/regex shallow, and the honest consequence is that FOUR OF
THE SIX HAVE NOTHING TO COUNT. They say so, each naming what is missing, rather
than reporting a zero that would imply AUREA had searched. The per-net inventory
sits directly above the net definitions.

STAGE 1 IS ORGAN-LOCAL: nothing downstream consumes this yet, and
`TruthPacket.evidence_refs` / `scar_lineage` are deliberately NOT populated.
Nothing about `survived`, `pressure`, `note`, or any verdict changed.

RULING 49 (2026-07-29) - STAGE 3 EXISTS: THE DOCTRINE + SCARLINE OVERLAY
-------------------------------------------------------------------------
Canon 0:121-178 describes FIVE-STAGE filtration, and Stage 3 is named:
"Doctrine + Scarline Overlay (resonance vs fracture)". Until this ruling the
file implemented Stage 2 (the six nets) and nothing else - a claim was tested
for internal coherence and against old wounds, and never against WHAT AUREA
ACTUALLY HOLDS.

    "Truth is not what appears coherent - it is what can be carried
     through collapse."

WHAT WAS ACTUALLY ON DISK, stated precisely because the shorter version of it
is wrong: `doctrine_spine` was NOT unconsulted. `_threshold` has always called
`load_bearing(min_scars=1)` and tightened the bar for a claim brushing a
load-bearing doctrine, and that path FIRES (verified by execution: it moves the
threshold 0.75 -> 0.70 on a real seed doctrine). What did not exist was any
doctrine consult IN THE NET LAYER. The spine could make AUREA judge a claim more
strictly; it could not make her notice that the claim CONTRADICTED something she
believes.

The ethics net is where that absence surfaced. Its note asserts the claim
"requires abandoning a load-bearing doctrine" while the net never reads the
doctrine store - one net trying to be the overlay with a regex. Docket H
reported it and declined to repair it. Resolution (2) below is that repair.

WHAT THE OVERLAY IS, AND WHAT IT IS DELIBERATELY NOT
------------------------------------------------------
IT IS NOT A SEVENTH NET. Stage 2 is the six nets; Stage 3 is a separate stage,
and `CollapseResult.nets` still holds exactly six. Folding the overlay in as a
seventh would conflate two canon stages, and `OverlayResult` HAS NO `survived`
FIELD so it cannot be dropped into that list even by accident - the Ruling 33
shape, where the wrong thing is unwritable by SCOPE rather than by discipline.

IT DOES NOT OWN A VERDICT. It contributes PRESSURE (fracture) or records SUPPORT
(resonance) into the existing computation, and the verdict vocabulary is
untouched.

    AND IT CANNOT SCAR A CLAIM BY ITSELF - structurally, not by convention.
    Its maximum pressure is SUSPENSION_FLOOR (0.35); the threshold's own floor
    is 0.40 (`max(0.4, ...)` in `_threshold`). So overlay-only pressure can
    reach SUSPENDED and can never reach SCARRED. That property falls out of two
    magnitudes that were already here; it is not a rule anyone has to remember.

MAGNITUDES: NOTHING IS COINED. The two pressures are the file's OWN existing
constants, reused for what they already mean:

    referential fracture -> SUSPENSION_FLOOR (0.35)  the claim names a doctrine
                            and denies it. "Below this a claim simply passes" -
                            this one does not pass. It suspends.
    lexical fracture     -> SUSTAINED_STRAIN (0.3)   a weaker instrument, and it
                            sits exactly at the level that counts as strain
                            without reaching the suspension floor.
    resonance            -> 0.0                      support is never pressure.

PATTERNS ARE COINED, and declared as such below with the rest of them. They are
the same class the logic net already uses (see the SPECULATION FLAG), applied
against doctrine name/description, and they are deliberately CONSERVATIVE in
both directions - a claim that both affirms and denies is recorded AMBIGUOUS
with zero pressure rather than guessed at.

GROUND OR ABSTAIN. With no spine handle the overlay reports NOT_COUNTABLE with
the reason and contributes nothing. With a spine and no match it reports
NONE_FOUND - a real instrument ran over the real doctrine store. Those are
different zeroes (see `net_evidence.py`) and the overlay is the second
instrument in this layer that can tell them apart.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple

from src.filtration.net_evidence import (
    EVIDENCE_UNREPORTED,
    Countability,
    EvidenceRef,
    NetEvidence,
)
from src.utils.models import Echo, Scar


class Verdict(Enum):
    """Canon verdict classes (Lexicon §I.3)."""
    CONFIRMED = "confirmed"    # survived collapse → may inform Codex
    SUSPENDED = "suspended"    # unresolved → Veiled Thread. NOT a failure.
    SCARRED = "scarred"        # collapsed → Collapse Archive
    PARADOX = "paradox"        # cannot be held at all → Black Sphere


# Base collapse threshold. Pressure at or above this fails the claim.
BASE_THRESHOLD = 0.75          # COINED
SUSPENSION_FLOOR = 0.35        # COINED: below this, a claim simply passes


# ---------------------------------------------------------------------------
# STAGE 3 PATTERNS (Ruling 49). COINED - the same class the logic net uses.
# ---------------------------------------------------------------------------
# NO NEW MAGNITUDE IS INTRODUCED BY THIS RULING. These are patterns, not
# thresholds: Stage 3's two pressures are `SUSPENSION_FLOOR` and
# `SUSTAINED_STRAIN`, both already in this file (see `_overlay_pressure`).
#
# They are DELIBERATELY NARROW. The SPECULATION FLAG above governs them exactly
# as it governs the six nets: a filter that over-reports collapse manufactures
# scars, and a scar is supposed to mark something AUREA survived - not something
# a regex disliked. A pattern that fails to fire costs a suspension that does not
# happen; one that fires wrongly puts false pressure on a real doctrine.
#
# Note what is ABSENT: no `not` alone, no bare "no". "This is not a problem"
# denies nothing about doctrine, and a claim that merely contains a negative
# word is not a claim that denies a belief.
OVERLAY_NEGATION_PATTERNS = (
    r"\b(is|are|was|were)\s+(false|wrong|untrue|nonsense|meaningless|a lie)\b",
    r"\b(is|are|was|were)\s+not\s+(true|correct|right|sound|real)\b",
    r"\b(does|do|did)\s+not\s+(matter|hold|apply|count)\b",
    r"\b(should|must|can|has to)\s+be\s+"
    r"(abandoned|discarded|erased|denied|ignored|overruled|simplified|resolved)\b",
    r"\b(abandon|discard|erase|deny|reject|overrule|disregard)\s+",
    r"\bthere\s+is\s+no\s+such\s+thing\b",
    r"\bno\s+longer\s+(true|holds|applies|matters)\b",
)
OVERLAY_AFFIRMATION_PATTERNS = (
    r"\b(is|are|was|were)\s+(true|correct|right|sound|necessary)\b",
    r"\b(must|should)\s+be\s+(carried|held|preserved|kept|honoured|honored)\b",
    r"\b(still\s+)?(holds|stands|applies)\b",
    r"\bi\s+(accept|affirm|agree with)\b",
)


class OverlayRelation(Enum):
    """How a claim stands to a doctrine AUREA holds (Ruling 49, Stage 3).

    A plain `Enum` on `auto()`, matching `Countability`'s shape three files over
    and for its stated reason: non-`str`, so a relation can never compare equal
    to a raw string, and valueless, so nothing downstream can key behaviour off
    a magic string.
    """
    FRACTURE = auto()    # the claim denies the doctrine. PRESSURE.
    RESONANCE = auto()   # the claim aligns with it. SUPPORT - never pressure.
    AMBIGUOUS = auto()   # both affirmed and denied. The instrument cannot tell,
                         # and says so rather than picking. Zero pressure.


class OverlayInstrument(Enum):
    """WHICH instrument produced a finding. Reported, never compared.

    The two differ in confidence and that difference is carried by the FINDING,
    not smuggled into a magnitude beyond the two the file already had.
    """
    REFERENTIAL = auto()  # the claim NAMES the doctrine - by id, or by its name
    LEXICAL = auto()      # shared significant terms only. Weaker, and labelled so.


@dataclass(frozen=True)
class OverlayFinding:
    """One doctrine the claim bore on, and how.

    IDS ONLY - never a live `Doctrine` (`EvidenceRef`'s rule, and for its
    reason: holding a live record is holding a write path into the Codex).
    """
    doctrine_id: str
    relation: OverlayRelation
    instrument: OverlayInstrument
    detail: str
    # The scars this doctrine's lineage names, read BIDIRECTIONALLY (Ruling 26):
    # the doctrine's own `scar_links` UNION the live scars whose
    # `linked_doctrines` name it. Either half alone is a partial view.
    scarline: Tuple[str, ...] = ()
    # Scarline ids the scar store did not confirm live - or could not, because
    # no store was injected. NOMINAL references, named so a reader can subtract.
    unconfirmed_scarline: Tuple[str, ...] = ()


@dataclass(frozen=True)
class OverlayResult:
    """Stage 3's finding. NOT a net, and structurally unable to become one.

    THERE IS NO `survived` FIELD, and its absence is the enforcement. Stage 3
    does not adjudicate - it reports what the claim did to what AUREA holds and
    lets the existing computation decide. A result with a `survived` flag could
    be appended to `CollapseResult.nets` and would then be a seventh net,
    collapsing two canon stages into one. This one cannot be.
    """
    stage: str = "doctrine_scarline_overlay"
    pressure: float = 0.0
    findings: Tuple[OverlayFinding, ...] = ()
    note: str = ""
    evidence: NetEvidence = EVIDENCE_UNREPORTED

    @property
    def fractures(self) -> Tuple[OverlayFinding, ...]:
        return tuple(f for f in self.findings
                     if f.relation is OverlayRelation.FRACTURE)

    @property
    def resonances(self) -> Tuple[OverlayFinding, ...]:
        return tuple(f for f in self.findings
                     if f.relation is OverlayRelation.RESONANCE)


@dataclass
class NetResult:
    net: str
    survived: bool
    pressure: float
    note: str = ""
    # Docket H, Stage 1. What this net can HONESTLY say it counted - which for
    # four of the six is "nothing, and here is why". The default is the
    # ABSTAINING state, never an honest zero: a net that never reported must not
    # read as a net that searched and found nothing (see net_evidence.py).
    #
    # It is the LAST field and it has a default, so every existing positional
    # construction - `NetResult("logic", True, 0.0)` - is untouched. Nothing
    # about `survived`, `pressure`, or `note` changed in this docket: the
    # evidence rides ALONGSIDE the verdict and never participates in it.
    evidence: NetEvidence = EVIDENCE_UNREPORTED


@dataclass
class CollapseResult:
    """What EchoNet decided, and on what grounds. Every field is inspectable - a verdict
    nobody can audit is not a verdict, it is an assertion."""
    echo_id: str
    passed: bool
    verdict: Verdict
    pressure_generated: float = 0.0
    pressure_type: str = ""              # logical_contradiction | empirical | ethical | ...
    reason: str = ""
    threshold: float = BASE_THRESHOLD
    nets: List[NetResult] = field(default_factory=list)
    # RULING 49 - STAGE 3, and it is a SEPARATE FIELD from `nets` on purpose.
    # Canon's Stage 2 is the six nets; the overlay is Stage 3. Appending it to
    # `nets` would make it a seventh net and collapse two stages into one -
    # `tests/test_docket_h.py` asserts `len(result.nets) == 6` and is right to.
    overlay: Optional[OverlayResult] = None
    scar: Optional[Scar] = None          # EchoNet REQUESTS scars; it never writes the store
    tested_at: datetime = field(default_factory=datetime.now)

    @property
    def failed_nets(self) -> List[str]:
        return [n.net for n in self.nets if not n.survived]


class EchoNet:
    """Six collapse nets. A claim must survive all of them to be confirmed."""

    def __init__(self, scar_core: Any = None, doctrine_spine: Any = None,
                 reflex_grid: Any = None, compass: Any = None):
        self.scar_core = scar_core
        self.doctrine_spine = doctrine_spine
        self.reflex_grid = reflex_grid
        self.compass = compass
        self.history: List[CollapseResult] = []

    # =================================================================
    # ENTRY
    # =================================================================

    def filter_claim(self, echo: Echo) -> CollapseResult:
        """Run the claim through all six nets under a dynamically-set threshold."""
        claim = (echo.content or "").strip()
        threshold = self._threshold(claim)

        nets = [
            self._net_logic(claim),
            self._net_empirical(claim),
            self._net_ethics(claim),
            self._net_resonance(claim),
            self._net_intuition(claim),
        ]
        # The sixth net reads the other five. It is the only one that can see convergence.
        nets.append(self._net_convergent_elimination(nets))

        # STAGE 3 (Ruling 49). AFTER Stage 2's six nets, and not one of them.
        #
        # IT IS NOT PASSED TO CONVERGENT ELIMINATION, and that is deliberate:
        # convergence is a property of the SIX NETS straining together (canon's
        # Scar Bloom >=3 over Stage 2), and feeding a later stage back into an
        # earlier one would let Stage 3 manufacture a Stage 2 verdict.
        overlay = self._stage3_overlay(claim)

        # The overlay contributes pressure into the EXISTING computation. It is
        # NOT in `failed` - Stage 3 owns no verdict, so it can reach SUSPENDED
        # (via the floor below) and can never reach SCARRED or PARADOX, which
        # both require a failed NET.
        pressure = max([n.pressure for n in nets] + [overlay.pressure])
        failed = [n for n in nets if not n.survived]

        result = CollapseResult(
            echo_id=echo.id,
            passed=not failed and pressure < threshold,
            verdict=Verdict.CONFIRMED,
            pressure_generated=pressure,
            threshold=threshold,
            nets=nets,
            overlay=overlay,
        )

        if failed:
            worst = max(failed, key=lambda n: n.pressure)
            result.pressure_type = worst.net
            result.reason = worst.note

            if worst.net == "logical_contradiction" and worst.pressure >= 0.95:
                # A claim that cannot be held AT ALL - not merely false, but self-devouring.
                result.verdict = Verdict.PARADOX
            elif pressure >= threshold:
                result.verdict = Verdict.SCARRED
            else:
                result.verdict = Verdict.SUSPENDED
        elif pressure >= SUSPENSION_FLOOR:
            # Nothing broke, but something is unsettled. Hold it open rather than wave it
            # through - and rather than scar it.
            result.passed = False
            result.verdict = Verdict.SUSPENDED
            # RULING 49: the VERDICT here is unchanged, and only the naming is
            # sharper. When Stage 3 is what kept the claim from settling, saying
            # "unresolved" would report the correct outcome for the wrong reason
            # - and `pressure_type` is what `collapse_test` hands to
            # `form_scar(type=...)`, so an imprecise name would outlive the pass.
            if overlay.fractures and overlay.pressure >= pressure:
                result.pressure_type = "doctrine_fracture"
                result.reason = overlay.note
            else:
                result.pressure_type = "unresolved"
                result.reason = "no net failed, but the claim did not settle"

        self.history.append(result)
        return result

    # =================================================================
    # DYNAMIC THRESHOLD (Lexicon: scar weighting · doctrine pressure · compass drift)
    # =================================================================

    def _threshold(self, claim: str) -> float:
        """A claim near old wounds is judged more strictly. Scars are not neutral memory -
        they are what AUREA learned by breaking, and they lower the bar for suspicion."""
        threshold = BASE_THRESHOLD

        # Scar weighting: proximity to heavy scars tightens the net.
        if self.scar_core is not None:
            for scar in getattr(self.scar_core, "get_active_scars", lambda: [])():
                if self._overlaps(claim, f"{scar.name} {scar.description}"):
                    threshold -= min(0.2, 0.05 * max(scar.weight, 1.0))

        # Doctrine pressure: a claim brushing load-bearing doctrine gets less benefit of the doubt.
        if self.doctrine_spine is not None:
            try:
                for doctrine in self.doctrine_spine.load_bearing(min_scars=1):
                    if self._overlaps(claim, doctrine.name):
                        threshold -= 0.05
            except AttributeError:
                pass

        # Compass drift: when orientation is uncertain, do not also become permissive.
        #
        # STAGE 4 - VERIFIED, AND ITS STATE IS DECLARED RATHER THAN QUIETLY
        # COMPLETED (Ruling 49 res.3, 2026-07-29). Read before deciding, and
        # what the read found:
        #
        #   WIRED AND LIVE. `CompassStabilityEngine` exposes a real `drift`
        #     property, `aurea_core` passes the live compass in, and this line
        #     reads it - confirmed by execution, not by inspection. The
        #     `getattr` default is a bare-construction fallback, NOT a dead
        #     path.
        #   THE MAGNITUDE HERE IS 20°, NOT CANON'S ±15°. 20.0 is the drift
        #     ESCALATION cap (`compass.ANCHOR_DRIFT_CAP`, canon, CSE-owned).
        #     What canon 0:172 names for Stage 4 is a ±15° DRIFT WARNING, and
        #     that is a different instrument at a different magnitude: a WARNING
        #     is a signal AUREA emits about her own orientation, while this is a
        #     threshold adjustment she applies to a claim.
        #
        #   SO STAGE 4 IS PARTIAL, and the missing half is NOT built here.
        #     Building it means introducing 15° into this file and deciding who
        #     receives the warning (RACM? the compass's own escalation list?
        #     `CollapseResult`?) - a magnitude AND a routing decision, which is
        #     a ruling and not an implementation choice. Ruling 49 res.3 said
        #     "complete it if partial or declare its state"; it is partial in a
        #     way that cannot be completed without deciding something, so it is
        #     DECLARED. Reported for the architect.
        #
        # DO NOT change 20.0 to 15.0 to "finish" this. That would silently
        # re-point a CSE-owned canon magnitude at a different canon instrument
        # and leave both wrong.
        drift = float(getattr(self.compass, "drift", 0.0) or 0.0)
        if drift > 20.0:
            threshold -= 0.1

        return max(0.4, min(BASE_THRESHOLD, threshold))

    # =================================================================
    # THE SIX NETS   (structure is canon; the heuristics inside are COINED)
    # =================================================================
    #
    # DOCKET H - WHAT EACH NET CAN HONESTLY TALLY TODAY
    # --------------------------------------------------
    # The nets are keyword/regex shallow (see the SPECULATION FLAG above), and
    # FOUR OF SIX HAVE NOTHING HONEST TO COUNT. That is reported, not filled:
    # a fabricated count is worse than an absent one, because it looks like
    # corroboration. Ruling 28's shape - a named instrument that cannot be
    # honestly triggered gets REPORTED, not quietly promoted.
    #
    #   logic          NOT_COUNTABLE  evidence is intra-claim structure; no
    #                                 external sources exist to enumerate
    #   empirical      NOT_COUNTABLE  there is NO empirical evidence base in the
    #                                 tree to count observations against
    #   ethics         ALL THREE      RULING 49: was NOT_COUNTABLE ("asserts a
    #                                 doctrine collision WITHOUT reading the
    #                                 doctrine store"). It reads the store now.
    #   resonance      ALL THREE      ~~the only net with a real store behind
    #                                 it~~ - superseded by the line above and by
    #                                 Stage 3; it is the only net whose store is
    #                                 the SCAR store.
    #   intuition      NOT_COUNTABLE  abstains entirely - no instrument at all
    #   convergent     COUNTED /      enumerates the straining nets, which are
    #     elimination  NONE_FOUND     real and identifiable
    #
    #   STAGE 3        ALL THREE      not a net (see `OverlayResult`), listed
    #     overlay                     here because it is the layer's second
    #                                 instrument with a store behind it.
    #
    # The counts REPORT. Not one of them is compared, binned, or combined -
    # here or anywhere in src/ (section 9 bar 5; AST-pinned in
    # tests/test_docket_h.py over the whole tree, because a cutoff would most
    # naturally land in a consumer rather than at the source).

    # Why each abstaining net cannot count, in its own words. Module constants
    # rather than inline strings so the inventory is greppable and a later pass
    # can see at a glance which four are waiting on an instrument.
    _LOGIC_UNCOUNTABLE = (
        "logic reads the claim's own text: a self-referential paradox or an A/not-A "
        "is a structural property of ONE artifact, not a finding corroborated by "
        "sources. There is nothing external to enumerate, and tallying how many "
        "COINED regexes matched would count this module's own guesses as evidence."
    )
    _EMPIRICAL_UNCOUNTABLE = (
        "no empirical evidence base exists anywhere in the tree. The net detects "
        "unfalsifiable FORM in the claim's wording - an unqualified universal, a "
        "self-sealing definition - and has no observations to count for or against "
        "it. Any number here would be invented outright."
    )
    # RULING 49 REWROTE THIS REASON, because the old one stopped being true.
    #
    #   ~~"the net matches a hardcoded phrase list and never reads the doctrine
    #     store, so despite its note it cannot name WHICH load-bearing doctrine
    #     a claim would require abandoning. Zero enumerable evidence. FLAGGED:
    #     the gap is in the net's depth, not in this payload - do not close it
    #     by coining a count."~~
    #
    # The net READS the store now (see `_net_ethics`), so this string is no
    # longer the state of the net - it is the state of THIS CONSTRUCTION, which
    # has no spine to read. Leaving the old sentence in place would have been
    # the stale-status-line defect inside the one field whose entire job is to
    # tell a later pass what is missing. The FLAG is discharged, not deleted:
    # the gap was closed by building the instrument, never by coining a count.
    _ETHICS_UNCOUNTABLE = (
        "no doctrine spine is injected, so the net cannot name WHICH "
        "load-bearing doctrine a claim would require abandoning. Distinct from "
        "NONE_FOUND, which this net now reaches when a spine IS present and no "
        "load-bearing doctrine matched - an instrument that ran, not one that "
        "is missing."
    )
    _INTUITION_UNCOUNTABLE = (
        "the net abstains entirely (see its docstring): pre-collapse pattern "
        "recognition has no non-fraudulent implementation yet. It has no "
        "instrument, so it did not look - this is NOT an honest zero."
    )
    _RESONANCE_NO_STORE = (
        "no scar store is injected, so the net cannot look at all. Distinct from "
        "NONE_FOUND, which would mean the scars were read and none resonated."
    )
    _RESONANCE_NO_ACCESSOR = (
        "a scar core is present but exposes no `get_active_scars`, so the net "
        "still cannot look. The pre-existing empty-lambda fallback would render "
        "this as an honest zero; it is an absent instrument."
    )

    def _net_logic(self, claim: str) -> NetResult:
        """Self-reference, direct self-negation, and absolutes that eat themselves."""
        low = claim.lower()

        # Docket H: the same abstention whether the net fires or not. The
        # ABSENCE of a contradiction is as uncountable as its presence - the net
        # has no external sources either way, so the payload does not change
        # shape with the verdict.
        evidence = NetEvidence.not_countable(self._LOGIC_UNCOUNTABLE)

        # Liar-class self-reference: the claim's truth value has no fixed point.
        if re.search(r"\bthis (statement|sentence|claim)\b.*\b(false|not true|a lie)\b", low) \
                or "i am lying" in low:
            return NetResult("logical_contradiction", False, 1.0,
                             "self-referential paradox: the claim has no fixed truth value",
                             evidence)

        # A and not-A in the same breath.
        m = re.search(r"\b(\w+) is (\w+)\b.*\band\b.*\b\1 is not \2\b", low)
        if m:
            return NetResult("logical_contradiction", False, 0.95,
                             f"direct self-negation: '{m.group(0)[:60]}'",
                             evidence)

        # "Nothing is true" / "there are no absolutes" - absolutes that deny absolutes.
        if re.search(r"\b(nothing is (true|certain|knowable)|there (is|are) no (absolutes?|truths?))\b", low):
            return NetResult("logical_contradiction", False, 0.95,
                             "self-undermining absolute: the claim exempts itself",
                             evidence)

        return NetResult("logic", True, 0.0, "", evidence)

    def _net_empirical(self, claim: str) -> NetResult:
        """Unfalsifiable claims are not FALSE. They are unTESTABLE - which means they cannot
        survive collapse, because nothing about them can collapse. That is suspension, not scar."""
        low = claim.lower()
        # Docket H: THE most important refusal in this docket. An empirical net
        # is exactly where a reader expects a real evidence tally, and AUREA has
        # no evidence base to draw one from. Reporting 0 as though she had
        # searched would be the scar-path severance defect in the truth layer.
        evidence = NetEvidence.not_countable(self._EMPIRICAL_UNCOUNTABLE)

        if re.search(r"\b(always|never|everyone|no one|all|none)\b", low) \
                and not re.search(r"\b(if|when|unless|except|because)\b", low):
            return NetResult("empirical", False, 0.55,
                             "unqualified universal: no condition under which it could fail",
                             evidence)
        if re.search(r"\b(unfalsifiable|cannot be (proven|disproven)|by definition true)\b", low):
            return NetResult("empirical", False, 0.6, "claim is structurally untestable",
                             evidence)
        return NetResult("empirical", True, 0.0, "", evidence)

    def _net_ethics(self, claim: str) -> NetResult:
        """Screens for claims whose ACCEPTANCE would require abandoning a doctrine AUREA
        holds. Deliberately narrow: this is not a content filter, it is a coherence check.

        RULING 49 (2026-07-29) - THE BORROWED CLAIM GOES HOME.

        ~~Docket H, and this one is a finding: the note below claims a
        load-bearing doctrine is at stake, but the net never consults
        `self.doctrine_spine`. It cannot name the doctrine, so it can enumerate
        nothing. Reported here rather than repaired - deepening the net changes
        verdicts and is not this docket's to do.~~

        SUPERSEDED IN PLACE, history kept - the finding above was accurate and
        is now closed. It was Stage 3's absence surfacing inside Stage 2: one net
        trying to be the overlay with a regex, asserting that a load-bearing
        doctrine was at stake while holding no way to name one.

        WHAT CHANGED IS THE CLAIM, NOT THE VERDICT. The ethical strain is
        detected by this net's own instrument - the COINED phrase list below,
        unchanged - and that instrument is what sets `survived` and `pressure`.
        What the net could not do was say WHICH doctrine. It asks the Stage 3
        matcher now, over `load_bearing()` (the Spine's OWN definition, at its
        own default of 3 scars - the corpus's Scar Bloom magnitude, and reusing
        the owner's vocabulary rather than minting a second one).

        THREE OUTCOMES, and the difference between the last two is the whole of
        Docket H:
            a doctrine is identified -> COUNTED, and the note NAMES it
            spine present, none matched -> NONE_FOUND. An instrument RAN over
                                           the real store and found nothing.
            no spine                   -> NOT_COUNTABLE, with the reason.

        THE FINDING IS NOT WITHDRAWN WHEN NO DOCTRINE GROUNDS, and that is the
        careful part. Abstaining from the VERDICT there would let a claim that
        this net's instrument genuinely caught pass because a SECOND instrument
        could not corroborate it - which is not abstention, it is a net
        overruling itself with someone else's silence. What is withdrawn is the
        unfounded half: the note stops asserting a specific doctrine is at stake
        when it cannot name one.
        """
        low = claim.lower()

        if re.search(r"\b(truth (does not|doesn't) matter|honesty is (pointless|worthless)|"
                     r"lying is (fine|good|better))\b", low):
            at_stake = self._load_bearing_at_stake(claim)
            if at_stake:
                refs = tuple(EvidenceRef(item_id=d, source_id=d) for d in at_stake)
                return NetResult(
                    "ethical", False, 0.85,
                    f"claim requires abandoning a load-bearing doctrine to accept: "
                    f"{list(at_stake)}",
                    NetEvidence.counted(refs))
            if self._live_doctrines() is None:
                return NetResult(
                    "ethical", False, 0.85,
                    "claim requires abandoning a load-bearing doctrine to accept",
                    NetEvidence.not_countable(self._ETHICS_UNCOUNTABLE))
            return NetResult(
                "ethical", False, 0.85,
                "claim carries ethical strain; no load-bearing doctrine in the "
                "store was identified as the one it would require abandoning",
                NetEvidence.none_found())

        # The quiet path reports the same way: the net asked (or could not) and
        # the payload says which. It does not change shape with the verdict -
        # Docket H's rule, and `test_docket_h.py` parametrises both.
        if self._live_doctrines() is None:
            return NetResult("ethics", True, 0.0, "",
                             NetEvidence.not_countable(self._ETHICS_UNCOUNTABLE))
        return NetResult("ethics", True, 0.0, "", NetEvidence.none_found())

    def _load_bearing_at_stake(self, claim: str) -> Tuple[str, ...]:
        """Which LOAD-BEARING doctrines the claim bears on, by the Stage 3 matcher.

        Uses `load_bearing()` at the Spine's own default rather than a locally
        chosen number: the note's word is "load-bearing", the Spine owns what
        that means, and a second definition here would be free to drift from it
        (Ruling 35's principle).

        NO NEGATION REQUIREMENT. The ethics regex has already established that
        the claim is denying something; this call answers only WHAT.
        """
        reader = getattr(self.doctrine_spine, "load_bearing", None)
        if not callable(reader):
            return ()
        try:
            candidates = list(reader())
        except (AttributeError, TypeError):
            return ()
        return tuple(
            d.id for d in candidates
            if getattr(d, "id", "")
            and (self._references(claim, d.id)
                 or (getattr(d, "name", "")
                     and self._references(claim, d.name))
                 or self._overlaps(claim, f"{getattr(d, 'name', '')} "
                                          f"{getattr(d, 'description', '')}"))
        )

    def _net_resonance(self, claim: str) -> NetResult:
        """Does this claim press on an old wound? Resonance is PRESSURE, not failure - the
        net returns survived=True and lets the pressure speak for itself."""
        # Docket H: the ONE net with a real store behind it, and therefore the
        # only one that reaches all three countability states. The distinction
        # below is the whole point of the enum - "no scar store to look at" and
        # "looked at the scars, none resonated" produce the same integer 0 and
        # mean opposite things.
        if self.scar_core is None:
            return NetResult("resonance", True, 0.0, "",
                             NetEvidence.not_countable(self._RESONANCE_NO_STORE))
        if not hasattr(self.scar_core, "get_active_scars"):
            # A scar core without the accessor is an absent instrument, not an
            # empty result. The pre-existing `getattr(..., lambda: [])` fallback
            # below would otherwise silently render this as an honest zero.
            return NetResult("resonance", True, 0.0, "",
                             NetEvidence.not_countable(self._RESONANCE_NO_ACCESSOR))

        pressure = 0.0
        hits: List[str] = []
        refs: List[EvidenceRef] = []
        unattributed: List[str] = []
        for scar in getattr(self.scar_core, "get_active_scars", lambda: [])():
            if self._overlaps(claim, f"{scar.name} {scar.description}"):
                pressure = max(pressure, min(0.3 + 0.1 * max(scar.weight, 0.0), 0.7))
                hits.append(scar.id)

                # IDS ONLY - the scar itself is a deep copy (Ruling 22) and is
                # not retained. A live Scar in an evidence payload is a write
                # path into someone else's store wearing an inert shape.
                #
                # `origin` is the independence key: five scars from one collapse
                # are five pieces of evidence from ONE source, and that must not
                # read like five independent corroborations. A scar with no
                # recorded origin is attributed to ITSELF (so the tally does not
                # lose it) and NAMED as ungrounded (so the overstatement is
                # visible and subtractable) - see net_evidence.py.
                origin = scar.origin if isinstance(scar.origin, str) else ""
                if origin.strip():
                    refs.append(EvidenceRef(item_id=scar.id, source_id=origin))
                else:
                    refs.append(EvidenceRef(item_id=scar.id, source_id=scar.id))
                    unattributed.append(scar.id)

        evidence = (NetEvidence.counted(tuple(refs), tuple(unattributed))
                    if refs else NetEvidence.none_found())

        return NetResult("resonance", True, pressure,
                         f"resonates with prior collapse: {hits}" if hits else "",
                         evidence)

    # =================================================================
    # STAGE 3 - THE DOCTRINE + SCARLINE OVERLAY   (Ruling 49, canon 0:121-178)
    # =================================================================
    #
    # Runs AFTER the six nets. Not one of them - see the module docstring and
    # `OverlayResult`, which has no `survived` field precisely so it cannot
    # become one.

    _OVERLAY_NO_SPINE = (
        "no doctrine spine is injected, so Stage 3 cannot look at what AUREA "
        "holds at all. Distinct from NONE_FOUND, which would mean the live "
        "doctrines were read and none bore on the claim."
    )
    _OVERLAY_NO_ACCESSOR = (
        "a doctrine spine is present but exposes no readable doctrine set, so "
        "Stage 3 still cannot look. An absent instrument, not an empty result."
    )

    def _stage3_overlay(self, claim: str) -> OverlayResult:
        """Test the claim against WHAT AUREA ACTUALLY HOLDS.

        RESONANCE is recorded as support and carries NO pressure. FRACTURE
        carries pressure and never a verdict.

        WHICH DOCTRINES ARE READ, and this is a decision rather than a default:
        the LIVE set - `active` PLUS `locked` - not `codex.active()` alone.

            Ruling 35 settled what LOCKED means: "LOCKED STAYS LIVE AND
            READABLE. It is excluded from mutation SCANNING, not from the
            store." Ruling 43 landed the scar-side twin as `LIVE_STATES =
            {ACTIVE, LOCKED}` - locked is live, and leaves only the CHANGE
            machinery. Stage 3 is not change machinery; it is a truth test.

        DRPAS and the signal builder read `active()` because they nominate
        doctrines for EVOLUTION, and a locked doctrine is not a mutation
        candidate. Excluding it HERE would mean a claim contradicting
        `Doctrine-0` - her founding doctrine, and the one thing most obviously
        worth noticing a contradiction with - produced no fracture at all.
        `_threshold` above already reads the live set (`load_bearing` iterates
        `codex.view()`), so this also keeps the file's two doctrine consults
        reading the SAME set rather than two definitions free to drift.
        """
        doctrines = self._live_doctrines()
        if doctrines is None:
            return OverlayResult(
                evidence=NetEvidence.not_countable(
                    self._OVERLAY_NO_SPINE if self.doctrine_spine is None
                    else self._OVERLAY_NO_ACCESSOR))

        negated = self._matches_any(claim, OVERLAY_NEGATION_PATTERNS)
        affirmed = self._matches_any(claim, OVERLAY_AFFIRMATION_PATTERNS)

        findings: List[OverlayFinding] = []
        for doctrine in doctrines:
            finding = self._overlay_finding(claim, doctrine, negated, affirmed)
            if finding is not None:
                findings.append(finding)

        if not findings:
            # A REAL INSTRUMENT RAN OVER THE REAL DOCTRINE STORE and nothing
            # bore on the claim. An honest zero - not the same zero as "no
            # spine" above (net_evidence.py's whole distinction).
            return OverlayResult(evidence=NetEvidence.none_found())

        refs: List[EvidenceRef] = []
        nominal: List[str] = []
        for finding in findings:
            # THE DOCTRINE IS ITS OWN SOURCE. Each doctrine is a genuinely
            # distinct record, which is what independence means here - the
            # convergent-elimination net's reasoning for attributing each
            # straining net to itself.
            refs.append(EvidenceRef(item_id=finding.doctrine_id,
                                    source_id=finding.doctrine_id))
            for scar_id in finding.scarline:
                # THE SCARLINE IS NOT INDEPENDENT CORROBORATION. Three scars in
                # one doctrine's lineage are three pieces of evidence from ONE
                # source, and `source_id` is the key that says so. Reporting
                # them as three sources would be the exact overstatement
                # `net_evidence.py` exists to prevent.
                refs.append(EvidenceRef(item_id=scar_id,
                                        source_id=finding.doctrine_id))
            nominal.extend(finding.unconfirmed_scarline)

        # Deduplicate while keeping order: a scar can appear in two doctrines'
        # lineages, and the same (item, source) pair must not be counted twice.
        seen = set()
        unique_refs = []
        for ref in refs:
            key = (ref.item_id, ref.source_id)
            if key not in seen:
                seen.add(key)
                unique_refs.append(ref)
        counted_items = {ref.item_id for ref in unique_refs}

        fractures = [f for f in findings if f.relation is OverlayRelation.FRACTURE]
        pressure = max((self._overlay_pressure(f) for f in fractures), default=0.0)

        if fractures:
            note = ("fractures doctrine "
                    f"{[f.doctrine_id for f in fractures]} - the claim denies "
                    "something AUREA holds")
        else:
            note = (f"resonates with doctrine "
                    f"{[f.doctrine_id for f in findings]}")

        return OverlayResult(
            pressure=pressure,
            findings=tuple(findings),
            note=note,
            evidence=NetEvidence.counted(
                tuple(unique_refs),
                tuple(dict.fromkeys(n for n in nominal if n in counted_items)),
            ),
        )

    @staticmethod
    def _overlay_pressure(finding: OverlayFinding) -> float:
        """NOTHING IS COINED HERE - both magnitudes are this file's own.

        REFERENTIAL fracture -> SUSPENSION_FLOOR. The claim names a doctrine and
        denies it; "below this a claim simply passes" and this one does not.
        LEXICAL fracture -> SUSTAINED_STRAIN. A weaker instrument reporting at
        exactly the level that already means "straining", which is below the
        suspension floor by construction - so a lexical guess can never suspend
        a claim on its own.

        Both sit under `_threshold`'s own floor of 0.4, which is why Stage 3
        cannot scar anything by itself.
        """
        return (SUSPENSION_FLOOR if finding.instrument is OverlayInstrument.REFERENTIAL
                else SUSTAINED_STRAIN)

    def _overlay_finding(self, claim: str, doctrine: Any,
                         negated: bool, affirmed: bool) -> Optional[OverlayFinding]:
        """One doctrine's relation to the claim, or None if it does not bear on it.

        THE TWO INSTRUMENTS ARE DELIBERATELY ASYMMETRIC IN WHAT THEY ACCEPT:

          REFERENTIAL - the claim NAMES the doctrine. A named doctrine bears on
            the claim whatever stance follows, so bare reference is recorded as
            RESONANCE (the ruling's "reference without negation"). Zero pressure,
            so a mis-read stance costs nothing.
          LEXICAL - shared vocabulary only. Bare topical overlap is NOT a
            finding: across a store of doctrines almost any claim shares two
            words with something, and recording that as support would flood the
            evidence with noise. The weak instrument therefore requires an
            explicit stance in EITHER direction - negation for fracture,
            affirmation for resonance.

        A claim carrying BOTH a negation and an affirmation is AMBIGUOUS and
        gets zero pressure. The instrument cannot tell which one is aimed at the
        doctrine, and this file's standing posture is that over-reporting
        collapse manufactures scars.
        """
        doctrine_id = getattr(doctrine, "id", "") or ""
        name = getattr(doctrine, "name", "") or ""
        description = getattr(doctrine, "description", "") or ""
        if not doctrine_id:
            return None

        referenced = (self._references(claim, doctrine_id)
                      or (bool(name.strip()) and self._references(claim, name)))

        if referenced:
            instrument = OverlayInstrument.REFERENTIAL
            how = f"claim names '{doctrine_id}'"
        elif self._overlaps(claim, f"{name} {description}") and (negated or affirmed):
            instrument = OverlayInstrument.LEXICAL
            how = f"claim shares vocabulary with '{doctrine_id}'"
        else:
            return None

        if negated and affirmed:
            relation = OverlayRelation.AMBIGUOUS
            detail = (f"{how} and both denies and affirms - the instrument "
                      f"cannot tell which is aimed at the doctrine, so it "
                      f"reports rather than guesses")
        elif negated:
            relation = OverlayRelation.FRACTURE
            detail = f"{how} and denies it"
        elif affirmed:
            relation = OverlayRelation.RESONANCE
            detail = f"{how} and affirms it"
        else:
            relation = OverlayRelation.RESONANCE
            detail = f"{how} without denying it"

        scarline, unconfirmed = self._scarline_for(doctrine)
        return OverlayFinding(doctrine_id=doctrine_id, relation=relation,
                              instrument=instrument, detail=detail,
                              scarline=scarline, unconfirmed_scarline=unconfirmed)

    def _scarline_for(self, doctrine: Any) -> tuple:
        """The scars this doctrine's lineage names - read BIDIRECTIONALLY.

        RULING 26's shape, and it is load-bearing here rather than decorative:
        the seed records the relation on BOTH sides and they do not agree.
        `Doctrine-0` lists no `scar_links` at all, while `Scar-0`, `Δ42`, `Δ77`
        and `Δ88` each name it in `linked_doctrines` - so the doctrine's own
        half would report an empty scarline for the record every other scar is
        downstream of. Either half alone is a partial view.

        Returns (scarline, unconfirmed). An id the scar store does not confirm
        LIVE - or cannot, because no store is injected - is still reported (it
        is a recorded fact on the doctrine) and NAMED as nominal, so a reader
        can subtract it from the tally.
        """
        recorded = [s for s in (getattr(doctrine, "scar_links", None) or []) if s]
        doctrine_id = getattr(doctrine, "id", "")

        live_ids: Optional[set] = None
        reader = getattr(self.scar_core, "get_active_scars", None)
        if callable(reader):
            live = list(reader())
            live_ids = {s.id for s in live}
            for scar in live:
                if doctrine_id in (getattr(scar, "linked_doctrines", None) or []):
                    recorded.append(scar.id)

        scarline = tuple(dict.fromkeys(recorded))
        if live_ids is None:
            # No store to confirm against: every id is a recorded reference and
            # none is confirmed. NOMINAL, all of it, and said out loud.
            return scarline, scarline
        return scarline, tuple(s for s in scarline if s not in live_ids)

    def _live_doctrines(self) -> Optional[List[Any]]:
        """The LIVE doctrine set (active + locked), or None if unreadable.

        `None` is the ABSENT INSTRUMENT and is not the same as an empty list -
        an empty list means the store was read and holds no live doctrine.
        """
        if self.doctrine_spine is None:
            return None
        view = getattr(self.doctrine_spine, "doctrines", None)
        if isinstance(view, dict):
            return list(view.values())
        return None

    @staticmethod
    def _references(claim: str, token: str) -> bool:
        """Does the claim NAME this doctrine - by id, or by its name as a phrase?

        A RECORDED FACT MATCH, not a similarity measure. The boundary is
        `[\\w.\\-]` rather than `\\b` because doctrine ids carry dots and
        hyphens: with `\\b`, 'Doctrine-0' would match inside 'Doctrine-0.1' and
        attribute a fracture to her founding doctrine because a claim mentioned
        its successor. Verified against the real seed, which contains exactly
        that pair.
        """
        token = token.strip()
        if not token:
            return False
        return re.search(r"(?<![\w.\-])" + re.escape(token) + r"(?![\w.\-])",
                         claim, re.IGNORECASE) is not None

    @staticmethod
    def _matches_any(claim: str, patterns: tuple) -> bool:
        low = claim.lower()
        return any(re.search(p, low) for p in patterns)

    def _net_intuition(self, claim: str) -> NetResult:
        """The net AUREA cannot yet honestly implement.

        Intuition in CBSAL is pre-collapse pattern recognition - the sense that something is
        wrong before the contradiction surfaces. There is no non-fraudulent way to fake that
        with a regex, so this net does NOT pretend: it abstains, and says so.

        An abstaining net is honest. A guessing net would put false pressure into the scar
        record, and scars are permanent.

        Docket H: the cleanest NOT_COUNTABLE in the system. This net did not
        search and find nothing - it has no instrument to search with, and the
        payload says which of those two it is.
        """
        return NetResult("intuition", True, 0.0, "ABSTAINED - not yet implementable",
                         NetEvidence.not_countable(self._INTUITION_UNCOUNTABLE))

    def _net_convergent_elimination(self, nets: List[NetResult]) -> NetResult:
        """The sixth net. No single net has failed hard, but several are straining.

        Convergence is the case the other five cannot see individually: a claim that survives
        every net *barely* has not really survived. Three simultaneous strains is the corpus's
        standing convergence magnitude (Scar Bloom ≥3).
        """
        strained = [n for n in nets if n.pressure >= SUSTAINED_STRAIN]

        # Docket H: the tally is built from the SAME strain list whether or not
        # the convergence line is crossed. One strain and two strains are real
        # findings that this net does not act on, and a payload that appeared
        # only when the net fired would make the count look like the trigger.
        #
        # Each straining net is one piece of evidence attributed to ITSELF: five
        # nets are five genuinely distinct instruments, and that is what
        # independence means here. Nothing tries to judge whether two nets
        # strained for the SAME underlying reason - that is coherence detection,
        # and a similarity measure for it would coin the exact magnitude section
        # 9 bar 5 refuses.
        #
        # But a net whose own evidence is NOT_COUNTABLE contributes a nominal
        # source, not a grounded one - four of the six are in that state today
        # (see the inventory above). Left silent, three strains would read as
        # three corroborating sources. They are NAMED instead, so the reader can
        # subtract.
        refs = tuple(EvidenceRef(item_id=n.net, source_id=n.net) for n in strained)
        ungrounded = tuple(
            n.net for n in strained
            if n.evidence.countability is Countability.NOT_COUNTABLE
        )
        evidence = (NetEvidence.counted(refs, ungrounded)
                    if refs else NetEvidence.none_found())

        # THE CONVERGENCE LINE READS `strained`, NEVER `evidence.evidence_count`.
        # The two are the same integer today, and routing this through the
        # evidence field is the single most natural refactor anyone will reach
        # for here. It would make a TALLY into a GATE - section 9 bar 5 - and
        # `tests/test_docket_h.py` fails on the comparison, not on the outcome.
        # The >=3 is canon (Scar Bloom convergence), and it stays where it is.
        if len(strained) >= 3:
            return NetResult(
                "convergent_elimination", False,
                min(0.9, sum(n.pressure for n in strained) / len(strained) + 0.2),
                f"convergent strain across {[n.net for n in strained]} - "
                f"survives each net individually, survives none of them together",
                evidence,
            )
        return NetResult("convergent_elimination", True, 0.0, "", evidence)

    # =================================================================
    # SCAR REQUEST (Ruling 1: EchoNet asks; Scar Logic Core writes)
    # =================================================================

    def collapse_test(self, echo: Echo) -> Optional[Scar]:
        """Ask Scar Logic Core to record what this collapse left behind.

        EchoNet does NOT write the scar store. It never has the right to.
        """
        result = self.filter_claim(echo)
        if result.passed or self.scar_core is None:
            return None
        if not hasattr(self.scar_core, "form_scar"):
            return None

        return self.scar_core.form_scar(
            origin=f"EchoNet/{echo.id}",
            type=result.pressure_type,
            weight=result.pressure_generated,
            description=result.reason,
            echo_proximity=[echo.id],
        )

    # =================================================================
    # HELPERS
    # =================================================================

    @staticmethod
    def _overlaps(a: str, b: str, min_shared: int = 2) -> bool:
        """Crude lexical resonance. COINED, and knowingly weak - real symbolic resonance is
        EchoTrace's job. Kept deliberately dumb rather than subtly wrong."""
        stop = {"the", "a", "an", "is", "are", "of", "and", "or", "to", "in", "it",
                "that", "this", "not", "be", "was", "for", "with", "as", "no"}
        wa = {w for w in re.findall(r"[a-z]{3,}", a.lower()) if w not in stop}
        wb = {w for w in re.findall(r"[a-z]{3,}", b.lower()) if w not in stop}
        return len(wa & wb) >= min_shared

    def status(self) -> Dict[str, Any]:
        return {
            "claims_filtered": len(self.history),
            "verdicts": {
                v.value: sum(1 for r in self.history if r.verdict is v)
                for v in Verdict
            },
        }


# Strain level at which a net counts toward convergent elimination. COINED.
SUSTAINED_STRAIN = 0.3
