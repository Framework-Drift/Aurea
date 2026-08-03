"""
model_provider.py - RULING 70 / DOCKET O item O6: EXTERNAL WORLD-MODEL ENGINES
AS SENSOR-TIER PROVIDERS. The docket's last item.

    A model is a SOURCE, not a SENSOR OF TRUTH. What it says is recorded as a
    claim, and a claim answers to collapse like any other claim.

THE GATE FINDING, recorded here because the gate is this module's foundation
-----------------------------------------------------------------------------
BAR §1 bars learned or generative models IN THE TRUTH-CONTENT PATH - rendering
verdicts, influencing arbitration, entering collapse scoring. O6 AS REGISTERED
REQUIRES NONE OF THAT, which is the only reason this file exists.

A world-model engine's output enters as a RECORDED CLAIM: `MODEL_PREDICTION`, a
full O1 ancestry declaration, routed through the SAME perception pipeline and
the SAME collapse machinery as any human assertion - canon's own XAIG law
verbatim: external input enters the same collapse machinery, NOT A BYPASS. The
model renders no verdict, writes no store, weights no net and pushes no
arbitration. It sits on the CLAIM side of the arbitration boundary, exactly
where a human asserter sits, and Ruling 12 G3's bar point is ARBITRATION.

Recording what a model said is L1's own move: EVIDENCE OF BELIEF, NEVER
EVIDENCE OF REALITY. "Sensor-tier provider" means INGRESS-LAYER provider, not
truth-sensor - outputs land in the PREDICTED tier, which Ruling 63 already
derived from `origin_kind` with no new machinery, and OBSERVED remains
structurally unproducible and untouched.

**Had O6 required a model's judgment to MEAN anything to a verdict, Ruling 70
would have been a second refusal in Ruling 62's shape.** Anything added here
that lets model output influence a verdict OTHER than by being a claim among
claims retroactively fails the gate this module stands on.

WHAT THIS MODULE IS: PURE PLUMBING, AND DELIBERATELY BORING
-------------------------------------------------------------
Two functions. One builds the O1 declaration for a model assertion; the other
builds it and hands the text to `process_input`. There is no second ingress, no
bypass, and not one line of the pipeline is reimplemented here.

THE COLLABORATOR IS THE CALLABLE, NOT THE CORE - a judgment call, stated.
Ruling 70's handoff permits either ("an `AureaCore` or its `process_input`
callable"), and the narrower handle is taken for Ruling 33's reason: **the
adapter cannot reach a store it is never handed.** Given an `AureaCore` this
module would hold the Codex, the scar store and SAE and be trusted not to touch
them; given `core.process_input` it holds a way to perceive a claim and nothing
else. ENFORCEMENT BY SCOPE, not by discipline. A caller with a core passes
`core.process_input` - one attribute access, and the whole bypass surface is
gone.

THE TEXT GOES THROUGH VERBATIM (res.7)
----------------------------------------
No strip, no normalization, no truncation, no summarization, no cleaning.
**A TRANSFORMED ASSERTION IS A DIFFERENT ASSERTION**, and this ledger records
what was asserted. Whatever the pipeline itself does downstream (SPL strips) is
the pipeline's business and is applied to every claim alike; what must not
happen is this layer editing a claim on its way in and filing the edit as the
original.

THE MODEL NEVER INITIATES (res.2)
-----------------------------------
This module INGESTS a response someone else obtained. There are no network
imports, no client libraries, no retry loops, no polling and nothing async -
AST-pinned, not merely absent. Querying, orchestration, model selection,
parallel prompting, prompt caps and tether autonomy are MLOC's unbuilt
territory, gated besides by AVT.017 (no tool acts unless traceable to collapse).

NO AUTO-COMMIT (res.5)
------------------------
If a model's output is prediction-shaped, THE CALLER commits it to O3 through
Ruling 61's existing API, explicitly, with the linkage the caller chooses. This
module carries NO import of the prediction ledger, pinned as ABSENCE - because
classifying "is this text a prediction" is INFERENCE, which is BAR §2-adjacent
and which this adapter must not perform. L2 then governs whatever is committed:
falsification pressures its chain, success promotes nothing.

DECLARED OUT, each with its owner
-----------------------------------
  * MODEL QUERYING / ORCHESTRATION -> MLOC, under AVT.017's binding conditions,
    adjacent to Docket Q's QL5.
  * TRUST DERIVATION from O3 track records -> its own ruling, the day a track
    record exists. NO per-model trust scores, NO model weighting, NO cross-model
    consensus counting exists here, and none is a near-miss away: this module
    holds no state at all, so there is nothing for a counter to accumulate on.
    Two models asserting the same text are TWO CLAIMS with TWO CLM ids and
    DISTINCT ASSERTERS - and Ruling 60's counter never says "independent",
    because two models sharing training corpora is exactly the shared-ancestry
    case O2 exists to keep honest.
  * LCAE's collapse-survivability arbitration across models -> UNBUILT, its own
    future work.
  * ANY Codex or TCA write from anything model-shaped -> PERMANENT, the
    docket's founding refusal.
  * RESPONSE-CONTENT transformation, summarization or cleaning -> refused
    above; the text goes through verbatim.

COINS NOTHING: no new enum member (`MODEL_PREDICTION` has been in O1's closed
set since Ruling 58, included then precisely so O6 would never have to reopen a
closed enum), no threshold, no score, no magnitude. One module of plumbing.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

# THE RECORD VOCABULARY ONLY - never the ledger, and the distinction is Ruling
# 63's own precedent: IMPORTING A RECORD TYPE IS NOT CONSUMING A STORE. This
# module names no path, opens no file and holds no ledger handle; the ledger is
# reached exactly once, by `process_input`, on the far side of a callable this
# module is handed.
from src.external.claim_ancestry import (ANCESTRY_FIELDS, AncestryField,
                                         OriginDeclaration, OriginKind, absent,
                                         provided)

# The four ancestry surfaces a CALLER may declare about a model assertion.
# `asserted_by` is deliberately NOT among them: it IS the declared model
# identity, and letting a caller override it would let a model assertion be
# filed under someone else's name.
CALLER_DECLARABLE_FIELDS = tuple(
    name for name in ANCESTRY_FIELDS if name != "asserted_by")


def model_declaration(
    model_identity: str,
    *,
    basis: Optional[AncestryField] = None,
    replication_refs: Optional[AncestryField] = None,
    connecting_assumptions: Optional[AncestryField] = None,
    defeaters: Optional[AncestryField] = None,
) -> OriginDeclaration:
    """The O1 declaration for a model assertion. RULING 70 res.1.

    `origin_kind` is `MODEL_PREDICTION` and `asserted_by` is the DECLARED model
    identity **exactly as the caller gave it** - recorded as declared, NEVER
    verified, NEVER normalized, NEVER parsed into parts. L1: a declaration is a
    fact about the declaration. This module cannot check that a string naming a
    provider and a version is true, and a layer that cannot verify something
    must not appear to have verified it, so the string is carried byte-identical
    into the record and the reader is told exactly what was claimed.

    THE IDENTITY IS ONE STRING, NOT THREE FIELDS - a judgment call, stated.
    Ruling 70 res.1 says "the DECLARED model identity STRING exactly as the
    caller gave it (provider/model/version)", and pin (a) asserts the recorded
    asserter is BYTE-IDENTICAL to the caller's declaration. Composing one string
    out of three parameters would make "byte-identical to the caller's
    declaration" unanswerable - the adapter would have authored the identity it
    claims to have merely recorded.

    EVERY O1 FIELD IS POPULATED, and "populated" means EVERY FIELD CARRIES AN
    EXPLICIT RECORDED STATE - not that every field carries a value. Ruling 58's
    three states are the whole vocabulary here, and ABSENT is a real answer: it
    says the channel said nothing. Manufacturing a `basis` for a model
    assertion because a model plainly HAS one in some sense would be L3's
    fabrication class - a fact stored because a field existed to hold it -
    which is the exact defect Ruling 58 was written to close.

    THE ABSENT DEFAULT IS ALSO THE HONEST GENEALOGY ANSWER, and this is worth
    stating because it looks like under-reporting and is not. With `basis` and
    `replication_refs` ABSENT, Ruling 60 reads two model claims as **UNKNOWN**
    rather than as two corroborating origins - which is correct and is res.4's
    own reasoning: two models with nothing declared about their descent may
    share a training corpus nobody wrote down. UNKNOWN never counts as
    corroboration; a caller who genuinely knows the descent declares it and
    gets a recorded answer instead.

    NOTED, NOT DECIDED - AN EMPTY IDENTITY STRING. `model_identity=""` is
    accepted here, and two records carrying it would compare EQUAL and be read
    by `source_genealogy.shares_recorded_asserter` as ONE SHARED ASSERTER -
    the identical failure mode Ruling 64 res.7 closed for `provided(None)`.
    It is NOT refused here because refusing it is a value judgment Ruling 70
    does not delegate, and the vocabulary's own guard lives in
    `claim_ancestry.provided()`, which is outside this pass's scope. FLAGGED
    for the board rather than decided in passing.
    """
    if not isinstance(model_identity, str):
        raise TypeError(
            f"model_identity must be str, got {type(model_identity).__name__}. "
            f"Ruling 70 res.1 records the DECLARED model identity STRING "
            f"exactly as the caller gave it; a non-string identity cannot be "
            f"carried byte-identical into the record.")

    declared = {
        "basis": basis,
        "replication_refs": replication_refs,
        "connecting_assumptions": connecting_assumptions,
        "defeaters": defeaters,
    }
    for name, value in declared.items():
        if value is not None and not isinstance(value, AncestryField):
            raise TypeError(
                f"{name} must be an AncestryField - use provided(...) / "
                f"declared_none() / absent(). A bare value cannot say WHICH "
                f"of Ruling 58's three answers it is.")

    return OriginDeclaration(
        kind=OriginKind.MODEL_PREDICTION,
        asserted_by=provided(model_identity),
        **{name: (value if value is not None else absent())
           for name, value in declared.items()},
    )


def ingest_model_assertion(
    perceive: Callable[..., Dict[str, Any]],
    response_text: str,
    model_identity: str,
    *,
    basis: Optional[AncestryField] = None,
    replication_refs: Optional[AncestryField] = None,
    connecting_assumptions: Optional[AncestryField] = None,
    defeaters: Optional[AncestryField] = None,
) -> Dict[str, Any]:
    """Record a model's response as a claim and route it through the pipeline.

    `perceive` is `AureaCore.process_input` (or an equally-shaped callable),
    INJECTED - this module never constructs a core, owns one, or reaches for a
    global. See the module docstring on why the callable and not the core.

    RULING 68'S DOOR IS THIS ADAPTER'S DOOR (res.6). The input contract is
    `str`, and a non-`str` response is refused HERE, at this boundary, BEFORE
    the pipeline is ever called - so a malformed ingest mints no claim id,
    writes no ledger line and perceives nothing. A plain `TypeError` and
    deliberately not a coined exception class: a violated type contract is the
    language's own vocabulary, and this is a caller's ordinary mistake rather
    than one of AUREA's guards firing (Docket N's form).

    THE RESULT IS RETURNED UNMODIFIED. Nothing is added to it and nothing is
    removed from it - the adapter has no verdict of its own to contribute, and
    a result this layer decorated would be a model-shaped surface on the far
    side of the arbitration boundary.
    """
    if not isinstance(response_text, str):
        raise TypeError(
            f"response_text must be str, got {type(response_text).__name__}. "
            f"A model response that is not text is not a claim, and an arrival "
            f"that is not a claim is not perceived (Ruling 68, one layer down).")

    declaration = model_declaration(
        model_identity,
        basis=basis,
        replication_refs=replication_refs,
        connecting_assumptions=connecting_assumptions,
        defeaters=defeaters,
    )

    # VERBATIM (res.7). `response_text` is passed exactly as received - no
    # strip, no normalization, no truncation. A transformed assertion is a
    # different assertion.
    return perceive(response_text, origin=declaration)
