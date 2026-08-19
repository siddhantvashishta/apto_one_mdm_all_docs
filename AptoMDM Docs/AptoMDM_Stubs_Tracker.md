# AptoMDM 2026 — Stubs Tracker

> **Version 1.0** — Initial creation. Companion file to `Apto_MDM_Bible.md` and `AptoMDM_Project_Instructions.md`. No modules have closed yet — this tracker is empty and ready to receive its first stub at Module 1.1.
> August 2026 | Confidential — Apto Engineering

---

## What a stub is

A stub is a **deliberate, recorded deferral** — a design decision a module needs but cannot finalize yet because it depends on a module that has not been designed. A stub is not a gap or an omission; it is a named placeholder with an explicit target module where it will be resolved.

**Every stub must record:**
- The module that raised it
- A plain description of what is deferred
- The module expected to resolve it
- Status: Open / Resolved / Superseded

**A module is not allowed to close with an unrecorded stub.**

---

## How to use this tracker

1. **At kickoff:** check for stubs whose target is the module about to start and carry them into `LEDGER.md`.
2. **At close:** record every new deferral before generating the module file.
3. **Never delete a resolved stub row:** mark it Resolved with the resolving module and date.
4. **Number stubs sequentially platform-wide:** Stub 1, Stub 2, Stub 3, regardless of phase or domain.

---

## Open Items Carried From the Project Bible (Section 10)

| Item | First likely to block | Notes |
|---|---|---|
| ERP connector priority order | Module 4.5 | Needs client-base input, not a design-session decision alone |
| Source precedence default posture (MDM-wins vs. ERP-can-request-deference) | Module 4.6 | Product-positioning decision |
| Competing-governance-system handling (e.g. client already runs SAP MDG) | Module 4.6 | |
| Golden Record confidence-decay thresholds | Module 8.3 | |
| Dual-control action list | Module 15.5 | |
| Reporting DB retention tiers per subscription tier | Module 10.3 | |
| AptoWMS/AptoTMS as default vs. opt-in distribution targets | Module 14.2 | Cross-product question |
| Fuzzy-match threshold seed values | Module 3.3 | Needs sample data or client input |
| Frontend/backend TypeScript client generation tooling | Module 1.5 | e.g. `openapi-typescript` from the `utoipa` spec |
| `sqlx` migration tooling choice | Module 1.1 | Lock before Module 1.1 starts |

---

## Stub Register

> Empty — no module has closed. First stub will be numbered **Stub 1**.

| Stub # | Raised in Module | Description | Target Module | Status |
|---|---|---|---|---|
| — | — | *(none yet)* | — | — |

---

*End of AptoMDM 2026 Stubs Tracker — Version 1.0*
