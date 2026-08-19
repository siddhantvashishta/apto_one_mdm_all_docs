# AptoMDM 2026 — Project Bible

> **Version 1.1** — current
> August 2026 | Confidential — Apto Engineering

---

## Version History

| Version | Date | Changed by | Summary of changes |
|---|---|---|---|
| **1.1** | Aug 2026 | Architecture review | **Locked the application tech stack** (Section 5 expanded): Frontend **React + Vite**; Backend **Rust + Axum**; DB **PostgreSQL** (unchanged); **no AI/ML integration in initial build** — Match Decisioning (7.3), Confidence Scoring (8.3), and Data Enrichment (6.3) ship as deterministic rule/config-driven engines only. Added supporting stack decisions consistent with the Rust backend: `sqlx` for compile-time-checked DB access, `tokio` async runtime, `utoipa` for OpenAPI generation (API-first pillar), `rdkafka` for the Kafka event bus, Redis for the metadata/rules cache, `strsim`/`pg_trgm` for deterministic fuzzy matching (no ML model). **Added Section 8.0 — Platform-Wide Technical Conventions** (schema standard, event envelope, permission naming pattern, AI boundary) ahead of the existing domain subsections, so Module 1.1 inherits conventions instead of inventing them. **Added four new Section 8 subsections** closing prior coverage gaps: 8.12 Data Ingestion, 8.13 Standardization & Validation, 8.14 Observability & Scalability, 8.15 Reference Data & Localization. Section 9 (File Reference Guide) unchanged; Section 10 open items updated to remove the now-resolved tech-stack question and add two new stack-driven open items. |
| 1.0 | Aug 2026 | Initial draft | Initial 10-section Project Bible seeded from `AptoMDM_Design_Roadmap.md` (v1.1) and the Senior Architect Mindset. No modules in detailed design yet; all 59 modules recorded as Not Started. |

---

## Table of Contents

1. What We Are Building
2. Why We Are Building It
3. Who Uses It
4. Architecture Philosophy
5. Technical Architecture — Finalized Decisions
6. Design Methodology
7. Module Roadmap & Status
8. Finalized Design Decisions by Domain
9. File Reference Guide
10. Open Items & How to Move Forward

---

## 1. What We Are Building

AptoMDM is a **cloud-native, SaaS Master Data Management platform** — the trust layer underneath every other Apto product (AptoWMS, AptoTMS) and every ERP/CRM/e-commerce system a tenant already runs. It is designed to answer one question for any business entity: *what is the authoritative representation of this entity, and why should the system trust it?*

It is delivered as part of the same multi-tenant SaaS family as AptoWMS: **Organization → Tenant → Product Instance (WMS / TMS / MDM)**. A tenant may run AptoMDM standalone — mastering Customer, Supplier, and Product data across their existing ERP landscape — or alongside AptoWMS/AptoTMS, in which case AptoMDM becomes the shared source of truth those products read from, rather than each product maintaining its own siloed master.

AptoMDM is not a data warehouse, not a data lake, and not a one-way ETL sync tool. It is a **governed, bidirectional trust engine**: source systems feed it, it resolves conflicts deterministically and explainably, and it distributes the resolved (golden) record back out to every system that needs it.

### What AptoMDM IS

| Characteristic | What it means in practice |
|---|---|
| Metadata-driven | Domains (Customer, Supplier, Product, etc.) are configuration on top of one engine, not separately coded applications |
| Match ≠ Merge | Two distinct, separately reversible engines — never conflated into one operation |
| Explainable | Every golden attribute traces to a source, a confidence score, and a survivorship rule — "why is this value X" always has an answer |
| Governed | Stewardship, approval, and audit are first-class modules, not bolted on after Match/Merge/Golden Record |
| ERP-agnostic by construction | New source systems (SAP, Oracle, Dynamics, NetSuite, Workday, and others) are a connector-and-mapping exercise, never a platform rewrite |
| Non-destructive | Source data and merge history are never deleted — only retired, versioned, and always reversible |
| Event-driven | Every meaningful state change (golden record update, merge, quality breach, distribution) publishes an event |
| API-first | Entity, Match, Merge, Golden Record, Quality, Workflow, Governance, and Audit are all APIs before they are screens |

### What AptoMDM is NOT

| Characteristic | What it means in practice |
|---|---|
| Not a one-way sync tool | It resolves conflicts and pushes a trusted record back out — it doesn't just copy data from A to B |
| Not a single "master system wins" model | Survivorship is attribute-level and configurable — no domain hardcodes "SAP is always right" |
| Not a per-domain application | Customer, Supplier, Product, Location, Employee, Asset, Account, Reference Data are configurations on one platform, not separate codebases |
| Not a passive golden-record store | The Golden Record is meaningless without the engines around it — Match, Survivorship, Quality, Governance, and Distribution are equally core |
| Not SAP-specific, Oracle-specific, or any-ERP-specific | The connector framework (Phase 4) is protocol- and vendor-agnostic; ERP-specific behavior is isolated to packaged connectors only |

