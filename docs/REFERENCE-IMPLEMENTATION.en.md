# Reference implementation: English usage guide

**English** | [한국어 상세 가이드](REFERENCE-IMPLEMENTATION.ko.md) · [Documentation map](README.md)

This guide summarizes how to run and connect the reference implementation. The [Korean detailed guide](REFERENCE-IMPLEMENTATION.ko.md) retains the complete conformance table and migration details; the Python source, schemas, and tests are the executable reference. This guide is not a production certification or a complete translation of the detailed specifications.

## 1. Install and inspect

Package metadata requires Python 3.11+. CI uses Python 3.12; the commands below select that version. From the repository root:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python scripts/validate_templates.py
.venv/bin/python -m pytest -q
```

The validator checks duplicate YAML keys, JSON Schema, semantic constraints and managed-document coverage/digests. The tests use synthetic fixtures. No live model provider, remote shell, cloud credentials, or operational data is bundled. Review [permitted use](../LICENSING.en.md) before running or adapting the software.

**Known compatibility limit:** the current code fails two gzip migration-archive tests in the observed Python 3.15 environment because `GzipFile` infers a write mode for the temporary stream. Use the CI Python 3.12 environment for these workflows. The package metadata currently has no upper Python bound; it is not evidence that all newer interpreters have passed validation. This documentation update does not repair the archive implementation.

## 2. Components

| Location | Role |
|---|---|
| `schemas/trace-gate.schema.json` | Core, DM and AH contract schemas |
| `schemas/document-migration.schema.json` | Optional migration contracts, separate from the document lifecycle |
| `src/trace_gate/validation.py` | Schema, semantic and document-manifest validation |
| `src/trace_gate/gates.py` | Deterministic Gate evaluation and bound evidence receipts |
| `src/trace_gate/context.py` | Purpose-limited context selection and prompt envelopes |
| `src/trace_gate/semantic.py` | Optional retrieval-candidate provenance, permission and freshness checks |
| `src/trace_gate/runtime.py` | Bounded model/tool/verifier loop and checkpoints |
| `src/trace_gate/multi_agent.py` | Local writer leases, cancellation state and merge checks |
| `src/trace_gate/migration*.py` | Scoped transfer, archive, link, stream and recovery helpers |
| `templates/`, `examples/`, `tests/` | Contract fixtures, deterministic demonstrations and regression checks |

## 3. Gate evaluation is not authorization

```bash
.venv/bin/python scripts/evaluate_gate.py \
  templates/gate-decision.yaml examples/gate-facts.yaml
