"""Pure opt-in adapters. No network, parser models, database writes or publishing."""
from __future__ import annotations

import copy
import hashlib
import json
import re
import uuid

from .provenance import RELATIONS, digest, validate_bundle


def docling_projection(document: dict, source: dict, *, parser_version: str) -> dict:
    """Import explicit Docling block geometry, never invent a confidence or bbox.

    Input origin must already be authenticated by the converter adapter. The
    document digest is recorded, not taken as proof it was parsed from source.
    This function imports text/table blocks; cell text and geometry stay in the
    converter's original JSON. Cell accuracy still requires visual comparison.
    """
    # Library 2.x and document schema versions are different version domains.
    if document.get("schema_name") != "DoclingDocument" or document.get("version") != "1.10.0":
        raise ValueError("DOCLING_VERSION_UNSUPPORTED")
    if not parser_version or source.get("kind") != "source":
        raise ValueError("DOCLING_SOURCE_REQUIRED")
    group_list = document.get("groups", [])
    items = document.get("texts", []) + document.get("tables", []) + document.get("pictures", [])
    nodes = group_list + items
    if len(nodes) > 500:
        raise ValueError("DOCLING_ITEM_BUDGET")
    if len({x["self_ref"] for x in nodes}) != len(nodes):
        raise ValueError("DOCLING_DUPLICATE_REF")
    groups = {x["self_ref"]: x for x in group_list}
    by_ref = {x["self_ref"]: x for x in nodes}
    ordered, visited, parent_refs = [], set(), {}
    def walk(node, parent_ref):
        for ref in node.get("children", []):
            if not isinstance(ref, dict) or set(ref) != {"$ref"} or not isinstance(ref["$ref"], str):
                raise ValueError("DOCLING_PUBLIC_EXPORT_REQUIRED")
            key = ref["$ref"]
            if key in visited:
                raise ValueError("DOCLING_TREE_CYCLE_OR_DUPLICATE")
            if key not in by_ref:
                raise ValueError("DOCLING_UNSUPPORTED_CHILD")
            if by_ref[key].get("parent") != {"$ref": parent_ref}:
                raise ValueError("DOCLING_PARENT_MISMATCH")
            visited.add(key); ordered.append(key); parent_refs[key] = parent_ref
            walk(by_ref[key], key)
    # Body and furniture are separate reading-order roots, not one sequence.
    walk(document.get("body", {}), "#/body")
    walk(document.get("furniture", {}), "#/furniture")
    if set(ordered) != set(by_ref):
        raise ValueError("DOCLING_INCOMPLETE_BODY_COVERAGE")
    mapping = {key: ("DOCGROUP." if key in groups else "DOCITEM.") +
               digest([source["id"], document["version"], key, by_ref[key]])[:32]
               for key in ordered}
    entities, relations, siblings, ordinals = [copy.deepcopy(source)], [], {}, {}
    missing = 0
    for key in ordered:
        item, eid = by_ref[key], mapping[key]
        payload = item if key in groups else item.get("text", item.get("data", item))
        content = payload.encode() if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        loc = None
        prov = item.get("prov", [])
        if len(prov) > 1:
            raise ValueError("DOCLING_MULTIPLE_LOCATORS_UNSUPPORTED")
        if prov:
            p = prov[0]
            page = document.get("pages", {}).get(str(p["page_no"]))
            if page is None:
                raise ValueError("DOCLING_PAGE_MISSING")
            box = p["bbox"]
            origin = box.get("coord_origin")
            if origin not in {"TOPLEFT", "BOTTOMLEFT"}:
                raise ValueError("DOCLING_COORD_ORIGIN")
            loc = {"source_id": source["id"], "source_sha256": source["sha256"],
                   "selector": {"type": "pdf", "page_no": p["page_no"],
                                "bbox": [box["l"], min(box["t"], box["b"]), box["r"], max(box["t"], box["b"])],
                                "page_width": page["size"]["width"], "page_height": page["size"]["height"], "origin": origin}}
        elif key not in groups:
            missing += 1
        parent_ref = parent_refs[key]
        parent_id = source["id"] if parent_ref in {"#/body", "#/furniture"} else mapping[parent_ref]
        # Include groups in sibling positions; don't skip their children when
        # assigning document reading order, or join body to furniture implicitly.
        ordinal = ordinals.get(parent_id, -1) + 1
        ordinals[parent_id] = ordinal
        previous = siblings.get(parent_ref)
        entity = dict(source, id=eid, artifact_id=eid, revision=1,
                      kind="section" if key in groups else "table" if key.startswith("#/tables/") else "block",
                      sha256=hashlib.sha256(content).hexdigest(), size_bytes=len(content),
                      media_type="application/json" if not isinstance(payload, str) else "text/plain",
                      locator=loc, ordinal=ordinal)
        entities.append(entity)
        relations.append({"from": eid, "to": parent_id, "type": "part_of", "status": "structural", "review_ref": None,
                          "scope": "Docling explicit item parent"})
        if previous:
            relations.append({"from": previous, "to": eid, "type": "next", "status": "structural", "review_ref": None, "scope": "Docling explicit sibling reading order"})
        siblings[parent_ref] = eid
    bundle = dict(schema_version="0.1.0", profile_id="TRACE.DOCLING.OPTIN", entities=entities, relations=relations, agents=[], runs=[])
    validate_bundle(bundle)
    return {"bundle": bundle, "adapter_receipt": {"parser_version": parser_version,
            "document_version": document["version"], "document_sha256": digest(document),
            "source_sha256": source["sha256"], "ref_map": mapping,
            "parent_refs": {k: by_ref[k].get("parent") for k in ordered},
            "content_layers": {k: by_ref[k].get("content_layer") for k in ordered},
            "groups": {k: {"parent": v.get("parent"), "children": v.get("children", [])} for k, v in groups.items()},
            "missing_geometry": missing, "visual_accuracy_verified": False,
            "source_conversion_binding_verified": False, "confidence": None}}


