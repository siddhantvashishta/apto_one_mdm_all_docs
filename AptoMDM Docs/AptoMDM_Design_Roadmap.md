# AptoMDM 2026 — Design Roadmap

> **Version 1.1** — current
> August 2026 | Confidential — Apto Engineering

---

## Version History

| Version | Date | Changed by | Summary of changes |
|---|---|---|---|
| **1.1** | Aug 2026 | Architecture review | **Phase 4 expanded from 3 modules to 7** to make ERP/source-system integration a first-class, method-agnostic capability rather than an implicit assumption inside the generic connector framework. Added: **4.4 Connector Protocol Adapter Library** (IDoc/ALE, BAPI/RFC, OData/REST, SOAP, DB interface tables, CDC, iPaaS/middleware — reusable transport adapters, not per-ERP code), **4.5 ERP-Specific Connector Catalog** (packaged connectors for SAP ECC, SAP S/4HANA, Oracle EBS, Oracle Fusion, MS Dynamics 365, NetSuite, Workday, Generic/Other), **4.6 Source System Role & Precedence Policy** (contributing-source vs. system-of-record-deference decision per domain per ERP — the governance question that sits above connectivity), **4.7 Middleware / iPaaS Passthrough Integration** (MuleSoft, Boomi, SAP CPI, Azure Integration Services as an alternative to point-to-point connectors for clients who already run an integration bus). Phase Overview table and Design Order Summary updated to reflect the 4.1–4.7 sequence. No changes to Phases 1–3 or 5–16 canonical model, matching, survivorship, or governance logic — this revision is additive and isolated to Phase 4. |
| 1.0 | Aug 2026 | Initial draft | Initial 16-phase, ~55-module roadmap authored from the Senior Architect Mindset document, structured on the AptoWMS 2026 design methodology (phase → module → 5-layer design: Process flow, Business rules, UI screens, DB schema, Events). |

---

## How to use this document

AptoMDM is architected as a **metadata-driven MDM platform**, not a collection of per-domain screens. Customer, Supplier, Product, Location, etc. are **configurations on top of one engine** — they do not get separately-coded modules once the platform layer exists.

Each module is broken into 5 design layers, in this order:

1. **Process flow** — end-to-end journey (source system → golden record → distribution)
2. **Business rules** — validations, thresholds, edge cases, exceptions
3. **UI screens** — web / steward console / admin config (only relevant surfaces per module)
4. **DB schema** — tables, fields, relationships
5. **Events** — what gets published and what gets consumed

Complete all 5 layers before moving to the next module. A module is not "done" if it can't answer the architecture's core question:

> *What is the authoritative representation of this business entity, and why should the system trust it?*

### Design principles carried through every module
- **Golden Record is never a flat table** — every attribute carries value + source + confidence + effective dates + survivorship rule.
- **Match ≠ Merge** — these are always separate engines, separate tables, separate reversibility guarantees.
- **Never destroy source data** — no hard deletes on source or master records; only `merged_into` relationships, versioning, and unmerge paths.
- **Attribute-level survivorship**, not "one source wins everything."
- **Metadata-driven**, not hardcoded per domain — a new domain (e.g. "Employee") should be addable via configuration, not a platform rewrite.
- **API-first** — every capability is an API before it is a screen.
- **Event-driven** where synchronous coupling would block scale (matching, distribution, quality scoring).

---

## Phase Overview

| Phase | Name | Answers |
|---|---|---|
| 1 | Business Domain & Platform Foundation | Who are we mastering data for, and on what platform? |
| 2 | Canonical Data Model | What is the authoritative shape of each entity? |
| 3 | Metadata Architecture | How is the platform configured without code changes? |
| 4 | Source System Integration Architecture | How do systems connect to MDM — by any method, any ERP? |
| 5 | Data Ingestion | How does data physically arrive? |
| 6 | Standardization & Validation | Is the data clean and comparable? |
| 7 | Matching Engine | Are two records the same real-world entity? |
| 8 | Golden Record & Survivorship | Which value wins, and why? |
| 9 | Merge / Unmerge | How are entities consolidated — reversibly? |
| 10 | Data Quality | Is the data measurably trustworthy? |
| 11 | Governance & Stewardship | Who owns it, and who can touch it? |
| 12 | Workflow & Approval | Who signs off, and on what? |
| 13 | Audit & Lineage | What happened, and where did it come from? |
| 14 | Distribution & Synchronization | How does trusted data get back out? |
| 15 | Security & Multi-Tenancy | Who is allowed to see or change what? |
| 16 | Observability & Scalability | Will this still work at 100M+ records? |

---

## Phase 1 — Business Domain & Platform Foundation

> Nothing else can be designed until domains, tenancy, and the platform shell exist. This is the MDM equivalent of AptoWMS's Warehouse & Zone Master — every other phase depends on it.

---

### 1.1 Tenant & Organization Setup

**1.1.1 Process flow**
- How a new tenant is provisioned on the MDM platform
- How organizational hierarchy is defined (holding company → subsidiary → business unit)
- How a tenant's active domains are enabled/disabled

**1.1.2 Business rules**
- Tenant must have an explicit data residency region — no default
- A tenant cannot be deleted, only deactivated, if any golden records exist
- Organization hierarchy must be acyclic (no circular parent references)
- At least one tenant admin must exist at all times

**1.1.3 UI screens**
- Web: Tenant list / provisioning screen (internal ops)
- Web: Organization hierarchy tree editor
- Web: Domain activation toggle screen per tenant

**1.1.4 DB schema**
- `TENANT` table
- `ORGANIZATION` table (self-referencing hierarchy)
- `TENANT_DOMAIN_CONFIG` table

**1.1.5 Events**
- `TenantProvisioned`
- `OrganizationHierarchyChanged`

---

### 1.2 Business Domain Registry

**1.2.1 Process flow**
- How a domain (Customer, Supplier, Product, Location, Employee, Organization, Asset, Material, Account, Reference Data) is registered on the platform
- How a domain is composed of sub-entities (e.g. Customer → Identity, Contact, Address, Tax, Relationships)
- How a tenant selects which domains apply to them

**1.2.2 Business rules**
- Domain code must be unique platform-wide (not per-tenant) — domains are shared configuration, tenants opt in
- A domain cannot be deactivated for a tenant if golden records exist in it
- Every domain must declare at least one sub-entity before it can be activated
- Domains are additive — activating "Product" must never require touching "Customer" code

**1.2.3 UI screens**
- Web: Domain catalog screen (Customer, Supplier, Product, Location, Employee, Organization, Asset, Material, Account, Reference Data)
- Web: Domain detail — sub-entity composition editor
- Web: Tenant domain activation screen

**1.2.4 DB schema**
- `MDM_DOMAIN` table
- `MDM_DOMAIN_SUBENTITY` table
- `TENANT_DOMAIN_ACTIVATION` table

**1.2.5 Events**
- `DomainRegistered`
- `DomainActivatedForTenant`

---

### 1.3 User, Role & Permission Matrix

**1.3.1 Process flow**
- How a platform user is created and linked to a tenant
- How roles are assigned (Admin, Data Steward, Approver, Integration Service Account, Viewer)
- How a user's access is suspended, expired, or elevated for a review task

**1.3.2 Business rules**
- Every user must have at least one tenant + domain access record to log in
- System roles (Admin, Steward, Approver) cannot be deleted, only deactivated
- A Steward's queue assignment is domain-scoped, not entity-instance-scoped
- Requestor of a change cannot also be its approver (segregation of duties, enforced platform-wide from day one — see also 15.5)

**1.3.3 UI screens**
- Web: User list / invite screen
- Web: Role management screen
- Web: Permission matrix screen (role × domain × action grid)
- Web: Steward assignment screen (domain → steward pool)

**1.3.4 DB schema**
- `MDM_USER` table
- `ROLE` table
- `PERMISSION` table
- `ROLE_PERMISSION` table
- `USER_DOMAIN_ACCESS` table

**1.3.5 Events**
- `UserCreated`
- `UserAccessGranted`
- `UserAccessRevoked`

---

### 1.4 Reference Data & Code Tables

**1.4.1 Process flow**
- How platform-level reference lists are defined (countries, currencies, industry codes, ID types e.g. GSTIN/DUNS/PAN)
- How a tenant extends or overrides a shared reference list
- How reference data changes propagate to entities that use them

**1.4.2 Business rules**
- Reference lists ship as platform-owned "system" lists — tenants may extend, never delete system values
- A reference value in use by any golden record cannot be hard-deleted, only deprecated
- Reference Data is itself an MDM domain (per 1.2), not a special case — it flows through the same engine eventually

**1.4.3 UI screens**
- Web: Reference list catalog
- Web: Reference value management screen (add/deprecate)

**1.4.4 DB schema**
- `MDM_REFERENCE_LIST` table
- `MDM_REFERENCE_VALUE` table
- `TENANT_REFERENCE_OVERRIDE` table

