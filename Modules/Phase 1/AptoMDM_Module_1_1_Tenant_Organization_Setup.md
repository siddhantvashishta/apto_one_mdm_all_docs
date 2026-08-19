# AptoMDM Module 1.1 — Tenant & Organization Setup

**Status: ✅ CLOSED — Version 1.0. Closed at all 5 audits (`/crosslayer`, `/crossmodule` [N/A, first module], `/gap`, staleness sweep), Ops-only self-service posture confirmed.**

## Dependencies
None — first module in design order, foundational to everything else.

## Config Object Overview
`TENANT`, `ORGANIZATION` (self-referencing hierarchy), `TENANT_DOMAIN_ACTIVATION` — per Roadmap Module 1.1 and Bible §8.2.

---

## Layer 1 — Process Flow

### 1.1.1.A Tenant Provisioning

**Actors:** Apto Platform Ops (internal, Control Plane), Tenant Admin (first user)

1. **Provisioning request initiated** — Platform Ops creates a new tenant record via the internal ops tool: legal name, data residency region, subscription tier, initial admin contact email.
2. **Data residency locked at creation** — the region selected in step 1 becomes permanent the moment the record is submitted; there is no migration path in this build.
3. **Tenant database provisioning** — Control Plane triggers a dedicated PostgreSQL database for the tenant (Data Plane) and applies the base schema migration set via `sqlx-cli` (Bible §5, Stub 1 resolved).
4. **Tenant status = `PROVISIONING`** in the Control Plane record.
5. **Initial Tenant Admin invited** — system emails an invite to the admin contact, with a **7-day expiry** on the invite token. Tenant remains `PROVISIONING` while the invite is outstanding.
6. **Admin accepts, sets credentials** — JWT-backed account created and linked to the tenant.
7. **Tenant status → `ACTIVE`** once the first admin is confirmed.
8. **Post-activation landing** — Tenant Admin sees an empty-state onboarding screen: no organization hierarchy, no domains active yet — this is the natural handoff into flows B and C below.

**Exception paths**
- **Invite expires (7 days, no acceptance)** → status `PROVISIONING → INVITE_EXPIRED` (explicit terminal-ish state, never silently stuck in `PROVISIONING`). **Evaluated lazily, not by a scheduled job** — see BR-1.1.22.
- **Regenerate from `INVITE_EXPIRED`** → Platform Ops or the original requester triggers regeneration; issues a fresh token + fresh 7-day expiry; status returns to `PROVISIONING`.
- **DB provisioning failure** → status `PROVISIONING_FAILED`, retried by Platform Ops; never exposed as `ACTIVE`, no partial access possible under any circumstance.

### 1.1.1.B Organizational Hierarchy Definition

**Actors:** Tenant Admin, Org Admin (optional delegated role)

1. Tenant Admin creates the **root Organization node** (typically the holding company / parent legal entity). **Optional** — a tenant with one flat business unit may operate with zero or one Organization node; this is a confirmed design default, not a temporary gap.
2. Tenant Admin or Org Admin adds a **child Organization** under a chosen parent: name, code, and optional legal-entity-linkage fields (full detail deferred to the Phase 2 Organization canonical model — recorded as Stub 2, see below).
3. System validates the new edge does not create a cycle **before** committing.
4. The hierarchy tree re-renders after every add/move/deactivate action.
5. An existing node can be **re-parented** — triggers the same cycle check as step 3.
6. An existing node can be **deactivated** (never deleted) only if it has no active child nodes and no active downstream data-domain dependents.

**Exception paths**
- Attempted cycle (moving a node under its own descendant) → blocked at validation, no partial write.
- Deactivating a node with active children → blocked, lists the dependent children.

### 1.1.1.C Tenant Domain Activation / Deactivation

**Actors:** Tenant Admin

1. Tenant Admin opens the Domain Activation screen — lists all platform-registered domains (Customer, Supplier, Product, Location, Employee, Organization, Asset, Material, Account, Reference Data) with this tenant's current state.
2. Toggling a domain **Active** creates a `TENANT_DOMAIN_ACTIVATION` record — the domain's screens/APIs become available immediately.
3. Toggling an active domain **Inactive** first checks for existing golden records in that domain — blocked if any exist.
4. Activation never backfills or creates data — it only unlocks configuration surfaces that later Phase 2/3 modules build on.

**Exception paths**
- Deactivation attempted with existing golden records → blocked, shows the blocking count.
- Duplicate/racing toggle on an already-active domain → idempotent no-op, no duplicate record.