def prov_projection(bundle: dict, *, trusted_reviews: dict | None = None) -> dict:
    validate_bundle(bundle, trusted_reviews=trusted_reviews)
    uri = lambda kind, identity: "urn:trace:" + kind + ":" + digest([bundle["profile_id"], identity])
    graph = []
    for e in bundle["entities"]:
        graph.append({"@id": uri("entity", e["id"]), "@type": "prov:Entity",
                      "trace:identity": e["id"], "trace:revision": e["revision"], "trace:sha256": e["sha256"],
                      "trace:artifactId": e["artifact_id"], "trace:tenantId": e["tenant_id"],
                      "trace:sensitivity": e["sensitivity"], "trace:observedAt": e["observed_at"]})
    for a in bundle["agents"]:
        graph.append({"@id": uri("agent", a["id"]), "@type": {"software": "prov:SoftwareAgent", "person": "prov:Person", "organization": "prov:Organization"}[a["kind"]],
                      "trace:identity": a["id"], "trace:version": a["version"]})
    for run in bundle["runs"]:
        graph.append({"@id": uri("activity", run["id"]), "@type": "prov:Activity",
                      "trace:identity": run["id"], "trace:jobId": run["job_id"], "trace:stage": run["stage"],
                      "trace:codeSha256": run["code_sha256"], "trace:parametersSha256": run["parameters_sha256"],
                      "prov:used": [{"@id": uri("entity", i)} for i in run["inputs"]],
                      "prov:wasAssociatedWith": [{"@id": uri("agent", i)} for i in run["agents"]],
                      "trace:status": run["status"], "prov:startedAtTime": run["started_at"], "prov:endedAtTime": run["ended_at"]})
        for out in run["outputs"]:
            graph.append({"@id": uri("entity", out), "prov:wasGeneratedBy": {"@id": uri("activity", run["id"])}})
    for relation in bundle["relations"]:
        # Supersession/approval/semantic support are NOT automatically PROV revision/derivation.
        if relation["type"] == "derived_from":
            graph.append({"@id": uri("entity", relation["from"]), "prov:wasDerivedFrom": {"@id": uri("entity", relation["to"])}})
        # Also retain qualification metadata for derived_from; native PROV alone
        # cannot retain TRACE scope/status/review semantics.
        graph.append({"@id": uri("relation", digest(relation)), "@type": "trace:Relation",
                          "trace:from": {"@id": uri("entity", relation["from"])},
                          "trace:to": {"@id": uri("entity", relation["to"])},
                          "trace:relationType": relation["type"], "trace:status": relation["status"],
                          "trace:reviewRef": relation["review_ref"], "trace:scope": relation["scope"]})
    return {"@context": {"prov": "http://www.w3.org/ns/prov#", "trace": "urn:trace:vocab:"},
            "trace:bundleSha256": digest(bundle), "@graph": graph}


