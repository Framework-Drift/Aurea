"""M7-a: the derived view -- the Executive's ENTIRE working state, computed.

L10: the component that loops holds no constitutive state. This module is the
enforcement in code shape: ONE frozen dataclass and ONE pure function. There is
no cache, no store, no file, no clock, and no write path anywhere in it. Two
calls over the same ledgers yield equal views; a view that could differ from
its own recomputation would be owned state wearing a derivation's name.

DUCK-TYPED READ HANDLES, NEVER IMPORTED (episode_record.py's M3-B precedent
verbatim): this module imports no ledger class, so the enforcement-by-scope
pins stay exact and a handle handed to a reader for one question cannot be
talked into answering others. The handles are used for their named read
methods ONLY: `open_items()`, `commitments()`, `resolutions()`, `read_all()`.

THE CHAIR IS DERIVED, NEVER HARDWIRED (ninety-eighth entry): the
delegated-cognition chair's state is a function of whether the M5 qualification
verdict has been registered as a consumed acquisition. Before that record
exists the chair is UNREGISTERED -- a visible state, not an error. After it,
EMPTY_BY_REFUSED_VERDICT. There is NO qualified state in this vocabulary,
because no package has ever cleared the gate; adding one is a ruling that
arrives with the first QUALIFIED verdict, not before (M7_GROUNDING section 3).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, Tuple

# The payload discriminator for the consumed-verdict acquisition. A closed,
# exact string: the derivation below matches it with equality, never with
# heuristics, so a payload that ALMOST looks like a verdict registration is
# nothing at all.
VERDICT_PAYLOAD_KIND = "M5_QUALIFICATION_VERDICT_CONSUMED"


class ChairState(str, Enum):
    """The delegated-cognition chair, v1: exactly two states.

    UNREGISTERED is the loop before its first submission -- the chair's state
    is not yet on the record, and the view says so rather than assuming.
    EMPTY_BY_REFUSED_VERDICT is the designed initial condition after the loop
    has read the verdict: the chair exists, the gate swung, nobody sits in it.
    """

    UNREGISTERED = "unregistered"
    EMPTY_BY_REFUSED_VERDICT = "empty_by_refused_verdict"


@dataclass(frozen=True)
class DerivedView:
    """One observation of the kernel, frozen. Equality is field equality.

    `open_obligations`: obligation ids with OPEN status, ledger order.
    `unresolved_predictions`: prediction ids committed and not yet resolved,
        commitment order.
    `committed_goals`: goal ids in commitment (append) order.
    `chair`: the delegated-cognition chair state, derived per module docstring.
    `verdict_acquisition_id`: the ACQ- id of the consumed-verdict record when
        the chair is EMPTY_BY_REFUSED_VERDICT, else None. Carried so any
        consumer of the view can cite the record rather than the view.
    """

    open_obligations: Tuple[str, ...]
    unresolved_predictions: Tuple[str, ...]
    committed_goals: Tuple[str, ...]
    chair: ChairState
    verdict_acquisition_id: Optional[str]


def _verdict_registration(acquisitions: Any) -> Optional[str]:
    """Return the ACQ- id of the consumed-verdict record, if exactly present.

    Scans `read_all()` for a record whose payload parses as JSON and carries
    `kind == VERDICT_PAYLOAD_KIND`. A payload that fails to parse is not a
    candidate -- the registration path writes canonical JSON, so anything else
    is some other arrival that happens to share bytes-shape, and guessing
    would be classification by resemblance.
    """
    for record in acquisitions.read_all():
        payload = getattr(record, "payload", None)
        if not isinstance(payload, str):
            continue
        try:
            parsed = json.loads(payload)
        except (ValueError, TypeError):
            continue
        if isinstance(parsed, dict) and parsed.get("kind") == VERDICT_PAYLOAD_KIND:
            return getattr(record, "acquisition_id", None)
    return None


def derive(obligations: Any, predictions: Any, goals: Any,
           acquisitions: Any) -> DerivedView:
    """Compute the Executive's working state from kernel ledgers. Pure.

    Reads only. Raises whatever the ledgers raise -- an unreadable kernel store
    is the kernel's fact to assert, and a derivation that swallowed it would be
    inventing an empty world.
    """
    open_obligations = tuple(
        str(item["obligation_id"]) for item in obligations.open_items())

    resolved_ids = frozenset(
        str(res.prediction_id) for res in predictions.resolutions())
    unresolved = tuple(
        str(com.prediction_id) for com in predictions.commitments()
        if str(com.prediction_id) not in resolved_ids)

    committed_goals = tuple(
        str(com.goal_id) for com in goals.commitments())

    verdict_id = _verdict_registration(acquisitions)
    chair = (ChairState.EMPTY_BY_REFUSED_VERDICT if verdict_id is not None
             else ChairState.UNREGISTERED)

    return DerivedView(
        open_obligations=open_obligations,
        unresolved_predictions=unresolved,
        committed_goals=committed_goals,
        chair=chair,
        verdict_acquisition_id=verdict_id,
    )