### 1.1.1.D Tenant Deactivation / Reactivation (resolves Stub 5)

**Actors:** Apto Platform Ops

1. Platform Ops opens S1.1.2 (Tenant Detail) for an `ACTIVE` tenant and selects **Deactivate Tenant** — typically triggered by contract end, non-payment, or a support/compliance action.
2. Confirmation dialog states plainly: all users of this tenant immediately lose access; no data is deleted; the tenant can be reactivated at any time.
3. On confirm: status `ACTIVE → DEACTIVATED`. All active JWT sessions for that tenant's users are invalidated immediately — a logged-in user's next request fails auth, not their next login attempt.
4. Underlying tenant database, Organization hierarchy, and domain activations are untouched — deactivation revokes access only, per the platform's non-destructive principle (Bible §8.4/§8.8), applied here at the tenant level even though this predates the Golden Record engine.
5. Reactivation: Platform Ops selects **Reactivate Tenant** on a `DEACTIVATED` tenant. Status `DEACTIVATED → ACTIVE`, all prior configuration (Organization nodes, active domains) is exactly as it was — nothing needs to be rebuilt, because nothing was destroyed.

**Exception paths**
- Deactivation attempted on a tenant not currently `ACTIVE` (e.g. still `PROVISIONING`) → blocked; those states have their own resolution paths (regenerate invite, retry provisioning) and deactivation is not a substitute for them.
- Reactivation attempted on a tenant in any status other than `DEACTIVATED` → not offered; the action only exists on that status.

---

## Layer 2 — Business Rules

### Tenant Provisioning Rules

**BR-1.1.1** A tenant's data residency region is immutable once the tenant record is submitted. No screen, API, or admin action may change it after creation.

**BR-1.1.2** A tenant cannot reach status `ACTIVE` without exactly one confirmed Tenant Admin. There is no "activate now, invite later" path.

**BR-1.1.3** An invite token expires exactly 7 days (168 hours) from issuance. Expiry is evaluated server-side on every access attempt against that token — a token is never trusted client-side as still valid.

**BR-1.1.4** Regenerating an expired invite issues a new token and invalidates the old one immediately; the old token must fail even if somehow still in a user's inbox/browser.

**BR-1.1.5** A tenant cannot be hard-deleted at any status. `PROVISIONING_FAILED` and `INVITE_EXPIRED` tenants are retained (not purged) for audit purposes — deactivation, not deletion, is the only terminal action available (mirrors the platform-wide non-destructive principle, Bible §8.4/§8.8, applied here even though Tenant predates the Golden Record engine).

**BR-1.1.6** Only Platform Ops can create a tenant. No self-service tenant creation exists in this build (flagged as a product-scope note, not a technical limitation — see Open Items below).

**BR-1.1.17** A tenant may only be deactivated from status `ACTIVE`. Deactivation is not offered as a resolution path for `PROVISIONING`, `PROVISIONING_FAILED`, or `INVITE_EXPIRED` — those states resolve via their own actions (retry, regenerate).

**BR-1.1.18** Deactivating a tenant never deletes or drops its database, Organization hierarchy, or domain activations. Deactivation revokes access only — the same non-destructive discipline the platform applies everywhere else (Bible §8.4/§8.8), applied here even though Tenant predates the Golden Record engine.

**BR-1.1.19** Deactivating a tenant immediately invalidates every active JWT session held by that tenant's users. A currently-logged-in user's very next request must fail authentication — access does not linger until their token's natural expiry or their next login attempt.

**BR-1.1.20** Reactivating a `DEACTIVATED` tenant restores it to `ACTIVE` with all prior configuration intact and requires no reconstruction — this is only possible because BR-1.1.18 guarantees nothing was destroyed.

**BR-1.1.21** Only Platform Ops can deactivate or reactivate a tenant (`CONFIG.TENANT.DEACTIVATE`) — no tenant-side user, including a Tenant Admin, can deactivate their own tenant.

**BR-1.1.22 (added at `/gap`, closes a real ambiguity, not a stub)** Expiry transitions — `tenant.status: PROVISIONING → INVITE_EXPIRED` and `mdm_tenant_invite.status: PENDING → EXPIRED` — are evaluated **lazily**, not by a scheduled background job: any read or write touch of a `PROVISIONING` tenant or its active invite first checks whether `expires_at` has passed; if so, both records are updated to their expired state before the request proceeds. This avoids introducing a new scheduled-worker dependency in this module's build scope. In practice, S1.1.1 (Tenant Registry) is the natural touch point that resolves any stale `PROVISIONING` row whenever Platform Ops views the list — access enforcement (BR-1.1.3) remains correct even in the interval before that touch happens, since it checks `expires_at` directly rather than trusting the stored status.