def openlineage_events(bundle: dict, *, namespace: str, trusted_reviews: dict | None = None) -> list[dict]:
    validate_bundle(bundle, trusted_reviews=trusted_reviews)
    if not re.fullmatch(r"[A-Za-z0-9._:-]{1,128}", namespace):
        raise ValueError("NAMESPACE_INVALID")
    entities = {e["id"]: e for e in bundle["entities"]}
    def datasets(ids):
        return [{"namespace": namespace, "name": i,
                 "facets": {"trace_identity": {"_producer": "https://github.com/401SPAG/trace-gate-framework",
                    "_schemaURL": "urn:trace:openlineage:identity:0.1.0",
                    "revision": entities[i]["revision"], "sha256": entities[i]["sha256"]}}} for i in ids]
    events = []
    for run in bundle["runs"]:
        rid = str(uuid.uuid5(uuid.NAMESPACE_URL, namespace + "/" + run["id"]))
        for state, timestamp, outputs in [("START", run["started_at"], []), (run["status"], run["ended_at"], run["outputs"])]:
            events.append({"eventType": state, "eventTime": timestamp,
                           "run": {"runId": rid, "facets": {"trace_execution": {
                               "_producer": "https://github.com/401SPAG/trace-gate-framework",
                               "_schemaURL": "urn:trace:openlineage:execution:0.1.0",
                               "originalRunId": run["id"], "stage": run["stage"],
                               "codeSha256": run["code_sha256"], "parametersSha256": run["parameters_sha256"],
                               "agentIds": run["agents"], "bundleSha256": digest(bundle)}}},
                           "job": {"namespace": namespace, "name": run["job_id"]},
                           "inputs": datasets(run["inputs"]), "outputs": datasets(outputs),
                           "producer": "https://github.com/401SPAG/trace-gate-framework",
                           "schemaURL": "https://openlineage.io/spec/2-0-2/OpenLineage.json"})
    return events


def provenance_exchange_package(bundle: dict, *, format: str, namespace: str = "trace",
                                trusted_reviews: dict | None = None) -> dict:
    """Lossless local envelope. Admission and transport authorization are external.

    The canonical sidecar contains tenant/locator metadata omitted by generic
    projections and must inherit its source's access policy. No network I/O.
    """
    if format not in {"prov", "openlineage"}:
        raise ValueError("EXCHANGE_FORMAT")
    validate_bundle(bundle, trusted_reviews=trusted_reviews)
    if format == "prov":
        namespace = "trace"
        projection = prov_projection(bundle, trusted_reviews=trusted_reviews)
    else:
        projection = openlineage_events(bundle, namespace=namespace, trusted_reviews=trusted_reviews)
    return {"schema_version": "trace-provenance-exchange/1", "format": format,
            "namespace": namespace, "canonical_bundle": copy.deepcopy(bundle),
            "canonical_sha256": digest(bundle), "projection": projection,
            "projection_sha256": digest(projection)}


def restore_provenance_exchange(package: dict, *, trusted_reviews: dict | None = None) -> dict:
    """Verify bytes/semantics, not authenticity, and return the canonical sidecar.

    A hash does not authenticate a sender. Independently trusted review bindings
    are required again; the envelope never supplies its own approval authority.
    """
    if set(package) != {"schema_version", "format", "namespace", "canonical_bundle",
                        "canonical_sha256", "projection", "projection_sha256"} or package["schema_version"] != "trace-provenance-exchange/1":
        raise ValueError("EXCHANGE_SCHEMA")
    if digest(package["canonical_bundle"]) != package["canonical_sha256"] or digest(package["projection"]) != package["projection_sha256"]:
        raise ValueError("EXCHANGE_HASH_MISMATCH")
    expected = provenance_exchange_package(package["canonical_bundle"], format=package["format"],
                                          namespace=package["namespace"], trusted_reviews=trusted_reviews)
    if expected != package:
        raise ValueError("EXCHANGE_PROJECTION_MISMATCH")
    return copy.deepcopy(package["canonical_bundle"])