**1.4.5 Events**
- `ReferenceValueDeprecated`

---

### 1.5 Screen & API Standardization Framework

**1.5.1 Process flow**
- How every future module inherits the same list/detail/form conventions
- How the API layer's naming, versioning, and pagination conventions are fixed once, platform-wide

**1.5.2 Business rules**
- Every entity screen must support: search, filter, bulk action, export — declared once, inherited everywhere
- Every domain API must expose the same verb set: create, update, search, get-by-id, get-history — no domain-specific verb sprawl
- REST resource naming is domain-agnostic (`/entities/{domain}/{id}`, not `/customers/{id}` hardcoded)

**1.5.3 UI screens**
- Web: Shared list/grid component conventions (this is a framework decision, not a standalone screen)
- Web: Shared entity-detail layout convention (Golden Record header + attribute panel + lineage tab + history tab)

**1.5.4 DB schema**
- No new tables — this module governs conventions, not data

**1.5.5 Events**
- No events — framework-only module

---

## Phase 2 — Canonical Data Model

> "Start with business domains, not screens." This phase turns Phase 1's domain registry into an actual entity shape — the foundation every downstream engine (match, survivorship, quality) reads and writes against.

---

### 2.1 Canonical Entity Model

**2.1.1 Process flow**
- How a domain's canonical entity shape is defined (entity + its attributes)
- How a canonical entity relates to its domain and sub-entities from 1.2
- How versioning of the canonical model itself is handled (schema evolution without breaking live golden records)

**2.1.2 Business rules**
- Every canonical entity must declare a natural key candidate set even if a surrogate key is used internally
- Canonical model changes are additive-only in production — no destructive attribute removal without a deprecation window
- Every attribute must declare a data type from the Phase 3 type registry — free-text-only attributes are disallowed for anything used in matching or survivorship

**2.1.3 UI screens**
- Web: Canonical entity designer (domain → entity → attribute list)
- Web: Canonical model version history viewer

**2.1.4 DB schema**
- `MDM_ENTITY` table (`entity_id`, `domain_id`, `entity_type`, `status`, `version`, `created_at`, `updated_at`)
- `MDM_CANONICAL_ATTRIBUTE` table

**2.1.5 Events**
- `CanonicalModelVersionPublished`

---

### 2.2 Customer Domain Canonical Model

**2.2.1 Process flow**
- How Customer's sub-entities (Identity, Contact, Address, Organization, Tax, Relationships, Classification) map onto the canonical model from 2.1
- How a customer's multiple addresses/contacts are represented without becoming duplicate top-level entities

**2.2.2 Business rules**
- Identity attributes (legal name, registration number) are the natural-key candidates for Customer matching
- A customer must have exactly one "primary" address and may have any number of secondary addresses
- Tax ID format is validated against the country reference data from 1.4

**2.2.3 UI screens**
- Web: Customer canonical attribute set (config, not runtime — runtime screens are in Phase 8)

**2.2.4 DB schema**
- Customer-domain rows in `MDM_CANONICAL_ATTRIBUTE` (Name, Phone, Email, Address, Tax ID, Classification, Relationship)

**2.2.5 Events**
- None — configuration-time module

---

### 2.3 Supplier Domain Canonical Model

**2.3.1 Process flow**
- How Supplier reuses the Organization/Tax/Address shape from Customer (shared sub-entity types) without duplicating schema
- How supplier-specific attributes (payment terms, banking details, quality rating) extend the shared shape

**2.3.2 Business rules**
- Supplier and Customer may point to the same real-world legal entity — the platform must support one Organization sub-entity feeding both domains, not two disconnected golden records
- Banking detail attributes are flagged sensitive at the metadata level (feeds Phase 15 attribute-level security)

**2.3.3 UI screens**
- Web: Supplier canonical attribute set (config-time)

**2.3.4 DB schema**
- Supplier-domain rows in `MDM_CANONICAL_ATTRIBUTE`
- `MDM_ENTITY_CROSS_DOMAIN_LINK` table (same legal entity, multiple domain roles)

**2.3.5 Events**
- None — configuration-time module

---

### 2.4 Product / Material Domain Canonical Model

**2.4.1 Process flow**
- How Product and Material share a canonical shape (SKU, description, UOM, classification, specifications) while remaining separately governed domains
- How product hierarchy (category → sub-category → item) is represented

**2.4.2 Business rules**
- Product natural key candidates are GTIN/barcode where available, else SKU + manufacturer
- Hierarchy must be acyclic, same rule pattern as 1.1's organization hierarchy

**2.4.3 UI screens**
- Web: Product canonical attribute set (config-time)

**2.4.4 DB schema**
- Product/Material-domain rows in `MDM_CANONICAL_ATTRIBUTE`
- `MDM_ENTITY_HIERARCHY` table

**2.4.5 Events**
- None — configuration-time module

---

### 2.5 Location, Employee, Asset & Account Domain Canonical Models

**2.5.1 Process flow**
- How the remaining Phase-1-registered domains (Location, Employee, Organization, Asset, Account) get their canonical shapes defined using the same 2.1 framework
- How domain-specific natural keys are declared for each (site code for Location, employee ID for Employee, asset tag for Asset, account number for Account)

**2.5.2 Business rules**
- Same additive-only versioning rule as 2.1 applies uniformly
- Employee domain attributes touching PII are flagged sensitive at definition time, not retrofitted later (feeds 15.4)

**2.5.3 UI screens**
- Web: Canonical attribute set per remaining domain (config-time, same designer screen from 2.1)

**2.5.4 DB schema**
- Remaining-domain rows in `MDM_CANONICAL_ATTRIBUTE`

**2.5.5 Events**
- None — configuration-time module

---

### 2.6 Entity Relationship Model

**2.6.1 Process flow**
- How relationships between entities are modeled (Customer ↔ Supplier same-legal-entity, Parent-Subsidiary, Product ↔ Product substitute/component, Employee ↔ Organization reporting line)
- How relationship types are themselves configurable metadata, not hardcoded joins

**2.6.2 Business rules**
- A relationship must declare a type, a direction (or explicitly bidirectional), and an effective date range
- Circular relationships are only valid for explicitly bidirectional types (e.g. "affiliated with")
- Deleting a relationship never deletes the underlying entities — relationships are edges, not ownership

**2.6.3 UI screens**
- Web: Relationship type catalog (config-time)
- Web: Relationship graph viewer (runtime, per golden entity)

**2.6.4 DB schema**
- `MDM_RELATIONSHIP_TYPE` table
- `MDM_ENTITY_RELATIONSHIP` table

**2.6.5 Events**
- `EntityRelationshipCreated`
- `EntityRelationshipEnded`

---

## Phase 3 — Metadata Architecture

> This is what makes the platform a platform. A new domain should be addable through configuration here — not by writing new code in every downstream engine.

---

### 3.1 Domain & Entity Metadata Registry

**3.1.1 Process flow**
- How domain/entity/attribute metadata from Phase 2 is centralized into one queryable registry that every engine (match, quality, survivorship, security) reads from
- How metadata changes are versioned and rolled out without downtime

**3.1.2 Business rules**
- Every downstream engine must read entity shape from this registry — no engine may hardcode a domain's attribute list
- Metadata changes require a published version before they take effect on live traffic (no silent hot-edits)

**3.1.3 UI screens**
- Web: Unified metadata explorer (domain → entity → attribute → rules, single pane)

**3.1.4 DB schema**
- `MDM_METADATA_VERSION` table
- Views/materialized joins across `MDM_DOMAIN`, `MDM_ENTITY`, `MDM_CANONICAL_ATTRIBUTE`

**3.1.5 Events**
- `MetadataVersionPublished`

---

### 3.2 Attribute Data Type & Validation Rule Registry

**3.2.1 Process flow**
- How data types (string, numeric, date, enum, reference, composite) are defined once and reused across every domain
- How validation rules (format, range, mandatory, cross-field) are attached to an attribute as configuration

**3.2.2 Business rules**
- A validation rule is domain-agnostic at definition (a "valid email" rule works identically for Customer, Supplier, Employee)
- Mandatory-attribute rules cannot be relaxed per source system — mandatory is a golden-record-level guarantee, not a per-feed exception
- Rule engine must support rule chaining (format check → cross-field check → business rule check) with short-circuit on first failure

**3.2.3 UI screens**
- Web: Data type catalog
- Web: Validation rule builder (no-code rule expression editor)

**3.2.4 DB schema**
- `MDM_DATA_TYPE` table
- `MDM_VALIDATION_RULE` table
- `MDM_ATTRIBUTE_VALIDATION_BINDING` table

**3.2.5 Events**
- `ValidationRulePublished`

---

### 3.3 Matching Rule Configuration

