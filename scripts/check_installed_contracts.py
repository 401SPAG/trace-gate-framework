"""Smoke test an installed distribution from outside its source checkout."""
import json
from importlib.metadata import distribution
from pathlib import Path
import subprocess
import sysconfig

import trace_gate
from trace_gate.provenance import validate_bundle
from trace_gate.resources import resource_root


def main():
    package = distribution("trace-gate-framework")
    resources = resource_root()
    source = Path(__file__).resolve().parents[1]
    assert resources.is_relative_to(Path(sysconfig.get_path("purelib")))
    assert trace_gate.__version__ == package.version

    for directory in ("schemas", "templates", "docs", "examples"):
        for path in (source / directory).rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts:
                assert (resources / path.relative_to(source)).read_bytes() == path.read_bytes(), path
    for notice in package.metadata.get_all("License-File"):
        assert (resources / notice).read_bytes() == (source / notice).read_bytes(), notice
    subprocess.run(["trace-gate-validate"], check=True)
    subprocess.run(["trace-gate-evaluate", resources / "templates/gate-decision.yaml",
                    resources / "examples/gate-facts.yaml"], check=True)
    bundle = json.loads((resources / "examples/provenance-bundle.json").read_text())
    receipt = validate_bundle(bundle)
    assert receipt["status"] == "STRUCTURAL_PASS" and not receipt["access_granted"]


if __name__ == "__main__":
    main()
