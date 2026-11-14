# Documentation map

**English** | [한국어](README.ko.md) · [Repository home](../README.md)

Start with the repository README for the conceptual architecture, then use the implementation guide and examples to inspect executable contracts. The detailed specifications below are currently in Korean. This English map and usage guide provide entry points, not a claim that all specifications have been translated.

## Reading paths

| Purpose | Document | Language / scope |
|---|---|---|
| Understand the framework | [Core specification](TRACE-GATE-FRAMEWORK.ko.md) | Korean; complete Core contract |
| Manage documents and context | [TRACE-DM](subframeworks/TRACE-DOCUMENT-MANAGEMENT.ko.md) | Korean; canonical revisions, access, projections, optional retrieval |
| Mediate agent execution | [TRACE-AH](subframeworks/TRACE-AGENT-HARNESS.ko.md) | Korean; model/tool/verifier, checkpoints, bounded subagents |
| Plan a scoped migration | [TRACE-DM-MIGRATION](subframeworks/TRACE-DM-MIGRATION.ko.md) | Korean; optional transfer, references, recovery and cutover |
| Run the reference implementation | [English usage guide](REFERENCE-IMPLEMENTATION.en.md) / [Korean detailed guide](REFERENCE-IMPLEMENTATION.ko.md) | Installation, adapters, limitations and conformance evidence |
| Try deterministic examples | [English](../examples/README.md) / [한국어](../examples/README.ko.md) | Synthetic local inputs |
| Contribute | [English guide](../CONTRIBUTING.en.md) / [Korean terms](../CONTRIBUTING.md) | Workflow, review and integration permissions |
| Check permitted use | [English](../LICENSING.en.md) / [한국어](../LICENSING.md) | Material-specific scope and prior permissions |

## Shared terminology

| Term | Meaning in this project |
|---|---|
| TRACE | Trace, Restrict, Assemble, Confirm, Elevate; five principles, not the separate runtime framework also named TRACE |
| Gate | An evidence-based decision point; a result is not itself operating authority |
| DM | Document Management |
| AH | Agent Harness |
| Canonical document | The designated source of reference for a subject |
| Projection | A derived representation, such as a summary or retrieval index; it does not replace its source |
| Receipt | A record binding a decision or observation to its relevant inputs and scope |
| Effect | An observed change in the target system, distinct from an attempted call or reported success |
| Verified resumption | Continuing only after approval, context, history, scope, and original limits are checked |
| Governance contract | Explicit operational conditions between responsibilities; not a statement that a software record is a legal contract |

## Template groups

- **Core:** [`request-receipt.yaml`](../templates/request-receipt.yaml), [`ticket.yaml`](../templates/ticket.yaml), [`evidence-manifest.yaml`](../templates/evidence-manifest.yaml), [`gate-decision.yaml`](../templates/gate-decision.yaml).
- **DM access and context:** [`document-access-intent.yaml`](../templates/document-access-intent.yaml), [`document-read-profile.yaml`](../templates/document-read-profile.yaml), [`document-manifest.yaml`](../templates/document-manifest.yaml), [`document-gate-receipt.yaml`](../templates/document-gate-receipt.yaml).
- **Optional semantic retrieval:** [`document-embedding-profile.yaml`](../templates/document-embedding-profile.yaml), [`document-embedding-manifest.yaml`](../templates/document-embedding-manifest.yaml). A vector graph is not mandatory.
- **AH execution:** [`agent-run.yaml`](../templates/agent-run.yaml), [`tool-definition.yaml`](../templates/tool-definition.yaml), optional [`subagent-task.yaml`](../templates/subagent-task.yaml).
- **Continuity:** [`HANDOFF.md`](../templates/HANDOFF.md).
- **Optional migration:** the `document-migration-*`, `document-relocation-map.yaml`, and `document-cutover-receipt.yaml` files in [`templates/`](../templates/), governed by the migration specification. Receipt of data, bilateral cutover, and permission to resume business are separate decisions.

## Evidence and maintenance

The [managed-document manifest](managed-document-manifest.yaml) records identities, content-derived revisions, hashes, lineage, freshness, and access metadata. Language counterparts have separate artifact identities; each translation identifies its source through provenance. Updating a translation does not silently revise its source.

The [public hardening record](status/TRACE-GATE-HARDENING-PUBLIC-20261017.json) and [detailed conformance table](REFERENCE-IMPLEMENTATION.ko.md#9-교정-적합성-연결표--2026-10-17) describe synthetic checks and remaining deployment obligations. Read the [changelog](../CHANGELOG.md) for compatibility changes. Preserve old receipts and agreements when updating documents.

The [licensing transition](LICENSING-TRANSITION.ko.md) and [1.1 clarification review](LICENSING-REVIEW-1.1.ko.md) are historical Korean records; their text is retained. Current legal texts are linked from the licensing guides.
