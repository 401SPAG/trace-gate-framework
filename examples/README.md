# Reference examples

**English** | [한국어](README.ko.md) · [Repository home](../README.md)

Run these commands from the repository root after completing the README's virtual-environment installation.

## Evaluate a Gate

```bash
.venv/bin/python scripts/evaluate_gate.py \
  templates/gate-decision.yaml examples/gate-facts.yaml
```

The evaluator computes a result and receipt from the policy and synthetic facts. A `pass` result is not operational approval. Evidence references must be authenticated by a trusted resolver in a deployment.

## Run a deterministic agent example

```bash
.venv/bin/python examples/runtime_demo.py
```

The example uses local fixture adapters for the model, tool and verifier. It does not call a live model or perform remote mutations. Inspect the printed result as an illustration of the runtime contract, not a production authorization receipt.

Before connecting a real tool, provide a verified Request Receipt, scoped Tool Definition, approval resolver, effect observations, and an appropriate executor. Review [adapter requirements and limitations](../docs/REFERENCE-IMPLEMENTATION.en.md). Keep unresolved effects blocked; a timeout or a stored checkpoint is not evidence that replay is safe.

Software examples follow [LICENSE-CODE](../LICENSE-CODE); surrounding explanatory text follows the [documentation terms](../LICENSING.en.md).
