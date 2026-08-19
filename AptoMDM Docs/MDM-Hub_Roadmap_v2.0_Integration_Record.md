# MDM-Hub Roadmap v2.0 — Integration Record

> Source: `Source Architecture/MDM-Hub_Roadmap_v2.0.md` (supplied as `sid.md`)
> Integrated: August 2026
> Authority: The AptoMDM Project Bible and 16-phase Design Roadmap remain the active decision and sequencing authorities.

## Purpose

This record explains how the seven-phase MDM-Hub blueprint is used with the detailed AptoMDM documentation system. The source blueprint is preserved verbatim for traceability, while this file records the decisions needed to prevent two competing roadmaps.

## Concept mapping

| MDM-Hub v2.0 | AptoMDM execution location |
|---|---|
| Foundation and governance | Phase 1 platform foundation, Phase 11 governance, Phase 15 security |
| Raw ingestion and integration | Phase 4 source integration and Phase 5 ingestion |
| Harmonization, matching, survivorship | Phases 6–9 |
| Stewardship and issue management | Phases 10–12 |
| Syndication and privacy filtering | Phase 14, with security/classification rules from Phase 15 |
| Hierarchies and relationships | Phase 2.6 and domain-specific canonical modules |
| Monitoring, scaling, archival | Phase 16 and relevant retention rules in Phase 10 |
| AI/ML augmentation | Future advisory-only scope; not part of the initial build |

## Resolved conflicts

- **Golden Record:** treat it as an explainable attribute-level projection with source, confidence, effective dates, and survivorship rule. A physical read model may exist for performance, but it is not a flat authoritative record.
- **Match thresholds:** use the thresholds locked in the Project Bible and future matching modules. The source blueprint's 60%/85% values are design input, not active platform policy.
- **AI/ML:** enrichment and self-learning matching remain future possibilities. Initial matching, confidence, and enrichment are deterministic and configuration-driven; any future ML must be advisory and steward-reviewable.
- **Build order:** use the AptoMDM 16-phase order. The source blueprint's ingestion-first sequence is a conceptual data-flow view, not the implementation sequence.
- **Security:** apply the AptoMDM JWT, Vault, RBAC/ABAC, tenant-isolation, and audit decisions. OAuth2 or mutual TLS may be used as connector transport options where required, but they do not replace platform authorization.
- **Trust scoring:** carry forward the source blueprint's source weight, recency, completeness, and stewardship principles into the metadata, matching, survivorship, and governance modules; do not introduce a separate trust model outside the Bible.

## Implementation rule

When a future design decision appears in both documents, update the Project Bible first, record any unresolved choice as a numbered stub, and update this integration record only when the relationship between the two roadmaps changes. Never use `sid.md` to update module completion status directly.