### Organizational Hierarchy Rules

**BR-1.1.7** An Organization hierarchy is optional. A tenant may have zero Organization nodes and still be fully operational — Phase 2+ canonical entities do not require an Organization node to exist.

**BR-1.1.8** The hierarchy must be acyclic at all times. Cycle validation runs before any write (create, re-parent) commits — never as a post-write cleanup check.

**BR-1.1.9** An Organization node cannot be deactivated while it has any active child node. The blocking child list must be shown, not just a generic refusal.

**BR-1.1.10** An Organization node cannot be deactivated while any active `TENANT_DOMAIN_ACTIVATION`-scoped data (once Phase 2+ modules exist) references it as an owning organization. This module records the *rule*; the actual referential check is implemented once a referencing module (Phase 2+) exists — tracked as Stub 3.

**BR-1.1.11** Re-parenting a node preserves its `created_at`/`created_by` — only `updated_at`/`updated_by` and the parent reference change. Re-parenting is not a delete-and-recreate.

**BR-1.1.12** Organization node `code` must be unique within a tenant (not globally) — two different tenants may both use code `HQ`.

### Domain Activation Rules

**BR-1.1.13** A domain cannot be deactivated for a tenant while any golden record exists in it. This is enforced at the platform level (Bible §8.2) and re-stated here as the first module to actually implement the check's UI/API surface.

**BR-1.1.14** Domain activation is immediate and has no approval workflow in this build — any user holding `CONFIG.DOMAIN_ACTIVATION.EDIT` can toggle a domain without a second approver. (Flagged: this may be too permissive for a Restricted-classification domain once Phase 11/15 governance modules exist — tracked as Stub 4.)

**BR-1.1.15** Deactivating and reactivating a domain does not reset or clear any configuration (canonical model, matching rules, etc.) built for it in Phase 2/3 — deactivation only hides the domain's runtime surfaces, it is not a factory reset.

**BR-1.1.16** The set of platform-registered domains itself (Customer, Supplier, Product, etc.) is fixed platform-wide metadata, not tenant-editable — a tenant activates/deactivates from this fixed list, it cannot invent a new domain name here (that capability, if ever needed, belongs to a future platform-admin-only module, not Module 1.1).

---

## Layer 3 — UI Screens

> Permission codes follow the `Domain.Module.Action` pattern (Bible §8.0). Tenant/Organization/Domain-Activation are platform-configuration surfaces, not an MDM business domain — they use the `CONFIG` pseudo-domain prefix. VIEW is a prerequisite permission for any other action on the same screen (Bible §8.0). These are the **first permission codes minted platform-wide** — Project Instructions §3 continuation points updated accordingly.

### S1.1.1 — Tenant Registry (internal, Platform Ops only)

**Purpose:** List and search all tenants across the platform.
**Permission:** `CONFIG.TENANT.VIEW`

- Table columns: Legal Name, Data Residency Region, Subscription Tier, Status (`PROVISIONING` / `ACTIVE` / `PROVISIONING_FAILED` / `INVITE_EXPIRED`), Created At
- Filter by Status, search by Legal Name
- Row click → S1.1.2 (Tenant Detail)
- "New Tenant" button → S1.1.3, visible only with `CONFIG.TENANT.CREATE`

### S1.1.2 — Tenant Detail (internal, Platform Ops only)

**Purpose:** View a single tenant's provisioning state and take invite-related action.
**Permission:** `CONFIG.TENANT.VIEW`; actions below require additional permissions as noted.

- Header: Legal Name, Status badge, Data Residency Region (shown as locked/read-only per BR-1.1.1 — no edit control exists for this field, not just a disabled one)
- Admin contact email, invite status (Pending / Expired / Accepted), invite expiry countdown while Pending
- **"Resend Invite"** button — visible only when status is `PROVISIONING` and invite is still within its 7-day window; requires `CONFIG.TENANT.RESEND_INVITE`
- **"Regenerate Invite"** button — visible only when status is `INVITE_EXPIRED`; requires `CONFIG.TENANT.RESEND_INVITE`; triggers BR-1.1.4 (old token invalidated)
- **"Retry Provisioning"** button — visible only when status is `PROVISIONING_FAILED`; requires `CONFIG.TENANT.CREATE`
- **"Deactivate Tenant"** button — visible only when status is `ACTIVE`; requires `CONFIG.TENANT.DEACTIVATE`; opens S1.1.9 confirmation modal (resolves Stub 5)
- **"Reactivate Tenant"** button — visible only when status is `DEACTIVATED`; requires `CONFIG.TENANT.DEACTIVATE`; no confirmation modal needed (reactivation is purely restorative, not destructive — BR-1.1.20)
- No delete action anywhere on this screen (BR-1.1.5 — deactivation, not deletion, is the only terminal-facing action, consistent with 1.1.1.D)

