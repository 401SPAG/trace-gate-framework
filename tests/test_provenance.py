import copy
import hashlib
import json
from pathlib import Path

import jsonschema
import pytest

from trace_gate.provenance import (SCHEMA, RELATIONS, context_receipt, digest,
                                   impacted_entities, validate_bundle, verify_locator)
from trace_gate.provenance_adapters import (bounded_neighbors, croissant_package,
                                           docling_projection, openlineage_events,
                                           prov_projection)

ROOT = Path(__file__).resolve().parents[1]
RAW = b"Example table\nEmployment level, thousands\n100\n"


@pytest.fixture
def bundle():
    return json.loads((ROOT / "examples/provenance-bundle.json").read_text())


def test_schema_and_fixture(bundle):
    jsonschema.Draft202012Validator.check_schema(json.loads(SCHEMA.read_text()))
    result = validate_bundle(bundle)
    assert result["status"] == "STRUCTURAL_PASS"
    assert not result["semantic_truth_verified"] and not result["access_granted"]
    assert RELATIONS["derived_from"] == "result_to_source"


@pytest.mark.parametrize("mutate,code", [
    (lambda b: b["entities"].append(copy.deepcopy(b["entities"][0])), "DUPLICATE_ID"),
    (lambda b: b["entities"][1]["locator"].update(source_sha256="a"*64), "LOCATOR_SOURCE_BINDING"),
    (lambda b: b["entities"][1].update(tenant_id="other"), "LOCATOR_ACCESS_BOUNDARY"),
    (lambda b: b["entities"][1].update(sensitivity="restricted"), "LOCATOR_ACCESS_BOUNDARY"),
    (lambda b: b["entities"][1]["locator"]["selector"].update(end=0), "TEXT_SPAN"),
    (lambda b: b["relations"][0].update(to="UNKNOWN"), "RELATION_ENDPOINT"),
    (lambda b: b["relations"][0].update(to="BLOCK.1"), "RELATION_ENDPOINT"),
    (lambda b: b["relations"][0].update(**{"from":"SRC.1","to":"BLOCK.1"}), "PARENT_DIRECTION"),
    (lambda b: b["relations"][3].update(status="reviewed", review_ref="UNTRUSTED"), "TRUSTED_REVIEW_REQUIRED"),
    (lambda b: b["relations"][3].update(**{"from":"CLAIM.1","to":"CHUNK.1"}), "EVIDENCE_DIRECTION"),
    (lambda b: b["runs"][0].update(ended_at="2025-01-01T00:00:00Z"), "RUN_TIME_ORDER"),
    (lambda b: b["runs"][0].update(agents=["UNKNOWN"]), "RUN_REFERENCE"),
    (lambda b: b["runs"][0].update(outputs=["SRC.1"]), "GENERATION_IDENTITY"),
    (lambda b: b["runs"][0].update(status="FAIL"), "FAILED_OUTPUT_PROMOTION"),
    (lambda b: b["entities"][0].update(observed_at="2026-01-01T00:00:00+09:00"), "UTC_REQUIRED"),
])
def test_bundle_negative(bundle, mutate, code):
    mutate(bundle)
    with pytest.raises(ValueError, match=code):
        validate_bundle(bundle)


def test_additional_fields_forbidden(bundle):
    bundle["approval"] = "self-issued"
    with pytest.raises(jsonschema.ValidationError):
        validate_bundle(bundle)


def test_review_exact_binding(bundle):
    relation = bundle["relations"][3]
    relation.update(status="reviewed", review_ref="REV.1")
    evidence, claim = bundle["entities"][2:]
    review = {"from": evidence["id"], "to": claim["id"], "type": "supports",
              "from_sha256": evidence["sha256"], "to_sha256": claim["sha256"], "scope": relation["scope"]}
    validate_bundle(bundle, trusted_reviews={"REV.1": review})
    review["to_sha256"] = "a"*64
    with pytest.raises(ValueError, match="TRUSTED_REVIEW_REQUIRED"):
        validate_bundle(bundle, trusted_reviews={"REV.1": review})


def test_cycle_rejected(bundle):
    bundle["relations"].append({"from":"SRC.1","to":"CHUNK.1","type":"derived_from","status":"structural","review_ref":None,"scope":"cycle"})
    with pytest.raises(ValueError, match="LINEAGE_CYCLE"):
        validate_bundle(bundle)


def test_source_content_binding(bundle):
    source, block = bundle["entities"][:2]
    assert verify_locator(block, source, RAW)["verified"]
    with pytest.raises(ValueError, match="SOURCE_BYTES_CHANGED"):
        verify_locator(block, source, RAW + b"x")
    block["sha256"] = "b"*64
    with pytest.raises(ValueError, match="LOCATOR_CONTENT_MISMATCH"):
        verify_locator(block, source, RAW)


