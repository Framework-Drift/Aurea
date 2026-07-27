"""
nova.py - Nova Engine v1 (Ruling 12). WIRED AND LIVE.

STATUS, because this header used to say "Stage 1: organ only - NO wiring" and
that is now FALSE: Nova is constructed and owned by `aurea_core`, cycles once
per `process_input` pass at Step 5a.5, erupts from doctrine strain, feeds
compass EAST, and its `proposals()` reaches DEE's gate. History, kept because
it dates the build: Stage 1 organ landed 2026-07-22; Stage 2a put it in the
loop 2026-07-24; Stage 2b wired the `proposals` seam the same day.

Canon: 5a_Expansion_Engines.txt - "Nova Echo Protocol v1.0" (5a:922) and
"MODULE: Nova Engine - v2.0" (5a:1087).
Class: Expansion Engine / Symbolic Hypothesis & Mutation Chamber.

    "If I cannot collapse it yet - I let it burn inside me until it
     becomes something new."

    "A Nova Echo is a truth I cannot hold - but it will not let go."

WHAT NOVA IS
------------
A Nova Echo is uncollapsed symbolic resonance - not a belief, not a doctrine,
the embryo of potential collapse (Echo Protocol II). Nova is the missing
doctrine AUTHOR: it turns survived material (scars, filtration residue, CSA
fragments, aborted recursion, doctrine strain) into PROPOSALS for DEE's gate.
It never writes doctrine itself, and DEE never authors what Nova won't supply
- that is why DEE ferments instead of mutating (a correct behavior this build
does not close: the ferment path never closes).

THE RULING-12 GATES (CLAUDE.md 1 row 12)
-----------------------------------------
G1  A NovaEcho CANNOT be constructed without a typed, non-empty origin
    reference into a real store record. UngroundedEchoViolation is raised at
    construction - the refusal IS the enforcement. An echo with no traceable
    origin is fabricated pressure, and fabricated pressure written into a
    fermentation index becomes doctrine-shaped over time.
G2  proposals() emits ONLY echoes at status MUTATED with scar linkage.
    "Unverified Echoes may not write doctrine" (Echo Protocol VII).
G3  A proposed new-form is RECOMBINATION of caller-supplied store-traceable
    fragments - every piece carries the id of the store record it came from,
    and the engine keeps a provenance map per emitted proposal. There is NO
    generative model anywhere in this path: an LLM's output is resolved
    consensus, and AUREA's founding axiom is survived contradiction.
G4  Nova is sole writer of the Nova Echo Index (`echo_index`) and of NOTHING
    else. Scar effects and CSA routing are REQUESTS parked on
    `scar_requests` / `csa_requests` (see PARKED SURFACES below); Codex is
    never a destination from here, in any form, ever.
G5  cycle() refuses to run under suppression: "Nova Engine must not initiate
    new symbolic expansion if RACM, Reflex Grid, or TCAML have active
    suppression or lockout states" (5a:1067). `suppressed` is a PARAMETER, and
    its caller is real: `aurea_core._nova_suppressed` performs the live
    RACM/Grid/TCAML read (wired 2026-07-24; this line used to end "the live
    RACM/Grid/TCAML read is Stage 2").

RULING 13 (2026-07-22): AN ECHO IS SPENT WHEN IT AUTHORS
--------------------------------------------------------
One echo backs one proposal, EVER. Authorship consumes: an echo that has
survived collapse carries exactly one act of doctrine-authorship in it, and
re-spending it would let a single survival multiply into many proposals -
resolved consensus wearing survived contradiction's face. Consumption is a
FIELD (`spent_on` = the proposal id, + `spent_at`), NOT a fifth
FermentationStatus - that enum is canon-closed at DORMANT/ACTIVE/DECAYING/
MUTATED and stays closed (Ruling 7's shape: a fact about an echo is not a
fermentation state; `status` remains MUTATED). `proposal_provenance` is
APPEND-ONLY: writing a key that already exists RAISES
ProvenanceOverwriteViolation - an overwrite means the one-proposal-ever gate
already failed upstream, and a forensic record is never overwritten
(Ruling 11's principle, second application). NOT over-narrowed: consumption
is per-ECHO, not per-doctrine - a second, distinct MUTATED echo may still
propose for the same strained doctrine; different survived material
legitimately bears on the same belief, each gated independently by DEE.

TIMER -> ELIGIBILITY ONLY (the overruled line)
----------------------------------------------
Nova Engine v2.0's core logic contains the literal step `Timer -> Mutation |
Collapse | CSA fallback` (5a:1113). That line is OVERRULED (CLAUDE.md 8) by
canon's own status definition a few lines later: `Mutated -> Doctrine
forged / scar fused / CSA rerouted` (5a:1123) - mutation is the RESULT of a
succeeded collapse attempt, not of elapsed time. A clock that mutates
doctrine is resolution without survival. Here, elapsed fermentation cycles
raise exactly one thing: COLLAPSE ELIGIBILITY (`NovaEcho.collapse_eligible`).
There is deliberately NO code path from cycle count to MUTATED; the only
writer of MUTATED is `record_collapse_result(success=True)` on an eligible
echo. Do not "complete" the timer line.

STAGE BOUNDARY - CLOSED 2026-07-24 (superseded in place, not deleted)
----------------------------------------------------------------------
This block used to read "This file is the ORGAN. Nothing imports it yet;
nothing here reaches into a wired module," and listed five parked seams. THAT
IS FALSE NOW and it is the dangerous kind of false: in this repo a header
claiming an organ is unwired is an INSTRUCTION TO WIRE IT.

Every seam below is CONNECTED. Kept as the record of what each one was waiting
for, and what now supplies it:
  - `cycle(suppressed=...)`         <- LIVE: `aurea_core._nova_suppressed`
                                       reads the accumulated RACM-authorized
                                       responses of the pass
  - `record_collapse_result(...)`   <- LIVE: `_nova_route_collapse` routes real
                                       EchoNet verdicts (SCARRED -> MUTATED,
                                       CONFIRMED -> DECAYING, SUSPENDED/PARADOX
                                       carried)
  - `proposals(...)`                <- LIVE: `_nova_proposals(signals)` hands
                                       the result to DEE.cycle's `proposals`
                                       argument; compass EAST reads
                                       `active_echoes()`
  - `csa_requests`                  <- LIVE: consumed into CSA
  - `scar_requests`                 <- STILL PARKED, and that is a RULING, not
                                       an omission (Ruling 15): `form_scar`
                                       wants a `weight` Nova does not honestly
                                       hold, and wiring it would mint
                                       zero-weight scars. Accumulates legibly.

DECLARED DORMANT (ICA dormant-trigger pattern - named, not fabricated)
----------------------------------------------------------------------
  - FUSION (Echo Protocol III.3; v2.0 fusion types Linear | Recursive |
    Scar-Merged): multi-echo merging into higher-order echoes. Engine v1 is
    SINGLE-ECHO by ruling. No fusion fields, no fusion branches - a merge
    that cannot happen yet must not have half an implementation inviting it.
  - NSC (Nova Synthesis Chamber, 5a 10) and NDR (Nova Density Regulator,
    Echo Protocol V saturation): unbuilt. Saturation/overload escalation
    is Stage-2+ territory under pressure-valve coordination.
  - Reawakening ("Reawakens echoes based on time-passed or paradox drift
    detection", 5a:262): DECAYING/DORMANT echoes are carried, not resolved;
    no reawakening heuristic is invented here.
  - Anchor Proximity Score / Symbolic Heat Index / Doctrine Proximity Score
    (Echo Protocol IV): each would require a COINED formula the corpus
    does not give. Omitted rather than guessed - an invented heat index is
    false pressure with decimal places.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Mapping, Optional, Sequence

from src.utils.models import Doctrine


# Canon eruption sources (Echo Protocol III.1: "Tagged with origin (e.g.,
# EchoNet filtration residue, scar conflict, CSA fragment)"; v2.0 input line:
# "Contradiction / Echo / Scar cluster / Doctrine strain"; SBSRE: "Failed
# contradiction loops escalate into Nova for fermentation"). CLOSED SET - a
# new origin kind requires a corpus citation, not an append.
ORIGIN_KINDS = frozenset({
    "scar",
    "echonet_verdict",
    "csa_fragment",
    "sbsre_abort",
    "doctrine_strain",
})

# RULING 20 (2026-07-25): the ONLY origin kind whose `origin_id` names a
# DOCTRINE, and therefore the only kind that can say which doctrine an echo
# is entitled to author for. The other four name a scar, a verdict, a CSA
# fragment or an aborted loop - real records, but not doctrine addresses.
# NOT a second closed set to keep in step with ORIGIN_KINDS: it is a member
# OF it, checked at import below, so a rename cannot silently orphan this
# rule. (A plain `assert` would vanish under -O; this does not.) Even if the
# check were somehow bypassed the failure direction is SAFE: an unmatched
# constant empties the author pool, every doctrine is refused, and nothing
# mutates. Fail-closed - the doctrine ferments, which is the correct default.
DOCTRINE_AUTHORSHIP_ORIGIN = "doctrine_strain"
if DOCTRINE_AUTHORSHIP_ORIGIN not in ORIGIN_KINDS:      # pragma: no cover
    raise ValueError(
        f"DOCTRINE_AUTHORSHIP_ORIGIN '{DOCTRINE_AUTHORSHIP_ORIGIN}' is not a "
        f"canon eruption source {sorted(ORIGIN_KINDS)} - Ruling 20's origin "
        f"match would silently refuse every doctrine."
    )


class UngroundedEchoViolation(Exception):
    """G1: a NovaEcho was constructed without a real, typed origin record.

    An echo with no traceable origin is fabricated pressure - it would sit in
    the fermentation index accumulating eligibility with nothing survived
    behind it, and G2 would eventually let it propose doctrine. This is not a
    warning to catch and proceed past: supply the origin record, or the echo
    does not exist.
    """


class UngroundedFragmentViolation(Exception):
    """G3: a proposal fragment does not name the store record it came from.

    Free text that traces to nothing is generative content wearing a
    fragment's clothes. Every piece of a proposed new-form carries the id of
    a store record; a fragment that can't say where it came from is refused
    at construction.
    """


class ProvenanceOverwriteViolation(Exception):
    """Ruling 13: an attempt to write `proposal_provenance` for a key that
    already exists.

    The provenance map is APPEND-ONLY. Its keys embed the authoring echo's
    id, and Ruling 13 spends an echo on its one authorship - so a colliding
    key cannot happen unless the one-proposal-ever gate has ALREADY failed
    upstream. This raise is the detector for that structural break, not an
    error to catch and route around: a forensic record is never overwritten
    (Ruling 11's principle, second application).
    """


class FermentationStatus(Enum):
    """Canon names EXACTLY (5a:1118-1123). Closed - do not extend."""
    DORMANT = "dormant"     # Awaiting context
    ACTIVE = "active"       # Accumulating symbolic pressure
    DECAYING = "decaying"   # Losing resonance
    MUTATED = "mutated"     # Doctrine forged / scar fused / CSA rerouted


# COINED (Ruling 12, 2026-07-22): canon demands fermentation before collapse
# eligibility ("Fermentation trigger check (convergence index >= threshold)",
# 5a:1109) but never gives the threshold. Reuses the CANON 5-cycle standard
# symbolic cycle horizon rather than inventing a fresh magnitude - the same
# pattern as RACM TTL_CYCLES=5 and DEE PRESSURE_HALF_LIFE=5: an echo must
# ferment through one full symbolic horizon before it may face collapse.
# Registered in Aurea Build/COINED_CONSTANTS.md. Never change it to make an
# echo eligible sooner.
FERMENTATION_ELIGIBILITY_CYCLES = 5


@dataclass(frozen=True)
class StoreFragment:
    """One store-traceable piece of proposal material (G3).

    `store` names the store the record lives in (e.g. "doctrines", "scars"),
    `record_id` the record within it, `content` the symbolic material being
    recombined. Construction refuses an untraceable fragment - the refusal
    is the enforcement, same shape as G1.
    """
    store: str
    record_id: str
    content: str = ""

    def __post_init__(self) -> None:
        if not self.store or not self.store.strip() \
                or not self.record_id or not self.record_id.strip():
            raise UngroundedFragmentViolation(
                "A proposal fragment must name the store and record id it "
                "came from (G3). Free text that traces to nothing may not "
                "enter a proposed doctrine form."
            )


@dataclass
class NovaEcho:
    """One Nova Echo (Echo Protocol IV metadata, the cheap-and-honest set).

    G1 lives in __post_init__: no origin, no echo. `origin_kind` is the typed
    class of the source record (closed set ORIGIN_KINDS); `origin_id` names
    the actual record in that source's store.
    """
    id: str
    origin_kind: str
    origin_id: str
    symbolic_domain: str = ""                                # IV Symbolic Domain
    scar_links: List[str] = field(default_factory=list)      # IV Scar Linkage Map
    status: FermentationStatus = FermentationStatus.DORMANT  # IV Fermentation Status
    fermentation_cycles: int = 0
    collapse_attempts: List[Dict[str, Any]] = field(default_factory=list)  # IV log
    created_at: datetime = field(default_factory=datetime.now)
    # Ruling 13: consumption. Set ONCE, by proposals() emission, in the same
    # operation that writes the provenance entry. A FIELD, not a status -
    # FermentationStatus is canon-closed and `status` stays MUTATED: being
    # spent is a fact about the echo's authorship, not a fermentation state.
    spent_on: Optional[str] = None          # the proposal id it authored
    spent_at: Optional[datetime] = None
    # Fusion History (IV) is DECLARED DORMANT - no field. Engine v1 is
    # single-echo by ruling; a fusion field with no fusion logic is an
    # invitation, not a record. See module docstring.

    def __post_init__(self) -> None:
        if self.origin_kind not in ORIGIN_KINDS:
            raise UngroundedEchoViolation(
                f"Unknown origin kind '{self.origin_kind}'. Canon eruption "
                f"sources are {sorted(ORIGIN_KINDS)} (Echo Protocol III.1). "
                f"An echo must erupt FROM something."
            )
        if not self.origin_id or not self.origin_id.strip():
            raise UngroundedEchoViolation(
                f"Echo of kind '{self.origin_kind}' names no origin record. "
                f"An echo with no traceable origin is fabricated pressure - "
                f"there is no placeholder origin and no default."
            )

    @property
    def is_spent(self) -> bool:
        """Ruling 13: this echo has authored its one proposal, ever."""
        return self.spent_on is not None

    @property
    def collapse_eligible(self) -> bool:
        """Timer -> ELIGIBILITY, and eligibility ONLY (the overruled-line
        boundary). True means this echo may now be SUBMITTED to collapse -
        it says nothing about surviving one."""
        return (self.status is FermentationStatus.ACTIVE
                and self.fermentation_cycles >= FERMENTATION_ELIGIBILITY_CYCLES)


class NovaEngine:
    """Symbolic hypothesis chamber. Owns ONE store: the Nova Echo Index.

    OWNERSHIP (Ruling 1 / G4): `echo_index` has exactly one writer - the
    methods of this class. Everything else Nova wants done to the world is a
    REQUEST list another owner may consume (ScarLogicCore for scar fusion,
    CSA for decay routing) or a RETURN VALUE the caller routes (proposals ->
    DEE). Codex is never a destination.
    """

    def __init__(self) -> None:
        # THE store (G4). Not named after any canonical store - `scars`,
        # `doctrines`, `threads` all have owners elsewhere.
        self.echo_index: Dict[str, NovaEcho] = {}

        # Legible refusal surface: every time the engine declines to act
        # (suppression, ineligible collapse result, ungated proposal), the
        # reason lands here instead of vanishing. The refusal is the answer;
        # this list is where the answer stays readable.
        self.refusals: List[Dict[str, Any]] = []

        # PARKED SURFACES (PSI-directive / RIL-Nova pattern - flagged
        # caller-less). Requests, not writes: Ruling 1 means Nova asks.
        #   scar_requests: "Mutated -> ... scar fused" (5a:1123) - fusion of
        #     the survived echo into scar tissue is ScarLogicCore's write.
        #     No consumer yet; Stage 2 routes these.
        #   csa_requests: failed collapse -> CSA / Veiled Thread decay
        #     (Echo Protocol III.5). CSA consumes these when wired.
        self.scar_requests: List[Dict[str, Any]] = []
        self.csa_requests: List[Dict[str, Any]] = []

        # Provenance map per emitted proposal id (G3): every piece of every
        # proposal, traceable to the store record it came from. Written only
        # at emission, APPEND-ONLY (Ruling 13) - all writes go through
        # _append_provenance, which raises on an existing key. Read by anyone.
        self.proposal_provenance: Dict[str, List[Dict[str, str]]] = {}

        self._seq = 0

    def _next_id(self) -> str:
        self._seq += 1
        return f"NE-{self._seq:04d}"

    def _append_provenance(self, proposal_id: str,
                           provenance: List[Dict[str, str]]) -> None:
        """THE only write path into `proposal_provenance` (Ruling 13).

        Append-only: an existing key raises ProvenanceOverwriteViolation.
        The raise is a detector, not a validation nicety - a colliding key
        means an echo authored twice, which the spent gate should have made
        impossible. Do not catch it here or soften it to a merge/skip.
        """
        if proposal_id in self.proposal_provenance:
            raise ProvenanceOverwriteViolation(
                f"proposal_provenance already holds '{proposal_id}'. The "
                f"provenance map is append-only (Ruling 13) - an overwrite "
                f"attempt means the one-proposal-ever gate failed upstream. "
                f"A forensic record is never overwritten."
            )
        self.proposal_provenance[proposal_id] = provenance

    # -----------------------------------------------------------------
    # Eruption (Echo Protocol III.1)
    # -----------------------------------------------------------------

    def erupt(self, origin_kind: str, origin_id: str,
              symbolic_domain: str = "",
              scar_links: Optional[List[str]] = None) -> NovaEcho:
        """Detect an eruption: admit a new echo to the index, DORMANT.

        G1 is enforced by NovaEcho construction itself - this method adds
        nothing to the gate and can subtract nothing from it. The echo enters
        DORMANT ("Awaiting context"); its first unsuppressed cycle activates
        it into the fermentation pressure phase.
        """
        echo = NovaEcho(
            id=self._next_id(),
            origin_kind=origin_kind,
            origin_id=origin_id,
            symbolic_domain=symbolic_domain,
            scar_links=list(scar_links or []),
        )
        self.echo_index[echo.id] = echo
        return echo

    # -----------------------------------------------------------------
    # Read surface (reads are free, Ruling 1) - what the compass consumes
    # -----------------------------------------------------------------

    def active_echoes(self) -> List["NovaEcho"]:
        """The echoes that PULL: status ACTIVE (Echo Protocol IV,
        "Accumulating symbolic pressure") - not yet collapsed, but exerting
        emergent-vector pull. This is CSE's EAST surface (compass canon:
        "Emergent Vectors - Nova echoes, not yet collapsed, but pulling").

        A pure read over Nova's own index - it writes nothing and owns
        nothing new (G4 intact). DORMANT echoes await context and do not yet
        pull; DECAYING/MUTATED have left the emergent phase. Deliberately NO
        per-echo `pull`/heat magnitude: the Symbolic Heat Index (Echo
        Protocol IV) is an un-coined score, and CSE weights each echo at its
        own getattr-default (1.0) - so EAST mass is an honest COUNT of
        pulling echoes, not a fabricated heat sum.
        """
        return [e for e in self.echo_index.values()
                if e.status is FermentationStatus.ACTIVE]

    # -----------------------------------------------------------------
    # Fermentation (Echo Protocol III.2) - G5 gate at cycle entry
    # -----------------------------------------------------------------

    def cycle(self, suppressed: bool, source: str = "unspecified") -> List[str]:
        """One fermentation pass. Returns ids of collapse-ELIGIBLE echoes.

        G5: `suppressed` is the caller's report of RACM/Grid/TCAML
        suppression or lockout state (5a:1067). It is a PARAMETER rather than a
        read Nova performs itself - an honest seam, and the caller is now real:
        `aurea_core._nova_suppressed` supplies it from the pass's accumulated
        RACM-authorized responses (wired 2026-07-24; this line used to say
        "Stage 2 wires the live check"). Under suppression NOTHING advances: no
        activation, no
        aging, no eligibility - one legible refusal, empty return.

        Aging raises ELIGIBILITY only. MUTATED is not reachable from here -
        see the module docstring's overruled-line note.
        """
        if suppressed:
            self.refusals.append({
                "action": "cycle",
                "reason": "suppression active (RACM/Grid/TCAML) - Nova must "
                          "not initiate symbolic expansion (5a:1067)",
                "source": source,
                "timestamp": datetime.now().isoformat(),
            })
            return []

        eligible: List[str] = []
        for echo in sorted(self.echo_index.values(), key=lambda e: e.id):
            if echo.status is FermentationStatus.DORMANT:
                # Context arrived: a live, unsuppressed cycle. Pressure
                # accumulation begins next pass.
                echo.status = FermentationStatus.ACTIVE
            elif echo.status is FermentationStatus.ACTIVE:
                echo.fermentation_cycles += 1
            # DECAYING and MUTATED do not age: decay routing and reawakening
            # are declared dormant (module docstring); mutation is terminal
            # for Engine v1.
            if echo.collapse_eligible:
                eligible.append(echo.id)
        return eligible

    # -----------------------------------------------------------------
    # Collapse result (Echo Protocol III.4) - the Stage-1 seam
    # -----------------------------------------------------------------

    def record_collapse_result(self, echo_id: str, success: bool,
                               detail: str = "",
                               pressure: Optional[float] = None) -> bool:
        """Record the outcome of a collapse attempt on an ELIGIBLE echo.

        THE ONLY WRITER OF MUTATED. Nova does not fabricate the collapse itself
        - whoever ran the attempt reports it here, and that caller is now real:
        `aurea_core._nova_route_collapse` routes genuine EchoNet verdicts
        (wired 2026-07-24; this line used to say "EchoNet/DEE routing is
        Stage 2"). success=True on an eligible echo -> MUTATED
        ("Doctrine forged / scar fused / CSA rerouted", 5a:1123) + a parked
        scar-fusion REQUEST. success=False -> DECAYING + a parked CSA/
        Veiled-Thread routing REQUEST (Echo Protocol III.5).

        An attempt on an unknown or ineligible echo is REFUSED, legibly,
        with no state change: an echo that has not fermented through its
        horizon has not earned a collapse verdict either way.
        """
        echo = self.echo_index.get(echo_id)
        if echo is None:
            self.refusals.append({
                "action": "record_collapse_result",
                "echo_id": echo_id,
                "reason": "no such echo in the Nova Echo Index",
                "timestamp": datetime.now().isoformat(),
            })
            return False
        if not echo.collapse_eligible:
            self.refusals.append({
                "action": "record_collapse_result",
                "echo_id": echo_id,
                "reason": f"echo not collapse-eligible (status="
                          f"{echo.status.value}, cycles="
                          f"{echo.fermentation_cycles}/"
                          f"{FERMENTATION_ELIGIBILITY_CYCLES})",
                "timestamp": datetime.now().isoformat(),
            })
            return False

        echo.collapse_attempts.append({
            "success": success,
            "detail": detail,
            "at_cycle": echo.fermentation_cycles,
            "timestamp": datetime.now().isoformat(),
        })
        if success:
            echo.status = FermentationStatus.MUTATED
            # RULING 15 (2026-07-24): the TRIGGER for this request is
            # UNRULED, not just its consumer. 5a:1123's "Mutated -> Doctrine
            # forged / scar fused / CSA rerouted" does not say whether
            # "scar fused" is a THIRD outcome cumulative with "doctrine
            # forged" on every successful collapse (fires below, as written)
            # or an ALTERNATIVE to it (only when doctrine authorship does
            # NOT happen - which this method cannot know, since proposals()
            # runs later and separately). Firing on every success is the
            # code's existing, unruled reading, left AS-IS. Ruling 15 parks
            # the CONSUMER (ScarLogicCore - no honest weight exists), not
            # this trigger. Do not "fix" this into looking decided either
            # way.
            self.scar_requests.append({
                "request": "fuse_scar",
                "echo_id": echo.id,
                "origin_kind": echo.origin_kind,
                "origin_id": echo.origin_id,
                "scar_links": list(echo.scar_links),
                "timestamp": datetime.now().isoformat(),
            })
        else:
            echo.status = FermentationStatus.DECAYING
            self.csa_requests.append({
                "request": "route_to_csa",
                "echo_id": echo.id,
                "reason": "collapse attempt failed - decay/suspension "
                          "routing (Echo Protocol III.5)",
                # The REAL pressure of the collapse attempt that failed, when
                # the caller has one (Stage 2b: EchoNet's pressure_generated).
                # None = unrecorded; the consumer must not invent one.
                "pressure": pressure,
                "timestamp": datetime.now().isoformat(),
            })
        return True

    # -----------------------------------------------------------------
    # Proposals (G2 + G3) - what Stage 2 hands to DEE.cycle(proposals=...)
    # -----------------------------------------------------------------

    def proposals(self, fragments: Mapping[str, Sequence[StoreFragment]]
                  ) -> Dict[str, Doctrine]:
        """Emit doctrine PROPOSALS keyed by the strained doctrine's id -
        the exact shape DEE.cycle's `proposals` seam consumes
        (`proposals.get(watched.doctrine_id)`).

        `fragments` maps each strained doctrine's id to the store-traceable
        material supplied for it - the strained doctrine's own content, scar
        records, origin residue. Every value is a StoreFragment, already
        provenance-gated at construction (G3).

        G2: only a MUTATED echo WITH scar linkage may back a proposal
        ("Unverified Echoes may not write doctrine", Echo Protocol VII).
        Engine v1 is single-echo: one echo backs at most one proposal per
        call.

        RULING 20 (2026-07-25) - AUTHORSHIP IS MATCHED BY ORIGIN, NEVER BY
        SORT ORDER. An echo may back a proposal for doctrine D only if
        `origin_kind == "doctrine_strain"` AND `origin_id == D`. This method
        previously did `echo = qualifying.pop(0)` - drawing from a globally
        id-sorted list while iterating `sorted(fragments)`, two orderings
        with NO relationship to each other. With two doctrines strained at
        once (which `_nova_erupt_from_doctrine_strain` produces routinely -
        one live echo per strained doctrine), the pairing silently crossed.

        THE DAMAGE WAS NOT MERELY MISATTRIBUTED AUTHORSHIP. The emitted
        proposal below merges `echo.scar_links` into its own `scar_links`,
        and DEE then hands `scar_links[0]` to SAE as the mutation's collapse
        lineage - so a mispaired echo writes scars from a DIFFERENT
        doctrine's collapse into the successor's permanent lineage. The
        successor would carry visible evidence of a fracture it never
        survived: lineage forgery by accident, arriving through a seam
        neither G2 nor G3 watches.

        No origin-matched echo for D -> the EXISTING refusal path: D
        ferments, the refusal is recorded. NEVER a substitute. The other
        four canon origin kinds (scar, echonet_verdict, csa_fragment,
        sbsre_abort) have no defined doctrine-authorship semantics - their
        `origin_id` names a scar or a verdict, not a doctrine - so they are
        excluded LEGIBLY (a recorded refusal naming the echo), not silently
        skipped. Admitting one is a ruling, not an edit.

        Ruling 13: authorship CONSUMES. A spent echo (`spent_on` set) never
        qualifies again - one echo, one proposal, ever. Emission marks the
        echo spent in the same operation that appends its provenance entry
        (which is append-only and raises on collision). Consumption is
        per-ECHO, not per-doctrine: a later, distinct MUTATED echo may
        still propose for the same strained doctrine.

        G3: the new form is pure RECOMBINATION. Every piece of the emitted
        Doctrine's description carries its [store:record_id] tag inline, and
        `proposal_provenance[new_id]` holds the full structured map. The
        proposal must include material from the strained doctrine itself -
        a fragment with store="doctrines" and record_id == the target id;
        recombining a doctrine you hold no material from would be invention.
        No generative model touches any of this, ever.
        """
        qualifying = [
            e for e in sorted(self.echo_index.values(), key=lambda e: e.id)
            if e.status is FermentationStatus.MUTATED and e.scar_links
            and not e.is_spent  # Ruling 13: authorship consumed the others
        ]
        # Ruling 20: partition BEFORE any doctrine is considered. Only a
        # doctrine_strain echo names a doctrine in `origin_id`; every other
        # kind is excluded, and the exclusion is recorded rather than dropped
        # on the floor - an echo that survived collapse and has nowhere to go
        # is a real unresolved condition, and it stays legible.
        authors = [e for e in qualifying
                   if e.origin_kind == DOCTRINE_AUTHORSHIP_ORIGIN]
        for echo in qualifying:
            if echo.origin_kind == DOCTRINE_AUTHORSHIP_ORIGIN:
                continue
            self.refusals.append({
                "action": "proposals",
                "echo_id": echo.id,
                "origin_kind": echo.origin_kind,
                "origin_id": echo.origin_id,
                "reason": f"origin kind '{echo.origin_kind}' has no defined "
                          f"doctrine-authorship semantics (Ruling 20) - its "
                          f"origin_id names a store record, not a doctrine. "
                          f"Only a '{DOCTRINE_AUTHORSHIP_ORIGIN}' echo may "
                          f"author, and admitting another kind is a ruling, "
                          f"not an edit.",
                "timestamp": datetime.now().isoformat(),
            })

        emitted: Dict[str, Doctrine] = {}

        for doctrine_id in sorted(fragments):
            frags = list(fragments[doctrine_id])
            if not qualifying:
                self.refusals.append({
                    "action": "proposals",
                    "doctrine_id": doctrine_id,
                    "reason": "no MUTATED, scar-linked echo available (G2) - "
                              "unverified echoes may not write doctrine",
                    "timestamp": datetime.now().isoformat(),
                })
                continue
            if not any(f.store == "doctrines" and f.record_id == doctrine_id
                       for f in frags):
                self.refusals.append({
                    "action": "proposals",
                    "doctrine_id": doctrine_id,
                    "reason": "no fragment from the strained doctrine itself "
                              "(store='doctrines', record_id matching) - "
                              "recombination requires the material being "
                              "recombined (G3)",
                    "timestamp": datetime.now().isoformat(),
                })
                continue

            # RULING 20: the echo that erupted from THIS doctrine's own
            # strain, or none. `not is_spent` is re-checked because an
            # earlier doctrine in this same call may already have consumed
            # it (Ruling 13 - one echo, one proposal, EVER).
            candidates = [e for e in authors
                          if e.origin_id == doctrine_id and not e.is_spent]
            if not candidates:
                self.refusals.append({
                    "action": "proposals",
                    "doctrine_id": doctrine_id,
                    "reason": "no MUTATED, scar-linked echo whose ORIGIN is "
                              "this doctrine (Ruling 20) - a proposal is "
                              "authored by the echo erupted from this "
                              "doctrine's own strain, and no substitute is "
                              "accepted. The doctrine ferments.",
                    "timestamp": datetime.now().isoformat(),
                })
                continue
            # Deterministic when two live echoes share an origin (legitimate -
            # consumption is per-ECHO, not per-doctrine, Ruling 13): oldest
            # id first. Never dict order, never the caller's iteration order.
            echo = min(candidates, key=lambda e: e.id)
            new_id = f"{doctrine_id}::nova::{echo.id}"

            # Recombination: every piece tagged inline with its source
            # record. Concatenation and tagging ONLY - no synthesis.
            new_form = " + ".join(
                f"[{f.store}:{f.record_id}] {f.content}".rstrip()
                for f in frags
            )

            provenance: List[Dict[str, str]] = [
                {"store": f.store, "record_id": f.record_id} for f in frags
            ]
            provenance.append({"store": "nova_echo_index",
                               "record_id": echo.id})
            provenance.append({"store": echo.origin_kind,
                               "record_id": echo.origin_id})
            # Ruling 13 - ONE operation: append the forensic record (raises
            # on collision, leaving the echo unspent and state consistent),
            # then consume the echo. Nothing between the two.
            self._append_provenance(new_id, provenance)
            echo.spent_on = new_id
            echo.spent_at = datetime.now()

            emitted[doctrine_id] = Doctrine(
                id=new_id,
                # Structural address, not truth content: the truth content
                # is entirely the recombined `description` below.
                name=f"{doctrine_id} (nova recombination via {echo.id})",
                mutation_lineage=[doctrine_id, echo.id],
                scar_links=sorted(set(
                    list(echo.scar_links)
                    + [f.record_id for f in frags if f.store == "scars"]
                )),
                # A proposal is not yet doctrine - it has not survived DEE's
                # gate. SAE/DEE own what status an EXECUTED mutation gets.
                status="proposed",
                description=new_form,
                tca_tags=[f"prov:{p['store']}:{p['record_id']}"
                          for p in provenance],
            )

        return emitted
