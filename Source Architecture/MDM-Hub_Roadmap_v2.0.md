# MDM-Hub: Enterprise Master Data Management — Design Roadmap v2.0

> **Version:** 2.0 | **Status:** Architectural Blueprint | **Target:** Multi-Domain (Product, Party, Site, Finance)
> **Architect:** 15+ Years MDM Experience | **Document Type:** Implementation & Design Roadmap
> 
> **Core Tenets:** 
> 1. **Trust Over Truth** – We don't assert what is true; we calculate what is *most trusted* based on source system weight, recency, and data completeness.
> 2. **Golden Record is a View** – The Golden Record (GR) is never physically stored as a single flat row; it is dynamically materialized at read-time or stored as a versioned delta from the base transaction.
> 3. **Stewardship over Automation** – 80% of matching can be automated. The remaining 20% *must* be routed to a skilled data steward with a purpose-built UI, not an IT ticket.

---

## How to Read This Roadmap
Each phase follows a **4-Layer MDM Architecture**:
1. **Data Ingestion & Integration** – How raw data arrives (batch, real-time, CDC).
2. **Harmonization & Matching** – Standardization, deduplication, and Golden Record calculation (Survivorship).
3. **Governance & Stewardship** – Workflow, approvals, issue tracking, and manual intervention.
4. **Syndication & Consumption** – How the trusted data is published back to operational systems (ERP, WMS, CRM).

---

## Phase 0: Foundation & Governance Strategy
> *Status: **Pre-requisite.** Must be completed before any data is loaded.*

### MDM-0.1 Data Governance Operating Model
Define the "Rules of the Road" for every domain.

- **Data Domain Owners:** Assign Business Owners for Product, Customer, Supplier, Location.
- **Source System Trust Matrix:** Define the scoring mechanism for each source. 
  - *Example:* ERP has a weight of `80` for Product Pricing, but MDM has `100` for Product Description.
- **Data Stewardship Assignment:** Defines who cleans the data when matching fails.

**Deliverables:**
- Governance Charter document.
- Trust Thresholds configured in `MDM_TRUST_CONFIG` table.

### MDM-0.2 Entity Resolution Strategy
Establish the matching logic before writing a single line of code.

- **Deterministic Matching:** Exact match on Tax ID, GTIN, or Email (Higher confidence).
- **Probabilistic Matching:** Fuzzy match on Name, Address (e.g., "Jon Smith" vs "John Smyth"). Uses algorithms like Jaro-Winkler, Soundex, or Tokenization.
- **Clerical Review Threshold:** If match score is between 60% and 85%, route to a Steward. Above 85% auto-link; below 60% auto-unlink.

**Deliverables:**
- Match Rule configurations per domain.
- Stewardship queue design.

---

## Phase 1: Master Data Ingestion & Integration Layer (The "Raw" Zone)
> *Status: **Critical Path - Phase 1.** We must build the intake before the hub.*

### MDM-1.1 Multi-Protocol Data Bus
Allow source systems (ERPs, CRMs, Legacy Spreadsheets) to push or pull data.

- **REST API** (Synchronous) – For immediate, real-time create/update (e.g., a new customer registered online).
- **Kafka / Event Bridge** (Asynchronous) – For high-volume ETL jobs from legacy ERP systems (millions of records).
- **Flat File Drop Zone** – For batch migration of frozen data (e.g., acquiring a new company).

### MDM-1.2 Delta Detection & Versioning
We never "overwrite" data blindly. We apply **Change Data Capture (CDC)** principles.

- **Schema:** `MDM_RAW_INGEST` (immutable append-only log).
- **Mechanics:** On ingestion, system hashes the incoming payload. If `hash` == last `hash` for that source key, the update is rejected (no point processing duplicates).
- **Versioning:** Every accepted update increments the `source_version` for that specific source record.

### MDM-1.3 Standardization & Parsing (Cleansing Pipeline)
Data must be normalized before matching. 

- *Addresses:* Pass through an Address Verification engine (e.g., Loqate, Google Maps API) to split "123 Main St" into `StreetNumber`, `StreetName`, `PostalCode`.
- *Names:* Expand abbreviations (e.g., "Acme Corp" → "Acme Corporation").
- *Identifiers:* Enforce canonical format (e.g., EU VAT numbers or EAN/GTIN-14 validation).

---

## Phase 2: Harmonization & Golden Record Construction (The "Trust" Zone)
> *Status: **The Core.** This is where the MDM Hub earns its keep.*

### MDM-2.1 Configurational Hub (Data Model)
Unlike transactional schemas, MDM schemas must be *shallow and wide* to accommodate all sources.

