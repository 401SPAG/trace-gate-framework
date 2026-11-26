"""Copy repository contracts into the installable package at build time."""
from pathlib import Path
from shutil import copy2

from setuptools.command.build_py import build_py


class ContractBuild(build_py):
    def run(self):
        super().run()
        root = Path(__file__).resolve().parents[1]
        destination = Path(self.build_lib) / "trace_gate" / "_resources"
        patterns = (
            "*.md", "LICENSE", "LICENSE-CODE", "licenses/*.txt",
            "schemas/*.json", "schemas/*.sql", "templates/*.yaml", "templates/*.md",
            "docs/**/*.md", "docs/**/*.yaml", "docs/**/*.json",
            "examples/*.md", "examples/*.json", "examples/*.yaml", "examples/*.py",
        )
        for pattern in patterns:
            for source in root.glob(pattern):
                target = destination / source.relative_to(root)
                target.parent.mkdir(parents=True, exist_ok=True)
                copy2(source, target)
