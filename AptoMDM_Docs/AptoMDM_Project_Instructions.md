# AptoMDM 2026 — Project Instructions

> **Version 1.0** — current
> August 2026 | Confidential — Apto Engineering

---

## Version History

| Version | Date | Changed by | Summary of changes |
|---|---|---|---|
| **1.0** | Aug 2026 | Initial authoring | First authored version, derived entirely from `Apto_MDM_Bible_v1.2.md` (§5 locked stack, §6 design methodology and document standards, §8.0 platform-wide conventions) and `AptoMDM_Design_Roadmap.md` v1.2 (five-layer scope, design principles, Design Order Summary). Introduces no new policy — this document is the *operating procedure* for the decisions those two documents already record. |

---

## Table of Contents

1. What this document is for
2. Document precedence — which file wins
3. Before you start a module
4. The five design layers
5. Conventions every module inherits
6. The seven design principles, used as review gates
7. Module document standard
8. Definition of Done
9. Close-out propagation checklist
10. Amending a module that is already closed
11. Choosing the next module
12. Review anti-patterns — what gets sent back
13. Hard rules
14. Open reconciliations

---

## 1. What this document is for

`AptoMDM_Design_Roadmap.md` says **what** to design — 16 phases, 73 modules, with planning-depth scope for each.
`Apto_MDM_Bible_v1.2.md` says **what has been decided and what is complete**.
**This document says how to do the work** — the procedure a designer follows to take a module from "listed in the roadmap" to "closed in the Bible."

It is written for whoever is running a design session: a human architect, or an AI agent working in this repo. Read it once end to end before your first module, then use §8 and §9 as checklists on every module after that.

The core question every module must be able to answer before it can be called done, quoted from the Roadmap:

> *What is the authoritative representation of this business entity, and why should the system trust it?*

---

## 2. Document precedence — which file wins

Overlap between these documents is deliberate, but conflicts must resolve predictably. When two documents disagree, the authority is:

| Question | Authoritative source |
|---|---|
| Is this module done? What is its status? | Bible §7 — status table |
| What is in scope for this module? | Roadmap — the module's own 5-layer entry |
| What technology may I use? | Bible §5 — locked stack |
| What must my schema / events / permissions look like? | Bible §8.0 — platform-wide conventions |
| What has been decided for this domain area? | Bible §8.1–8.15 — decisions by domain |
| How do I structure the module file? | This document, §7 |
| What order do I build in? | Roadmap — Design Order Summary |
| What is still open or deferred? | `AptoMDM_Stubs_Tracker.md` |
| What changed, and when? | `LEDGER.md` |

The Bible is the source of truth for **decisions and state**. The Roadmap is the source of truth for **plan and scope**. If you find a genuine contradiction between them, that is a defect: stop, record it in the Stubs Tracker, and raise it. Do not silently pick one and design against it.

---

## 3. Before you start a module

Do all five of these before writing any design content.

1. **Read the module's Roadmap entry in full.** It already lists the intended process flow, business rules, screens, schema and events at planning depth. Your job is to deepen it, not to re-derive it from scratch — and not to quietly narrow it.
2. **Read Bible §8.0.** Standard columns, the event envelope, the permission pattern and the ML boundary are inherited, not renegotiated per module.
3. **Read the Bible §8 subsection covering this module's domain area.** Decisions already recorded there are binding.
4. **Identify dependencies.** List the modules this one consumes and the modules that will consume it. A module that reads matching thresholds depends on 3.3; a module that publishes to the bus depends on the envelope in §8.0. Dependencies go in the module file's first section (§7).
5. **Check the Stubs Tracker** for open stubs this module is expected to close, and for forward references pointed at it.

If a dependency you need is itself not yet designed, that is normal and acceptable — record it as a stub with an explicit closing condition rather than inventing the dependency's behaviour.

---

## 4. The five design layers

Every module is designed in five layers, **in order**, per Bible §6. No layer starts until the previous one is agreed. All five must be complete before the next module begins.