def test_json_pointer_exact_and_unicode(bundle):
    source, item = bundle["entities"][:2]
    raw='{"시계열":[{"a/b":123}]}'.encode()
    source.update(sha256=hashlib.sha256(raw).hexdigest(),size_bytes=len(raw))
    item.update(sha256=hashlib.sha256(b"123").hexdigest())
    item["locator"]={"source_id":source["id"],"source_sha256":source["sha256"],"selector":{"type":"json","pointer":"/시계열/0/a~1b"}}
    assert verify_locator(item, source, raw)["verified"]


def test_context_subsets_budget_and_time(bundle):
    args=dict(candidate_ids=["CHUNK.1"],selected_ids=["CHUNK.1"],cited_ids=["CHUNK.1"],admitted_ids={"CHUNK.1"},cutoff="2026-01-01T00:01:00Z",max_bytes=1000,query_sha256="c"*64)
    result=context_receipt(bundle,**args)
    assert result["selected_bytes"]==len(RAW) and not result["citations_prove_support"]
    for key,value,code in [("admitted_ids",set(),"CONTEXT_ADMISSION"),("max_bytes",1,"CONTEXT_BUDGET"),("cited_ids",["SRC.1"],"CONTEXT_SUBSET"),("cutoff","2025-01-01T00:00:00Z","FUTURE_EVIDENCE")]:
        with pytest.raises((ValueError,PermissionError),match=code):
            context_receipt(bundle,**dict(args,**{key:value}))


def test_impact_is_projection(bundle):
    before=digest(bundle)
    assert impacted_entities(bundle,{"SRC.1"})==["BLOCK.1","CHUNK.1","CLAIM.1"]
    assert digest(bundle)==before


def test_graph_admission_and_bounding(bundle):
    assert bounded_neighbors(bundle,["CHUNK.1"],admitted_ids={"CHUNK.1"},limit=4)==["CHUNK.1"]
    assert len(bounded_neighbors(bundle,["CHUNK.1"],admitted_ids={"CHUNK.1","BLOCK.1"},limit=2))==2
    with pytest.raises(PermissionError):
        bounded_neighbors(bundle,["CHUNK.1"],admitted_ids=set(),limit=3)


def test_openlineage_identity_and_failure(bundle):
    events=openlineage_events(bundle,namespace="example")
    assert [e["eventType"] for e in events]==["START","COMPLETE"]
    assert events[0]["run"]==events[1]["run"]
    assert openlineage_events(bundle,namespace="other")[0]["run"]!=events[0]["run"]
    bundle["runs"][0].update(status="FAIL",outputs=[])
    assert openlineage_events(bundle,namespace="example")[1]["eventType"]=="FAIL"
    assert "prompt" not in json.dumps(events)


def test_prov_mapping_keeps_semantics_separate(bundle):
    graph=prov_projection(bundle)["@graph"]
    assert any("prov:wasDerivedFrom" in x for x in graph)
    assert any(x.get("trace:relationType")=="supports" and x["trace:status"]=="candidate" for x in graph)
    assert any("prov:wasAssociatedWith" in x for x in graph)


def test_dataset_rights_and_family_leakage():
    rows=[dict(record_id="r1",source_family="doc1",source_revision="1",source_sha256="a"*64,split="test",label="unreviewed",review_ref="PENDING",rights_ref="EXAMPLE")]
    args=dict(dataset_id="example",license_url="https://creativecommons.org/licenses/by/4.0/",purpose="evaluation",approved_uses={"evaluation"})
    result=croissant_package(rows,**args)
    assert result["descriptor"]["@context"]["recordSet"]=="cr:recordSet"
    assert result["descriptor"]["@context"]["@language"]=="en"
    assert all(f["source"]["extract"]=={"column":f["name"]} for f in result["descriptor"]["recordSet"][0]["field"])
    assert not result["receipt"]["training_started"]
    with pytest.raises(PermissionError):croissant_package(rows,**dict(args,purpose="training"))
    with pytest.raises(ValueError,match="DATASET_FAMILY_SPLIT_LEAKAGE"):
        croissant_package(rows+[dict(rows[0],record_id="r2",split="train")],**args)


def docling_doc():
    return dict(schema_name="DoclingDocument",version="1.10.0",body={"children":[{"$ref":"#/texts/0"}]},groups=[],texts=[{"self_ref":"#/texts/0","text":"example","parent":{"$ref":"#/body"},"prov":[{"page_no":1,"bbox":{"l":1,"t":10,"r":100,"b":20,"coord_origin":"TOPLEFT"}}]}],tables=[],pages={"1":{"size":{"width":600,"height":800}}})


def test_docling_adapter_not_a_parser_or_visual_certification(bundle):
    result=docling_projection(docling_doc(),bundle["entities"][0],parser_version="fixture-only")
    assert result["adapter_receipt"]["missing_geometry"]==0
    assert not result["adapter_receipt"]["visual_accuracy_verified"]
    assert result["adapter_receipt"]["confidence"] is None
    assert verify_locator(result["bundle"]["entities"][1],bundle["entities"][0],RAW)["status"]=="VISUAL_OR_TABLE_CHECK_REQUIRED"


