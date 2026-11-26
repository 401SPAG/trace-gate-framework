# Documentation map

**English** | [한국어](README.ko.md) · [Repository home](../README.md)

To run a Gate locally, start with the examples. To see what an adapter must check before granting access or resuming work, follow the DM or AH specification below. The detailed specifications are in Korean. The English usage guide covers installation, adapters, and the limits of the reference implementation.

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

Use the [managed-document manifest](managed-document-manifest.yaml) to find a document’s ID, revision, hash, lineage, freshness, and access metadata. Each translation has its own ID and links to its source, so the two revisions can be checked separately.

The [October 17 hardening record](status/TRACE-GATE-HARDENING-PUBLIC-20261017.json) reports 422 passing tests for reference package 1.2.0. The [conformance table](REFERENCE-IMPLEMENTATION.ko.md#9-교정-적합성-연결표--2026-10-17) identifies the controls each deployment still has to supply. Consult the [changelog](../CHANGELOG.md) for compatibility changes and preserve earlier receipts and agreements when revising documents.

The [licensing transition](LICENSING-TRANSITION.ko.md) and [1.1 clarification review](LICENSING-REVIEW-1.1.ko.md) are historical Korean records; their text is retained. Current legal texts are linked from the licensing guides.
