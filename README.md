# TRACE-GATE Framework

**English** | [한국어](README.ko.md)

TRACE-GATE records the change an agent was asked to make, who approved which part of it, which document revision the agent used, and what actually changed. If a write times out, the next session can use that record to investigate the outcome before anyone authorizes another attempt.

The specifications propose an architecture for governing software delivery. The Python reference implementation and its machine-readable contracts let you test selected parts with synthetic inputs. Production safety, distributed authorization, and operational effectiveness require evidence from the deployment. [Reference implementation](docs/REFERENCE-IMPLEMENTATION.en.md#8-evidence-and-deployment-limits)

**Official repository:** [401SPAG/trace-gate-framework](https://github.com/401SPAG/trace-gate-framework) · [401SPAG](https://401spag.com) · [Contact](mailto:mail@401spag.com)

## What TRACE means

| Principle | Meaning | Question |
|---|---|---|
| **T — Trace** | Trace requests, decisions, and evidence | Why is the work needed, and what was approved? |
| **R — Restrict** | Limit authority and effects | What may change, and what must remain protected? |
| **A — Assemble** | Compose bounded capabilities with recovery paths | How can the work be divided into manageable units? |
| **C — Confirm** | Establish facts through evidence | What was observed, and what remains unknown? |
| **E — Elevate** | Grant further operating authority through a Gate | When may the next stage be authorized? |

A **Gate** is an evidence-based decision point, not an acronym. A passing evaluation alone does not grant execution or promotion authority. The five TRACE principles here are distinct from other projects named TRACE.

The optional [DM/AH provenance profile](docs/subframeworks/TRACE-DOCUMENT-MANAGEMENT.ko.md#23-선택적-근거-위치실행-계보-프로필-010) binds source locations, selected context, citations and execution records. To check the bundled example offline from the checkout, run `python scripts/validate_provenance.py examples/provenance-bundle.json`.

## Three responsibilities

| Area | Responsibility |
|---|---|
| **TRACE Core** | Requests, boundaries, approvals, evidence, and decisions about further authority |
| **TRACE-DM — Document Management** | Canonical documents, revisions, lineage, integrity, freshness, and purpose-limited context |
| **TRACE-AH — Agent Harness** | Mediated model/tool execution, observations, verification, checkpoints, and verified resumption |

```mermaid
flowchart LR
    CORE["TRACE Core<br/>Authority and evidence"] -->|Authorized scope| AH["TRACE-AH<br/>Agent Harness"]
    CORE -->|Document governance| DM["TRACE-DM<br/>Document Management"]
    DM -->|Verified context| AH
    AH -->|Execution evidence| CORE
```

Core, DM, and AH can run in one deployment. When a search result or summary informs a decision, trace it back to the canonical revision. Semantic retrieval, multi-agent coordination, and TRACE-DM-MIGRATION are optional.

## Conditions to preserve

- Bind the request, approval, scope, and relevant document revisions **before an effect**.
- Distinguish an attempted action, a reported success, and an observed effect. A timeout is not evidence that nothing changed.
- Keep unresolved writes blocked in the same run. Investigate actual effects before deciding on recovery or a newly authorized run.
- Resume only after approval, context, execution history, scope, and original limits remain valid. A checkpoint alone is not permission to resume.
- Supply trusted observation and approval resolvers, protected evidence and independent ledger anchors, and host-enforced concurrency controls where required.

The single-process reference runtime checks a Python handler’s timeout only after the handler returns. A tool can therefore change state after its deadline. A production executor must enforce isolation and deadlines and check the target for changes. [Implementation guide](docs/REFERENCE-IMPLEMENTATION.en.md)

## Start locally

Review the [license scope](LICENSING.en.md) before using the software. Package metadata requires Python **3.11+**. CI tests **3.12** and **3.15**. From a repository checkout, create a project virtual environment using the POSIX commands below. For Python 3.15, see the [implementation guide](docs/REFERENCE-IMPLEMENTATION.en.md#1-install-and-inspect).

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python scripts/validate_templates.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/evaluate_gate.py \
  templates/gate-decision.yaml examples/gate-facts.yaml
.venv/bin/python examples/runtime_demo.py
```

The examples run locally with synthetic inputs. You can follow a Gate decision and an agent run without a production model, cloud credentials, a remote write, or an approval service. [Example guide](examples/README.md)

Begin with `request-receipt.yaml`, `ticket.yaml`, `evidence-manifest.yaml`, and `gate-decision.yaml` in [`templates/`](templates/). Add document access/read/manifest contracts for TRACE-DM, and `agent-run.yaml` plus `tool-definition.yaml` for TRACE-AH. Use `templates/HANDOFF.md` for session continuity. The [documentation map](docs/README.md) links the optional contracts and detailed specifications.

## Documentation and versions

| Read next | English | 한국어 |
|---|---|---|
| Documentation map and terminology | [Guide](docs/README.md) | [안내](docs/README.ko.md) |
| Reference implementation | [Usage guide](docs/REFERENCE-IMPLEMENTATION.en.md) | [상세 가이드](docs/REFERENCE-IMPLEMENTATION.ko.md) |
| Examples | [Examples](examples/README.md) | [예제](examples/README.ko.md) |
| Contributions | [Guide and terms translation](CONTRIBUTING.en.md) | [기여 절차·합의 원문](CONTRIBUTING.md) |
| Licensing | [Scope guide](LICENSING.en.md) | [적용 범위](LICENSING.md) |

Both documentation maps link to the full Core, DM, AH, and migration specifications in Korean. For past changes, see the [changelog](CHANGELOG.md). For the revision and hash of a particular document, see the [TRACE-DM document manifest](docs/managed-document-manifest.yaml).

Repository version markers are independent: Python package **2.1.0**, Core **1.1.0**, DM **0.2.0**, AH **0.1.0**, optional DM-MIGRATION **0.1.0**. These are not an announcement of a package-registry release. Package 2.0.x records licensing changes without changing the 1.2.0 execution logic. The earlier 1.2.0 hardening introduced breaking adapter requirements; preserve historical receipts/checkpoints and consult the implementation guide before migration.

## License and contributions

Copyright © 2026 D. JEONG and the respective contributors.

- **Documentation:** [CC BY-NC-ND 4.0](LICENSE). Noncommercial sharing of unadapted material is allowed with the required notices; commercial use or sharing translations/adaptations requires separate permission unless another applicable permission or exception covers it.
- **Software and machine-readable contracts:** [401SPAG Noncommercial Software License 1.1](LICENSE-CODE). It permits noncommercial execution, study, private modification, and unmodified redistribution with notices. Commercial use/distribution and external distribution of modified software require separate permission unless otherwise authorized. A business pilot or customer proof of concept does not become noncommercial merely because it is free.
- **Contributions:** purpose-limited official review permissions and an additional, explicit integration/sublicensing agreement are distinct. See [CONTRIBUTING](CONTRIBUTING.en.md).

Earlier valid permissions, including CC BY and code license 1.0, and independent rights under applicable hosting-platform terms remain available for the material they cover. This distribution is publicly readable source with use and redistribution restrictions; it is not described as OSI-approved open source. The guides do not change the operative licenses or past agreements. [Scope and precedence](LICENSING.en.md) · [Separate permissions](mailto:mail@401spag.com).
