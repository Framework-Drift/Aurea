# CROSS-REPO PROTOCOL

**Identity**: CROSS_REPO_PROTOCOL v1.0.0
**Ratified**: 2026-08-16, by the Constitutional Principal, in session
**Status**: ACTIVE -- governs all work spanning the AUREA repository and the AUREA-Foundry repository
**Supersedes**: the carried-work-order model (work orders drafted in the Projects lane, executed in a separate Foundry pipeline, verdicts returned by the architect). That model's records remain valid historical evidence; its findings, precedents, and house laws carry forward in full.
**Provenance note**: a prior version of this document was adjudicated in chat on 2026-08-16 under the carried-work-order model; its write timed out and its text was lost with the session. This document is a fresh draft under the one-roof model ratified the same day, not a recovery of the lost text.

---

## 1. The one-roof model

Both repositories are built under one governed lane, in one project, by one working session.

- **AUREA** (`C:\Users\huber\Desktop\Aurea`) -- the system under construction.
- **AUREA-Foundry** (`C:\Projects\AUREA-Foundry`) -- the evaluation lab: capability acquisition, qualification instruments, corpora, protocols, runs.

The manifest (`integration_review_manifest.md`, beside this document) remains the single governing record of the build. Foundry work performed under this roof still lands in the Foundry's own records (`FOUNDRY_STATUS.md`, committed review documents, references/) as the lab's record -- and still becomes build law only when a manifest entry rules on it. One roof, still two records, still one authority.

**Location-never-authority extends across the repo boundary.** No fact is true because of which repository records it. A Foundry acceptance is evidence; the manifest ruling on it is law.

## 2. Switch discipline

Work moves between repositories only through a **declared switch**. A switch is never implied by the content of an edit.

1. **Declaration form**: `SWITCH: AUREA -> FOUNDRY` or `SWITCH: FOUNDRY -> AUREA`, stated in the session at the moment of the switch.
2. **A forward switch names its cause**: the specific AUREA work item that is blocked, and the specific Foundry work that unblocks it. A switch without a named blocking item is a scope question and stops for a ruling.
3. **A return switch names its yield**: what landed in Foundry (commit, files, review state) and which blocked item is now unblocked.
4. **No interleaved edits**: between a forward declaration and its return, disk writes go to the active repository only. Reads of the inactive repository are always permitted (verification is never blocked).
5. **Switches are cited in the record**: the manifest entry covering the work names each switch and its blocking item, so the record shows why the lane was in the other repository.

## 3. Session-open discipline (dual-repo, unconditional)

Every session opens with both repositories verified, regardless of which is active:

1. `AUREA_PIVOT_ARCHITECTURE.md` present on disk and cited by the standing PATH.
2. AUREA manifest tail read (tail param -- the file is ~1MB).
3. Foundry `FOUNDRY_STATUS.md` checked by targeted grep/read of its current-phase and latest-entry sections (the file is sectioned, not append-only; tail-only reads miss state).
4. Both reflogs tail-read (`.git\logs\HEAD`); no reported HEAD is trusted without them.
5. Every count, hash, and stat is re-taken at use. Nothing is carried from a prior session's report, including this lane's own.

## 4. Builder/reviewer separation (Foundry work under one roof)

The Foundry's independent builder/reviewer separation survives as **separate passes, not separate parties** -- the same discipline the AUREA lane runs as verify-from-tree, under the labels the Foundry's records already use.

1. **Build pass**: implementation lands and commits. The build pass writes no acceptance.
2. **Review pass**: a distinct pass, taken fresh from the committed tree, adversarial in posture, producing its own committed review document under `references/`. The review pass re-derives claims from disk; it does not accept the build pass's report as evidence.
3. **Ruling**: acceptance is ruled in the manifest after the review pass, never before.
4. A review pass that cannot verify a claim says so; REJECTED is a complete outcome and is recorded, not softened. (Precedent: the gamma-2a trap-flip defect was caught in review after the build pass missed it; the two-pass structure is load-bearing and is not collapsed for convenience.)

## 5. Findings jurisdiction

Errors charge by lane and by authorship, not by where they are caught:

- A defect in an order, ruling, or manifest entry charges the **drafting lane**, even when a Foundry control exposes it (precedent: the `c839c3a` protocol refusal -- the twentieth drafting-lane finding, upheld against this lane's own resume order).
- A defect in landed implementation charges the **pass lane**.
- Foundry-internal process findings are additionally recorded in the Foundry's own record.
- Counts remain separately tracked and are never merged.

## 6. House law held in common

The following bind on both repositories without restatement:

- **Freeze-once**: a protocol identity freezes once, against a stable aggregate.
- **Abstain-not-accuse**: an assessor that cannot read a response says it cannot read it; accusation is never the fallback state.
- **Instrument-suspicion**: a total floor or ceiling triggers instrument re-verification before any verdict.
- **Era honesty**: pins bound their era; superseded identities are not re-frozen, and byte-identity of prior-era artifacts is proven, not assumed.
- **Report -> disk -> rule**: every count in a ruling is a claim about a tree and requires a disk read after commit.
- **Commit-existence proof**: rev-parse HEAD differs from base; log -1 parent equals base; status porcelain empty.
- **A clean record is evidence the system behaved as designed; it is not evidence that the judgment was true.**

## 7. Amendment

This protocol amends only by a ratified manifest entry naming the changed clause. Silent drift between practiced law and this document is a drafting-lane finding.
