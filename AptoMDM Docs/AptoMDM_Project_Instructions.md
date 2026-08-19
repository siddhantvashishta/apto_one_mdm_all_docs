# AptoMDM 2026 — Project Instructions

> **Version 1.0** — Initial creation. Companion file to `Apto_MDM_Bible.md` (Section 6/10) and `AptoMDM_Design_Roadmap.md` (v1.1). This file is the **operational** counterpart to the Bible: where the Bible records *what was decided*, this file records *how a design session runs* and the **Module Design Order** used to cross-check the Design Roadmap's next-module pointer at every kickoff and close (Process Rule 10).
> August 2026 | Confidential — Apto Engineering

---

## 1. Purpose

Three files track module sequencing independently, on purpose:

| File | What it tracks |
|---|---|
| `AptoMDM_Design_Roadmap.md` | Per-module scope (5-layer plan) and a **next-module pointer** in its Design Order Summary |
| `Apto_MDM_Bible.md` | Section 7 status table (actual close status) |
| `AptoMDM_Project_Instructions.md` (this file) | Section 2's **Module Design Order**, independently maintained |

If any two of these disagree at a kickoff or close, that is a real defect (Process Rule 10) — report it, do not silently pick one.

---

## 2. Module Design Order

**Current sequence (unchanged from Roadmap v1.1):** Phase 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13 → 14 → 15 → 16, modules within each phase in ascending numeric order (sub-numbered modules, e.g. a future 4.4.1/4.4.2 split, insert immediately after their parent number).

**Next module: 1.1 — Tenant & Organization Setup.**

No modules have closed. This line has not yet been tested against a close-time update — the first real test of Process Rule 10 (Roadmap vs. Instructions agreement) will be at Module 1.1's close.

---

## 3. Continuation Points (ID / Code High-Water Marks)

> Read from body rows, never from banners/prose (Process Rule 3). All at zero — no module has closed yet.

| Registry | Prefix / format | Next value |
|---|---|---|
| UUID sample-data prefix | `mu001xxx` (MDM user), `mt001xxx` (MDM tenant), `me001xxx` (MDM entity) — pattern TBD, confirm at Module 1.1 | Not yet minted |
| Permission code | `Domain.Module.Action` (Bible §8.0) | Not yet minted |
| Event registration | `{Domain}{Action}` PascalCase (e.g. `GoldenRecordCreated`) on topic `tenant-{id}.mdm.{domain}.events` — topic convention TBD, confirm at Module 1.1 | Not yet minted |
| Stub number | Sequential, platform-wide, not per-domain | Stub 1 available |
| Notification type | TBD — pattern to be set when Module 3.5/12.x needs it | Not yet minted |

---

## 4. Navigation & Menu Structure

Not yet designed — owned by Module 1.5 (Screen & API Standardization Framework), following the same discipline as AptoWMS Module 1.20. This section will be filled in at that module's close.

---

## 5. Process Rules

> Numbered fresh for AptoMDM. These encode lessons already known to be true of any large multi-module design project (carried over from the AptoWMS process, which discovered each of them the hard way across 59 modules) — seeded here proactively so AptoMDM does not have to re-learn them by trial and error. Each rule below is cited by number from the `.claude/commands/*.md` slash commands in this repo.

**Rule 1 — Version arithmetic is string-decimal, not float.** `v1.11` → `v1.12`, never `v1.2`. A version bump script or manual edit must treat the part after the dot as an integer counter, not a decimal fraction.

**Rule 2 — Staleness sweep after every version bump, including siblings.** Live pointers only: the Project Instructions Module Design Order line (Section 2), the Project Bible's Section 7 status table, the Design Roadmap's module badges and Design Order Summary. Never touch historical changelog rows, `> Updated at Module X close` notes, or amendment-history entries — those are records of their own moment, and rewriting them destroys the record of what a later design was built on.

**Rule 3 — Banner-vs-body.** Continuation points (next UUID prefix, next permission code, next event registration, next stub number, next notification type) are read from a registry's actual body rows, never from banner/changelog prose. Prose can drift stale without the underlying registry being wrong, and vice versa — check both, trust only the body.

**Rule 4 — Module-number regex edits require negative lookahead or word boundaries.** A plain-text replace on `Module 2.1` will also match inside `Module 2.13`, `Module 2.1.4`, etc. Every automated edit touching a module number must assert the match count before writing, and use a pattern that cannot cross-match a longer sibling number.

**Rule 5 — A same-context gap-pass is not an adversarial gap-pass.** A drafting session checking its own output inherits the assumptions that produced any defects in the first place. A genuine gap-check must run in a fresh context.

**Rule 6 — A citation must be verified, not assumed.** Open the cited file and confirm it actually supports the claim being made.

**Rule 7 — Cross-module boundary values need explicit unit/precision/classification checks.** Check currency and decimal precision, classification, and survivorship scope explicitly at every module handoff.

**Rule 8 — Sibling-rule propagation.** When a fix is tied to one field, screen, or scenario, check whether the same rule applies to sibling fields or scenarios.

**Rule 9 — Never mark a task done before verifying the edit landed.** Re-read the file after every write.

**Rule 10 — Roadmap vs. Instructions next-module agreement.** The Design Roadmap's Design Order Summary and this file's Section 2 Module Design Order line must agree at every kickoff and close.

**Rule 11 — DRAFT marker discipline.** An active module file carries `**DRAFT — Layer N in progress. Not a closed module. Do not cite this file.**` as the second line of its header. Remove it only at close.

**Rule 12 — One squashed commit per module on `main`; granular history preserved on a branch.** Keep full branch history during design, then push `module/<n>-history` and squash-merge to `main` at close.

---

## 6. Design Session Response Rules

- State the module number and name before starting
- Go through Process Flow → Business Rules → UI Screens → DB Schema → Events in order
- Check the Stubs Tracker at kickoff and at close
- Every module produces exactly one `.md` file: `AptoMDM_Module_{phase}_{sequence}_{Name}.md`, placed in `Modules/Phase {phase}/`
- If a prior module's design changes, that module's file receives a versioned amendment section — never a silent edit with no trace

---

## 7. Cross-Cutting Decisions

All architecture-level decisions live in `Apto_MDM_Bible.md` Sections 5 and 8. This file does not duplicate them; it references them.

---

*End of AptoMDM 2026 Project Instructions — Version 1.0*
