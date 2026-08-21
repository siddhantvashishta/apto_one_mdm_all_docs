# AptoMDM 2026 — Stubs Tracker

> **Version 1.0** — current · operational register
> August 2026 | Confidential — Apto Engineering

**This file is the operational register of record for every open item in AptoMDM design.**
It is machine-validated: run `python tools/stubs.py --check` before any commit that closes
a module. Procedure for using it lives in `AptoMDM_Project_Instructions.md` §3 and §9.

---

## Version History

| Version | Date | Changed by | Summary of changes |
|---|---|---|---|
| **1.0** | Aug 2026 | Initial authoring | Converted from empty scaffold into a working register. Added stub taxonomy, severity ladder, lifecycle states, module-doc Stub Summary template, phase-boundary sweep procedure, and machine validation via `tools/stubs.py`. Seeded with 15 pre-existing open items collected from documents where they were already recorded but not centrally tracked: nine from Bible §10 *Open design items*, one forward reference from Bible §7 (Module 1.1 `STATUS_HISTORY` → 13.1), and five doc-set reconciliations from `AptoMDM_Project_Instructions.md` §14. **No stub in this register was invented** — each cites its source document. |

---

## 1. What counts as a stub

A **stub** is any point where the design deliberately defers something. Stubs are healthy:
they let design proceed without stalling on a dependency that is three phases away. Stubs
that are *forgotten* are the problem — across 73 modules, an untracked deferral becomes a
production defect nobody can trace back to a decision.

**The test:** if a module doc says *"for now"*, *"TBD"*, *"placeholder"*, *"assume"*, or
forward-refers to a module that is not yet designed, it belongs here.

Every stub needs a **closing condition** — a specific, checkable event. *"Later"* is not a
closing condition. *"Module 3.6 defines the promotion pipeline"* is. A stub with no closing
condition is indistinguishable from an oversight six months later, which is why
`stubs.py --check` rejects one.

---

## 2. Taxonomy

| Type | Meaning | Typical closing condition |
|---|---|---|
| **FWD** | Forward reference — this design leans on a module not yet designed | That module closes |
| **DEF** | Deferred design — a table, column or flow intentionally left at placeholder depth | The owning module deepens it |
| **CFG** | Hardcoded value awaiting a configuration surface | The config module exposes it |
| **DEC** | Open decision — a product, positioning or architecture question with no answer yet | The decision is made and recorded in the Bible |
| **EXT** | External dependency — client input, tooling choice, sample data, third-party contract | The input arrives or the choice is made |
| **DOC** | Doc-set defect — two documents disagree, or a document asserts something untrue | The documents are reconciled |

`DOC` stubs matter more than they look. This project's entire value proposition is that a
record's state is explainable and trustworthy; a doc set that misreports its own state
fails that standard internally before a customer ever sees it.

---

## 3. Severity

Severity is about **what is blocked**, not about how hard the fix is.

| Sev | Meaning | Rule |
|---|---|---|
| **S1** | Launch-blocking — cannot go live with a real tenant while open | Must close before first production onboarding. Reviewed every phase boundary without exception. |
| **S2** | Phase-blocking — blocks the design or build of a specific named module | Must close before that module's design session starts |
| **S3** | Carry — safe to carry forward with a known resolution target | Swept at phase boundaries; may cross a boundary with an explicit decision |

An S3 that has crossed two phase boundaries should be re-examined: either it is really an
S2 whose blocked module was mis-identified, or the resolution target is wrong.

---

## 4. Lifecycle

```
Open  ──▶  In design  ──▶  Closed
  │                          ▲
  └────────▶ Superseded ─────┘
```

| Status | Meaning |
|---|---|
| **Open** | Recorded, not being worked |
| **In design** | The resolving module's design session is underway |
| **Closed** | Resolved. Row moves to §7 with the closing module and date. The ID is never reused. |
| **Superseded** | No longer applicable — the design changed such that the question disappeared. Requires a one-line reason; "superseded" without a reason is indistinguishable from abandonment. |

**Never delete a row.** Closed and superseded stubs are the fastest available explanation
for why a design looks the way it does.

---

## 5. Register — open stubs

