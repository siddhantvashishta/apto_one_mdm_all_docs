# AptoMDM Documentation Workflow

This repository now keeps the toolkit's documentation controls alongside the main design records.

## Canonical records

| Record | Location | Update timing |
|---|---|---|
| Architecture decisions and module status | `AptoMDM Docs/Apto_MDM_Bible.md` | At module close or architecture amendment |
| Planned module scope and next-module pointer | `AptoMDM Docs/AptoMDM_Design_Roadmap.md` | At roadmap change and module close |
| Operating rules and independent sequence check | `AptoMDM Docs/AptoMDM_Project_Instructions.md` | At process or sequence change |
| Deferred decisions and their target modules | `AptoMDM Docs/AptoMDM_Stubs_Tracker.md` | At kickoff and close |
| Current design-session scratch state | `LEDGER.md` | Throughout one active module; reset at close |
| Closed module designs | `Modules/Phase {n}/AptoMDM_Module_{phase}_{sequence}_{Name}.md` | Created once per module; amended with a versioned section only |

## Implementing a module

1. Confirm the Roadmap and Project Instructions name the same next module.
2. Read `LEDGER.md`, the module scope in the Roadmap, the relevant Bible sections, and target stubs.
3. Create one draft module file and mark it as draft until all five layers are agreed.
4. Design in order: Process Flow, Business Rules, UI Screens, DB Schema plus sample data, then Events.
5. Record every deferred decision in the Stubs Tracker and carry blocking stubs into the Ledger.
6. Before close, run completeness, cross-layer, cross-module, adversarial gap, and staleness checks.
7. At close, remove the draft marker, update the Bible status and domain decisions, advance both next-module pointers, update stubs and continuation points, and reset the Ledger.

## Tracking changes cleanly

- Keep historical changelog rows and resolved stub rows; do not rewrite history.
- Use one module file per module and versioned amendment sections for later changes.
- Review changes as a documentation unit: Bible, Roadmap, Instructions, Stubs Tracker, Ledger, and the module file.
- The attached `aptomdm_toolkit/.claude/commands/` directory contains optional command playbooks for kickoff, layer progression, gap checks, synchronization, close, and ledger maintenance. Those commands currently expect the toolkit's canonical Bible name `AptoMDM_Project_Bible.md`; this main repo retains the existing `Apto_MDM_Bible.md` name, so update command paths before running them from this root.

## First implementation

The next module is **1.1 — Tenant & Organization Setup**. Start by reconciling the `sqlx` migration tooling open item, then initialize the Ledger and create the draft module file under `Modules/Phase 1/`.