### S1.1.9 — Deactivate Tenant Confirmation (modal, Platform Ops only)

**Purpose:** Confirm the consequences of tenant deactivation before committing (Layer 1, flow D, step 2).
**Permission:** `CONFIG.TENANT.DEACTIVATE`

- States plainly, as three separate lines rather than one paragraph: "All users of this tenant will immediately lose access," "No data will be deleted," "You can reactivate this tenant at any time"
- Requires typing the tenant's legal name to confirm (same discipline as any irreversible-feeling action, even though it is technically reversible per BR-1.1.20) — prevents a misclick on a list of many tenants from deactivating the wrong one
- Confirm → executes 1.1.1.D steps 3–4, returns to S1.1.2 showing `DEACTIVATED` status

### S1.1.3 — New Tenant (internal, Platform Ops only)

**Purpose:** Create a new tenant record (Layer 1, flow A, steps 1–2).
**Permission:** `CONFIG.TENANT.CREATE`

- Fields: Legal Name (required), Data Residency Region (required, dropdown from Bible §8.15 reference list, **shown with an explicit "cannot be changed after creation" inline warning** directly under the field — not just enforced silently server-side, so Ops sees the consequence before submitting), Subscription Tier (required, dropdown), Initial Admin Contact Email (required, validated format)
- Submit → creates tenant, status `PROVISIONING`, sends invite (Layer 1 steps 3–5), redirects to S1.1.2
- No draft-save — a partially filled form is not persisted; this is a short single-purpose form, not a multi-step wizard

### S1.1.4 — Invite Acceptance (public, unauthenticated, token-gated)

**Purpose:** Let the invited Tenant Admin accept and set credentials (Layer 1, flow A, step 6).
**Access:** Valid, unexpired invite token in the URL — no separate permission code, since the user doesn't exist yet.

- Shows Tenant Legal Name (read-only) so the invitee confirms which organization they're joining
- Fields: Full Name, Email (pre-filled from invite, read-only), Password, Confirm Password
- On expired-token access: shows "This invite has expired — contact your Apto representative for a new one" rather than a generic error, and does **not** reveal whether the tenant itself exists (avoids leaking tenant existence to an unauthenticated visitor)
- Submit → creates JWT-backed admin account, tenant status → `ACTIVE`, redirects to S1.1.5

### S1.1.5 — Tenant Onboarding Landing (Tenant Admin, first login)

**Purpose:** Empty-state landing after activation (Layer 1, flow A, step 8) — orients the new admin toward Organization setup and Domain activation without forcing either.
**Permission:** Implicit — any authenticated Tenant Admin of an `ACTIVE` tenant with no Organization nodes and no active domains yet.

- Two clearly optional cards, neither blocking the other: "Set up your Organization structure" → S1.1.6, "Activate your data domains" → S1.1.8
- This screen stops appearing once the tenant has at least one Organization node **or** at least one active domain — it's a one-time orientation, not a permanent dashboard

### S1.1.6 — Organization Hierarchy Tree Editor (Tenant Admin / Org Admin)

**Purpose:** View, add, re-parent, and deactivate Organization nodes (Layer 1, flow B).
**Permission:** `CONFIG.ORGANIZATION.VIEW`

- Tree view, expand/collapse, root-level "Add Organization" action requires `CONFIG.ORGANIZATION.CREATE`
- Each node: name, code, status (Active/Inactive), child count
- Node context menu: Edit (`CONFIG.ORGANIZATION.EDIT`), Add Child (`CONFIG.ORGANIZATION.CREATE`), Re-parent (`CONFIG.ORGANIZATION.EDIT` — drag-and-drop or explicit "Move to..." picker), Deactivate (`CONFIG.ORGANIZATION.DEACTIVATE`)
- **Cycle-attempt feedback:** if a re-parent action would create a cycle, the drop target is visually rejected (red outline) at drag-time, before any request is sent — client-side pre-check backed by the same server-side validation (BR-1.1.8) as the final authority, never trusted alone
- **Deactivation-blocked feedback:** attempting to deactivate a node with active children opens a blocking-list modal naming each active child (BR-1.1.9), not a bare "cannot deactivate" message
- Empty state (zero nodes): "No organization structure yet — this is optional. Add one if you need to model multiple business units." — explicitly reassures the optional nature (BR-1.1.7), rather than presenting emptiness as an incomplete setup step