| # | Layer | What it must contain | The bar it must clear |
|---|---|---|---|
| 1 | **Process Flow** | What happens, in what order, by whom — end to end, source system → golden record → distribution | A developer can trace one record's full journey without asking who acts next |
| 2 | **Business Rules** | What is allowed, what is blocked, what defaults apply — validations, thresholds, edge cases, exceptions | Every rule is decidable by a machine; no rule reads "handle appropriately" |
| 3 | **UI Screens** | What screens exist, what they show, what actions are available — web / steward console / admin config, only the surfaces this module actually needs | Each screen names its permission (§5) and its empty, loading and error states |
| 4 | **DB Schema + Sample Data** | Tables, columns, constraints, indexes, relationships — **plus representative sample rows** | Schema conforms to §8.0 standard columns; sample data shows at least one realistic multi-source conflict, not tidy placeholder rows |
| 5 | **Events** | What events are published, by whom, consumed by whom, with what payload | Every event carries the §8.0 envelope; every consumer is idempotent on `event_id` |

**Sample data is part of Layer 4, never a separate file** (Bible §6). This matters more than it sounds: sample rows are where survivorship and matching designs are proven to actually work, so tidy one-source-per-entity examples defeat the purpose.

---

## 5. Conventions every module inherits

Summarised from Bible §8.0, which is authoritative. Every Layer 4 and Layer 5 must conform; a deviation is permitted only with explicit justification recorded in that module's file.

**Standard columns.** Every operational table carries `id` (UUID PK), `tenant_id` (mandatory, indexed), `created_at`, `created_by`, `updated_at`, `updated_by`. Configuration tables add soft-delete (`is_deleted`, `deleted_at`, `deleted_by`). Source and golden-record tables use **no soft-delete at all** — they retire non-destructively via `merged_into`, `effective_from`/`effective_to` and `version`, because "deleted" is not a valid state for a record that must stay traceable and reversibly unmergeable. Tenant-extensible fields use `custom_data JSONB NULL DEFAULT '{}'` — never `custom_text_1..N`.

**Event envelope.** Every event carries `event_id` (UUID, the dedupe key), `tenant_id`, `correlation_id`, `timestamp_utc`. Events publish **after** DB commit, never inside the transaction. Consumers deduplicate on `event_id` and never assume at-most-once delivery. A breaking payload change means a new event version, never a silent in-place change.

**Permissions.** Fixed pattern `Domain.Module.Action` — e.g. `CUSTOMER.GOLDEN_RECORD.MERGE`, `CONFIG.MATCH_RULE.EDIT`. `VIEW` is a prerequisite for any other action on the same screen.

**Locked stack (Bible §5).** React + Vite; Rust + Axum; `sqlx`; `tokio`; `utoipa` → OpenAPI; Kafka via `rdkafka`; PostgreSQL; Redis for the metadata/rules cache; `strsim`/`pg_trgm` for fuzzy matching. Do not reopen these.

**The AI/ML boundary.** No AI/ML in the initial build. Match Decisioning (7.3), Confidence Scoring (8.3) and Data Enrichment (6.3) ship as deterministic, config-driven rule engines. If a future module introduces ML-assisted matching, enrichment or scoring, the boundary is absolute: **AI advises, it never mutates the golden record directly.** Any ML-produced score still routes through the human/steward review path at 7.3 — it never creates a new auto-decision path. Module 7.4 governs that lifecycle; it is an additive enhancement, explicitly **not** a go-live dependency for 7.1–7.3.

---

## 6. The seven design principles, used as review gates

Quoted from the Roadmap. Treat each as a question asked against your finished module, not as background reading.

1. **Golden Record is never a flat table** — every attribute carries value + source + confidence + effective dates + survivorship rule. *Gate: does your schema store a bare value anywhere it should store an attributed one?*
2. **Match ≠ Merge** — always separate engines, separate tables, separate reversibility guarantees. *Gate: has your design let a match outcome write directly to a merge?*
3. **Never destroy source data** — no hard deletes on source or master records; only `merged_into`, versioning and unmerge paths. *Gate: is there any DELETE in your design?*
4. **Attribute-level survivorship**, not "one source wins everything." *Gate: does any rule you wrote decide at record level?*
5. **Metadata-driven, not hardcoded per domain** — adding a domain like "Employee" is configuration, not a rewrite. *Gate: see the agnostic test below.*
6. **API-first** — every capability is an API before it is a screen. *Gate: could this module be driven headlessly, with no UI?*
7. **Event-driven** where synchronous coupling would block scale — matching, distribution, quality scoring. *Gate: does a user-facing action block on work that could be published?*

