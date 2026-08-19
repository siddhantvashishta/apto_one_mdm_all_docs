# AptoMDM 2026 — Stubs Tracker

> **Version 1.1** — Module 1.1 closed. Stubs 1–6 registered: 1, 5, and 6 resolved within Module 1.1 itself; 2, 3, and 4 remain open, targeting Phase 2, Phase 2+ (incremental), and Phase 11/12 respectively.
> August 2026 | Confidential — Apto Engineering

---

## What a stub is

A stub is a **deliberate, recorded deferral** — a design decision a module needs but cannot finalize yet because it depends on a module that hasn't been designed. A stub is not a gap or an omission; it is a named placeholder with an explicit target module where it will be resolved.

**Every stub must record:**
- The module that raised it (what couldn't be finished without it)
- A plain description of what is being deferred
- The module expected to resolve it
- Status: Open / Resolved / Superseded

**A module is not allowed to close with an unrecorded stub.** If a design session defers something, it goes in this table before the module's `.md` file is generated — never left as an implicit gap discoverable only by reading the file closely.

---

## How to use this tracker

1. **At kickoff** (Process Rule per Project Instructions §6): check this table for any stub whose target module is the one about to start. Resolve it as part of that module's design, then mark it Resolved and note which layer/section resolved it.
2. **At close**: check whether the module being closed introduced any new deferrals. If so, add them here before generating the module file, not after.
3. **Never delete a resolved stub row** — mark it Resolved with the resolving module/date. The row is a historical record (Process Rule 2 — do not rewrite history).
4. **Stub numbers are platform-wide and sequential**, not per-domain or per-phase — Stub 1, Stub 2, Stub 3, regardless of which module raised them.

---

## Open Items Carried From the Project Bible (Section 10)

> These are pre-existing open items identified during Roadmap/Bible design, before any module formally raised them as a stub. They will convert to numbered stubs the first time a module's design session actually depends on them being resolved.

| Item | First likely to block | Notes |
|---|---|---|
| ERP connector priority order | Module 4.5 | Needs client-base input, not a design-session decision alone |
| Source precedence default posture (MDM-wins vs. ERP-can-request-deference) | Module 4.6 | Product-positioning decision |
| Competing-governance-system handling (e.g. client already runs SAP MDG) | Module 4.6 | |
| Golden Record confidence-decay thresholds | Module 8.3 | |
| Dual-control action list | Module 15.5 | |
| Reporting DB retention tiers per subscription tier | Module 10.3 | |
| AptoWMS/AptoTMS as default vs. opt-in distribution targets | Module 14.2 | Cross-product question |
| Fuzzy-match threshold seed values (no ML to learn them — Bible §5) | Module 3.3 | Needs sample data or client input |
| Frontend/backend TypeScript client generation tooling | Module 1.5 | e.g. `openapi-typescript` from the `utoipa` spec |

---

## Stub Register

| Stub # | Raised in Module | Description | Target Module | Status |
|---|---|---|---|---|
| 1 | Module 1.1 | Database migration tooling choice for the `sqlx`-based backend | Module 1.1 | ✅ Resolved — `sqlx-cli` locked. See `Apto_MDM_Bible.md` §5. |
| 2 | Module 1.1 | Organization legal-entity-linkage field detail (full shape) | Phase 2 — Organization canonical model | 🔲 Open |
| 3 | Module 1.1 | Referential check enforcing BR-1.1.10 (Org node deactivation blocked by dependent domain data) | Incremental — every Phase 2+ module that can reference an Organization node | 🔲 Open |
| 4 | Module 1.1 | Whether domain activation (BR-1.1.14) needs an approval workflow for Restricted-classification domains | Phase 11 (Governance) or Phase 12 (Workflow & Approval) | 🔲 Open |
| 5 | Module 1.1 | Tenant-level deactivation had no defined flow or screen — gap in Module 1.1's own stated scope | Module 1.1 | ✅ Resolved within the same module — Layer 1 flow D, BR-1.1.17–22, S1.1.2/S1.1.9 |
| 6 | Module 1.1 | `tenant.data_residency_region` uses an interim hardcoded `CHECK` list instead of a real reference-data FK | Module 1.4 — Reference Data & Code Tables | 🔲 Open |

---

*End of AptoMDM 2026 Stubs Tracker — Version 1.1*