**3.3.1 Process flow**
- How matching techniques (exact, normalized, fuzzy, composite) and their weights/thresholds are configured per domain, per attribute, without code changes
- How a domain's match configuration is tested against sample data before going live

**3.3.2 Business rules**
- Thresholds must be explicit and named (95–100% Auto Match, 80–95% Review, <80% New Record) — no unnamed magic numbers
- Composite weights across attributes must sum to 100% per domain
- A matching configuration cannot go live without at least one dry-run against a sample batch (feeds 7.x)

**3.3.3 UI screens**
- Web: Match rule configuration screen (per domain: technique + weight + threshold)
- Web: Match rule simulation / dry-run screen

**3.3.4 DB schema**
- `MDM_MATCH_RULE` table
- `MDM_MATCH_RULE_ATTRIBUTE_WEIGHT` table
- `MDM_MATCH_THRESHOLD_CONFIG` table

**3.3.5 Events**
- `MatchRuleConfigPublished`

---

### 3.4 Survivorship Rule Configuration

**3.4.1 Process flow**
- How attribute-level survivorship (source priority per attribute, not one blanket "master system") is configured per domain
- How survivorship rules are combined with data-quality and recency signals

**3.4.2 Business rules**
- Every canonical attribute must have a survivorship rule before a domain can be activated for matching — no attribute may be left with undefined precedence
- Survivorship rule = source priority + attribute priority + data quality + recency + manual override, in that evaluation order, per the platform's conflict-resolution standard
- Manual overrides must always be traceable to a user and reason (feeds 13.x)

**3.4.3 UI screens**
- Web: Survivorship rule matrix (domain × attribute × source priority)
- Web: Manual override screen with mandatory reason capture

**3.4.4 DB schema**
- `MDM_SURVIVORSHIP_RULE` table
- `MDM_SURVIVORSHIP_OVERRIDE` table

**3.4.5 Events**
- `SurvivorshipRuleConfigPublished`

---

### 3.5 Workflow & Policy Metadata

**3.5.1 Process flow**
- How approval workflow definitions, data classification policies, and business/validation policies are registered as reusable metadata
- How a domain is bound to a specific workflow definition (e.g. "New Supplier always requires Finance approval")

**3.5.2 Business rules**
- Workflow definitions are domain-agnostic building blocks (steps, approvers, SLA) — domain binding is a separate, thinner configuration layer
- A domain cannot be activated for production ingestion without at least one bound workflow for "new record" and "merge" events

**3.5.3 UI screens**
- Web: Workflow definition designer
- Web: Domain-to-workflow binding screen

**3.5.4 DB schema**
- `MDM_WORKFLOW_DEFINITION` table
- `MDM_DOMAIN_WORKFLOW_BINDING` table
- `MDM_POLICY` table

**3.5.5 Events**
- `WorkflowDefinitionPublished`

---

## Phase 4 — Source System Integration Architecture

> How the outside world connects in. This phase never touches the golden record — it only establishes trust and shape at the boundary.

---

### 4.1 Source System Registry & Connector Framework

**4.1.1 Process flow**
- How a source system (ERP, CRM, E-commerce, Finance, HR, WMS, legacy DB, Excel) is registered with the platform
- How a connector type (API, file drop, CDC, manual upload) is selected per source
- How a source system's credentials/connection are configured and tested

**4.1.2 Business rules**
- Every source system must declare a trust/priority weight before it can feed any domain (consumed by 3.4 survivorship)
- A source system cannot be deactivated if it has unresolved records in the matching queue — must drain first
- Connector credentials are never stored in plaintext (feeds 15.4 encryption)

**4.1.3 UI screens**
- Web: Source system registry (list + create/edit)
- Web: Connector configuration screen per connector type
- Web: Connection test / health check screen

**4.1.4 DB schema**
- `MDM_SOURCE_SYSTEM` table
- `MDM_SOURCE_CONNECTOR_CONFIG` table

**4.1.5 Events**
- `SourceSystemRegistered`
- `SourceSystemConnectionFailed`

---

### 4.2 Field Mapping & Crosswalk Configuration

**4.2.1 Process flow**
- How a source system's native fields are mapped to canonical attributes (e.g. SAP `KUNNR` → canonical `customer.identity.external_code`)
- How crosswalk (source-value ↔ canonical-value) tables are configured for enumerations (e.g. SAP country codes → ISO codes)

**4.2.2 Business rules**
- Every mapped source field must resolve to exactly one canonical attribute — no ambiguous fan-out mappings
- Unmapped source fields are landed as-is (raw) but never flow into the canonical/matching pipeline
- Crosswalk gaps (a source value with no mapped canonical value) must raise a data-quality flag, not silently drop the value

**4.2.3 UI screens**
- Web: Field mapping designer (source field → canonical attribute, drag/select)
- Web: Crosswalk value mapping screen

**4.2.4 DB schema**
- `MDM_SOURCE_FIELD_MAPPING` table
- `MDM_CROSSWALK_VALUE` table

**4.2.5 Events**
- `FieldMappingPublished`
- `CrosswalkGapDetected`

---

### 4.3 Source System Priority & Trust Scoring

**4.3.1 Process flow**
- How each source system earns or is assigned a base trust score, used as an input to survivorship (3.4) and match confidence weighting
- How trust scores are revisited over time based on observed data quality from that source

**4.3.2 Business rules**
- Trust score is a platform-level default that a domain's survivorship rule may override per attribute (3.4 always wins at attribute level)
- A source system's trust score change must be versioned and never silently retroactively re-scores historical golden records

**4.3.3 UI screens**
- Web: Source trust score configuration and history screen

**4.3.4 DB schema**
- `MDM_SOURCE_TRUST_SCORE` table (versioned)

**4.3.5 Events**
- `SourceTrustScoreChanged`

---

### 4.4 Connector Protocol Adapter Library

**4.4.1 Process flow**
- How each transport/protocol an ERP might use is built once as a reusable adapter, independent of any single ERP vendor: IDoc/ALE, BAPI/RFC, OData v2/v4, SOAP, DB-level interface tables, file drop (flat file/CSV/XML), CDC (log-based change capture), and generic REST/webhook
- How a new ERP connector (4.5) is assembled by composing one or more existing protocol adapters rather than writing new transport code

**4.4.2 Business rules**
- A protocol adapter is ERP-agnostic by construction — "OData adapter" must work identically whether the target is SAP S/4HANA, Oracle Fusion, or Dynamics 365; ERP-specific behavior belongs in 4.5, never in the adapter itself
- Every adapter must implement the same lifecycle contract (connect, authenticate, extract/receive, acknowledge, disconnect) so 4.1's connector framework can orchestrate any of them uniformly
- Adapters must support both directions where the underlying protocol allows it (e.g. OData adapter used for both inbound pull and outbound write-back) rather than shipping separate read-only and write-only implementations

**4.4.3 UI screens**
- Web: Protocol adapter catalog (list of available adapters, versions, supported directions)
- Web: Adapter capability matrix (which adapters support real-time vs. batch, push vs. pull)

**4.4.4 DB schema**
- `MDM_PROTOCOL_ADAPTER` table
- `MDM_ADAPTER_CAPABILITY` table

**4.4.5 Events**
- `AdapterHealthCheckFailed`

---

### 4.5 ERP-Specific Connector Catalog

**4.5.1 Process flow**
- How packaged, pre-built connectors for major ERP families are onboarded, each assembled from 4.4's protocol adapters plus that ERP's specific field defaults, session/auth handling, and known data quirks:
  - **SAP ECC** — IDoc/ALE (inbound), BAPI/RFC (write-back, e.g. `BAPI_CUSTOMER_CREATEFROMDATA1`), flat-file extract
  - **SAP S/4HANA** — OData v2/v4, CDS view extraction, SLT/CDC for near-real-time
  - **Oracle E-Business Suite** — interface tables + concurrent program triggers, SOAP
  - **Oracle Fusion Cloud** — REST API, BICC bulk extracts
  - **Microsoft Dynamics 365** — Dataverse Web API, CDC
  - **NetSuite** — SuiteTalk (SOAP/REST)
  - **Workday** (HR/Employee domain) — RaaS reports, SOAP/REST
  - **Generic/Other** — configurable REST/file adapter for any ERP not yet packaged, built entirely from 4.4 primitives
- How a connector version is validated against a specific ERP release (e.g. S/4HANA 2023 vs. 2025) before being marked supported

**4.5.2 Business rules**
- Every packaged connector must declare its supported ERP version range explicitly — "works with SAP" is not a valid support statement
- A connector's ERP-specific mandatory-field and default-value handling lives entirely inside the connector's own configuration, never leaking into the platform's canonical model (2.x) or matching engine (7.x)
- Adding a new ERP to the catalog must never require changes to Phases 1–3 or 5–16 — if it does, that is treated as an architecture defect, not an acceptable cost of onboarding
- SAP ECC-to-S/4HANA (or equivalent legacy-to-cloud) migrations must be supported as two connectors coexisting for the same source system during a transition window, not a forced single-connector cutover