- **Base Core (Half A):** Unique entity ID (`global_entity_id`), Domain Type (`PRODUCT`, `PARTY`), Trust Score, Status (`ACTIVE`, `MERGE_PENDING`, `SUPERSEDED`).
- **Flexible Payload (Half B):** Store the aggregated attributes in a combination of relational columns (for indexed search) and JSONB (for dynamic source-specific attributes). 

### MDM-2.2 The Matching Engine
This runs on every ingestion, asynchronously or synchronously depending on complexity.

- **Process Flow:**
  1. Incoming record is standardized.
  2. Engine queries the Hub for potential duplicates using a "Blocking Key" (e.g., first 4 characters of last name or Area Code) to reduce the search space (important for databases with > 50 million records).
  3. The selected candidates are scored against the incoming record using the defined Probabilistic algorithm.
  4. **Decision:** `AUTO_LINK` (High Score), `CLERICAL_REVIEW` (Medium Score), `AUTO_UNLINK` (Low Score).

### MDM-2.3 Survivorship (Rules of the Golden Record)
How does the system decide *which* phone number or address makes it into the Golden Record?

- **Weighted Averaging:** The source with the highest Trust Weight wins for that specific field.
- **Recency:** If two sources have the same weight, the one with the latest `last_updated` timestamp wins.
- **Null Handling:** A `NULL` value from a high-trust source does not overwrite a valid value from a low-trust source (Nulls are treated as "No Opinion" rather than "Blank Out").
- **Output:** The Golden Record is stored either as a *physical* `MDM_GOLDEN_RECORD` table (simpler for version 1) or *materialized views*.

---

## Phase 3: Data Stewardship & Issue Management (The "Human" Zone)
> *Status: **Essential.** No MDM project survives without a dedicated User Interface for humans.*

### MDM-3.1 Stewardship Dashboard
This is not an IT admin screen; this is a Business User's daily workstation.

- **Queue 1: Unresolved Duplicates (Clerical Review).** Side-by-side view of two suspected duplicates. Steward clicks "Merge" or "Separate". The selection becomes a permanent overridden rule in the Match Engine.
- **Queue 2: Data Quality Violations.** Entities with missing mandatory attributes (e.g., Product missing Weight, Customer missing Tax ID).
- **Queue 3: Merge Candidates Pending Approval.** High-volume merge operations (e.g., merging Duplicate Suppliers) require a Supervisor double-click to Approve or Reject.

### MDM-3.2 Golden Record Audit Trail (Consumption)
When a Steward manually edits the Golden Record, we treat this as a "System Override."

- We record `GOLDEN_OVERRIDE` separately from the source data.
- Rule: The Steward is a "Source" with the *highest possible Trust Weight* (infinite). Steward edits *must* trigger an immediate Syndication event to push the corrected value back to the original source system (if bi-directional sync is allowed) or strictly to downstream consumers.

---

## Phase 4: Master Data Syndication & Distribution (The "Value" Zone)
> *Status: **The payoff.** If data only lives in MDM, it's useless. It must flow downstream.*

### MDM-4.1 Output Schema Mapping
Each consuming system (WMS, ERP, CRM) wants data in a specific format.

- WMS wants `Length, Width, Height` in **centimeters**.
- CRM wants `Product Description` to be **200 characters** max.
- **Deliverable:** `MDM_SYNDICATION_MAPPING` table. Stores a "Target Entity" and a "Field Transform" (e.g., `source.weight_kg * 2.20462` for lbs).

### MDM-4.2 Syndication Delivery Methods
- **Push (Webhook/Kafka):** On Golden Record Update, publish the delta (`before` and `after` payload) to a topic. Downstream systems listen and pull the updated data.
- **Pull (Batch ETL):** For legacy systems that don't support webhooks, a scheduled job exports a flat file (CSV/XML) of all changed entities since the last successful run (Delta export).

### MDM-4.3 Consent & Privacy Filter (GDPR/CCPA)
A specialized filter before syndication.

- If a Customer has opted out of Marketing, the Marketing Cloud *must* receive the Golden Record but with a `marketing_consent = FALSE` flag.
- If a Customer requests a "Right to be Forgotten," the Syndication pipeline broadcasts a `SUPPRESS` event, instructing all downstream systems to anonymize the record without deleting the transactional history.

---

## Phase 5: Hierarchy & Relationship Management
> *Status: **Advanced.** Often ignored in V1, but critical for reporting.*

