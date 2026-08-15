# docs/

This folder was retired down to its living members on 2026-08-15 (manifest,
eighty-second entry). Twelve pre-pivot documents were deleted: their status
tables were false against the tree, their API claims named functions that do
not exist, and one (`api_reference.md`) documented the exact defects Rulings
68 and 75 removed. A false doc is worse than no doc. The bodies remain in git
history — M1's own reasoning: a name does not need a file to hold its place.

Where the living documentation is:

- **`../README.md`** — system overview, the kernel loop, the acquisition
  boundary, module map, data & persistence, canonical models. Verified against
  the tree when written; the manifest entry that wrote it names the commit.
- **`../DOMAINS.md`** — reserved names, their heading phases and destinations.
  A concept without a built module lives THERE, not here.
- **`../CLAUDE.md`** — pass-owned build state: suite counts, invariant ledger,
  baselines, method register.
- **`../AGENTS.md`** — operating instructions for agents working this tree.
- **`../../Aurea Build/AUREA_PIVOT_ARCHITECTURE.md`** — the governing heading.
- **`../../Aurea Build/integration_review_manifest.md`** — every ruling,
  every closure, the standing PATH.
- **`../../Aurea Build/BUILD_CONTRACT.md`** — contract law: domains, ownership,
  call graph.

What remains in this folder:

- **`tether_protocol.md`** — the Tether Protocol (Phase-3 safeguard). Its API
  claims were verified against `src/expansion/tether_protocol.py` on
  2026-08-15 (4/4 present).
- **`module_template.md`** — the template for any future module doc. A new
  module doc must have its API claims read from source at writing time; a doc
  that names a function nobody built is how this folder died the first time.
- **`formal/`** — Quint models (TCAML lock).