### The agnostic test

This is the single question that produced the seven v1.2 module additions, and it is the most valuable review question in the project:

> **If we onboard a domain, geography, or scale tier we haven't thought of yet, does anything in this design force a code change instead of a configuration change?**

If the answer is yes, the design is not finished. Configuration belongs in the Metadata/MDM Config layer. A design that hardcodes tenant-variable behaviour has failed review even when it is otherwise correct and complete.

---

## 7. Module document standard

**One `.md` file per module**, written after all five layers are agreed — not incrementally as a scratchpad.

**Filename** (Bible §6): `AptoMDM_Module_{phase}_{sequence}_{Name}.md`
Example: `AptoMDM_Module_1_1_Tenant_Organization_Setup.md`

**Location:** `Modules/Phase_{NN}/` — zero-padded, so phases sort correctly past nine. See §14.

**Required section order** (Bible §6 — do not reorder):

1. **Dependencies** — modules consumed, modules that will consume this one
2. **Config Object Overview** — what this module contributes to the Metadata/MDM Config layer
3. **Layer 1** — Process Flow
4. **Layer 2** — Business Rules
5. **Layer 3** — UI Screens
6. **Layer 4** — DB Schema + Sample Data
7. **Layer 5** — Events
8. **Stub Summary** — every stub and forward reference this module opens or closes

**Header block:** each module file opens with its own version line and a version-history table, in the same format this document uses. The version is bumped by amendments (§10), not by the initial authoring.

---

## 8. Definition of Done

A module is done when **all** of the following are true. Partial completion is legitimate progress but must be recorded as partial in the Roadmap and Bible §7 — never rounded up to complete.

- [ ] All five layers complete, in order, none deferred
- [ ] Layer 4 includes sample data with at least one realistic multi-source conflict
- [ ] Schema conforms to §8.0 standard columns; the no-soft-delete rule is respected on source/golden tables
- [ ] Every event carries the §8.0 envelope; consumers are idempotent
- [ ] Every screen names its `Domain.Module.Action` permission
- [ ] All seven design principles (§6) checked, and the agnostic test passed
- [ ] Nothing in the design requires AI/ML to function
- [ ] Dependencies section is complete in both directions
- [ ] Every stub opened is recorded with an explicit closing condition
- [ ] The module answers the core question: *what is the authoritative representation of this entity, and why should the system trust it?*
- [ ] Close-out propagation (§9) complete

---

## 9. Close-out propagation checklist

**A module document is never a standalone deliverable.** Closing a module means updating every document that references it, in the same pass. An unpropagated close leaves the Bible misreporting project state — which is precisely the failure mode AptoMDM exists to prevent for its customers.

- [ ] **Bible §7** — module status line updated
- [ ] **Bible §8.x** — the relevant domain subsection updated with any decision this module settled (Bible §6 amendment rule)
- [ ] **Bible §9** — File Reference Guide updated so the new filename is discoverable
- [ ] **Bible version history** — version bumped, with a scoped changelog entry stating what changed *and what deliberately did not*
- [ ] **Roadmap** — status and any scope change reflected
- [ ] **Stubs Tracker** — stubs opened, and stubs this module closes marked closed
- [ ] **LEDGER.md** — one append-only line

Then re-read the touched documents and confirm module counts, statuses and filenames agree across all of them. **A mismatch is a bug, not a cosmetic issue.**

---

## 10. Amending a module that is already closed

Per Bible §6. If a later module's design changes an earlier module's design:

1. Update the earlier module's `.md` file by **appending a versioned amendment section at the bottom** — never by silently editing the original layers, which would destroy the record of what was originally agreed.
2. Bump the version number in that file's header.
3. Record the amendment in the Stubs Tracker.
4. Update Bible §7 and the relevant Bible §8 subsection in the same close.

The amendment rule exists so that the reasoning behind a superseded decision stays readable. Overwriting history here has the same cost as a hard delete on a golden record.

---

## 11. Choosing the next module

Default to the Roadmap's Design Order Summary: phases in numeric order, modules in numeric order within a phase. As of Roadmap v1.2 the next module is **1.2 — Business Domain Registry**; 1.1 is closed.