### MDM-5.1 Cross-Domain Relationships
- **Product → Supplier:** Which Supplier supplies this Product?
- **Customer → Ship-To Locations:** A single Corporate Customer has 5 warehouse ship-to addresses.
- **Finance → Product:** What is the cost center / GL code attached to this product category?

### MDM-5.2 Graph-Based Hierarchy Engine
- **Store:** Relationships as edges (`MDM_RELATIONSHIP` table) rather than nested JSON.
- **Visualization:** The Stewardship UI must have a "Graph View" to click through hierarchy layers.
- **Syndication:** Flatten hierarchies for reporting systems (e.g., provide a pre-calculated `full_hierarchy_path` string for the Product Master).

---

## Phase 6: Operational Monitoring & Performance Scaling
> *Status: **Infrastructure.** Required before V1 goes to Production with 10M+ records.*

### MDM-6.1 Observability Pipeline
- **Business KPIs:**
  - *Match Rate:* Percentage of incoming records successfully auto-linked.
  - *Golden Record Coverage:* % of required attributes populated in the Golden Record.
  - *Stewardship Queue Age:* Average time a record sits in a Review Queue.
- **Technical KPIs:**
  - Matching Engine latency (p99 should be under 200ms).
  - Syndication Lag (time between Hub update and downstream system update).

### MDM-6.2 Data Archiving & Purge
- Source system raw data (Phase 1) grows exponentially. 
- **Rule:** Archive `MDM_RAW_INGEST` data older than 13 months to cold storage (AWS S3 Glacier).
- **Rule:** Only the **latest 3 versions** of the Golden Record are kept in the active DB; older versions are compressed and archived.

---

## Phase 7: Advanced Augmentation (AI/ML)
> *Status: **Future Roadmap.** Enhances the human process.*

### MDM-7.1 Attribute Enrichment
- When a new Product is created (e.g., "iPhone 15"), the MDM calls an external Data-as-a-Service (DaaS) provider (e.g., GDSN or OpenCorporates) to auto-populate missing fields (Weight, Category, Tech Specs).
- The Steward simply approves the suggested enrichment.

### MDM-7.2 Self-Learning Matching Engine
- Analyzing the Steward's Merge/Separate decisions to dynamically adjust the matching thresholds (ML feedback loop).
- If the Steward keeps rejecting matches that scored 82%, the system dynamically raises the "Auto Link" threshold for that specific source pair.

---

## MDM Maturity Model (CMMI Framework)

To track progress, we use the following maturity matrix:

| Level | Name | Capability | Estimated Timeline |
| :--- | :--- | :--- | :--- |
| **1** | **Initial** | Siloed data. No central Hub. Spreadsheets everywhere. | Starting Point |
| **2** | **Repeatable** | Hub is built. Data is ingested. **Automated Matching** works for exact matches only. | *End of Phase 1* |
| **3** | **Defined** | **Probabilistic Matching** is operational. Golden Record is created. Data is syndicated down to 1 system. | *End of Phase 2* |
| **4** | **Managed** | **Stewardship UI** is live. KPIs are tracked. The "Humans in the Loop" are effective. | *End of Phase 3* |
| **5** | **Optimizing** | Hierarchies are managed. AI/Enrichment is enabled. Syndication is real-time to all systems. | *End of Phase 5/7* |

---

## Critical Implementation Dependencies

| Dependency | Phase Needed | Failure Impact |
| :--- | :--- | :--- |
| **Source System API Stability** | Phase 1 | If sources are inconsistent, matching quality degrades significantly. |
| **Golden Key Identification** | Phase 0 | We must know the legal/tax identifier for Parties and GTIN for Products. Without a reliable "Anchor Key," probabilistic matching becomes a nightmare. |
| **Security (OAuth2/Mutual TLS)** | Phase 1 | We are dealing with sensitive PII (Customer data) and proprietary Pricing. Security must be established *before* the first byte is ingested. |

---

## Summary: The "15-Year Architect" Reality Check

1. **Do not build a "Master Data" system.** Build a **"Trust Scoring"** system. The Golden Record is the byproduct.
2. **Do not automate everything.** The 20% of data that fails to match *will* cause your business to lose money if not routed to a human expert. Build a damn good Stewardship UI; it is the most critical part of the Hub.
3. **Syndication is harder than Ingestion.** Getting data *into* the Hub is the easy part. Getting every downstream system to gracefully accept the updated `item_weight` without breaking their integration is the hard part. Invest heavily in the Syndication mapping layer (Phase 4).
4. **Versioning saves lives.** Never hard delete a Master Record. Always set `status = 'SUPERSEDED'` and link the new ID to the old. Your audit team will thank you.

---

*End of Enterprise MDM Design Roadmap — v2.0*