| ID | Type | Sev | Stub | Introduced by | Blocks / affects | Closing condition | Resolves in | Status |
|---|---|---|---|---|---|---|---|---|
| STUB-001 | DEC | S2 | ERP connector priority order — which ERP family (SAP ECC, S/4HANA, Oracle EBS/Fusion, Dynamics 365, NetSuite, Workday) is built first | Bible §10, Phase 4 design discussion | 4.5 design cannot sequence its connector build order | Client-base priority input received and the build order recorded in the Bible | 4.5 | Open |
| STUB-002 | DEC | S2 | Source precedence default posture — does the platform default to "MDM always wins" or "ERP can request deference"? Product positioning, not purely architectural | Bible §10, Phase 4 design discussion | 4.6 policy design; downstream survivorship defaults in 3.4/8.2 | Default posture decided and recorded in Bible §8 | 4.6 | Open |
| STUB-003 | DEC | S3 | Competing-governance-system handling — behaviour when a client already runs SAP MDG or equivalent | Bible §10, Phase 4 design discussion | 4.6; affects sales positioning more than architecture | Coexistence stance defined in 4.6 | 4.6 | Open |
| STUB-004 | DEC | S2 | Golden Record confidence-decay thresholds — when does an unconfirmed attribute get flagged for steward review? | Bible §10, Phase 8 roadmap scope | 8.3 design; steward queue volume in 7.3 and 11.1 | Threshold model defined in 8.3 | 8.3 | Open |
| STUB-005 | DEC | S2 | Dual-control action list — which actions require two independent approvers (bulk unmerge, classification downgrade, others) | Bible §10, Phase 15 roadmap scope | 15.5; also 11.5 bulk remediation, which inherits the list | Action list enumerated in 15.5 | 15.5 | Open |
| STUB-006 | DEC | S3 | Reporting DB retention tiers per tenant subscription — mirrors an AptoWMS pattern, not yet defined for MDM | Bible §10, Phase 10 roadmap scope | 10.3 dashboard/reporting design | Retention tiers defined per subscription level in 10.3 | 10.3 | Open |
| STUB-007 | DEC | S3 | Cross-product default — does an MDM-active tenant's WMS/TMS instance become a *consuming* target system by default, or explicit opt-in? | Bible §10, cross-product architecture question | 14.2 subscription management; cross-product onboarding flow | Decided in 14.2, or in a dedicated cross-product amendment | 14.2 | Open |
| STUB-008 | EXT | S1 | Fuzzy-match threshold seed inputs — with no ML model, initial `pg_trgm`/`strsim` thresholds must be set from sample data or client input, not learned. What sample data seeds the first tenant's 3.3 config? | Bible §10, v1.1 tech-stack lock | First tenant onboarding cannot be tuned; 7.1/7.2 match quality unverifiable | Seed sample data identified and first-tenant 3.3 configuration produced | 3.3 | Open |
| STUB-009 | EXT | S2 | Frontend/backend type-contract tooling — the `utoipa`-generated OpenAPI spec needs a concrete TypeScript client generation step (e.g. `openapi-typescript`) wired into the build; not yet chosen | Bible §10, v1.1 tech-stack lock | 1.5 standardization framework; every React screen thereafter | Tool chosen and wired into the build, recorded in Bible §5 | 1.5 | Open |
| STUB-010 | FWD | S3 | Module 1.1's `STATUS_HISTORY` table is stubbed — full design belongs to the append-only audit log engine | Bible §7, Module 1.1 close | Audit completeness for status/config changes made before 13.1 lands | 13.1 gives `STATUS_HISTORY` its full design; 1.1 amended per the amendment rule | 13.1 | Open |
| STUB-011 | DOC | S1 | Bible §7 marks Module 1.1 ✅ Complete and §9 references `AptoMDM_Module_1_1_Tenant_Organization_Setup.md`, but that file is absent from the repo — the Bible asserts a completed module whose document does not exist | Instructions §14 | Any propagation audit; 1.2 onward cannot check its dependency on 1.1 | The module file is added to `Modules/Phase_01/`, or §7 status is corrected to reflect reality | — | Open |
| STUB-012 | DOC | S3 | Phase folder naming — repo and Instructions use `Modules/Phase_01/` (zero-padded, sorts correctly past Phase 9); the Roadmap's Design Order Summary refers to `Modules/Phase 1/` | Instructions §14 | Tooling that resolves phase paths; nothing functional yet | Either the folder is renamed or the Roadmap line is updated — one-line change either way | — | Open |
| STUB-013 | DOC | S3 | Bible v1.2 changelog states the module count went "from 59 to 73" via seven additions (59+7=66). The Roadmap's own v1.1→v1.2 summary records v1.1 at 66, consistent with 73. The 59 is a stale v1.0 figure | Instructions §14 | Confidence in the Bible's version history as an audit record | Bible v1.3 corrects the figure to "from 66 to 73" | — | Open |
| STUB-014 | DOC | S3 | Bible §9 File Reference Guide points at `Apto_MDM_Bible.md`; the file on disk is `Apto_MDM_Bible_v1.2.md` — the Bible's own index cannot locate the Bible | Instructions §14 | Anyone following §9 to find a document | Bible v1.3 updates the reference, or the file is renamed | — | Open |
| STUB-015 | DOC | S3 | Layer 4 naming — Bible §6 calls it "DB Schema + Sample Data" and mandates sample rows; the Roadmap's five-layer list calls it "DB schema — tables, fields, relationships", omitting sample data. Instructions follow the Bible | Instructions §14 | Risk that a module ships Layer 4 without sample data | Roadmap's layer list updated to name sample data explicitly | — | Open |