Three v1.2 additions are **deliberately not** meant to be built in numeric position, and the Roadmap is explicit about why:

- **3.6 Configuration Environment & Promotion Pipeline** — land this *before* serious use of 3.3–3.5. Once matching thresholds and survivorship rules are live configuration, a bad config change is a production incident rather than a code-review catch.
- **15.6 Data Subject Rights & Retention/Purge** — treat as **launch-blocking** for any GDPR/DPDP-region client. Do not sequence it last merely because it is numbered last.
- **16.5 Search & Candidate-Generation Infrastructure** — pull forward alongside Phase 7 if any onboarding domain is expected to exceed roughly 5–10M records. Fuzzy matching at scale depends entirely on blocking/indexing; discovering that during a performance crisis is the expensive path.

Also note **6.4** (multi-script normalization) should precede Phase 7 build if any target client operates across scripts, since 7.x consumes its output; and **7.4** is additive, not blocking.

Security (Phase 15) and Observability (Phase 16) principles are referenced throughout earlier phases by design — classification at 2.x/11.3, idempotency at 5.2, segregation of duties at 1.3 — so that the dedicated phases *formalize* what earlier modules already assumed rather than bolting it on at the end. Design earlier modules accordingly.

---

## 12. Review anti-patterns — what gets sent back

These follow directly from the principles in §6 and the conventions in §5.

- Designing **Customer Page, Supplier Page, Product Page as separate applications.** Design the platform — Metadata, Rules, Policies, Core Engine — and let domains become configurations on top of it.
- A **hard delete** anywhere in a schema or process flow.
- A business rule that requires **human judgement to evaluate** ("validate reasonableness") rather than stating the decidable condition.
- **Record-level survivorship** logic, in any form.
- A screen designed before its API.
- An event published **inside** a database transaction.
- **Tidy sample data** — one source per entity, no conflicts — which proves nothing about matching or survivorship.
- A **new stub with no closing condition**, which is indistinguishable from an oversight six months later.
- Scope **silently narrowed** from the Roadmap entry without recording why.
- A module marked complete whose **document does not exist**, or whose propagation (§9) was skipped.

---

## 13. Hard rules

**Never delete a file.** Not as cleanup, not as a temp-file teardown, not as part of a reorganisation. Deletion happens only when the repo owner names a specific file and asks for it. This extends to `git rm`, `git clean`, `git restore`/`git checkout --` that discards work, and truncating overwrites.

**Never commit unless asked.** The repo owner decides when to commit. Commits are authored as `Siddhant Kumar <siddhant.kumar@codeapto.com>` with concise imperative subjects. `git push` is always run by the owner.

**Never invent project state.** A scaffold says it is a scaffold at the top. An empty section is honest; a plausible-sounding fabricated one is expensive to discover later.

**Never create scratch files inside this repo.** Use a location outside it.

---

## 14. Open reconciliations

Recorded here rather than silently resolved, per §2.

**Phase folder naming.** This document and the repo on disk use `Modules/Phase_01/` (zero-padded, so ordering survives past Phase 9). The Roadmap's Design Order Summary refers to `Modules/Phase 1/`. One of the two needs a one-line change — flagged for the repo owner, not decided here.

**Layer 4 naming.** Bible §6 calls Layer 4 "DB Schema + Sample Data" and requires sample rows; the Roadmap's five-layer list calls it "DB schema — tables, fields, relationships." These are not in conflict, but the Bible is the stricter and authoritative statement, and this document follows it: **sample data is mandatory.**

**Bible v1.2 changelog arithmetic.** The Bible states the module count went "from 59 to 73, reflecting the seven modules added." The Roadmap's own v1.1 → v1.2 summary table records v1.1 at **66** modules and v1.2 at 73, which is consistent with seven additions. The Bible's "59" appears to be a stale v1.0 figure that never absorbed v1.1's Phase 4 expansion. Direct count of the Roadmap confirms **73**.

**Module 1.1 file.** Bible §7 marks 1.1 ✅ Complete and Bible §9 references `AptoMDM_Module_1_1_Tenant_Organization_Setup.md`, but that file is not present in the repo. Until it is added, the Bible asserts a completed module whose document does not exist.