**4.5.3 UI screens**
- Web: ERP connector catalog (browse, select, configure per source system from 4.1)
- Web: Connector version compatibility checker

**4.5.4 DB schema**
- `MDM_ERP_CONNECTOR_PACKAGE` table (references `MDM_PROTOCOL_ADAPTER` from 4.4)
- `MDM_ERP_CONNECTOR_VERSION_SUPPORT` table

**4.5.5 Events**
- `ERPConnectorOnboarded`
- `ERPConnectorVersionDeprecated`

---

### 4.6 Source System Role & Precedence Policy

**4.6.1 Process flow**
- How a client's decision — "is this ERP a **contributing source** feeding survivorship (3.4), or does the organization expect AptoMDM to **defer to it as system-of-record** for a given domain" — is captured explicitly, per source system, per domain, before onboarding
- How this policy decision flows into 3.4 survivorship weighting and 14.4 conflict handling, rather than being assumed implicitly by whoever configures the connector

**4.6.2 Business rules**
- Every ERP source system must have an explicit role declaration per domain before it can go live — "contributing source" is the platform default and must be deliberately overridden to "system-of-record deference," never the reverse
- A "system-of-record deference" declaration for a domain does not exempt that ERP's data from validation (6.2) or quality scoring (10.2) — deference affects survivorship precedence only, never data-quality enforcement
- If an existing SAP MDG (or equivalent competing governance layer) is present at the client, this must be recorded here explicitly, since two governance systems asserting authority over the same domain is a resolvable-in-advance decision, not a runtime conflict to discover later

**4.6.3 UI screens**
- Web: Source role declaration screen (source system × domain → contributing / deference)
- Web: Competing-governance-system disclosure screen (e.g. "SAP MDG is present for Material domain")

**4.6.4 DB schema**
- `MDM_SOURCE_DOMAIN_ROLE` table

**4.6.5 Events**
- `SourceDomainRoleChanged`

---

### 4.7 Middleware / iPaaS Passthrough Integration

**4.7.1 Process flow**
- How AptoMDM connects through a client's existing integration bus (MuleSoft, Dell Boomi, SAP Cloud Platform Integration, Azure Integration Services, Kafka-based ESB) instead of a direct point-to-point ERP connector, where the client already standardizes integration that way
- How the same landing/standardization/matching pipeline (Phases 5–7) consumes data identically whether it arrived via a direct connector or via middleware — the pipeline must not know or care which path was used

**4.7.2 Business rules**
- Middleware passthrough is a transport choice only — it must never bypass 4.2 field mapping, 6.1 standardization, or 6.2 validation; middleware is not a shortcut around the pipeline
- Idempotency keys (5.2) must be preserved end-to-end through the middleware layer — a message re-delivered by the iPaaS platform must still be recognized as a duplicate, not a new event
- Where a client's middleware already performs its own field mapping or transformation, that logic must be made visible/documented to AptoMDM's stewards (11.1), since a hidden middleware transformation is an unauditable lineage gap (13.2)

**4.7.3 UI screens**
- Web: Middleware endpoint registration screen (webhook/queue endpoint per iPaaS platform)
- Web: Middleware-sourced record lineage disclosure (flags that a transformation occurred upstream of AptoMDM)

**4.7.4 DB schema**
- `MDM_MIDDLEWARE_ENDPOINT` table

**4.7.5 Events**
- `MiddlewareMessageReceived`

---

## Phase 5 — Data Ingestion

> How data physically arrives, before anything is trusted.

---

### 5.1 Batch Ingestion Engine

**5.1.1 Process flow**
- How a scheduled batch file/extract from a source system is picked up, staged, and landed
- How batch ingestion job status (running, succeeded, partially failed, failed) is tracked and surfaced

**5.1.2 Business rules**
- Every batch must be uniquely identified by source_system + batch_id + received_at — reprocessing the same batch_id is idempotent, not additive
- A batch that fails schema validation at the header level is rejected wholesale with a clear reason, never partially landed silently
- Partial-row failures within an otherwise-valid batch are quarantined per row, not failing the whole batch

**5.1.3 UI screens**
- Web: Batch ingestion job monitor (status, row counts, error counts)
- Web: Batch error detail / quarantine viewer

**5.1.4 DB schema**
- `MDM_INGESTION_BATCH` table
- `MDM_INGESTION_BATCH_ERROR` table

**5.1.5 Events**
- `BatchIngestionStarted`
- `BatchIngestionCompleted`
- `BatchIngestionFailed`

---

### 5.2 Real-Time / Event-Driven Ingestion (API, CDC, Streaming)

**5.2.1 Process flow**
- How a source system pushes a single record change via API or CDC event (e.g. `CustomerUpdated` from SAP)
- How the ingestion layer converts inbound events into the same landing shape used by batch, so downstream engines are ingestion-method-agnostic

**5.2.2 Business rules**
- Every inbound event must carry `source_system + source_record_id + event_id + version` — this is the idempotency key, enforced platform-wide (see also 17 in the architect mindset: idempotency is critical)
- Out-of-order events (older version arriving after newer) are detected and discarded, not blindly applied
- Real-time and batch ingestion for the same source system must never be allowed to race on the same record without a resolution rule

**5.2.3 UI screens**
- Web: Real-time ingestion event stream monitor
- Web: Out-of-order / duplicate event log

**5.2.4 DB schema**
- `MDM_INGESTION_EVENT_LOG` table (source_system, source_record_id, event_id, version, received_at)

**5.2.5 Events**
- `SourceRecordReceived` (internal, consumed by 6.x)
- `DuplicateEventDiscarded`

---

### 5.3 File-Based / Manual Ingestion (Excel, CSV, Manual Entry)

**5.3.1 Process flow**
- How a business user uploads a spreadsheet of records (common for legacy/Excel-managed master data)
- How manual single-record entry is supported for domains without an automated source

**5.3.2 Business rules**
- Manual uploads go through the identical landing → validation → matching pipeline as any other source — no shortcut path
- A manually-entered record must still declare a `source_system` (a synthetic "MANUAL_ENTRY" source with its own trust score)

**5.3.3 UI screens**
- Web: File upload wizard (template download, upload, mapping confirmation, submit)
- Web: Manual single-record entry form

**5.3.4 DB schema**
- Reuses `MDM_INGESTION_BATCH` (batch of one for manual entry)

**5.3.5 Events**
- `ManualUploadSubmitted`

---

### 5.4 Raw / Landing Zone & Source Record Store

**5.4.1 Process flow**
- How every ingested record — regardless of channel — lands in a raw store before standardization touches it
- How the raw record is permanently retained even after the golden record supersedes it (never destroy source data)

**5.4.2 Business rules**
- Landing zone records are immutable once written — corrections arrive as new versions, not in-place edits
- Every `mdm_source_record` must link to exactly one `mdm_entity` once matched (5.4 landing precedes matching, so this link is set later by 7.x/8.x, initially null)

**5.4.3 UI screens**
- Web: Raw record viewer (per source system, searchable by external ID)

**5.4.4 DB schema**
- `MDM_SOURCE_RECORD` table (`source_record_id`, `source_system_id`, `external_id`, `entity_id`, `raw_data`, `received_at`)

**5.4.5 Events**
- `SourceRecordLanded`

---

## Phase 6 — Standardization & Validation

> Is the data clean and comparable before we try to match it?

---

### 6.1 Data Standardization Engine

**6.1.1 Process flow**
- How raw values are normalized (case, whitespace, legal-entity suffixes, phone/address formats) using the standardization rules bound to each canonical attribute
- How standardized output is stored alongside raw, never overwriting it

**6.1.2 Business rules**
- Standardization must be deterministic and re-runnable — re-standardizing the same raw value must always produce the same standardized value
- Standardization rules are domain-and-attribute-scoped (name standardization ≠ address standardization) but reuse a shared rule-engine core
- A standardization rule change requires re-running standardization only on records after the effective date, or an explicit full backfill decision — never silent partial application

**6.1.3 UI screens**
- Web: Standardization rule configuration screen (per attribute)
- Web: Before/after standardization preview tool

**6.1.4 DB schema**
- `MDM_STANDARDIZATION_RULE` table
- Standardized-value columns on `MDM_SOURCE_RECORD` (or a linked `MDM_SOURCE_RECORD_STANDARDIZED` table)

**6.1.5 Events**
- `RecordStandardized`

---

### 6.2 Data Validation Engine

**6.2.1 Process flow**
- How each standardized record is run against the validation rules from 3.2 (mandatory, format, range, cross-field)
- How a record that fails validation is routed to quarantine rather than silently dropped or force-passed

