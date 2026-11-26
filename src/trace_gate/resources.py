"""Stable resource root for source checkouts and installed wheels."""
from pathlib import Path


def resource_root() -> Path:
    source = Path(__file__).resolve().parents[2]
    if (source / "pyproject.toml").is_file() and (source / "schemas/trace-gate.schema.json").is_file():
        return source
    packaged = Path(__file__).resolve().parent / "_resources"
    if not (packaged / "schemas/trace-gate.schema.json").is_file():
        raise FileNotFoundError("TRACE_CONTRACT_RESOURCES_MISSING")
    return packaged