---

## 6. Adding a stub — 30 seconds

1. Take the next unused ID. Never reuse a retired one.
2. Pick a **Type** (§2) and a **Severity** (§3) — severity is about what is blocked.
3. Write the **closing condition** as a checkable event, not an intention.
4. Name the module in **Resolves in**, or `—` if it is a doc-set item with no owning module.
5. Add the same stub to the module doc's **Stub Summary** section (template below).
6. Run `python tools/stubs.py --check`.

### Stub Summary block for module docs

Copy into the final section of the module file, per Bible §6's required structure:

```markdown
## Stub Summary

**Opened by this module**

| ID | Type | Sev | Stub | Closing condition | Resolves in |
|---|---|---|---|---|---|
| STUB-0NN | FWD | S3 | ... | ... | 13.1 |

**Closed by this module**

| ID | Stub | How it was closed |
|---|---|---|
| STUB-0NN | ... | ... |

*Every row above is mirrored in `AptoMDM_Stubs_Tracker.md`. If they disagree, the
tracker is authoritative and the module file is wrong.*
```

---

## 7. Closed and superseded stubs

Rows move here on close. They are never removed.

| ID | Type | Stub | Closed by | Date | How it was closed |
|---|---|---|---|---|---|
| _(none yet)_ | | | | | |

---

## 8. Phase-boundary sweep

Run at the close of every phase, before the next phase's first design session.

1. `python tools/stubs.py --report` — read the whole open register, not just new rows.
2. **Every S1 gets an explicit decision.** No S1 crosses a phase boundary silently.
3. **Check for missed closes.** `stubs.py --check` flags any stub whose resolving module is
   already marked ✅ Complete in Bible §7 — that means the module closed without closing
   its stub, which is the single most common way this register rots.
4. Re-examine any S3 that has crossed two boundaries (§3).
5. Record the sweep in `LEDGER.md`.

Carrying stubs silently across phase boundaries is how a 73-module project accumulates
debt nobody can attribute. The sweep is cheap; the alternative is a Phase 12 surprise.

---

## 9. Ownership

Single-owner project: stubs default to **Siddhant Kumar** unless a row says otherwise. If
the team grows, add an Owner column rather than tracking ownership in side conversations —
a register whose ownership lives in chat history is not a register.

---

## 10. Relationship to Bible §10

Bible §10 *Open design items* currently lists nine of the items above in its own table.
Those nine are seeded here as STUB-001 through STUB-009, each citing §10 as its source.

**This is deliberate duplication and should not persist.** Two registers of open items
will drift, and a drifting open-items list is worse than none. The recommendation, for the
next Bible revision: replace §10's table with a pointer to this file, keeping §10 as the
executive narrative — *how to run a design session* and *principles never to compromise* —
and letting the operational register live here where it is machine-validated.

That change is a Bible edit and therefore the repo owner's call. Until it is made, treat
§10 as the historical record and this file as operational, and update both.