@pytest.mark.parametrize("change,code",[
    (lambda d:d["body"].update(children=[{"cref":"#/texts/0"}]),"DOCLING_PUBLIC_EXPORT_REQUIRED"),
    (lambda d:d.update(version="3.0.0"),"DOCLING_VERSION_UNSUPPORTED"),
    (lambda d:d["texts"][0]["prov"][0]["bbox"].update(r=700),"PDF_BOUNDS"),
    (lambda d:d["body"].update(children=[]),"DOCLING_INCOMPLETE_BODY_COVERAGE"),
    (lambda d:d.update(pages={}),"DOCLING_PAGE_MISSING"),
    (lambda d:d["texts"][0]["prov"].append(copy.deepcopy(d["texts"][0]["prov"][0])),"DOCLING_MULTIPLE_LOCATORS_UNSUPPORTED"),
])
def test_docling_negative(bundle,change,code):
    d=docling_doc();change(d)
    with pytest.raises(ValueError,match=code):docling_projection(d,bundle["entities"][0],parser_version="fixture-only")


def test_docling_group_hierarchy(bundle):
    d=docling_doc()
    d["groups"]=[{"self_ref":"#/groups/0","parent":{"$ref":"#/body"},"children":[{"$ref":"#/texts/0"}]}]
    d["body"]["children"]=[{"$ref":"#/groups/0"}]
    d["texts"][0]["parent"]={"$ref":"#/groups/0"}
    result=docling_projection(d,bundle["entities"][0],parser_version="fixture-only")
    assert [e["kind"] for e in result["bundle"]["entities"]]==["source","section","block"]
    assert result["bundle"]["relations"][1]["to"].startswith("DOCGROUP.")


def test_docling_group_below_text_and_sibling_order(bundle):
    d=docling_doc()
    parent=d["texts"][0]
    child=copy.deepcopy(parent);child.update(self_ref="#/texts/1",parent={"$ref":"#/groups/0"},children=[])
    parent["children"]=[{"$ref":"#/groups/0"}]
    d["texts"].append(child)
    d["groups"]=[{"self_ref":"#/groups/0","parent":{"$ref":"#/texts/0"},"children":[{"$ref":"#/texts/1"}]}]
    result=docling_projection(d,bundle["entities"][0],parser_version="fixture-only")
    assert [e["kind"] for e in result["bundle"]["entities"]]==["source","block","section","block"]
    assert all(e["type"]=="part_of" for e in result["bundle"]["relations"])
    d["groups"][0]["parent"]={"$ref":"#/body"}
    with pytest.raises(ValueError,match="DOCLING_PARENT_MISMATCH"):
        docling_projection(d,bundle["entities"][0],parser_version="fixture-only")


def test_pilot_on_existing_files_and_exclusive_run(tmp_path):
    import subprocess,sys
    state_root=tmp_path/"existing";blobs=state_root/"blobs";blobs.mkdir(parents=True)
    artifacts=[]
    for i in range(3):
        raw=("<html><body><p>"+"Synthetic Korean 한국어 paragraph "*4+"</p></body></html>").encode()
        h=hashlib.sha256(raw).hexdigest();path=blobs/(h+str(i));path.write_bytes(raw)
        artifacts.append(dict(source_id="source-"+str(i),location=str(path),media_type="text/html",bytes=len(raw),content_sha256=h,retrieved_at="2026-01-01T00:00:00Z"))
    state=state_root/"state.json";state.write_text(json.dumps(dict(artifacts=artifacts)))
    out=tmp_path/"pilot"
    command=[sys.executable,str(ROOT/"scripts/pilot_provenance.py"),"--state",str(state),"--output",str(out)]
    p=subprocess.run(command,capture_output=True,text=True)
    assert p.returncode==0,p.stderr+p.stdout
    receipt=json.loads(p.stdout)
    assert receipt["source_count"]==3 and receipt["exact_locator_checks"]==3
    assert receipt["original_sources_unchanged"] and receipt["model_calls"]==0
    prior=(out/"receipt.json").read_bytes()
    assert subprocess.run(command,capture_output=True).returncode!=0
    assert (out/"receipt.json").read_bytes()==prior


def test_offline_cli_and_error_redaction(tmp_path, bundle):
    import subprocess,sys
    p=tmp_path/"input.json"
    command=[sys.executable,str(ROOT/"scripts/validate_provenance.py"),str(p)]
    p.write_text(json.dumps(bundle))
    ok=subprocess.run(command,capture_output=True,text=True)
    assert ok.returncode==0 and json.loads(ok.stdout)["status"]=="STRUCTURAL_PASS"
    bundle["secret-like-unexpected-field"]="MUST_NOT_ECHO"
    p.write_text(json.dumps(bundle))
    fail=subprocess.run(command,capture_output=True,text=True)
    assert fail.returncode==2 and "MUST_NOT_ECHO" not in fail.stdout+fail.stderr