### S1.1.7 — Add / Edit Organization Node (modal, Tenant Admin / Org Admin)

**Purpose:** Create or edit a single node's fields.
**Permission:** `CONFIG.ORGANIZATION.CREATE` (add) / `CONFIG.ORGANIZATION.EDIT` (edit)

- Fields: Name (required), Code (required, tenant-unique per BR-1.1.12, inline validation on blur), Parent (pre-filled if launched from a node's "Add Child," otherwise a picker), Legal-entity-linkage fields — **shown as a single "More details available once Organization domain is configured (Phase 2)" placeholder note, not empty editable fields** (Stub 2 — do not imply a capability that doesn't exist yet)
- Save → returns to S1.1.6 with the tree updated in place

### S1.1.8 — Domain Activation (Tenant Admin)

**Purpose:** Enable/disable which MDM domains this tenant uses (Layer 1, flow C).
**Permission:** `CONFIG.DOMAIN_ACTIVATION.VIEW`

- List of all 10 platform-registered domains (Customer, Supplier, Product, Location, Employee, Organization, Asset, Material, Account, Reference Data), each with a toggle
- Toggle requires `CONFIG.DOMAIN_ACTIVATION.EDIT` — visible but disabled (not hidden) without it, so a Viewer-role user can still see the tenant's domain footprint (read access is a separate concern from write access)
- Toggling off with existing golden records: toggle visually reverts and an inline message shows the blocking record count (BR-1.1.13) — this module does not yet have a domain that can produce a golden record, so this state is **not reachable in practice until Phase 7/8 exist**, but the screen and rule are built now so no later module has to retrofit this check onto an already-shipped screen
- No confirmation dialog for turning a domain **on** — it's non-destructive and instant (BR-1.1.14); confirmation dialog **is** required for turning a domain **off**, stating plainly what becomes inaccessible

---

## Layer 4 — DB Schema + Sample Data

> Standard columns and conventions per Bible §8.0. `TENANT` lives in the **Control Plane DB** (it precedes tenant existence, so it cannot itself be tenant-scoped). `ORGANIZATION` and `TENANT_DOMAIN_ACTIVATION` live in each tenant's own **Data Plane DB** and still carry `tenant_id`, per the platform-wide invariant that every operational table is tenant-scoped by construction (Bible §8.10/§15.1) — kept even inside a per-tenant database, for forward consistency if the architecture ever pools schemas.
>
> **Known forward reference (not a stub — resolves in the very next module):** `created_by`/`updated_by`/`activated_by`/`deactivated_by` columns below are typed `UUID` with no enforced foreign key yet, because `MDM_USER` doesn't formally exist until Module 1.3. The FK constraint is added via a Module 1.3 migration once that table exists — this is expected sequencing for the platform's first module, not a defect.

### TENANT (Control Plane DB)

```sql
CREATE TABLE tenant (
    tenant_id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    legal_name               VARCHAR(255) NOT NULL,
    data_residency_region     VARCHAR(50)  NOT NULL
        CHECK (data_residency_region IN ('us-east','eu-west','ap-south')),  -- immutable after insert (BR-1.1.1); interim fixed list, added at /gap to close an unconstrained-value gap — upgrades to an FK against Module 1.4's Reference Data list once that module closes (Stub 6)
    subscription_tier        VARCHAR(50)  NOT NULL,
    status                    VARCHAR(30)  NOT NULL
        CHECK (status IN ('PROVISIONING','ACTIVE','PROVISIONING_FAILED','INVITE_EXPIRED','DEACTIVATED')),
    admin_contact_email       VARCHAR(255) NOT NULL,
    created_at                TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by                UUID NOT NULL,           -- Platform Ops user (internal ops system, not MDM_USER)
    updated_at                TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_by                UUID NOT NULL,
    version                   INT NOT NULL DEFAULT 1   -- optimistic locking
);

CREATE INDEX idx_tenant_status ON tenant (status);
```

**Note:** no unique constraint on `legal_name` — two different customers may legitimately share a name (e.g. two unrelated companies both called "Summit Logistics"). No soft-delete columns (`is_deleted`) on this table — status itself carries the full lifecycle (BR-1.1.5, BR-1.1.18), so a separate deletion flag would be a redundant, contradictable second source of truth.

### MDM_TENANT_INVITE (Control Plane DB)

