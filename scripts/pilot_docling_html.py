#!/usr/bin/env python3
"""One existing HTML document, isolated Docling backend, network disabled.

No PDF/OCR, model weights, server, report generation or semantic quality claim.
"""
import argparse
from datetime import datetime, timezone
import hashlib
from io import BytesIO
import json
import os
from pathlib import Path
import resource
import socket
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from pilot_provenance import read_source
from trace_gate.provenance import digest
from trace_gate.provenance_adapters import docling_projection


def run(state, output):
    os.umask(0o077);output.mkdir(parents=False,mode=0o700,exist_ok=False)
    def save(name,value):
        with (output/name).open('x') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
    save('claim.json',{'automatic_retry':False,'network_during_conversion':False})
    try:
        from bs4 import BeautifulSoup
        from docling.backend.html_backend import HTMLDocumentBackend
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.document import InputDocument
        from docling.datamodel.backend_options import HTMLBackendOptions
        import importlib.metadata
        # Deny network before reading/converting user material, independent of defaults.
        def denied(*args,**kwargs):raise PermissionError('NETWORK_DISABLED_FOR_PILOT')
        socket.socket.connect=denied;socket.create_connection=denied
        resource.setrlimit(resource.RLIMIT_CPU,(30,30))
        resource.setrlimit(resource.RLIMIT_AS,(3*1024**3,3*1024**3))
        inventory=json.loads(read_source(state, state.parent, 8 * 1024 * 1024))
        candidates=[x for x in inventory['artifacts'] if x['source_id']=='bea-income-current' and x['media_type']=='text/html']
        item=max(candidates,key=lambda x:x['retrieved_at'])
        path = Path(item['location'])
        blob_root = state.parent / 'blobs'
        raw = read_source(path, blob_root, 1024 * 1024)
        h = hashlib.sha256(raw).hexdigest()
        if h != item['content_sha256'] or len(raw) != item['bytes']:
            raise ValueError('SOURCE_HASH_OR_SIZE')
        started=time.monotonic()
        options=HTMLBackendOptions(enable_remote_fetch=False,enable_local_fetch=False,fetch_images=False,render_page=False)
        in_doc=InputDocument(BytesIO(raw),format=InputFormat.HTML,backend=HTMLDocumentBackend,backend_options=options,filename='existing-source.html')
        backend=HTMLDocumentBackend(in_doc,BytesIO(raw),options=options)
        # The public export uses JSON-schema aliases ($ref); model_dump defaults
        # to internal Python names (cref), which are not the interchange format.
        document=backend.convert();serialized=document.export_to_dict()
        source=dict(id='SOURCE.'+h[:32],artifact_id='SOURCE.bea-income-current',revision=1,kind='source',sha256=h,size_bytes=len(raw),media_type='text/html',tenant_id='pilot',sensitivity='internal',observed_at=item['retrieved_at'],locator=None,ordinal=None)
        result=docling_projection(serialized,source,parser_version='docling-slim/'+importlib.metadata.version('docling-slim'))
        normal=lambda s:' '.join(s.split())
        soup=BeautifulSoup(raw,'html.parser')
        paragraphs=[normal(p.get_text(' ',strip=True)) for p in soup.find_all('p')]
        paragraphs=[p for p in paragraphs if len(p)>=30]
        extracted=normal(' '.join(x.get('text','') for x in serialized.get('texts',[])))
        retained=sum(p in extracted for p in paragraphs)
        if read_source(path, blob_root, 1024 * 1024) != raw:
            raise ValueError('SOURCE_CHANGED_DURING_PILOT')
        save('docling-document.json',serialized);save('projection.json',result)
        receipt=dict(status='DOCLING_HTML_ADAPTER_PASS',source_sha256=h,source_bytes=len(raw),document_schema=serialized['version'],versions={n:importlib.metadata.version(n) for n in ['docling-slim','docling-core']},entities=len(result['bundle']['entities']),relations=len(result['bundle']['relations']),missing_geometry=result['adapter_receipt']['missing_geometry'],raw_paragraphs=len(paragraphs),paragraph_text_matches=retained,paragraph_match_measure='whitespace-normalized substring; not human gold or table alignment',elapsed_seconds=round(time.monotonic()-started,3),peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,network_during_conversion=False,model_calls=0,original_unchanged=True,output_on_source_host_only=True,report_publications=0,visual_accuracy_verified=False,pdf_ocr_qualified=False,semantic_quality_measured=False,bundle_sha256=digest(result['bundle']),completed_at=datetime.now(timezone.utc).isoformat(),automatic_retry=False)
        save('receipt.json',receipt);print(json.dumps(receipt,sort_keys=True))
    except Exception as exc:
        receipt={'status':'FAIL_CLOSED','error_class':type(exc).__name__,'error_code':str(exc)[:120],'automatic_retry':False}
        save('failure.json',receipt);print(json.dumps(receipt));raise SystemExit(1)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--state',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run(a.state,a.output)