def croissant_package(records: list[dict], *, dataset_id: str, license_url: str,
                      purpose: str, approved_uses: set[str]) -> dict:
    """Local descriptor + JSONL; no training permission inferred from a license."""
    if purpose not in approved_uses or not re.fullmatch(r"[A-Za-z0-9._-]{1,100}", dataset_id):
        raise PermissionError("DATASET_USE_NOT_ADMITTED")
    if not license_url.startswith("https://") or not records or len(records) > 10000:
        raise ValueError("DATASET_METADATA")
    fields = {"record_id", "source_family", "source_revision", "source_sha256", "split", "label", "review_ref", "rights_ref"}
    ids, families = set(), {}
    for record in records:
        if set(record) != fields or any(not isinstance(v, str) or not v for v in record.values()):
            raise ValueError("DATASET_RECORD_SCHEMA")
        if record["record_id"] in ids or not re.fullmatch("[a-f0-9]{64}", record["source_sha256"]):
            raise ValueError("DATASET_IDENTITY")
        if record["split"] not in {"train", "validation", "test", "retrieval", "unassigned"}:
            raise ValueError("DATASET_SPLIT")
        ids.add(record["record_id"])
        family = record["source_family"]
        if family in families and families[family] != record["split"]:
            raise ValueError("DATASET_FAMILY_SPLIT_LEAKAGE")
        families[family] = record["split"]
    jsonl = "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records)
    # Inline the 1.0 namespace mappings: no remote JSON-LD context fetch is needed.
    context = {name: "cr:" + name for name in (
        "citeAs column equivalentProperty extract field fileProperty fileObject fileSet format "
        "includes isLiveDataset jsonPath key md5 parentField path recordSet references regex "
        "repeated replace samplingRate separator source subField transform").split()}
    context.update({"@language": "en", "@vocab": "https://schema.org/", "sc": "https://schema.org/",
                    "cr": "http://mlcommons.org/croissant/", "rai": "http://mlcommons.org/croissant/RAI/",
                    "dct": "http://purl.org/dc/terms/", "conformsTo": "dct:conformsTo",
                    "data": {"@id": "cr:data", "@type": "@json"},
                    "examples": {"@id": "cr:examples", "@type": "@json"},
                    "dataType": {"@id": "cr:dataType", "@type": "@vocab"}})
    description = {
        "@context": context,
        "@type": "Dataset", "@id": dataset_id, "name": dataset_id,
        "description": "TRACE metadata records only; rights and reviews remain independent receipts.",
        "conformsTo": "http://mlcommons.org/croissant/1.0", "license": license_url,
        "distribution": [{"@type": "cr:FileObject", "@id": "records", "name": "records",
                          "contentUrl": "records.jsonl", "encodingFormat": "application/jsonlines",
                          "sha256": hashlib.sha256(jsonl.encode()).hexdigest()}],
        "recordSet": [{"@type": "cr:RecordSet", "@id": "recordset", "name": "recordset",
                       "field": [{"@type": "cr:Field", "@id": "recordset/" + f, "name": f,
                                  "dataType": "https://schema.org/Text",
                                  "source": {"fileObject": {"@id": "records"}, "extract": {"column": f}}} for f in sorted(fields)]}]}
    return {"descriptor": description, "records_jsonl": jsonl,
            "receipt": {"record_count": len(records), "purpose": purpose,
                        "descriptor_sha256": digest(description), "training_started": False,
                        "gold_promoted": False, "license_verified_by_exporter": False}}


def bounded_neighbors(bundle: dict, seeds: list[str], *, admitted_ids: set[str], limit: int,
                      trusted_reviews: dict | None = None) -> list[str]:
    """Deterministic lexical context expansion; not vector or semantic ranking."""
    validate_bundle(bundle, trusted_reviews=trusted_reviews)
    if type(limit) is not int or not 0 < limit <= 100 or len(set(seeds)) > limit:
        raise ValueError("GRAPH_BUDGET")
    known = {e["id"] for e in bundle["entities"]}
    if not set(seeds) <= known or not set(seeds) <= admitted_ids:
        raise PermissionError("GRAPH_ADMISSION")
    result = list(dict.fromkeys(seeds))
    for node in list(result):
        for edge in bundle["relations"]:
            if edge["type"] not in {"part_of", "next"}:
                continue
            other = edge["to"] if edge["from"] == node else edge["from"] if edge["to"] == node else None
            if other and other in admitted_ids and other not in result and len(result) < limit:
                result.append(other)
    return result
