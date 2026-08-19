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
| `AptoMDM_Project_Instructions.md` (this file) | Section 2's **Module Design Order** line, independently maintained |

If any two of these disagree at a kickoff or close, that is a real defect (Process Rule 10) — report it, do not silently pick one.

---

## 2. Module Design Order

**Current sequence (unchanged from Roadmap v1.1):** Phase 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13 → 14 → 15 → 16, modules within each phase in ascending numeric order (sub-numbered modules, e.g. a future 4.4.1/4.4.2 split, insert immediately after their parent number).

**Next module: 1.2 — Business Domain Registry.**

Module 1.1 closed Aug 2026 (v1.0) — all 5 layers, 5 audits (`/crosslayer`, `/crossmodule` [N/A, first module], `/gap` — 2 findings fixed, staleness sweep — 0 mismatches). This is the first real test of Process Rule 10 (Roadmap vs. Instructions agreement): this line and the Roadmap's Design Order Summary now both point to 1.2. The high-water marks below are confirmed final for what Module 1.1 minted.

---

## 3. Continuation Points (ID / Code High-Water Marks)

> Read from body rows, never from banners/prose (Process Rule 3). Confirmed final as of Module 1.1's close.

| Registry | Prefix / format | Next value |
|---|---|---|
| UUID sample-data prefix | **Locked at Module 1.1** — short mnemonic prefixes, not the originally speculated `mu001xxx` pattern: `t-XXXX` (Tenant), `inv-XXXX` (Tenant Invite), `org-XXXX` (Organization), `tda-XXXX` (Tenant Domain Activation). Module 1.2 continues this style with its own mnemonic prefix, not a renumbering of these. | Module 1.1 used `t-0001`–`t-0003`, `org-0001`–`org-0003`, `inv-0001`–`inv-0002`, `tda-0001`–`tda-0003`. Module 1.2 mints its own prefix (e.g. `dom-XXXX`). |
| Permission code | `Domain.Module.Action` (Bible §8.0) | Module 1.1 minted 10 codes under the `CONFIG` pseudo-domain: `CONFIG.TENANT.VIEW/CREATE/RESEND_INVITE/DEACTIVATE`, `CONFIG.ORGANIZATION.VIEW/CREATE/EDIT/DEACTIVATE`, `CONFIG.DOMAIN_ACTIVATION.VIEW/EDIT`. Module 1.2 continues under `CONFIG` for platform-config screens, or a new pseudo-domain if it introduces one. |
| Event registration | `{Domain}{Action}` PascalCase (e.g. `TenantDeactivated`, `OrganizationCreated`). Topic convention **locked at Module 1.1**: control-plane events (Tenant lifecycle) → `platform.tenant-lifecycle.events`; tenant-scoped config events (Organization, Domain Activation) → `tenant.{tenant_id}.config.events`; future business-domain events (Phase 5+) → `tenant.{tenant_id}.mdm.{domain}.events` | Module 1.1 minted 12 events — see that module's Layer 5 for the full list. Last: `TenantDomainActivated`/`TenantDomainDeactivated`. |
| Stub number | Sequential, platform-wide, not per-domain | Stub 7 available |
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

**Rule 4 — Module-number regex edits require negative lookahead or word boundaries.** A plain-text replace on `Module 2.1` will also match inside `Module 2.13`, `Module 2.1.4`, etc. Every automated edit touching a module number must assert the match count before writing, and use a pattern that cannot cross-match a longer sibling number (relevant to AptoMDM given planned sub-numbered modules like a future split of 4.4 or 6.1).

**Rule 5 — A same-context gap-pass is not an adversarial gap-pass.** A drafting session checking its own output inherits the assumptions that produced any defects in the first place. A genuine gap-check must run in a fresh context (a subagent that reads only the file and its cited sources, not the drafting conversation).

**Rule 6 — A citation must be verified, not assumed.** Open the cited file and confirm it actually supports the claim being made. A citation that resolves but does not support the claim is worse than no citation at all — it provides false coverage evidence to anyone who trusts it later.

**Rule 7 — Cross-module boundary values need explicit unit/precision/classification checks.** AptoWMS's version of this was millimetre/centimetre and m³/cm³ mismatches. AptoMDM's equivalent risk class: currency and decimal-precision mismatches on numeric attributes (e.g. `unit_cost`), classification-level mismatches between a source system's implied sensitivity and the platform's declared classification (Bible §8.3), and survivorship-rule scope mismatches (an attribute-level rule applied as if it were record-level). Check these explicitly at every module handoff — they are invisible inside any single module's own layer.

**Rule 8 — Sibling-rule propagation.** When a fix is tied to one field, screen, or scenario, check whether the same rule applies to sibling fields/scenarios sharing identical wording, and apply the fix to all of them — not just the one that prompted it.

**Rule 9 — Never mark a task done before verifying the edit landed.** Re-read the file after every write. A silent no-match failure (e.g. a `rep()` regex that matched zero times) must never be reported as a successful change.

**Rule 10 — Roadmap vs. Instructions next-module agreement.** The Design Roadmap's Design Order Summary and this file's Section 2 Module Design Order line must agree on which module is next, at every kickoff and every close. If they disagree, report it as a defect — do not silently trust one over the other.

**Rule 11 — DRAFT marker discipline.** A module file under active design carries `**DRAFT — Layer N in progress. Not a closed module. Do not cite this file.**` as the second line of its header. That marker is updated at every layer and removed only by the close process. Nothing may cite a DRAFT-marked file as a settled source.

**Rule 12 — One squashed commit per module on `main`; granular history preserved on a branch.** The working branch keeps its full commit-by-commit history (audit trail and crash insurance — never thinned mid-module). At close, that history is pushed to a `module/<n>-history` branch, then squash-merged to `main` as one commit titled `Module <n> Added — <name> (v1.0)`.

---

## 6. Design Session Response Rules

- State the module number and name before starting
- Go through Process Flow → Business Rules → UI Screens → DB Schema → Events in order — no layer starts before the previous is agreed (Bible §6)
- Check the Stubs Tracker at kickoff and at close — consumed stubs and newly minted stubs both recorded
- Every module produces exactly one `.md` file: `AptoMDM_Module_{phase}_{sequence}_{Name}.md`, placed in `Modules/Phase {phase}/`
- If a prior module's design changes, that module's file receives a versioned amendment section — never a silent edit with no trace

---

## 7. Cross-Cutting Decisions

All architecture-level decisions (tech stack, schema conventions, event envelope, permission pattern, AI boundary, domain-by-domain locked decisions) live in `Apto_MDM_Bible.md` Sections 5 and 8 — this file does not duplicate them, only references them. See Bible §8.0 for the platform-wide technical conventions every module inherits.

---

*End of AptoMDM 2026 Project Instructions — Version 1.0*