> Append-only by design — a regenerated invite creates a **new row**, it never overwrites the old one (BR-1.1.4, Bible §8.8 non-destructive/audit principle). This is what makes "who requested which invite, when, and how many times" answerable later without a separate audit table.

```sql
CREATE TABLE mdm_tenant_invite (
    invite_id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id                 UUID NOT NULL REFERENCES tenant (tenant_id),
    token_hash                 VARCHAR(255) NOT NULL,   -- hashed, never store the raw token
    status                     VARCHAR(20) NOT NULL
        CHECK (status IN ('PENDING','ACCEPTED','EXPIRED','SUPERSEDED')),
    issued_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at                 TIMESTAMPTZ NOT NULL,     -- issued_at + 7 days (BR-1.1.3)
    accepted_at                TIMESTAMPTZ NULL,
    issued_by                  UUID NOT NULL,            -- Platform Ops user
    superseded_by_invite_id     UUID NULL REFERENCES mdm_tenant_invite (invite_id)
);

CREATE INDEX idx_invite_tenant ON mdm_tenant_invite (tenant_id);
CREATE INDEX idx_invite_token_hash ON mdm_tenant_invite (token_hash);
```

### ORGANIZATION (Tenant Data Plane DB)

```sql
CREATE TABLE organization (
    organization_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id                  UUID NOT NULL,            -- platform-wide invariant (Bible §15.1), even within a per-tenant DB
    parent_organization_id      UUID NULL REFERENCES organization (organization_id),
    name                       VARCHAR(255) NOT NULL,
    code                        VARCHAR(50) NOT NULL,
    is_active                  BOOLEAN NOT NULL DEFAULT true,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by                  UUID NOT NULL,
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_by                  UUID NOT NULL,
    version                     INT NOT NULL DEFAULT 1,
    CONSTRAINT chk_not_self_parent CHECK (organization_id <> parent_organization_id),
    CONSTRAINT uq_org_code_per_tenant UNIQUE (tenant_id, code)   -- BR-1.1.12
);

CREATE INDEX idx_org_parent ON organization (parent_organization_id);
CREATE INDEX idx_org_tenant ON organization (tenant_id);
```

**Cycle prevention (BR-1.1.8) is deliberately not a DB constraint.** PostgreSQL cannot declaratively enforce "no cycle at arbitrary depth" without a recursive trigger, which would run on every write and add complexity disproportionate to this table's write volume. It is enforced at the application layer before every create/re-parent commits — flagged here explicitly as a design decision, not an oversight, so `/gap` doesn't flag it as a missing constraint later.

### TENANT_DOMAIN_ACTIVATION (Tenant Data Plane DB)

```sql
CREATE TABLE tenant_domain_activation (
    id                         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id                  UUID NOT NULL,
    domain_code                 VARCHAR(50) NOT NULL,    -- forward FK to mdm_domain.domain_code, added when Module 1.2 closes (next module — expected sequencing, not a stub)
    is_active                  BOOLEAN NOT NULL DEFAULT false,
    activated_at                TIMESTAMPTZ NULL,
    activated_by                UUID NULL,
    deactivated_at               TIMESTAMPTZ NULL,
    deactivated_by               UUID NULL,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_domain_per_tenant UNIQUE (tenant_id, domain_code)
);

CREATE INDEX idx_domain_activation_tenant ON tenant_domain_activation (tenant_id);
```

### Sample data

**tenant**

| tenant_id | legal_name | data_residency_region | subscription_tier | status | admin_contact_email |
|---|---|---|---|---|---|
| `t-0001` | Acme Global Holdings | `ap-south` | `enterprise` | `ACTIVE` | admin@acmeglobal.example |
| `t-0002` | Northwind Traders | `us-east` | `growth` | `PROVISIONING` | ops@northwind.example |
| `t-0003` | Summit Logistics (old) | `eu-west` | `growth` | `DEACTIVATED` | billing@summitlog.example |

**mdm_tenant_invite** (showing a regenerate — old row superseded, not deleted)

| invite_id | tenant_id | status | issued_at | expires_at | superseded_by_invite_id |
|---|---|---|---|---|---|
| `inv-0001` | `t-0002` | `SUPERSEDED` | Day 1 | Day 8 | `inv-0002` |
| `inv-0002` | `t-0002` | `PENDING` | Day 9 | Day 16 | `NULL` |

**organization** (Acme's hierarchy — matches the Roadmap's holding-company → subsidiary → business-unit example)