---

## 2. Why We Are Building It

Enterprise master data today typically lives fragmented across ERP, CRM, e-commerce, finance, HR, WMS, legacy databases, and spreadsheets — each holding its own version of "the truth" for the same customer, supplier, or product. Existing MDM tools (Informatica MDM, Reltio, SAP MDG, Stibo, and similar) carry the same category of technical debt the Senior Architect Mindset warns against:

- Configuration complexity requiring long, consultant-heavy implementation projects
- Golden Record models that are flat tables, not explainable attribute-level structures
- Match and Merge conflated into one operation, making reversal difficult or impossible
- Governance treated as an afterthought rather than a first-class module
- ERP connectivity sold as a separate, expensive "connector pack" rather than a platform-native capability

**The opportunity:** build an MDM platform that is metadata-driven, explainable by design, non-destructive by default, and genuinely ERP-agnostic — configurable enough for enterprise governance requirements, simple enough that a mid-market tenant isn't locked into a 12-month implementation.

**The strategic position:** AptoMDM targets the gap between point-solution data-cleansing tools (too shallow — no governance, no lineage, no reversible merge) and legacy enterprise MDM suites (too expensive, too rigid, too tightly coupled to one ERP vendor's own governance layer, e.g. SAP MDG). It grows with the tenant — starting with one domain and one source system, activating additional domains and additional ERPs without re-architecture.

---

## 3. Who Uses It

### Data Operations Team (Primary Users)

| Role | What they do in AptoMDM |
|---|---|
| Data Steward | Reviews match candidates, resolves quarantined/quality-flagged records, approves or rejects merges and unmerges |
| Data Owner | Accountable for a domain or attribute's correctness; sets classification and survivorship policy |
| MDM Admin | Configures domains, canonical models, matching/survivorship rules, source system connectors |

### Platform / IT Team

| Role | What they do in AptoMDM |
|---|---|
| Tenant Admin | Manages users, roles, domain activation, tenant-level settings |
| Integration Engineer | Configures ERP/CRM/source-system connectors, field mappings; monitors ingestion and distribution health |
| Apto Platform Team (vendor) | Monitors all tenants, manages upgrades, responds to SLA breaches |

### Business Stakeholders

| Role | What they use |
|---|---|
| Compliance / Governance Lead | Classification policy, audit log, segregation-of-duties configuration |
| Finance / Procurement | Golden Supplier/Customer records, Tax ID, banking detail access (where entitled) |
| Downstream System Owners (ERP/CRM/WMS) | Consume distributed golden records via their own system — generally unaware AptoMDM is the source |

---

## 4. Architecture Philosophy

### The north star

> AptoMDM is a Cloud-Native, Metadata-Driven, Event-Driven, Horizontally Scalable Modular Monolith — and an Explainable Trust Engine.

Every design decision is evaluated against this north star. If a proposed design conflicts with any of these properties, it requires explicit justification to proceed.

### Five core design pillars

**1. Metadata drives everything**
No engine — Match, Survivorship, Quality, Security — may hardcode a domain's attribute list. A new domain is addable through configuration (Phase 3), never a platform rewrite.

**2. Match and Merge are separate, and neither destroys data**
A match decision only says "these might be the same." A merge decision consolidates. Source data is never deleted — only retired with a `merged_into` relationship — so every merge is reversible.

**3. Every golden value is explainable**
A golden attribute is never a flat, overwritten value — it always carries source, confidence, effective dates, and the survivorship rule that produced it.

**4. API-first**
Entity, Match, Merge, Golden Record, Quality, Workflow, Governance, and Audit are APIs before they are screens — external systems and the UI call the same contract.

**5. Event-driven where synchronous coupling would block scale**
Matching, quality scoring, and distribution are event-driven so no engine blocks another under load.

### Build-phase evolution

| Build Phase | Architecture | When |
|---|---|---|
| Build Phase 1 | Modular monolith, internal event dispatcher, single DB per tenant | Now — in design |
| Build Phase 2 | Extract reporting/quality-scoring, read replicas, externalize message bus | After initial launch |
| Build Phase 3 | Selective microservice extraction for high-load engines (matching, distribution), multi-region scale | Scale-driven |

> **Note:** "Build Phase" (infrastructure maturity, above) is distinct from the **16 design phases** tracked in Section 7 — the same distinction AptoWMS draws between its infra-phase evolution and its module-phase roadmap. Do not conflate the two axes.

---

## 5. Technical Architecture — Finalized Decisions

### Infrastructure

- **Cloud provider:** Agnostic — deployable on AWS, Azure, GCP
- **Database:** PostgreSQL — one database per tenant
- **Message bus:** Kafka — event streaming backbone, shared convention with AptoWMS
- **Secrets management:** Vault — all connector credentials, never in DB or config files
- **Authentication:** JWT — stateless, validated on every request
- **Authorization:** RBAC + ABAC — roles at tenant/domain level, attribute-level access layered on top (Phase 15)

### Application stack — Frontend

- **Framework:** React + Vite
- **Data fetching:** TanStack Query (React Query) — aligns with the event-driven pillar by making cache invalidation explicit rather than polling
- **Typed API contract:** frontend types generated from the backend's OpenAPI spec (see `utoipa` below) — frontend and backend must never hand-maintain two separate type definitions for the same API
- **State management:** component/local state by default; a global store (Zustand or equivalent) only where cross-screen state genuinely requires it — avoid defaulting to a heavy global store for every screen

### Application stack — Backend

- **Language / framework:** Rust + Axum
- **Async runtime:** Tokio
- **Database access:** `sqlx` — compile-time-checked SQL, no ORM query-builder abstraction between the code and the actual SQL. This is a deliberate fit with the platform's **explainability pillar**: a golden-attribute survivorship query should be readable and auditable as SQL, not hidden behind ORM-generated joins.
- **API documentation:** `utoipa` — generates the OpenAPI spec directly from Axum route/handler definitions, which is what the frontend's typed client (above) consumes. This makes "API-first" mechanically enforced rather than a written policy.
- **Kafka client:** `rdkafka`
- **Caching:** Redis — used for the Phase 3 metadata/rules cache (domain, entity, attribute, matching, survivorship, validation config) and session-scoped data. Per the Senior Architect Mindset's explicit warning, **cache invalidation on metadata/rule publish (Module 3.1) must be immediate and event-driven** — a stale cached rule silently misapplied is a correctness defect, not a performance one.

### Matching & search infrastructure

- **Deterministic fuzzy matching, no ML model:** `strsim` (Rust crate — Levenshtein, Jaro-Winkler, and similar string-distance algorithms) for in-process composite scoring (Module 7.2), backed by PostgreSQL `pg_trgm` (trigram similarity + GIN index) for the pre-filtering/candidate-generation pass, so the matching engine never has to fuzzy-compare against the entire table.
- Every matching technique used is explainable and deterministic by construction — no embedding/vector similarity, no black-box scoring — consistent with the "every survivorship outcome must be explainable" principle (8.5) and the "no AI/ML integration" decision below.

### AI / ML boundary

- **No AI or ML integration in the initial build.** Match Decisioning (7.3), Confidence Scoring (8.3), and Data Enrichment (6.3) are deterministic, rule- and configuration-driven engines only — no ML model scores a match, sets a confidence value, or enriches a record in Phase 1.
- This is a **build-scope decision, not a permanent architectural ceiling.** The platform's metadata-driven design (8.1 below) does not preclude a future ML-assisted matching or enrichment module — but if one is added later, it must follow the same AI-boundary discipline AptoWMS applies: **advisory only, never a silent auto-decision.** Any future ML-assisted score would still route through the existing Review-band steward queue (Module 7.3), never bypass it. See Section 8.0 for the explicit boundary statement, and Section 10 for this as a tracked forward item.

### Multi-tenancy

- Organization → Tenant → Product Instance (WMS / TMS / **MDM**) — same platform-wide model as AptoWMS
- One tenant = one dedicated database, one dedicated URL, isolated config
- **Control Plane (Platform DB):** SaaS governance, tenant lifecycle, domain activation, feature flags
- **Data Plane (Tenant Product DB):** all operational MDM data — source records, golden records, match/merge history
- **Reporting / Quality DB:** separate star schema for quality dashboards and trend reporting — never queried by operational engines
- **Observability DB:** aggregated metrics and logs — separate from all of the above

### Performance targets

| Operation | Target |
|---|---|
| Golden Record read (by ID) | < 150ms |
| Exact / normalized match pass (single record) | < 300ms |
| Composite / fuzzy match pass (single record, per domain-configured attribute set) | < 800ms |
| Golden Record write (survivorship re-evaluation + commit) | < 500ms |
| Distribution publish (single target, single record) | < 1s, async with retry |

---

## 6. Design Methodology

### Five-layer module design

Every module is designed in five layers, in order — identical discipline to AptoWMS. No layer is started until the previous is agreed:

1. **Process Flow** — what happens, in what order, by whom
2. **Business Rules** — what is allowed, what is blocked, what defaults apply
3. **UI Screens** — what screens exist, what they show, what actions are available
4. **DB Schema + Sample Data** — tables, columns, constraints, indexes, representative rows
5. **Events** — what events are published, by whom, consumed by whom, with what payload

### Document standards

- Every module produces one `.md` file after all 5 layers are agreed
- Filename: `AptoMDM_Module_{phase}_{sequence}_{Name}.md`
- Structure: Dependencies → Config Object Overview → Layer 1 → Layer 2 → Layer 3 → Layer 4 (schema + sample data) → Layer 5 → Stub summary
- Sample data is part of Layer 4 — not a separate file

### Amendment rule

- If a prior module's design changes during a later module's design, the prior module's `.md` file is updated with a versioned amendment section at the bottom
- Version number in the file header is bumped
- Stubs Tracker updated to note the amendment
- Project Bible Section 7 (status table) and the relevant Section 8 domain subsection updated in the same close

---

## 7. Module Roadmap & Status

> Full module-level scope (process flow, business rules, screens, schema, events at planning depth) lives in `AptoMDM_Design_Roadmap.md` (v1.1). This table tracks **actual design-session completion status** — distinct from the Roadmap, which is the target plan. No module has entered detailed 5-layer design yet; the Roadmap itself is the only artifact complete so far.

### Phase 1 — Business Domain & Platform Foundation

| Module | Name | Status |
|---|---|---|
| 1.1 | Tenant & Organization Setup | 🔲 Not started — first module in design order |
| 1.2 | Business Domain Registry | 🔲 Not started |
| 1.3 | User, Role & Permission Matrix | 🔲 Not started |
| 1.4 | Reference Data & Code Tables | 🔲 Not started |
| 1.5 | Screen & API Standardization Framework | 🔲 Not started |

### Phase 2 — Canonical Data Model

| Module | Name | Status |
|---|---|---|
| 2.1 | Canonical Entity Model | 🔲 Not started |
| 2.2 | Customer Domain Canonical Model | 🔲 Not started |
| 2.3 | Supplier Domain Canonical Model | 🔲 Not started |
| 2.4 | Product / Material Domain Canonical Model | 🔲 Not started |
| 2.5 | Location, Employee, Asset & Account Domain Canonical Models | 🔲 Not started |
| 2.6 | Entity Relationship Model | 🔲 Not started |

### Phase 3 — Metadata Architecture

| Module | Name | Status |
|---|---|---|
| 3.1 | Domain & Entity Metadata Registry | 🔲 Not started |
| 3.2 | Attribute Data Type & Validation Rule Registry | 🔲 Not started |
| 3.3 | Matching Rule Configuration | 🔲 Not started |
| 3.4 | Survivorship Rule Configuration | 🔲 Not started |
| 3.5 | Workflow & Policy Metadata | 🔲 Not started |

### Phase 4 — Source System Integration Architecture

| Module | Name | Status |
|---|---|---|
| 4.1 | Source System Registry & Connector Framework | 🔲 Not started |
| 4.2 | Field Mapping & Crosswalk Configuration | 🔲 Not started |
| 4.3 | Source System Priority & Trust Scoring | 🔲 Not started |
| 4.4 | Connector Protocol Adapter Library | 🔲 Not started — added at Roadmap v1.1 |
| 4.5 | ERP-Specific Connector Catalog | 🔲 Not started — added at Roadmap v1.1 |
| 4.6 | Source System Role & Precedence Policy | 🔲 Not started — added at Roadmap v1.1 |
| 4.7 | Middleware / iPaaS Passthrough Integration | 🔲 Not started — added at Roadmap v1.1 |

### Phase 5 — Data Ingestion

| Module | Name | Status |
|---|---|---|
| 5.1 | Batch Ingestion Engine | 🔲 Not started |
| 5.2 | Real-Time / Event-Driven Ingestion (API, CDC, Streaming) | 🔲 Not started |
| 5.3 | File-Based / Manual Ingestion (Excel, CSV, Manual Entry) | 🔲 Not started |
| 5.4 | Raw / Landing Zone & Source Record Store | 🔲 Not started |

### Phase 6 — Standardization & Validation

| Module | Name | Status |
|---|---|---|
| 6.1 | Data Standardization Engine | 🔲 Not started |
| 6.2 | Data Validation Engine | 🔲 Not started |
| 6.3 | Data Enrichment | 🔲 Not started |

### Phase 7 — Matching Engine

| Module | Name | Status |
|---|---|---|
| 7.1 | Exact & Normalized Matching | 🔲 Not started |
| 7.2 | Fuzzy & Composite Matching | 🔲 Not started |
| 7.3 | Match Decisioning & Steward Review Queue | 🔲 Not started |

### Phase 8 — Golden Record & Survivorship

| Module | Name | Status |
|---|---|---|
| 8.1 | Golden Record Engine | 🔲 Not started |
| 8.2 | Attribute-Level Survivorship Execution | 🔲 Not started |
| 8.3 | Confidence Scoring | 🔲 Not started |

### Phase 9 — Merge / Unmerge

| Module | Name | Status |
|---|---|---|
| 9.1 | Merge Engine | 🔲 Not started |
| 9.2 | Unmerge Engine | 🔲 Not started |
| 9.3 | Merge History & Relationship Tracking | 🔲 Not started |

### Phase 10 — Data Quality

| Module | Name | Status |
|---|---|---|
| 10.1 | Data Quality Dimension Framework | 🔲 Not started |
| 10.2 | Data Quality Scoring Engine | 🔲 Not started |
| 10.3 | Data Quality Dashboard & Reporting | 🔲 Not started |
| 10.4 | Data Quality Issue Remediation Workflow | 🔲 Not started |

### Phase 11 — Governance & Stewardship

| Module | Name | Status |
|---|---|---|
| 11.1 | Data Stewardship Workbench | 🔲 Not started |
| 11.2 | Ownership & Accountability Model | 🔲 Not started |
| 11.3 | Data Classification & Policy Management | 🔲 Not started |
| 11.4 | Business Glossary | 🔲 Not started |

### Phase 12 — Workflow & Approval

| Module | Name | Status |
|---|---|---|
| 12.1 | Generic Workflow Engine | 🔲 Not started |
| 12.2 | New Record & Change Request Approval | 🔲 Not started |
| 12.3 | Merge / Unmerge Approval | 🔲 Not started |

### Phase 13 — Audit & Lineage

| Module | Name | Status |
|---|---|---|
| 13.1 | Audit Log Engine | 🔲 Not started |
| 13.2 | Data Lineage Tracking | 🔲 Not started |
| 13.3 | Temporal History & Change Timeline | 🔲 Not started |

### Phase 14 — Distribution & Synchronization

| Module | Name | Status |
|---|---|---|
| 14.1 | Distribution / Publish Engine | 🔲 Not started |
| 14.2 | Target System Subscription Management | 🔲 Not started |
| 14.3 | Delivery Status Tracking & Reconciliation | 🔲 Not started |
| 14.4 | Conflict & Failure Handling in Distribution | 🔲 Not started |

### Phase 15 — Security & Multi-Tenancy

| Module | Name | Status |
|---|---|---|
| 15.1 | Tenant Isolation Architecture | 🔲 Not started |
| 15.2 | RBAC / ABAC Authorization Engine | 🔲 Not started |
| 15.3 | Row-Level & Attribute-Level Security Enforcement | 🔲 Not started |
| 15.4 | PII Masking & Encryption | 🔲 Not started |
| 15.5 | Segregation of Duties & Approval Integrity | 🔲 Not started |

### Phase 16 — Observability & Scalability

| Module | Name | Status |
|---|---|---|
| 16.1 | Monitoring & Alerting | 🔲 Not started |
| 16.2 | Performance & Scalability Architecture | 🔲 Not started |
| 16.3 | Disaster Recovery & Failover | 🔲 Not started |
| 16.4 | API Gateway & Rate Limiting | 🔲 Not started |

**Total: 16 phases, 59 modules, 1 complete, 58 not started.** Design order per the Roadmap's Design Order Summary: Phase 1 → 2 → 3 → 4 → 5 → ... → 16, modules within each phase in ascending numeric order. **Next module: 1.2 — Business Domain Registry.**

---

## 8. Finalized Design Decisions by Domain

> These are architecture-level decisions locked during Roadmap design, ahead of any module's detailed 5-layer session. Each subsection will be refined and superseded, where applicable, by its owning module's actual design close, per the amendment rule in Section 6. Read this section as "what we've already committed to," not as a substitute for the modules themselves.

### 8.0 Platform-Wide Technical Conventions

> Declared before Module 1.1 begins, so the first module inherits these conventions rather than inventing them — the same discipline behind AptoWMS's 8.16/8.17/8.19. Every module's Layer 4 (schema) and Layer 5 (events) must conform to this subsection; deviations require explicit justification recorded in that module's file.

**Standard DB columns**
- Every operational table carries: `id` (UUID primary key), `tenant_id` (mandatory, indexed — see 8.10), `created_at`, `created_by`, `updated_at`, `updated_by`
- **Configuration tables** (domain, entity, attribute, rule, policy definitions) use soft-delete: `is_deleted`, `deleted_at`, `deleted_by`
- **Source and golden-record tables** (`MDM_SOURCE_RECORD`, `MDM_GOLDEN_RECORD`, `MDM_GOLDEN_ATTRIBUTE`) never use soft-delete at all — they use the non-destructive retirement/versioning pattern from 8.4/8.8 (`merged_into`, `effective_from`/`effective_to`, `version`) instead, because "deleted" is not a valid state for a record that must remain traceable and unmergeable-in-reverse
- Custom/tenant-extensible fields, where a module needs them, use a `custom_data JSONB NULL DEFAULT '{}'` column — no fixed `custom_text_1..N` columns, matching the pattern AptoWMS standardized on at its Module 1.12

**Standard event envelope**
- Every event published to Kafka, from any module, carries the same mandatory envelope fields: `event_id` (UUID, the deduplication key), `tenant_id`, `correlation_id` (groups all events from one logical operation), `timestamp_utc`
- Events publish after DB commit, never inside a transaction
- Consumers are idempotent by construction — deduplicate on `event_id`, never assume at-most-once delivery
- Breaking changes to an event's payload schema require a new event version, never an in-place silent change

**Permission naming pattern**
- Fixed pattern: `Domain.Module.Action` (e.g. `CUSTOMER.GOLDEN_RECORD.MERGE`, `CONFIG.MATCH_RULE.EDIT`) — declared here so Module 1.3 designs the permission matrix against a pattern that every later module can extend without renegotiating the format
- VIEW is a prerequisite permission for any other action on the same screen — same convention as AptoWMS

**AI / ML boundary**
- No AI or ML integration in the initial build (see Section 5). If a future module introduces ML-assisted matching, enrichment, or scoring, it must follow the same boundary AptoWMS applies to its AI Advisory phase: **AI advises, it never mutates the golden record directly.** Any ML-produced score must still route through the existing human/steward review path (Module 7.3) rather than create a new auto-decision path — this is a platform boundary, not a per-module choice.

### 8.1 Platform & Architecture

- Cloud-native, event-driven, horizontally scalable modular monolith (Build Phase 1)
- Metadata-driven — no engine hardcodes a domain's attribute list; every engine reads from the Phase 3 metadata registry
- API-first — Entity, Match, Merge, Golden Record, Quality, Workflow, Governance, and Audit APIs precede any screen
- Kafka as event highway — shared convention with AptoWMS
- DB-per-tenant — full data isolation, same pattern as AptoWMS

### 8.2 Tenant & Domain Model

- Organization → Tenant → Product Instance (WMS / TMS / **MDM**) — same platform-wide model as AptoWMS
- Domains (Customer, Supplier, Product, Location, Employee, Organization, Asset, Material, Account, Reference Data) are platform-shared configuration; tenants opt in per domain (Module 1.2)
- A domain cannot be deactivated for a tenant while golden records exist in it
- Organization hierarchy (Module 1.1) must be acyclic — no circular parent references, same discipline as canonical entity hierarchies (Module 2.4) and relationship types (Module 2.6)

### 8.3 Canonical Entity Model

- Every canonical entity declares a natural-key candidate set even where a surrogate key is used internally (Module 2.1)
- Canonical model changes are additive-only in production — no destructive attribute removal without a deprecation window
- The Golden Record is never a flat table — every attribute carries value + source + confidence + effective dates + survivorship rule (Module 8.1)
- Customer and Supplier may share one underlying Organization/Tax/Address sub-entity via `MDM_ENTITY_CROSS_DOMAIN_LINK` (Module 2.3) rather than maintaining two disconnected golden records for the same legal entity
- Every canonical attribute must carry a data classification (Public / Internal / Confidential / Restricted) before a domain goes live — unclassified is not a valid production state (feeds 8.10 below)

### 8.4 Matching & Merge

- Match and Merge are permanently separate engines and separate tables — a match decision never itself performs consolidation (Modules 7.x / 9.x)
- Matching techniques run in a fixed cascade: exact → normalized → fuzzy → composite, per domain configuration (Module 3.3)
- Thresholds are explicit and named: 95–100% Auto Match, 80–95% Review, <80% New Record — no unnamed magic numbers, no ad hoc code-level overrides
- Merge never physically deletes a record — retired records carry `merged_into`; every merge is unmergeable by design (Modules 9.1 / 9.2)
- Two users cannot resolve the same match candidate simultaneously — first decision wins (Module 7.3)

### 8.5 Survivorship

- Attribute-level, not record-level — no domain may declare "Source X wins everything" (Module 3.4)
- Evaluation order is fixed platform-wide: source priority → attribute priority → data quality signal → recency → manual override (Modules 3.4 / 8.2)
- A manual override always outranks computed survivorship until explicitly cleared by an authorized steward, and is always traceable to a user and reason

### 8.6 Data Quality

- Six standard dimensions: Completeness, Accuracy, Consistency, Uniqueness, Validity, Timeliness — shared platform metadata, not private per-domain definitions (Module 10.1)
- Quality scoring is attribute-level and re-runs on every golden record update, not just on a schedule (Module 10.2)
- A score drop below a configurable threshold automatically raises a remediation task (Module 10.4) — never a silent, unactioned dashboard number

### 8.7 Governance & Stewardship

- Requestor cannot self-approve — enforced platform-wide from Module 1.3 onward, re-verified at every workflow execution (Module 12.1), not just at the UI level
- Every active domain must have exactly one accountable business owner (Module 11.2), distinct from the technical steward pool (Module 11.1)
- Unmerge approval is mandatory by default (Module 12.3); merge approval requirement is policy-driven per domain/classification, not universal

### 8.8 Audit & Lineage

- Audit records capture who / what / when / why / before / after / source / approval as mandatory fields — no partial audit rows (Module 13.1)
- Audit data is never mixed into operational tables — separate store, append-only, no updates or deletes
- Golden attributes carry `effective_from` / `effective_to` / `version` — never simply overwritten (Module 13.3)
- Lineage is a derived view over existing tables (`MDM_SOURCE_RECORD`, `MDM_GOLDEN_ATTRIBUTE`, `MDM_SURVIVORSHIP_*`) — never a separately-maintained parallel structure that can drift out of sync (Module 13.2)

### 8.9 Source System Integration & ERP Connectivity

- The connector framework (Module 4.1) is a registry pattern — a new source system is configuration, not new platform code
- Transport is decomposed into reusable protocol adapters (Module 4.4: IDoc/ALE, BAPI/RFC, OData, SOAP, DB interface tables, file drop, CDC, REST/webhook) — ERP-specific behavior lives only in the packaged connector (Module 4.5), never in the adapter or the platform core
- Packaged connectors ship for SAP ECC, SAP S/4HANA, Oracle EBS, Oracle Fusion, MS Dynamics 365, NetSuite, Workday, and Generic/Other — every connector declares its supported ERP version range explicitly
- **Source role is an explicit, per-domain decision (Module 4.6)** — every ERP source system is either a "contributing source" (platform default, survivorship decides) or has "system-of-record deference" declared for a domain; deference affects survivorship precedence only, never data-quality enforcement
- Middleware/iPaaS passthrough (Module 4.7) is a transport choice only — it must never bypass field mapping, standardization, or validation
- Idempotency key is fixed platform-wide: `source_system + source_record_id + event_id + version` (Module 5.2)
- Adding a new ERP to the catalog must never require changes to Phases 1–3 or 5–16 — if it does, that is treated as an architecture defect, not an acceptable cost of onboarding

### 8.10 Security & Multi-Tenancy

- Security hierarchy: Tenant → Organization → Domain → Entity → Attribute → Action (Module 15.2)
- ABAC narrows RBAC access, never expands it
- Restricted/PII-classified attributes are encrypted at rest by default at classification-assignment time (Module 15.4), not left to per-domain discretion
- Masking happens server-side before data leaves the platform boundary — never a client-side hide that still ships the raw value (Module 15.3)
- Every query, cache key, and event topic is tenant-scoped by construction — no code path queries "all tenants" outside internal platform-ops tooling with its own separate authorization (Module 15.1)

### 8.11 Distribution

- The golden record lifecycle is not "done" at creation — distribution status is tracked as part of the record's lifecycle (Module 14.1)
- Publish failures must not block internal correctness — publishing is decoupled and retryable
- A target system only receives attributes it is entitled to per subscription and classification rules (Module 14.2)
- Reconciliation mismatches route to the steward workbench (Module 11.1) — never silently auto-corrected (Module 14.3)

### 8.12 Data Ingestion

- Landing-zone records (`MDM_SOURCE_RECORD`) are immutable once written — corrections arrive as new versions, never in-place edits (Module 5.4)
- Every ingestion channel — batch, real-time/CDC, file, manual — lands in the same raw store and flows through the identical standardization → validation → matching pipeline; no channel gets a shortcut path (Modules 5.1–5.3)
- A batch that fails schema validation at the header level is rejected wholesale with a clear reason; partial-row failures within an otherwise-valid batch are quarantined per row, never failing the whole batch silently (Module 5.1)
- Idempotency key `source_system + source_record_id + event_id + version` (already declared in 8.9) is enforced at ingestion, not downstream — out-of-order or duplicate events are detected and discarded before they reach standardization

### 8.13 Standardization & Validation

- Standardization must be deterministic and re-runnable — re-standardizing the same raw value always produces the same standardized value (Module 6.1); this is a hard requirement given the "no AI/ML" decision in Section 5 — standardization rules are rule-engine-based, not model-based, specifically so this determinism holds
- Standardized values are stored alongside raw values, never overwriting them
- Validation failures are attribute-level, not record-level — a record with one bad attribute is quarantined for that attribute while other valid attributes proceed where domain config allows (Module 6.2)
- A quarantined record is always visible to a data steward with a plain-language reason — never silently dropped or force-passed
- Enrichment (Module 6.3) is additive and competes for survivorship like any other source — it never overwrites a source-provided value outright, and enrichment service failures never block the pipeline

### 8.14 Observability & Scalability

- Every engine (ingestion, standardization, matching, survivorship, distribution) exposes latency, throughput, and error-rate metrics as a baseline — no engine ships without observability (Module 16.1)
- No engine may assume unbounded single-node processing — every batch/streaming engine declares its partitioning strategy (by tenant/domain) at design time (Module 16.2)
- Per the Senior Architect Mindset's explicit "design for failure" principle, every module's design session must produce a tested answer for its own failure scenarios (source system down, malformed data, mid-batch crash, partial publish failure, duplicate event delivery, concurrent merge, rejected/incorrect merge needing undo) before that module is considered closed — this is a Layer 2 (Business Rules) obligation, not a separate afterthought phase
- Golden records and merge/unmerge history must never be silently lost or duplicated during recovery — this is only safe because of the idempotency (8.9/8.12) and append-only audit (8.8) guarantees already locked elsewhere in this section; Module 16.3 (DR & Failover) does not invent new safety guarantees, it exercises the ones already designed in

### 8.15 Reference Data & Localization

- Reference lists (countries, currencies, industry codes, ID types) ship as platform-owned "system" lists; tenants may extend but never delete system values (Module 1.4)
- A reference value in use by any golden record cannot be hard-deleted, only deprecated
- All DB timestamps are stored in UTC without exception; display resolution follows the same priority chain AptoWMS uses — User → Warehouse/Tenant-equivalent → Tenant — highest specificity wins
- Reference Data is itself an MDM domain (per 8.2), not a platform special case — it eventually flows through the same ingestion/standardization/golden-record pipeline as any other domain, not a separate hardcoded table set

---

## 9. File Reference Guide

| Topic | File |
|---|---|
| Full 16-phase, 59-module roadmap with 5-layer scope for every module | `AptoMDM_Design_Roadmap.md` (v1.1) |
| Architecture overview, all finalized decisions | `Apto_MDM_Bible.md` (this file) |
| Senior architect design principles the Roadmap and Bible are built from | `Senior_Architect_Mindset` (source document) |
| All stubbed design elements — what they are, where they will be resolved | `AptoMDM_Stubs_Tracker.md` |
| Active design session rules, response rules, cross-cutting decisions | `AptoMDM_Project_Instructions.md` |
| Module-level detailed designs (process flow, business rules, screens, schema, events) | `Modules/Phase {phase}/AptoMDM_Module_{phase}_{sequence}_{Name}.md` — Module 1.1 closed; Module 1.2 is next |

---

## 10. Open Items & How to Move Forward

### Open design items (not yet resolved)

| Item | Raised in | Will be resolved in |
|---|---|---|
| ERP connector priority order — which ERP family (SAP ECC, S/4HANA, Oracle, Dynamics, NetSuite, Workday) gets built first | Phase 4 design discussion | Module 4.5 — ERP-Specific Connector Catalog, pending client-base priority input |
| Source precedence default posture — should the platform default to "MDM always wins" or "ERP can request deference"? A product-positioning decision, not purely architectural | Phase 4 design discussion | Module 4.6 — Source System Role & Precedence Policy |
| Competing-governance-system handling (e.g. a client already running SAP MDG) | Phase 4 design discussion | Module 4.6 |
| Golden Record confidence-decay thresholds — when does an unconfirmed attribute get flagged for steward review? | Phase 8 roadmap scope | Module 8.3 — Confidence Scoring |
| Dual-control action list — which actions require two independent approvers (bulk unmerge, classification downgrade, others)? | Phase 15 roadmap scope | Module 15.5 — Segregation of Duties & Approval Integrity |
| Reporting DB retention tiers per tenant subscription — mirrors an AptoWMS pattern, not yet defined for MDM | Phase 10 roadmap scope | Module 10.3 — Data Quality Dashboard & Reporting |
| Relationship to AptoWMS/AptoTMS product instances — does an MDM-active tenant's WMS/TMS instance become a *consuming* target system by default, or is that an explicit opt-in? | Cross-product architecture question | Module 14.2 — Target System Subscription Management, or a dedicated cross-product amendment |
| **Fuzzy-match threshold tuning inputs** — with no ML model (Section 5), initial `pg_trgm`/`strsim` thresholds must be set from sample data or client input, not learned; what sample data seeds the first tenant's Module 3.3 configuration? | Bible v1.1 tech-stack lock | Module 3.3 — Matching Rule Configuration, first tenant onboarding |
| **Frontend/backend type-contract tooling** — `utoipa`-generated OpenAPI spec needs a concrete TypeScript client generation step (e.g. `openapi-typescript`) wired into the build; not yet chosen | Bible v1.1 tech-stack lock | Module 1.5 — Screen & API Standardization Framework |

### How to run each design session

1. State the module number and name
2. Raise any concept-level questions before starting Layer 1
3. Go through all 5 layers in order — agree each layer before moving to the next
4. Check the Stubs Tracker — does this module consume any stubs? Does it introduce new ones?
5. After all 5 layers are agreed — generate the module `.md` file
6. Update the Stubs Tracker
7. Update this Project Bible's Section 7 status table and the relevant Section 8 subsection
8. If any prior module was changed — update that module's file with an amendment section

### Design principles to never compromise

1. **Golden Record is sacred** — every value must be explainable back to a source, confidence, and rule; no silent overwrites
2. **Match and Merge never collapse into one operation** — reversibility depends on this separation holding
3. **Tenant isolation is non-negotiable** — no design that could leak data between tenants
4. **Events after commit, not inside transactions** — this is what makes the system reliable, same discipline as AptoWMS
5. **Source data is never destroyed** — retirement and versioning only; unmerge must always be possible
6. **Metadata drives every engine** — adding a domain or an ERP is configuration, never a platform rewrite
7. **Simple defaults, advanced configuration** — every config should have a sensible default so small tenants can operate without touching it, and advanced options for large tenants who need them

---

*End of AptoMDM 2026 Project Bible — Version 1.1*