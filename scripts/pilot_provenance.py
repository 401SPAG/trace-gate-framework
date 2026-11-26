#!/usr/bin/env python3
"""One-shot provenance pilot over existing, hash-bound local HTML sources.

No acquisition, inference, embeddings, database mutations, report publication,
or automatic retry. All source processing and generated files stay on the host.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from trace_gate.provenance import digest, validate_bundle, verify_locator, context_receipt
from trace_gate.provenance_adapters import bounded_neighbors, openlineage_events, prov_projection


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_source(path, base, limit):
    if not path.is_relative_to(base) or path.resolve() != path:
        raise ValueError("SOURCE_PATH_BOUNDARY")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        before = os.fstat(fd)
        if before.st_size > limit:
            raise ValueError("SOURCE_SIZE_BOUNDARY")
        raw = os.read(fd, limit + 1)
        after = os.fstat(fd)
        if len(raw) != before.st_size or (before.st_mtime_ns, before.st_size) != (after.st_mtime_ns, after.st_size):
            raise ValueError("SOURCE_CHANGED_DURING_READ")
        return raw
    finally:
        os.close(fd)


def run(state, out):
    os.umask(0o077)
    out.mkdir(mode=0o700, parents=False, exist_ok=False)
    def save(name, value):
        with (out/name).open("x", encoding="utf-8") as f:
            json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
            f.write("\n");f.flush();os.fsync(f.fileno())
    started = datetime.now(timezone.utc).isoformat()
    save("claim.json", {"started_at":started,"automatic_retry":False,"source_mode":"READ_ONLY"})
    try:
        rawstate = read_source(state, state.parent, 8*1024*1024)
        inventory = json.loads(rawstate)
        latest = {}
        for row in inventory["artifacts"]:
            if row["media_type"].split(";")[0] != "text/html" or row["bytes"] > 1024*1024:
                continue
            if row["source_id"] not in latest or row["retrieved_at"] > latest[row["source_id"]]["retrieved_at"]:
                latest[row["source_id"]] = row
        # Stable deterministic selection of three existing sources. No new requests.
        chosen = [latest[key] for key in sorted(latest)[:3]]
        if len(chosen) != 3:
            raise ValueError("THREE_EXISTING_HTML_SOURCES_REQUIRED")
        entities, relations, runs, rawmap, verified = [], [], [], {}, 0
        snippets, seeds = set(), []
        code_sha = sha(Path(__file__).read_bytes())
        source_bytes = 0
        for n, row in enumerate(chosen):
            path=Path(row["location"])
            raw=read_source(path,state.parent/"blobs",1024*1024)
            if sha(raw)!=row["content_sha256"] or len(raw)!=row["bytes"]:
                raise ValueError("REGISTERED_SOURCE_HASH_MISMATCH")
            source_bytes+=len(raw)
            text=raw.decode("utf-8")
            sid="SOURCE."+digest([row["source_id"],row["content_sha256"]])[:32]
            source=dict(id=sid,artifact_id="SOURCE."+row["source_id"],revision=1,kind="source",sha256=sha(raw),size_bytes=len(raw),media_type="text/html",tenant_id="pilot",sensitivity="internal",observed_at=row["retrieved_at"],locator=None,ordinal=None)
            entities.append(source);rawmap[sid]=(path,raw)
            matches=[m for m in re.finditer(r"<p\b[^>]*>.*?</p\s*>",text,re.I|re.S) if 30<=len(m.group())<=1800][:8]
            if not matches:
                raise ValueError("PARAGRAPH_LOCATOR_UNAVAILABLE")
            outputs=[];previous=None
            for ordinal,m in enumerate(matches):
                content=m.group().encode();bid="BLOCK."+digest([sid,m.start(),m.end()])[:32]
                loc={"source_id":sid,"source_sha256":sha(raw),"selector":{"type":"text","start":m.start(),"end":m.end(),"encoding":"unicode_codepoints"}}
                block=dict(source,id=bid,artifact_id=bid,kind="block",sha256=sha(content),size_bytes=len(content),locator=loc,ordinal=ordinal,media_type="text/html")
                chunk=dict(block,id="CHUNK."+digest([bid])[:32],artifact_id="CHUNK."+digest([bid])[:32],kind="chunk",ordinal=0)
                entities.extend([block,chunk]);outputs.extend([bid,chunk["id"]]);snippets.update([bid,chunk["id"]])
                verified+=int(verify_locator(block,source,raw)["verified"])
                for a,b,t in [(bid,sid,"part_of"),(chunk["id"],bid,"part_of"),(chunk["id"],bid,"derived_from")]+([(previous,bid,"next")] if previous else []):
                    relations.append({"from":a,"to":b,"type":t,"status":"structural","review_ref":None,"scope":"exact raw HTML paragraph span; content not semantically reviewed"})
                if ordinal==0:seeds.append(chunk["id"])
                previous=bid
            runs.append(dict(id="RUN.PARSE."+str(n),job_id="JOB.LOCATOR.PILOT",stage="parse",status="COMPLETE",started_at=started,ended_at=datetime.now(timezone.utc).isoformat(),inputs=[sid],outputs=outputs,agents=["AGENT.LOCATOR"],code_sha256=code_sha,parameters_sha256=digest({"max_paragraphs":8,"method":"raw-html-p-element"})))
        bundle=dict(schema_version="0.1.0",profile_id="TRACE.EXISTING.SOURCE.PILOT",entities=entities,relations=relations,agents=[dict(id="AGENT.LOCATOR",kind="software",version="raw-html-span/0.1.0")],runs=runs)
        validation=validate_bundle(bundle)
        expanded=bounded_neighbors(bundle,seeds,admitted_ids=snippets,limit=12)
        usage=context_receipt(bundle,candidate_ids=expanded,selected_ids=expanded,cited_ids=[],admitted_ids=snippets,cutoff=datetime.now(timezone.utc).isoformat(),max_bytes=65536,query_sha256=digest("structural pilot; no semantic question"))
        for sid,(path,raw) in rawmap.items():
            if sha(read_source(path,state.parent/"blobs",1024*1024))!=sha(raw):
                raise ValueError("SOURCE_CHANGED_AFTER_PILOT")
        save("bundle.json",bundle);save("context-use.json",usage)
        save("prov.jsonld",prov_projection(bundle));save("openlineage.json",openlineage_events(bundle,namespace="trace.local.pilot"))
        receipt=dict(status="EXISTING_SOURCE_STRUCTURAL_PILOT_PASS",started_at=started,completed_at=datetime.now(timezone.utc).isoformat(),state_sha256=sha(rawstate),source_count=len(chosen),source_bytes=source_bytes,exact_locator_checks=verified,entities=len(entities),relations=len(relations),runs=len(runs),baseline_seed_count=len(seeds),expanded_count=len(expanded),selected_bytes=usage["selected_bytes"],bundle_sha256=validation["bundle_sha256"],original_sources_unchanged=True,raw_content_exported=False,model_calls=0,api_calls=0,report_publications=0,production_changes=False,semantic_quality_measured=False,docling_parser_available=False,automatic_retry=False,artifacts={p.name:sha(p.read_bytes()) for p in out.iterdir() if p.is_file()})
        save("receipt.json",receipt);print(json.dumps(receipt,sort_keys=True))
    except Exception as exc:
        failure={"status":"FAIL_CLOSED","error_class":type(exc).__name__,"error_code":str(exc)[:120],"automatic_retry":False}
        save("failure.json",failure);print(json.dumps(failure));raise SystemExit(1)


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--state",type=Path,required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args();run(a.state,a.output)