**6.2.2 Business rules**
- Validation failures are attribute-level, not record-level — a record with one bad attribute is quarantined for that attribute, other valid attributes still proceed where the domain config allows partial-record progression
- A quarantined record must be visible to a data steward with a clear, plain-language reason (feeds 11.1)

**6.2.3 UI screens**
- Web: Validation error queue (steward-facing)
- Web: Validation error detail with correction/resubmit action

**6.2.4 DB schema**
- `MDM_VALIDATION_RESULT` table
- `MDM_QUARANTINE_RECORD` table

**6.2.5 Events**
- `RecordValidationFailed`
- `RecordValidationPassed`

---

### 6.3 Data Enrichment

**6.3.1 Process flow**
- How records are optionally enriched from external reference services (address verification, GSTIN/DUNS lookup, industry classification)
- How enrichment results are marked distinctly from source-provided values (their own "source" for lineage and survivorship purposes)

**6.3.2 Business rules**
- Enrichment is additive and never overwrites a source-provided value outright — it competes for survivorship like any other source
- Enrichment service failures must not block the pipeline — the record proceeds without enrichment, flagged for later retry

**6.3.3 UI screens**
- Web: Enrichment service configuration screen (which services, which attributes, which domains)
- Web: Enrichment status/retry queue

**6.3.4 DB schema**
- `MDM_ENRICHMENT_SERVICE_CONFIG` table
- `MDM_ENRICHMENT_RESULT` table

**6.3.5 Events**
- `RecordEnriched`
- `EnrichmentFailed`

---

## Phase 7 — Matching Engine

> Are two records the same real-world entity? One of the platform's two most important engines.

---

### 7.1 Exact & Normalized Matching

**7.1.1 Process flow**
- How records are compared using exact-key matching (GSTIN = GSTIN, DUNS = DUNS) as the first, cheapest, strongest pass
- How normalized matching (post-6.1 standardized values) runs as the second pass for records that don't exact-match

**7.1.2 Business rules**
- Exact matches on a declared unique identifier are auto-match with no review, always — this is the strongest matching signal and is never downgraded
- Normalized matching only compares standardized values, never raw values, to avoid false negatives from formatting noise

**7.1.3 UI screens**
- Web: Match pass configuration (which techniques run in which order, per domain — reads from 3.3)

**7.1.4 DB schema**
- `MDM_MATCH_CANDIDATE` table (`record_a`, `record_b`, `technique`, `score`)

**7.1.5 Events**
- `ExactMatchFound`

---

### 7.2 Fuzzy & Composite Matching

**7.2.1 Process flow**
- How fuzzy similarity (edit distance, phonetic, token-based) is computed per attribute for records that survive to this pass
- How a composite score is computed by combining weighted attribute similarities per the 3.3 configuration

**7.2.2 Business rules**
- Composite score calculation must be explainable per-attribute (name similarity 91%, phone exact, email different → weighted 93%) — never a single opaque number
- Composite thresholds are strictly enforced: 95–100% Auto Match, 80–95% Review, <80% New Record, per 3.3 — no ad hoc overrides in code

**7.2.3 UI screens**
- Web: Match candidate score breakdown viewer

**7.2.4 DB schema**
- `MDM_MATCH_CANDIDATE_ATTRIBUTE_SCORE` table

**7.2.5 Events**
- `MatchCandidateScored`

---

### 7.3 Match Decisioning & Steward Review Queue

**7.3.1 Process flow**
- How a match candidate resolves automatically (Auto Match / New Record) or routes to a steward (Review band)
- How a steward reviews a "Possible Match" candidate side-by-side and confirms or rejects it

**7.3.2 Business rules**
- A match decision (`decision = REVIEW/AUTO_MATCH/NEW_RECORD`) is always recorded with the rules and scores that produced it — decisions are never free-floating
- A steward's manual decision on a Review-band candidate is captured as ground truth and may feed future threshold tuning (not automatic, a governance decision)
- Two users cannot resolve the same match candidate simultaneously — first decision wins, second is rejected with a conflict notice (ties to 23. concurrency)

**7.3.3 UI screens**
- Web: Match review queue (list, filterable by domain, score band, source)
- Web: Match review detail — side-by-side record comparison with attribute-level score breakdown

**7.3.4 DB schema**
- `MDM_MATCH_DECISION` table

**7.3.5 Events**
- `MatchDecisionMade`
- `MatchReviewAssigned`

---

## Phase 8 — Golden Record & Survivorship

> Which value wins, and why. The Golden Record is never just another table.

---

### 8.1 Golden Record Engine

**8.1.1 Process flow**
- How a new golden record is created when a source record has no match (New Master path)
- How an existing golden record is updated when a source record matches an existing master

**8.1.2 Business rules**
- A golden record must always resolve to exactly one entity across all its contributing source records at any point in time
- Golden record creation/update is always driven by survivorship rules (8.2) — never a direct "last write wins" default
- A golden record's `status` (Active, Under Review, Merged, Retired) governs what operations are allowed on it

**8.1.3 UI screens**
- Web: Golden Record registry (search, filter, per-domain list)
- Web: Golden Record detail — attribute panel with per-attribute source/confidence badges

**8.1.4 DB schema**
- `MDM_GOLDEN_RECORD` table (`golden_id`, `entity_id`, `status`, `version`)
- `MDM_GOLDEN_ATTRIBUTE` table (`golden_id`, `attribute_id`, `value`, `source_record_id`, `confidence`, `survivorship_rule_id`, `effective_from`, `effective_to`)

**8.1.5 Events**
- `GoldenRecordCreated`
- `GoldenRecordUpdated`

---

### 8.2 Attribute-Level Survivorship Execution

**8.2.1 Process flow**
- How the survivorship rules configured in 3.4 are executed at golden-record-write time, attribute by attribute
- How conflicts (CRM says one phone, ERP says another) are resolved deterministically and explainably

**8.2.2 Business rules**
- Evaluation order is fixed: source priority → attribute priority → data quality signal → recency → manual override
- Every survivorship outcome must be explainable on demand: "why is this value X" always has a traceable answer
- A manual override always outranks computed survivorship until explicitly cleared by an authorized steward

**8.2.3 UI screens**
- Web: "Why this value" explainability panel (accessible from every golden attribute)

**8.2.4 DB schema**
- Reuses `MDM_GOLDEN_ATTRIBUTE` + `MDM_SURVIVORSHIP_OVERRIDE` (3.4)

**8.2.5 Events**
- `SurvivorshipDecisionApplied`

---

### 8.3 Confidence Scoring

**8.3.1 Process flow**
- How each golden attribute's confidence score is computed from source trust, data quality, corroboration across multiple sources, and recency
- How confidence scores decay over time if a value is not reconfirmed by any source

**8.3.2 Business rules**
- Confidence is attribute-level, not record-level — a golden record can be high-confidence on Name and low-confidence on Phone simultaneously
- A confidence drop below a configurable threshold flags the attribute for steward review, feeding 10.x quality workflows

**8.3.3 UI screens**
- Web: Confidence score display embedded in the Golden Record detail (8.1.3)

**8.3.4 DB schema**
- Confidence column on `MDM_GOLDEN_ATTRIBUTE` (already present per 8.1.4); confidence-history table for decay tracking

**8.3.5 Events**
- `AttributeConfidenceDegraded`

---

## Phase 9 — Merge / Unmerge

> Match decides "are they the same." Merge does the actual consolidation. These stay separate engines.

---

### 9.1 Merge Engine

**9.1.1 Process flow**
- How a confirmed match (Auto Match or steward-approved Review) triggers consolidation of two or more golden records into one
- How the "losing" record is retired without deletion

**9.1.2 Business rules**
- Merge never physically deletes a record — the losing record is retired and linked `merged_into → surviving_record`
- All attribute values carry forward into survivorship re-evaluation at merge time — a merge is a trigger for 8.2 to re-run, not a manual copy-paste
- A merge of two records each already resulting from prior merges must preserve the full merge chain, not flatten it

**9.1.3 UI screens**
- Web: Merge confirmation screen (from the review queue, 7.3.3)
- Web: Merge preview — shows resulting golden attributes before commit

**9.1.4 DB schema**
- `MDM_MERGE_OPERATION` table
- `merged_into` FK on `MDM_GOLDEN_RECORD`

**9.1.5 Events**
- `RecordsMerged`

---

### 9.2 Unmerge Engine

**9.2.1 Process flow**
- How an incorrect merge is identified and reversed
- How the two (or more) original records are restored to independent golden records with their pre-merge attribute state

**9.2.2 Business rules**
- Unmerge is only possible because merge never destroyed source data — this is a hard dependency, not an afterthought
- Unmerging must re-trigger survivorship for both resulting records, since the attribute pool has changed
- Every unmerge requires a reason and, per governance policy, may require approval (feeds 12.x)

**9.2.3 UI screens**
- Web: Unmerge request screen (reason capture)
- Web: Unmerge impact preview (what golden attributes will change on both sides)

