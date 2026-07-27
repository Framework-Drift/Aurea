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
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

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

        pressure = max((n.pressure for n in nets), default=0.0)
        failed = [n for n in nets if not n.survived]

        result = CollapseResult(
            echo_id=echo.id,
            passed=not failed and pressure < threshold,
            verdict=Verdict.CONFIRMED,
            pressure_generated=pressure,
            threshold=threshold,
            nets=nets,
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
    #   ethics         NOT_COUNTABLE  asserts a doctrine collision WITHOUT
    #                                 reading the doctrine store
    #   resonance      ALL THREE      the only net with a real store behind it
    #   intuition      NOT_COUNTABLE  abstains entirely - no instrument at all
    #   convergent     COUNTED /      enumerates the straining nets, which are
    #     elimination  NONE_FOUND     real and identifiable
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
    _ETHICS_UNCOUNTABLE = (
        "the net matches a hardcoded phrase list and never reads the doctrine "
        "store, so despite its note it cannot name WHICH load-bearing doctrine a "
        "claim would require abandoning. Zero enumerable evidence. FLAGGED: the "
        "gap is in the net's depth, not in this payload - do not close it by "
        "coining a count."
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
        holds. Deliberately narrow: this is not a content filter, it is a coherence check."""
        low = claim.lower()
        # Docket H, and this one is a finding: the note below claims a
        # load-bearing doctrine is at stake, but the net never consults
        # `self.doctrine_spine`. It cannot name the doctrine, so it can enumerate
        # nothing. Reported here rather than repaired - deepening the net changes
        # verdicts and is not this docket's to do.
        evidence = NetEvidence.not_countable(self._ETHICS_UNCOUNTABLE)

        if re.search(r"\b(truth (does not|doesn't) matter|honesty is (pointless|worthless)|"
                     r"lying is (fine|good|better))\b", low):
            return NetResult("ethical", False, 0.85,
                             "claim requires abandoning a load-bearing doctrine to accept",
                             evidence)
        return NetResult("ethics", True, 0.0, "", evidence)

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
