# Reference examples

**English** | [한국어](README.ko.md) · [Repository home](../README.md)

Run these commands from the repository root after completing the README's virtual-environment installation.

## Evaluate a Gate

```bash
.venv/bin/python scripts/evaluate_gate.py \
  templates/gate-decision.yaml examples/gate-facts.yaml
```

The [sample facts](gate-facts.yaml) report a 99.5% success rate, zero duplicate writes, zero forbidden changes, and a passing rollback rehearsal. These meet the [policy requirements](../templates/gate-decision.yaml), including the 99% minimum success rate, so the evaluator returns a receipt with status `pass`. In a deployment, a trusted resolver must authenticate the cited evidence and the responsible authority must approve promotion separately.

## Run a deterministic agent example

```bash
.venv/bin/python examples/runtime_demo.py
```

The [demo](runtime_demo.py) calls the local `status.read` tool for the collector. The tool returns `staging-only`, and the verifier checks that the scripted answer contains that text. The printed result records this local run. The demo needs no live model, performs no remote writes, and grants no operating authority.

Before connecting a real tool, provide a verified Request Receipt, scoped Tool Definition, approval resolver, effect observations, and an appropriate executor. Review [adapter requirements and limitations](../docs/REFERENCE-IMPLEMENTATION.en.md). Keep unresolved effects blocked; a timeout or a stored checkpoint is not evidence that replay is safe.

Software examples follow [LICENSE-CODE](../LICENSE-CODE); surrounding explanatory text follows the [documentation terms](../LICENSING.en.md).