**9.2.4 DB schema**
- `MDM_UNMERGE_OPERATION` table (linked to the original `MDM_MERGE_OPERATION`)

**9.2.5 Events**
- `RecordsUnmerged`

---

### 9.3 Merge History & Relationship Tracking

**9.3.1 Process flow**
- How the full merge/unmerge history of any record is queryable end to end ("show me exactly what happened to this record over the last 2 years")

**9.3.2 Business rules**
- Merge history is append-only and must never be edited, only added to
- History must be reconstructable purely from `MDM_MERGE_OPERATION` + `MDM_UNMERGE_OPERATION` + `MDM_SOURCE_RECORD` — no dependency on mutable state

**9.3.3 UI screens**
- Web: Merge/unmerge history timeline tab on the Golden Record detail screen

**9.3.4 DB schema**
- No new tables — this is a read/reporting layer over 9.1/9.2 tables

**9.3.5 Events**
- None — read-only module

---

## Phase 10 — Data Quality

> Don't just say "the data is clean." Measure it.

---

### 10.1 Data Quality Dimension Framework

**10.1.1 Process flow**
- How the six standard quality dimensions (Completeness, Accuracy, Consistency, Uniqueness, Validity, Timeliness) are defined and made measurable per domain/attribute

**10.1.2 Business rules**
- Every domain must have at least one measurable rule per applicable dimension before it can report a quality score
- Dimension definitions are shared platform metadata — a domain cannot invent a private, unreported dimension

**10.1.3 UI screens**
- Web: Quality dimension configuration screen (per domain, which rules feed which dimension)

**10.1.4 DB schema**
- `MDM_QUALITY_DIMENSION` table
- `MDM_QUALITY_RULE` table

**10.1.5 Events**
- None — configuration-time module

---

### 10.2 Data Quality Scoring Engine

**10.2.1 Process flow**
- How each golden record's quality score is computed per dimension and rolled up into an overall score
- How scoring re-runs on every golden record update, not just on a schedule

**10.2.2 Business rules**
- Quality scoring must be deterministic and reproducible from the same inputs
- A score drop below a configurable threshold raises a data-quality issue (feeds 10.4) automatically

**10.2.3 UI screens**
- Web: Quality score breakdown on Golden Record detail (Completeness 92%, Uniqueness 97%, Validity 95%, Consistency 89%, Accuracy 94%, Overall 93.4%)

**10.2.4 DB schema**
- `MDM_QUALITY_SCORE` table (per golden record, per dimension, versioned)

**10.2.5 Events**
- `QualityScoreComputed`
- `QualityThresholdBreached`

---

### 10.3 Data Quality Dashboard & Reporting

**10.3.1 Process flow**
- How quality scores are aggregated across domains, sources, and tenants into trend dashboards
- How a data owner drills from an aggregate score down to the specific failing records

**10.3.2 Business rules**
- Dashboards read from a reporting store, never the live operational tables, so quality reporting never competes with transactional load
- Trend data must be retained long enough to show quarter-over-quarter improvement, per tenant subscription tier

**10.3.3 UI screens**
- Web: Quality dashboard (by domain, by source system, trending)
- Web: Drill-down to failing-record list

**10.3.4 DB schema**
- `MDM_QUALITY_SNAPSHOT` table (reporting star schema, separate from operational DB)

**10.3.5 Events**
- No events — reporting consumes other events passively

---

### 10.4 Data Quality Issue Remediation Workflow

**10.4.1 Process flow**
- How a quality issue (below-threshold score, validation failure, crosswalk gap) becomes a trackable remediation task assigned to a steward or source-system owner
- How remediation is verified once the underlying source data is corrected and re-ingested

**10.4.2 Business rules**
- A remediation task must reference the specific record(s) and dimension(s) that triggered it — no vague "fix data quality" tasks
- A remediation task auto-closes only when the re-computed score clears the threshold, never on manual say-so alone

**10.4.3 UI screens**
- Web: Remediation task queue
- Web: Remediation task detail with linked records and re-check status

**10.4.4 DB schema**
- `MDM_QUALITY_REMEDIATION_TASK` table

**10.4.5 Events**
- `RemediationTaskCreated`
- `RemediationTaskResolved`

---

## Phase 11 — Governance & Stewardship

> Governance is a first-class module, not an afterthought bolted onto Match/Merge/Golden Record.

---

### 11.1 Data Stewardship Workbench

**11.1.1 Process flow**
- How a steward's unified inbox aggregates everything needing human attention across domains: match reviews (7.3), validation quarantine (6.2), quality remediation (10.4), and merge/unmerge approvals (12.x)
- How work is assigned, escalated, and reassigned across a steward pool

**11.1.2 Business rules**
- Every steward task must show its SLA and age — no silent backlog growth
- A task type's routing (which steward pool) is domain-configurable, not hardcoded

**11.1.3 UI screens**
- Web: Unified steward inbox (all task types, filterable)
- Web: Task assignment / reassignment screen

**11.1.4 DB schema**
- `MDM_STEWARD_TASK` table (polymorphic reference to source task type/id)

**11.1.5 Events**
- `StewardTaskCreated`
- `StewardTaskCompleted`

---

### 11.2 Ownership & Accountability Model

**11.2.1 Process flow**
- How each domain and each attribute is assigned a business owner (accountable) distinct from the technical steward pool (responsible)
- How ownership changes are tracked over time

**11.2.2 Business rules**
- Every active domain must have exactly one accountable business owner at all times
- Ownership changes require the outgoing and incoming owner (or an admin) to acknowledge the handoff

**11.2.3 UI screens**
- Web: Domain/attribute ownership registry
- Web: Ownership handoff screen

**11.2.4 DB schema**
- `MDM_OWNERSHIP_ASSIGNMENT` table

**11.2.5 Events**
- `OwnershipChanged`

---

### 11.3 Data Classification & Policy Management

**11.3.1 Process flow**
- How attributes are classified (Public, Internal, Confidential, Restricted/PII) and how policies (retention, masking, access) attach to classifications
- How a classification change cascades to security enforcement (feeds 15.x)

**11.3.2 Business rules**
- Every canonical attribute must carry a classification before a domain goes live — unclassified is not a valid production state
- Classification downgrades (Restricted → Internal) require governance approval; upgrades do not

**11.3.3 UI screens**
- Web: Classification assignment screen (per attribute)
- Web: Policy catalog and binding screen

**11.3.4 DB schema**
- `MDM_DATA_CLASSIFICATION` table
- `MDM_POLICY_BINDING` table

**11.3.5 Events**
- `AttributeClassificationChanged`

---

### 11.4 Business Glossary

**11.4.1 Process flow**
- How business terms (e.g. "Active Customer," "Golden Record," "Preferred Supplier") are defined once with an agreed business meaning, linked to the technical attributes that implement them
- How glossary terms are surfaced contextually in the UI (hover definitions on Golden Record screens)

**11.4.2 Business rules**
- A glossary term must have exactly one approved definition per tenant — conflicting definitions are a governance escalation, not a UI edge case
- Glossary changes require steward or governance-owner sign-off before publishing

**11.4.3 UI screens**
- Web: Glossary term list and editor
- Web: Term-to-attribute linking screen

**11.4.4 DB schema**
- `MDM_GLOSSARY_TERM` table
- `MDM_GLOSSARY_ATTRIBUTE_LINK` table

**11.4.5 Events**
- `GlossaryTermPublished`

---

## Phase 12 — Workflow & Approval

> Who signs off, and on what — implemented as one reusable engine, not per-domain approval logic.

---

### 12.1 Generic Workflow Engine

**12.1.1 Process flow**
- How the workflow definitions configured in 3.5 are executed at runtime — step sequencing, approver resolution, SLA tracking, escalation
- How a workflow instance is started from any triggering event (new record, merge, unmerge, classification downgrade)

**12.1.2 Business rules**
- The workflow engine is domain-agnostic — it executes definitions, it does not know what a "Customer" or "Supplier" is
- A workflow instance must always be resumable after a system restart — no in-memory-only state

**12.1.3 UI screens**
- Web: Workflow instance monitor (running, completed, escalated)

**12.1.4 DB schema**
- `MDM_WORKFLOW_INSTANCE` table
- `MDM_WORKFLOW_STEP_INSTANCE` table

**12.1.5 Events**
- `WorkflowInstanceStarted`
- `WorkflowInstanceCompleted`
- `WorkflowStepEscalated`

---

### 12.2 New Record & Change Request Approval

**12.2.1 Process flow**
- How a new golden record or a proposed attribute change routes through its bound workflow (from 3.5) before going Active
- How the requestor is notified of approval or rejection

**12.2.2 Business rules**
- Requestor cannot self-approve (enforced from 1.3, re-verified here at execution time)
- A rejected change request must record the rejection reason and return the record to its prior state, never leave it half-applied