| organization_id | tenant_id | parent_organization_id | name | code | is_active |
|---|---|---|---|---|---|
| `org-0001` | `t-0001` | `NULL` | Acme Global Holdings | `HQ` | true |
| `org-0002` | `t-0001` | `org-0001` | Acme North America | `ACME-NA` | true |
| `org-0003` | `t-0001` | `org-0002` | Acme Retail Division | `ACME-NA-RETAIL` | true |

**tenant_domain_activation**

| id | tenant_id | domain_code | is_active | activated_at |
|---|---|---|---|---|
| `tda-0001` | `t-0001` | `CUSTOMER` | true | Day 3 |
| `tda-0002` | `t-0001` | `SUPPLIER` | true | Day 3 |
| `tda-0003` | `t-0001` | `PRODUCT` | false | `NULL` |

---

## Layer 5 — Events

> Every event carries the standard envelope (Bible §8.0): `event_id` (dedup key), `tenant_id`, `correlation_id`, `timestamp_utc`. Published after DB commit, never inside a transaction. Consumers are idempotent by construction — dedupe on `event_id`.

### Topic convention (locked at this module — resolves the Project Instructions §3 stub)

Two tiers, split by where the concern actually lives:

- **Control Plane topic:** `platform.tenant-lifecycle.events` — for events about the `TENANT` record itself (provisioning, invite, activation, deactivation). These occur on the Control Plane, independent of any tenant Data Plane database, so they don't fit a `tenant.{id}.*` pattern.
- **Tenant config topic:** `tenant.{tenant_id}.config.events` — for events from tenant Data Plane configuration (Organization, Domain Activation). These live inside the tenant's own database once it exists.
- **Future business-domain topic** (not used by this module, locked now for consistency): `tenant.{tenant_id}.mdm.{domain}.events` — e.g. `tenant.t-0001.mdm.customer.events`, for Phase 5+ golden-record-bearing domains.

### Events published

| Event | Topic | Trigger (Layer 1 step) | Consumers (known or expected) |
|---|---|---|---|
| `TenantProvisioningStarted` | `platform.tenant-lifecycle.events` | 1.1.1.A step 1 (record submitted) | Billing/ops systems (future); not consumed within this module |
| `TenantProvisioningFailed` | `platform.tenant-lifecycle.events` | 1.1.1.A DB provisioning failure exception path | Platform Ops alerting |
| `TenantInviteIssued` | `platform.tenant-lifecycle.events` | 1.1.1.A step 5 (initial issue) and BR-1.1.4 (regenerate) | Notification service (sends the actual invite email) |
| `TenantInviteExpired` | `platform.tenant-lifecycle.events` | 1.1.1.A exception path — system-triggered on 7-day expiry (BR-1.1.3), not a user action | Platform Ops alerting |
| `TenantActivated` | `platform.tenant-lifecycle.events` | 1.1.1.A step 7 | Notification service; future AptoWMS/AptoTMS product-instance provisioning, if the same tenant activates those products |
| `TenantDeactivated` | `platform.tenant-lifecycle.events` | 1.1.1.D step 3 | **Auth service must consume this synchronously enough to satisfy BR-1.1.19** (immediate session invalidation) — this is the one event in this module with a hard latency expectation, not just eventual consistency |
| `TenantReactivated` | `platform.tenant-lifecycle.events` | 1.1.1.D step 5 | Notification service |
| `OrganizationCreated` | `tenant.{tenant_id}.config.events` | 1.1.1.B step 1–2 | None within this module; available for future Phase 2+ modules that reference Organization |
| `OrganizationUpdated` | `tenant.{tenant_id}.config.events` | 1.1.1.B steps 2 (edit) and 5 (re-parent) | Same as above |
| `OrganizationDeactivated` | `tenant.{tenant_id}.config.events` | 1.1.1.B step 6 | Same as above |
| `TenantDomainActivated` | `tenant.{tenant_id}.config.events` | 1.1.1.C step 2 | Future Phase 2+ modules gating on domain activation state |
| `TenantDomainDeactivated` | `tenant.{tenant_id}.config.events` | 1.1.1.C step 3 | Same as above |

### Payload — worked example

`TenantDeactivated` is the one event in this module with a real downstream consumer requirement (BR-1.1.19), so its full payload is shown as the reference shape every other event in this module follows:

```json
{
  "event_id": "8f14e45f-ceea-4b7d-9f1a-3f2c1a0e9b21",
  "tenant_id": "t-0003",
  "correlation_id": "corr-2f9a7e10",
  "timestamp_utc": "2026-08-19T10:15:32Z",
  "event_type": "TenantDeactivated",
  "payload": {
    "deactivated_by": "ops-user-0007",
    "previous_status": "ACTIVE",
    "reason": "contract_ended"
  }
}
```