```

Missing required facts or evidence references block evaluation; unmet thresholds fail; satisfied requirements pass. The receipt includes canonical input and receipt digests, evaluator identity and version. Changing `evaluated_at` changes the receipt digest; replay requires the same time, policy and facts.

Evaluator 1.1.1 rejects non-finite values, non-JSON objects, malformed evidence references, and boolean/numeric equivalence. `facts_schema` constrains types, units and ranges. A `fail` or `blocked` receipt grants no new authority, and `pass` is not itself permission to execute.

Use `evaluate_bound_gate` when integrating a deployment. Bind trusted evidence digests to the run, subject revision, Gate, facts and freshness window. A digest computed from untrusted evidence is not an independent trust anchor. Authentication, completeness of the observation window, domain meaning and promotion approval remain deployment responsibilities. The CLI is an evaluation example, not an operational promotion endpoint.

## 4. Runtime and verified resumption

A product adapter supplies the model interface, scoped tool handlers, an independent verifier, authenticated approval resolution and durable ordered storage. The reference `RunKernel` is a single-process implementation.

- A missing verifier blocks the run before model or tool calls. Malformed verification does not count as completion.
- New ledgers use runtime format 2 and retain the original scope/limits digest and absolute deadline. Failed attempts still consume budget.
- Explicit resumption requires a `resume_approval_ref` verified by a trusted application. Resumption must not enlarge the original scope, budget or deadline.
- A write with an unknown outcome cannot be replayed in the same run. Investigate actual effects and idempotency evidence; use a separately approved new run when appropriate, preserving the failure history.
- `EventStore` checks ordering, digest links and attempt/observation/verifier bindings. Append is synchronized before memory state is updated. Detecting a truncated valid prefix requires an independently stored `expected_head`.

**Timeout limitation:** the Python handler timeout is measured after the handler returns. It is not cancellation or a guarantee that a tool stopped before changing state. A production executor must enforce isolation/deadlines and reconcile observed effects. Malicious writers that recompute hashes, concurrent processes, durable trust roots and clock rollback require controls outside this JSONL example.

Package 1.2.0 introduced breaking hardening requirements. Package 2.0.x changes licensing metadata while retaining that execution logic. Preserve historical receipts and ledgers; do not rewrite old records to appear compliant with the new format. Move an unfinished older-format run into a newly authorized run as described in the detailed guide.

## 5. Document context and optional retrieval

`select_context` requires an active ReadProfile permitting the purpose/operation, explicit targets, passing validation, current freshness, allowed sensitivity and tiers, and record/byte limits. Trusted adapters supply validation times, field policies, tier digests and source digests. Empty targets do not authorize all documents. The selector does not independently fetch or authenticate source manifests and lineage.

Rejected artifacts and reasons remain in the Context Pack. There is no automatic fallback to broader sensitivity or tiers. Do not pack multiple records into one item to bypass limits. A redaction adapter must produce a new digest when it changes content. Prompt assembly checks for Context Pack changes.

`select_semantic_candidates` validates externally retrieved identities against access intent, read/embedding profiles, index manifests, current document revisions, sensitivity, group membership and candidate limits. It returns identities/provenance; ordinary context selection then obtains permitted content. It does not generate embeddings or operate an approximate-nearest-neighbor index. Exact retrieval works without these optional components. Relevance is not authority.

## 6. Multi-agent and migration extensions

`AgentCoordinator` is optional. Its local path checks detect overlapping ancestor/descendant scopes and conservative alias conflicts; it does not implement cross-host fencing. An expired lease is not automatically safe to reuse when effects remain unresolved. Deployments supply durable leases, authenticated child identities, cancellation acknowledgement, scoped policy inheritance and post-merge verification. Conflicting digests for the same artifact block a merge rather than allowing a model to choose a winner.

[TRACE-DM-MIGRATION](subframeworks/TRACE-DM-MIGRATION.ko.md) is an optional scoped contract. Data receipt, bilateral cutover and business activation are separate decisions. The default archive rejects links and retains its 256 MiB limit. Relative-link restoration and bounded chunk streams require separate opt-in policy and approval; they must not weaken the default path.

`reference_only` transfers approved reference metadata instead of external payload. It requires pinned identity/revision/hash, owner, access, persistence and dependency/rollback evidence. It must not be reported as payload delivery. Archive helpers, transition models and local locks do not implement distributed compare-and-swap, external writer fencing, or a complete application restoration. Owner/ACL/xattr/executable/sparse and engine-specific dependency restoration have limitations; block when a required property is unsupported. Consult the detailed migration guide before selecting these helpers.

## 7. Managed documents and translations

Every repository Markdown file is registered in [`managed-document-manifest.yaml`](managed-document-manifest.yaml), including its identity, scope, owner, provenance, digest, lineage, freshness and access policy. The manifest avoids a self-hash cycle.

For a new Markdown file, add its metadata entry first. Then refresh content-derived values and validate:

```bash
.venv/bin/python scripts/update_document_manifest.py
.venv/bin/python scripts/validate_templates.py
.venv/bin/python -m pytest -q
```

Keep language counterparts and links synchronized. Translations have separate identities and a source relationship; do not silently overwrite the source document or historical terms. Updating documentation does not change the execution contract or require inventing a new package release.

## 8. Evidence and deployment limits

The [public hardening record](status/TRACE-GATE-HARDENING-PUBLIC-20261017.json) and [conformance table](REFERENCE-IMPLEMENTATION.ko.md#9-교정-적합성-연결표--2026-10-17) cover verifier, checkpoint, resumption, evidence binding, context and writer-boundary regressions. These tests are synthetic.

The repository does not supply cryptographic signers, production authentication, a distributed single writer, forced Python-tool cancellation, provider token accounting, embedding generation, or all domain-specific Gate semantics. `scripts/check_quality_shadow_binding.py` loads an adapter module for an isolated synthetic check; module loading is not a security sandbox. Review any adapter before executing it.

Record remaining obligations as evidence and unknowns. Enable a deployment only after its own adapters, trust boundaries, approvals and recovery process are verified.