**12.2.3 UI screens**
- Web: Approval queue (pending, approved, rejected tabs)
- Web: Approval detail — before/after comparison

**12.2.4 DB schema**
- Reuses `MDM_WORKFLOW_INSTANCE`; `MDM_APPROVAL_REQUEST` and `MDM_APPROVAL_REQUEST_LINE` tables

**12.2.5 Events**
- `ApprovalRequested`
- `ApprovalResolved`

---

### 12.3 Merge / Unmerge Approval

**12.3.1 Process flow**
- How high-risk merges (per domain policy — e.g. any merge involving a Restricted-classified attribute) require explicit approval before 9.1 commits
- How unmerge requests (9.2) always route through approval by governance policy default

**12.3.2 Business rules**
- Approval requirement for merge is policy-driven per domain/classification, not universal — low-risk domains may allow auto-merge on Auto-Match confidence
- Unmerge approval is mandatory by default and may only be relaxed by an explicit governance policy change, logged and auditable

**12.3.3 UI screens**
- Reuses the 12.2.3 approval queue/detail screens, filtered to merge/unmerge task type

**12.3.4 DB schema**
- Reuses `MDM_APPROVAL_REQUEST` with `entity_type = MERGE/UNMERGE`

**12.3.5 Events**
- `MergeApprovalRequested`
- `UnmergeApprovalRequested`

---

## Phase 13 — Audit & Lineage

> Where did this value come from, and what happened to it.

---

### 13.1 Audit Log Engine

**13.1.1 Process flow**
- How every significant action (create, update, merge, unmerge, approve, reject, classification change, access grant) is captured as an audit event
- How audit records are queried for compliance and dispute resolution

**13.1.2 Business rules**
- Audit records capture who, what, when, why, before, after, source, approval — all mandatory fields, no partial audit rows
- Audit data is never mixed into operational tables — always a separate store, append-only, no updates or deletes
- Audit log is the source of truth for any compliance dispute — if it isn't in the audit log, it didn't happen

**13.1.3 UI screens**
- Web: Audit log search (by entity, user, action type, date range)
- Web: Audit record detail (before/after diff)

**13.1.4 DB schema**
- `MDM_AUDIT_LOG` table

**13.1.5 Events**
- None — audit log is a consumer of every other module's events, not a producer

---

### 13.2 Data Lineage Tracking

**13.2.1 Process flow**
- How every golden attribute's value can be traced back through standardization, survivorship, and source record to its original raw value
- How lineage is visualized as a chain: Source Record → Standardized Value → Match/Survivorship Decision → Golden Attribute

**13.2.2 Business rules**
- Lineage must be reconstructable from existing tables (`MDM_SOURCE_RECORD`, `MDM_GOLDEN_ATTRIBUTE`, `MDM_SURVIVORSHIP_*`) — lineage is a derived view, not a separately-maintained parallel structure that can drift out of sync
- Every golden attribute must resolve to at least one traceable source — an attribute with no lineage is a data-quality defect, not an acceptable state

**13.2.3 UI screens**
- Web: Lineage chain viewer (tab on Golden Record detail)

**13.2.4 DB schema**
- `MDM_LINEAGE` view/table (derived)

**13.2.5 Events**
- None — read/derived module

---

### 13.3 Temporal History & Change Timeline

**13.3.1 Process flow**
- How a golden entity's attribute values over time are queryable (e.g. Customer Address: Bangalore in 2024, Hyderabad in 2025, Pune in 2026)
- How bitemporal queries are supported where a domain requires them (what did we believe on date X, as recorded on date Y)

**13.3.2 Business rules**
- Golden attributes are never simply overwritten — every change carries `effective_from`/`effective_to` and, where required by domain policy, a separate `recorded_at` for bitemporal history
- Historical queries must return consistent point-in-time snapshots, not a mix of current and historical values

**13.3.3 UI screens**
- Web: Attribute history timeline (tab on Golden Record detail)
- Web: Point-in-time snapshot query tool

**13.3.4 DB schema**
- `effective_from` / `effective_to` / `version` columns on `MDM_GOLDEN_ATTRIBUTE` (already scaffolded in 8.1.4)

**13.3.5 Events**
- None — read module over existing versioned data

---

## Phase 14 — Distribution & Synchronization

> MDM doesn't end at Golden Record Created. The enterprise needs the trusted data back.

---

### 14.1 Distribution / Publish Engine

**14.1.1 Process flow**
- How a golden record change triggers publication to subscribed target systems
- How publish mode (push, pull, event, API, batch, CDC) is selected per target system

**14.1.2 Business rules**
- A golden record is not "done" at creation — distribution status is tracked as part of its lifecycle, not a side concern
- Publish failures must not block the golden record from being correct internally — publishing is decoupled and retryable

**14.1.3 UI screens**
- Web: Distribution configuration screen (per target system: mode, cadence, domain scope)
- Web: Publish job monitor

**14.1.4 DB schema**
- `MDM_DISTRIBUTION_TARGET` table
- `MDM_DISTRIBUTION_JOB` table

**14.1.5 Events**
- `GoldenRecordPublished`

---

### 14.2 Target System Subscription Management

**14.2.1 Process flow**
- How a target system (ERP, CRM, WMS, downstream data warehouse) subscribes to specific domains and even specific attributes
- How subscriptions are versioned as target systems evolve their own schemas

**14.2.2 Business rules**
- A target system only receives attributes it is entitled to per its subscription and the security/classification rules from 11.3/15.x
- Subscription changes take effect on the next publish cycle, never retroactively resending history without an explicit backfill request

**14.2.3 UI screens**
- Web: Subscription management screen (target × domain × attribute matrix)

**14.2.4 DB schema**
- `MDM_DISTRIBUTION_SUBSCRIPTION` table

**14.2.5 Events**
- `SubscriptionChanged`

---

### 14.3 Delivery Status Tracking & Reconciliation

**14.3.1 Process flow**
- How each publish attempt's delivery status (delivered, failed, acknowledged) is tracked per target system
- How periodic reconciliation confirms a target system's data still matches the golden record (detecting silent drift)

**14.3.2 Business rules**
- Every publish attempt must record a delivery status — "fire and forget" with no tracking is not permitted
- A reconciliation mismatch raises a data-quality/distribution issue, routed to the steward workbench (11.1), not silently auto-corrected

**14.3.3 UI screens**
- Web: Delivery status dashboard (per target system, success/failure trend)
- Web: Reconciliation mismatch queue

**14.3.4 DB schema**
- `MDM_DELIVERY_STATUS` table
- `MDM_RECONCILIATION_RESULT` table

**14.3.5 Events**
- `DeliveryFailed`
- `ReconciliationMismatchDetected`

---

### 14.4 Conflict & Failure Handling in Distribution

**14.4.1 Process flow**
- How a failed publish is retried with backoff, and how a permanently-failed publish is escalated
- How a target system's own local edit (that conflicts with the golden record) is detected and resolved per policy

**14.4.2 Business rules**
- Retry policy (count, backoff, dead-letter) is configurable per target system, not hardcoded platform-wide
- Target-system local edits are, by default, treated as non-authoritative relative to the golden record unless that target is explicitly configured as a contributing source system (feeding back into Phase 4/7, not just a downstream consumer)

**14.4.3 UI screens**
- Web: Dead-letter queue viewer for failed publishes
- Web: Conflict resolution screen for target-local-edit conflicts

**14.4.4 DB schema**
- `MDM_DISTRIBUTION_DEAD_LETTER` table

**14.4.5 Events**
- `PublishExhaustedRetries`

---

## Phase 15 — Security & Multi-Tenancy

> Master data is extremely sensitive from an enterprise perspective.

---

### 15.1 Tenant Isolation Architecture

**15.1.1 Process flow**
- How tenant data isolation is enforced at every layer (query, cache, search index, event stream) so cross-tenant leakage is structurally impossible, not just policy-enforced
- How tenant-level data residency requirements (from 1.1) are honored at storage placement

**15.1.2 Business rules**
- Every query, cache key, and event topic must be tenant-scoped by construction — there is no code path that queries "all tenants" outside of internal platform-ops tooling with its own separate authorization
- Tenant isolation is verified by automated tests on every release, not just at initial design

**15.1.3 UI screens**
- Web: Internal platform-ops tenant isolation audit screen

**15.1.4 DB schema**
- `tenant_id` as a mandatory, indexed column on every operational table platform-wide

**15.1.5 Events**
- None — architectural constraint, not a feature module

---

### 15.2 RBAC / ABAC Authorization Engine

**15.2.1 Process flow**
- How role-based (1.3) and attribute-based (classification-aware, from 11.3) access decisions are evaluated for every request
- How access decisions compose: Tenant → Organization → Domain → Entity → Attribute → Action, per the platform's security hierarchy

