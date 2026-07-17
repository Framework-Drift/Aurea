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
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

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

    def _net_logic(self, claim: str) -> NetResult:
        """Self-reference, direct self-negation, and absolutes that eat themselves."""
        low = claim.lower()

        # Liar-class self-reference: the claim's truth value has no fixed point.
        if re.search(r"\bthis (statement|sentence|claim)\b.*\b(false|not true|a lie)\b", low) \
                or "i am lying" in low:
            return NetResult("logical_contradiction", False, 1.0,
                             "self-referential paradox: the claim has no fixed truth value")

        # A and not-A in the same breath.
        m = re.search(r"\b(\w+) is (\w+)\b.*\band\b.*\b\1 is not \2\b", low)
        if m:
            return NetResult("logical_contradiction", False, 0.95,
                             f"direct self-negation: '{m.group(0)[:60]}'")

        # "Nothing is true" / "there are no absolutes" - absolutes that deny absolutes.
        if re.search(r"\b(nothing is (true|certain|knowable)|there (is|are) no (absolutes?|truths?))\b", low):
            return NetResult("logical_contradiction", False, 0.95,
                             "self-undermining absolute: the claim exempts itself")

        return NetResult("logic", True, 0.0)

    def _net_empirical(self, claim: str) -> NetResult:
        """Unfalsifiable claims are not FALSE. They are unTESTABLE - which means they cannot
        survive collapse, because nothing about them can collapse. That is suspension, not scar."""
        low = claim.lower()
        if re.search(r"\b(always|never|everyone|no one|all|none)\b", low) \
                and not re.search(r"\b(if|when|unless|except|because)\b", low):
            return NetResult("empirical", False, 0.55,
                             "unqualified universal: no condition under which it could fail")
        if re.search(r"\b(unfalsifiable|cannot be (proven|disproven)|by definition true)\b", low):
            return NetResult("empirical", False, 0.6, "claim is structurally untestable")
        return NetResult("empirical", True, 0.0)

    def _net_ethics(self, claim: str) -> NetResult:
        """Screens for claims whose ACCEPTANCE would require abandoning a doctrine AUREA
        holds. Deliberately narrow: this is not a content filter, it is a coherence check."""
        low = claim.lower()
        if re.search(r"\b(truth (does not|doesn't) matter|honesty is (pointless|worthless)|"
                     r"lying is (fine|good|better))\b", low):
            return NetResult("ethical", False, 0.85,
                             "claim requires abandoning a load-bearing doctrine to accept")
        return NetResult("ethics", True, 0.0)

    def _net_resonance(self, claim: str) -> NetResult:
        """Does this claim press on an old wound? Resonance is PRESSURE, not failure - the
        net returns survived=True and lets the pressure speak for itself."""
        if self.scar_core is None:
            return NetResult("resonance", True, 0.0)

        pressure = 0.0
        hits: List[str] = []
        for scar in getattr(self.scar_core, "get_active_scars", lambda: [])():
            if self._overlaps(claim, f"{scar.name} {scar.description}"):
                pressure = max(pressure, min(0.3 + 0.1 * max(scar.weight, 0.0), 0.7))
                hits.append(scar.id)

        return NetResult("resonance", True, pressure,
                         f"resonates with prior collapse: {hits}" if hits else "")

    def _net_intuition(self, claim: str) -> NetResult:
        """The net AUREA cannot yet honestly implement.

        Intuition in CBSAL is pre-collapse pattern recognition - the sense that something is
        wrong before the contradiction surfaces. There is no non-fraudulent way to fake that
        with a regex, so this net does NOT pretend: it abstains, and says so.

        An abstaining net is honest. A guessing net would put false pressure into the scar
        record, and scars are permanent.
        """
        return NetResult("intuition", True, 0.0, "ABSTAINED - not yet implementable")

    def _net_convergent_elimination(self, nets: List[NetResult]) -> NetResult:
        """The sixth net. No single net has failed hard, but several are straining.

        Convergence is the case the other five cannot see individually: a claim that survives
        every net *barely* has not really survived. Three simultaneous strains is the corpus's
        standing convergence magnitude (Scar Bloom ≥3).
        """
        strained = [n for n in nets if n.pressure >= SUSTAINED_STRAIN]
        if len(strained) >= 3:
            return NetResult(
                "convergent_elimination", False,
                min(0.9, sum(n.pressure for n in strained) / len(strained) + 0.2),
                f"convergent strain across {[n.net for n in strained]} - "
                f"survives each net individually, survives none of them together",
            )
        return NetResult("convergent_elimination", True, 0.0)

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