Every other event in this module's table follows the same envelope shape, with a `payload` object scoped to that event — e.g. `OrganizationCreated`'s payload carries `organization_id`, `parent_organization_id`, `name`, `code`; `TenantDomainActivated`'s carries `domain_code`, `activated_by`. Full per-event payload schemas are not separately reproduced here since they map directly to the Layer 4 columns already defined for each table (`organization`, `tenant_domain_activation`) — an event's payload is the changed row's relevant columns, not a separate schema to design.

### Cross-layer check

Every event above traces to an explicit Layer 1 step (table's third column). No event exists without a trigger, and every stateful Layer 1 transition (`PROVISIONING→ACTIVE`, `ACTIVE→DEACTIVATED`, `DEACTIVATED→ACTIVE`, invite issue/expire, Organization create/update/deactivate, domain activate/deactivate) has a corresponding event — none were silently left un-announced.

---

| Stub # | Description | Target Module |
|---|---|---|
| 2 | Organization legal-entity-linkage field detail (full shape) | Deferred to Phase 2 — Organization canonical model |
| 3 | Referential check enforcing BR-1.1.10 (Org node deactivation blocked by dependent domain data) | Implemented incrementally as each Phase 2+ module that can reference an Organization node closes |
| 4 | Whether domain activation (BR-1.1.14) needs an approval workflow for Restricted-classification domains | Phase 11 (Governance) or Phase 12 (Workflow & Approval) |
| 5 | **Tenant-level deactivation has no defined flow or screen.** Layer 1 only covers `PROVISIONING` / `ACTIVE` / `PROVISIONING_FAILED` / `INVITE_EXPIRED` — there is no path to retire a tenant whose contract has ended. Surfaced while drafting S1.1.2, which needed a delete/deactivate action and had none to reference. | ✅ Resolved within this module — see Layer 1 flow D, BR-1.1.17–21, S1.1.2/S1.1.9 |
| 6 | `tenant.data_residency_region` uses an interim hardcoded `CHECK` list (`us-east`, `eu-west`, `ap-south`) instead of a real reference-data FK. Added at the `/gap` audit to close an unconstrained-value gap. | Module 1.4 — Reference Data & Code Tables; migrate to FK against the platform region reference list once that module closes |

### Findings fixed at `/gap` audit (not deferred — genuine gaps in this module's own scope)

| Finding | Fix |
|---|---|
| No actor/mechanism specified for `PROVISIONING → INVITE_EXPIRED` transition | BR-1.1.22 added — lazy evaluation on any read/write touch, not a scheduled job |
| `data_residency_region` had zero constraint despite BR-1.1.1 treating it as controlled/immutable | Interim `CHECK` constraint added; Stub 6 tracks the upgrade to a real FK at Module 1.4 |

### Newly minted permission codes (first platform-wide — Project Instructions §3 updated)

| Code | Screen(s) |
|---|---|
| `CONFIG.TENANT.VIEW` | S1.1.1, S1.1.2 |
| `CONFIG.TENANT.CREATE` | S1.1.1, S1.1.3, S1.1.2 (retry) |
| `CONFIG.TENANT.RESEND_INVITE` | S1.1.2 |
| `CONFIG.TENANT.DEACTIVATE` | S1.1.2, S1.1.9 |
| `CONFIG.ORGANIZATION.VIEW` | S1.1.6 |
| `CONFIG.ORGANIZATION.CREATE` | S1.1.6, S1.1.7 |
| `CONFIG.ORGANIZATION.EDIT` | S1.1.6, S1.1.7 |
| `CONFIG.ORGANIZATION.DEACTIVATE` | S1.1.6 |
| `CONFIG.DOMAIN_ACTIVATION.VIEW` | S1.1.8 |
| `CONFIG.DOMAIN_ACTIVATION.EDIT` | S1.1.8 |

### Open item for you (product-scope, not a design default I should assume)

### Self-service tenant creation — confirmed Ops-only (resolved at close)

**BR-1.1.6** stands as designed: no self-service tenant creation in this build, every tenant is provisioned by Apto Platform Ops. Confirmed at module close. If self-service signup is needed in the future, it is a materially different Layer 1 flow (new public signup screen, new validation surface, likely a payment/billing touchpoint) and should be scoped as its own amendment or follow-on module rather than retrofitted into this one.

---

*All 5 layers drafted. Ready for `/crosslayer`, `/crossmodule`, `/gap`, and staleness-sweep audits before `/close`.*