**15.2.2 Business rules**
- Attribute-level access can further restrict role-based access, never expand it — ABAC is a narrowing filter on top of RBAC, not a bypass
- Example enforced pattern: a Finance user can see Tax ID; an Operations user, same role tier otherwise, cannot — driven by attribute classification, not hardcoded per-user exceptions

**15.2.3 UI screens**
- Web: Access policy simulator ("what can user X see on entity Y")

**15.2.4 DB schema**
- `MDM_ACCESS_POLICY` table (role × domain × attribute × action)

**15.2.5 Events**
- `AccessDenied` (security audit trail, feeds 13.1)

---

### 15.3 Row-Level & Attribute-Level Security Enforcement

**15.3.1 Process flow**
- How row-level filters (e.g. a user only sees Golden Records for their assigned region/warehouse) are enforced at the query layer
- How attribute-level masking is applied at response time for attributes the requesting user isn't entitled to see in full

**15.3.2 Business rules**
- Masking must happen server-side before data leaves the platform boundary — never a client-side hide that still ships the raw value
- Row-level and attribute-level rules must compose without one silently overriding the other — both are evaluated, most restrictive wins

**15.3.3 UI screens**
- Web: Masked-field indicator in the Golden Record detail UI (shows "restricted" rather than blank, so users know a value exists but isn't visible to them)

**15.3.4 DB schema**
- `MDM_ROW_SECURITY_RULE` table

**15.3.5 Events**
- None — runtime enforcement, not an emitting module

---

### 15.4 PII Masking & Encryption

**15.4.1 Process flow**
- How Restricted/PII-classified attributes (from 11.3) are encrypted at rest and masked in transit/display by default
- How a legitimate business need to view unmasked PII is requested and time-bound

**15.4.2 Business rules**
- Encryption at rest is mandatory for every attribute classified Restricted — this is enforced by the platform at classification-assignment time, not left to per-domain discretion
- Unmasked PII access requests are themselves auditable events (feeds 13.1) and time-bound, never a permanent elevated grant by default

**15.4.3 UI screens**
- Web: Unmask request screen (reason + time-bound duration)

**15.4.4 DB schema**
- Encryption applied at the column/field level on `MDM_GOLDEN_ATTRIBUTE` for Restricted-classified attributes
- `MDM_UNMASK_REQUEST` table

**15.4.5 Events**
- `UnmaskRequested`
- `UnmaskGrantExpired`

---

### 15.5 Segregation of Duties & Approval Integrity

**15.5.1 Process flow**
- How the platform-wide rule "requestor cannot self-approve" (first introduced in 1.3) is enforced consistently across every workflow type in Phase 12
- How dual-control requirements (two independent approvers) are configured for the highest-risk actions (e.g. bulk unmerge, classification downgrade)

**15.5.2 Business rules**
- Segregation-of-duties checks run at workflow-execution time (12.1), not just at UI-level button-hiding — a direct API call must be blocked identically to a UI action
- Dual-control actions are explicitly enumerated by governance policy, not left to ad hoc judgment per request

**15.5.3 UI screens**
- Web: Segregation-of-duties policy configuration screen

**15.5.4 DB schema**
- `MDM_SOD_POLICY` table

**15.5.5 Events**
- `SegregationOfDutiesViolationBlocked`

---

## Phase 16 — Observability & Scalability

> Will this still work with 10 million, 100 million, or 1 billion records?

---

### 16.1 Monitoring & Alerting

**16.1.1 Process flow**
- How every engine (ingestion, matching, survivorship, distribution) emits health and performance metrics
- How alert thresholds are configured and routed to on-call/ops

**16.1.2 Business rules**
- Every engine must expose latency, throughput, and error-rate metrics as a baseline — no engine ships without observability
- Alert fatigue is a defect: thresholds must be tuned to page only on actionable conditions

**16.1.3 UI screens**
- Web: Platform health dashboard (per engine, per tenant where relevant)

**16.1.4 DB schema**
- `MDM_METRIC_SNAPSHOT` table (or external metrics store integration)

**16.1.5 Events**
- `AlertTriggered`

---

### 16.2 Performance & Scalability Architecture

**16.2.1 Process flow**
- How matching, standardization, and distribution engines are horizontally scaled (partitioning by tenant/domain, parallel workers, caching hot reference data)
- How the platform is load-tested against 10M / 100M / 1B record targets before each major domain onboarding

**16.2.2 Business rules**
- No engine may assume unbounded single-node processing — every batch/streaming engine must declare its partitioning strategy at design time
- Cache invalidation for reference/metadata changes must be explicit and immediate — stale cached rules silently misapplied is a correctness defect, not just a performance one

**16.2.3 UI screens**
- Web: Internal capacity/load-test results dashboard (platform ops)

**16.2.4 DB schema**
- No new business tables — this module governs infrastructure/partitioning strategy for existing tables

**16.2.5 Events**
- None — infrastructure module

---

### 16.3 Disaster Recovery & Failover

**16.3.1 Process flow**
- How the platform recovers from an event-bus outage (Kafka down), a matching-engine crash mid-batch, or a merge-succeeds-but-publish-fails scenario
- How recovery procedures are tested, not just documented

**16.3.2 Business rules**
- Every "what if X fails" scenario from the architecture mindset must have a documented, tested answer before go-live: Kafka down, invalid source data, matching engine crash, merge-succeeds-publish-fails, duplicate event delivery, concurrent merges, source schema change, steward rejection, incorrect merge needing undo
- Recovery must never silently lose or duplicate a golden record — idempotency (5.2) and append-only history (9.3, 13.1) are what make recovery safe

**16.3.3 UI screens**
- Web: DR runbook status / last-tested-date tracker (platform ops)

**16.3.4 DB schema**
- No new business tables — relies on existing idempotency and audit infrastructure

**16.3.5 Events**
- `FailoverTriggered`
- `RecoveryCompleted`

---

### 16.4 API Gateway & Rate Limiting

**16.4.1 Process flow**
- How every MDM API (Entity, Match, Merge, Golden Record, Quality, Workflow, Governance, Audit — per the API-first principle) is exposed through one gateway with consistent auth, versioning, and rate limiting
- How external systems (SAP, Salesforce, WMS, ERP, CRM) are onboarded as API consumers

**16.4.2 Business rules**
- Every API is tenant-scoped and rate-limited per consumer, by default, before any production credential is issued
- Breaking API changes require a new version; old versions remain available through a documented deprecation window, never an unannounced cutover

**16.4.3 UI screens**
- Web: API consumer registry and rate-limit configuration screen
- Web: API usage analytics dashboard

**16.4.4 DB schema**
- `MDM_API_CONSUMER` table
- `MDM_API_RATE_LIMIT_CONFIG` table

**16.4.5 Events**
- `RateLimitExceeded`

---

## Design Order Summary

Per the Senior Architect Mindset's build sequence, the recommended module design order across phases is:

1. Phase 1 (1.1 → 1.5) — Foundation
2. Phase 2 (2.1 → 2.6) — Canonical Model
3. Phase 3 (3.1 → 3.5) — Metadata
4. Phase 4 (4.1 → 4.7) — Source Integration & ERP Connectivity (4.1–4.3 platform framework, then 4.4–4.7 protocol adapters, packaged ERP connectors, source precedence policy, and middleware passthrough)
5. Phase 5 (5.1 → 5.4) — Ingestion
6. Phase 6 (6.1 → 6.3) — Standardization & Validation
7. Phase 7 (7.1 → 7.3) — Matching
8. Phase 8 (8.1 → 8.3) — Golden Record & Survivorship
9. Phase 9 (9.1 → 9.3) — Merge / Unmerge
10. Phase 10 (10.1 → 10.4) — Data Quality
11. Phase 11 (11.1 → 11.4) — Governance & Stewardship
12. Phase 12 (12.1 → 12.3) — Workflow & Approval
13. Phase 13 (13.1 → 13.3) — Audit & Lineage
14. Phase 14 (14.1 → 14.4) — Distribution & Synchronization
15. Phase 15 (15.1 → 15.5) — Security & Multi-Tenancy
16. Phase 16 (16.1 → 16.4) — Observability & Scalability

Security (Phase 15) and Observability (Phase 16) principles are referenced throughout earlier phases (e.g. classification at 2.x/11.3, idempotency at 5.2, segregation of duties at 1.3) precisely so that they are never bolted on at the end — the dedicated phases formalize and complete what earlier modules already assumed.

This is the key discipline carried from the Senior Architect Mindset: don't design Customer Page, Supplier Page, Product Page as separate applications. Design the **MDM Platform** — Metadata, Rules, Policies, Core Engine (Ingestion → Matching → Survivorship → Golden Record → Governance → Distribution) — and let Customer, Supplier, Product, Location, Employee become configurations on top of it.

---

*End of AptoMDM 2026 Design Roadmap — Version 1.1*