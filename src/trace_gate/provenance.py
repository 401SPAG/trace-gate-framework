"""Opt-in, content-free document/run provenance. No I/O or authority issuance.

Schema validation is structural evidence, not semantic truth or authorization.
The host supplies admitted identities and independently verified reviews.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from .resources import resource_root

SCHEMA = resource_root() / "schemas/provenance.schema.json"
RELATIONS = {
    "part_of": "child_to_parent",
    "next": "preceding_to_following",
    "derived_from": "result_to_source",
    "supersedes": "new_revision_to_previous",
    "references": "referrer_to_referent",
    "mentions": "text_to_concept",
    "supports": "evidence_to_claim",
    "refutes": "evidence_to_claim",
    "limits": "evidence_to_claim",
}


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise ValueError("UTC_REQUIRED")
    return parsed


def _acyclic(pairs: list[tuple[str, str]], code: str) -> None:
    graph: dict[str, list[str]] = {}
    for left, right in pairs:
        graph.setdefault(left, []).append(right)
    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(node: str) -> None:
        if node in visiting:
            raise ValueError(code)
        if node in visited:
            return
        visiting.add(node)
        for child in graph.get(node, []):
            visit(child)
        visiting.remove(node)
        visited.add(node)
    for node in graph:
        visit(node)


def validate_bundle(bundle: dict, *, trusted_reviews: dict | None = None) -> dict:
    """Check exact references/direction/versions; never grant access or truth."""
    import jsonschema
    jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text())).validate(bundle)
    trusted_reviews = trusted_reviews or {}
    entities = {x["id"]: x for x in bundle["entities"]}
    agents = {x["id"]: x for x in bundle["agents"]}
    runs = {x["id"]: x for x in bundle["runs"]}
    if any(len(index) != len(bundle[name]) for name, index in
           [("entities", entities), ("agents", agents), ("runs", runs)]):
        raise ValueError("DUPLICATE_ID")
    identities = {(e["tenant_id"], e["artifact_id"], e["revision"]) for e in entities.values()}
    if len(identities) != len(entities):
        raise ValueError("DUPLICATE_REVISION")
    for entity in entities.values():
        utc(entity["observed_at"])
        loc = entity["locator"]
        if loc is None:
            continue
        source = entities.get(loc["source_id"])
        if not source or source["kind"] != "source" or source["sha256"] != loc["source_sha256"]:
            raise ValueError("LOCATOR_SOURCE_BINDING")
        if entity["tenant_id"] != source["tenant_id"] or entity["sensitivity"] != source["sensitivity"]:
            raise ValueError("LOCATOR_ACCESS_BOUNDARY")
        selector = loc["selector"]
        if selector["type"] == "text":
            if selector["end"] <= selector["start"]:
                raise ValueError("TEXT_SPAN")
        elif selector["type"] == "pdf":
            x0, y0, x1, y1 = selector["bbox"]
            if not (all(math.isfinite(v) for v in selector["bbox"]) and
                    0 <= x0 < x1 <= selector["page_width"] and
                    0 <= y0 < y1 <= selector["page_height"]):
                raise ValueError("PDF_BOUNDS")
        elif selector["type"] == "json":
            if re.search(r"~(?![01])", selector["pointer"]):
                raise ValueError("JSON_POINTER_ESCAPE")
    parent: dict[str, str] = {}
    edges = set()
    acyclic: list[tuple[str, str]] = []
    for relation in bundle["relations"]:
        left, right, kind = relation["from"], relation["to"], relation["type"]
        key = (left, right, kind)
        if key in edges or left == right or left not in entities or right not in entities:
            raise ValueError("RELATION_ENDPOINT")
        edges.add(key)
        a, b = entities[left], entities[right]
        if a["tenant_id"] != b["tenant_id"]:
            raise ValueError("RELATION_TENANT")
        if kind in {"part_of", "derived_from", "supersedes"}:
            acyclic.append((left, right))
        if kind == "part_of":
            if left in parent or a["kind"] == "source" or b["kind"] not in {"source", "parsed_document", "section", "table", "block"}:
                raise ValueError("PARENT_DIRECTION")
            parent[left] = right
        if kind == "supersedes" and (a["artifact_id"] != b["artifact_id"] or a["revision"] <= b["revision"]):
            raise ValueError("REVISION_DIRECTION")
        if kind == "mentions" and (a["kind"] not in {"chunk", "block"} or b["kind"] != "concept"):
            raise ValueError("MENTION_DIRECTION")
        if kind in {"supports", "refutes", "limits"}:
            if b["kind"] != "claim" or relation["status"] not in {"candidate", "reviewed"}:
                raise ValueError("EVIDENCE_DIRECTION")
            if relation["status"] == "reviewed":
                expected = {"from": left, "to": right, "type": kind,
                            "from_sha256": a["sha256"], "to_sha256": b["sha256"],
                            "scope": relation["scope"]}
                if trusted_reviews.get(relation["review_ref"]) != expected:
                    raise ValueError("TRUSTED_REVIEW_REQUIRED")
            elif relation["review_ref"] is not None:
                raise ValueError("CANDIDATE_REVIEW_REF")
        elif relation["status"] != "structural" or relation["review_ref"] is not None:
            raise ValueError("STRUCTURAL_RELATION_STATE")
    _acyclic(acyclic, "LINEAGE_CYCLE")
    next_edges = []
    for left, right, kind in edges:
        if kind == "next":
            if left not in parent or parent.get(left) != parent.get(right):
                raise ValueError("NEXT_PARENT")
            if entities[left]["ordinal"] is None or entities[right]["ordinal"] != entities[left]["ordinal"] + 1:
                raise ValueError("NEXT_ORDER")
            next_edges.append((left, right))
    _acyclic(next_edges, "NEXT_CYCLE")
    generated: set[str] = set()
    for run in runs.values():
        if utc(run["ended_at"]) < utc(run["started_at"]):
            raise ValueError("RUN_TIME_ORDER")
        if not set(run["inputs"] + run["outputs"]) <= entities.keys() or not set(run["agents"]) <= agents.keys():
            raise ValueError("RUN_REFERENCE")
        if set(run["inputs"]) & set(run["outputs"]) or generated & set(run["outputs"]):
            raise ValueError("GENERATION_IDENTITY")
        if run["status"] != "COMPLETE" and run["outputs"]:
            raise ValueError("FAILED_OUTPUT_PROMOTION")
        if len({entities[i]["tenant_id"] for i in run["inputs"] + run["outputs"]}) > 1:
            raise ValueError("RUN_TENANT")
        generated.update(run["outputs"])
    return {"status": "STRUCTURAL_PASS", "bundle_sha256": digest(bundle),
            "entities": len(entities), "relations": len(edges), "runs": len(runs),
            "semantic_truth_verified": False, "access_granted": False}


def verify_locator(entity: dict, source: dict, raw: bytes) -> dict:
    """Text/JSON exact checks. PDF geometry needs independent visual validation."""
    if hashlib.sha256(raw).hexdigest() != source["sha256"] or len(raw) != source["size_bytes"]:
        raise ValueError("SOURCE_BYTES_CHANGED")
    loc = entity["locator"]
    if loc is None or loc["source_id"] != source["id"] or loc["source_sha256"] != source["sha256"]:
        raise ValueError("LOCATOR_SOURCE_BINDING")
    sel = loc["selector"]
    if sel["type"] == "text":
        text = raw.decode("utf-8")
        if not 0 <= sel["start"] < sel["end"] <= len(text):
            raise ValueError("TEXT_SPAN")
        content = text[sel["start"]:sel["end"]].encode()
    elif sel["type"] == "json":
        def unique(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError("JSON_DUPLICATE_KEY")
                result[key] = value
            return result
        value = json.loads(raw, object_pairs_hook=unique,
                           parse_constant=lambda _: (_ for _ in ()).throw(ValueError("JSON_NONFINITE")))
        for part in sel["pointer"].split("/")[1:] if sel["pointer"] else []:
            token = part.replace("~1", "/").replace("~0", "~")
            if isinstance(value, list):
                if not re.fullmatch(r"0|[1-9][0-9]*", token):
                    raise ValueError("JSON_ARRAY_INDEX")
                value = value[int(token)]
            else:
                value = value[token]
        content = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    else:
        return {"status": "VISUAL_OR_TABLE_CHECK_REQUIRED", "verified": False}
    if hashlib.sha256(content).hexdigest() != entity["sha256"]:
        raise ValueError("LOCATOR_CONTENT_MISMATCH")
    return {"status": "EXACT_CONTENT_PASS", "verified": True}


def context_receipt(bundle: dict, *, candidate_ids: list[str], selected_ids: list[str],
                    cited_ids: list[str], admitted_ids: set[str], cutoff: str,
                    max_bytes: int, query_sha256: str, index_sha256: str | None = None,
                    trusted_reviews: dict | None = None) -> dict:
    """Host MUST resolve admission with existing DM gates before calling this."""
    validate_bundle(bundle, trusted_reviews=trusted_reviews)
    index = {x["id"]: x for x in bundle["entities"]}
    if type(max_bytes) is not int or max_bytes < 1:
        raise ValueError("CONTEXT_BUDGET")
    if not re.fullmatch("[a-f0-9]{64}", query_sha256) or (index_sha256 is not None and not re.fullmatch("[a-f0-9]{64}", index_sha256)):
        raise ValueError("RETRIEVAL_IDENTITY")
    for ids in [candidate_ids, selected_ids, cited_ids]:
        if len(ids) != len(set(ids)) or not set(ids) <= index.keys():
            raise ValueError("CONTEXT_IDENTITY")
    if not set(selected_ids) <= set(candidate_ids) or not set(cited_ids) <= set(selected_ids):
        raise ValueError("CONTEXT_SUBSET")
    # Admission applies before exposing candidate identity, including graph expansion.
    if not set(candidate_ids) <= admitted_ids:
        raise PermissionError("CONTEXT_ADMISSION")
    if any(utc(index[i]["observed_at"]) > utc(cutoff) for i in candidate_ids):
        raise ValueError("FUTURE_EVIDENCE")
    size = sum(index[i]["size_bytes"] for i in selected_ids)
    if size > max_bytes:
        raise ValueError("CONTEXT_BUDGET")
    return {"schema": "trace-context-use/0.1", "bundle_sha256": digest(bundle),
            "candidate_ids": candidate_ids, "selected_ids": selected_ids, "cited_ids": cited_ids,
            "selected_bytes": size, "query_sha256": query_sha256, "index_sha256": index_sha256,
            "cutoff": cutoff, "citations_prove_support": False}


def impacted_entities(bundle: dict, changed_ids: set[str], *, trusted_reviews: dict | None = None) -> list[str]:
    """Review-needed candidates only; never mutate old decisions or revisions."""
    validate_bundle(bundle, trusted_reviews=trusted_reviews)
    if not changed_ids <= {e["id"] for e in bundle["entities"]}:
        raise ValueError("UNKNOWN_CHANGED_ID")
    affected = set(changed_ids)
    while True:
        previous = set(affected)
        for edge in bundle["relations"]:
            if edge["type"] in {"derived_from", "part_of"} and edge["to"] in affected:
                affected.add(edge["from"])
            elif edge["type"] in {"supports", "refutes", "limits"} and edge["from"] in affected:
                affected.add(edge["to"])
        if previous == affected:
            return sorted(affected - changed_ids)
