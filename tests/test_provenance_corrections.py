import copy
import hashlib
import hmac
import json
from datetime import UTC,datetime
from pathlib import Path

import pytest

from trace_gate.provenance import digest
from trace_gate.provenance_access import authorized_context
from trace_gate.provenance_adapters import provenance_exchange_package, restore_provenance_exchange
from trace_gate.provenance_quality import evaluate_cells

ROOT=Path(__file__).resolve().parents[1]

@pytest.fixture
def bundle():return json.loads((ROOT/'examples/provenance-bundle.json').read_text())

@pytest.mark.parametrize('format',['prov','openlineage'])
def test_exchange_lossless(format,bundle):
    package=provenance_exchange_package(bundle,format=format)
    assert restore_provenance_exchange(package)==bundle
    serialized=json.dumps(package['projection'])
    for f in ['id','code_sha256','parameters_sha256','stage']:
        assert bundle['runs'][0][f] in serialized
    restored=restore_provenance_exchange(package);restored['entities'].clear()
    assert package['canonical_bundle']['entities']

@pytest.mark.parametrize('format',['prov','openlineage'])
@pytest.mark.parametrize('target',['canonical_bundle','projection'])
def test_exchange_tamper(format,target,bundle):
    p=provenance_exchange_package(bundle,format=format)
    p[target]={}
    with pytest.raises(ValueError,match='EXCHANGE_HASH'):restore_provenance_exchange(p)

def test_exchange_rehashed_projection_still_must_match(bundle):
    p=provenance_exchange_package(bundle,format='prov');p['projection']['@graph']=[];p['projection_sha256']=digest(p['projection'])
    with pytest.raises(ValueError,match='EXCHANGE_PROJECTION'):restore_provenance_exchange(p)

def test_exchange_cannot_import_own_review_authority(bundle):
    bundle['relations'][3].update(status='reviewed',review_ref='SELF')
    with pytest.raises(ValueError,match='TRUSTED_REVIEW'):provenance_exchange_package(bundle,format='prov')

KEY=b'qualification-key-not-a-real-credential-0001'
def signed(grant):return {'grant':grant,'mac':hmac.new(KEY,digest(grant).encode(),hashlib.sha256).hexdigest()}
def grant_args(bundle):
    g={'version':'trace-read-grant/1','principal':'test-user','tenant_id':'example','purpose':'review',
       'query_sha256':'a'*64,'read_profile_sha256':'b'*64,'bundle_sha256':digest(bundle),
       'issued_at':'2026-01-01T00:00:00Z','expires_at':'2026-01-01T00:05:00Z',
       'cutoff':'2026-01-01T00:01:00Z','max_bytes':512,
       'members':[{k:bundle['entities'][2][k] for k in ['id','artifact_id','revision','sha256']}]}
    kw=dict(verifier_key=KEY,authenticated_principal='test-user',purpose='review',query_sha256='a'*64,
            read_profile_sha256='b'*64,seeds=['CHUNK.1'],cited_ids=['CHUNK.1'],limit=3,
            now=datetime(2026,1,1,0,2,tzinfo=UTC))
    return g,kw

def test_authenticated_exact_grant_limits_graph(bundle):
    g,kw=grant_args(bundle);r=authorized_context(bundle,signed(g),**kw)
    assert r['selected_ids']==['CHUNK.1'] and not r['execution_authorized']

@pytest.mark.parametrize('change',[
    lambda g:g.update(principal='other'),lambda g:g.update(tenant_id='other'),
    lambda g:g.update(purpose='execute'),lambda g:g.update(query_sha256='c'*64),
    lambda g:g.update(read_profile_sha256='c'*64),lambda g:g.update(bundle_sha256='c'*64),
    lambda g:g.update(expires_at='2026-01-01T00:02:00Z'),
    lambda g:g.update(expires_at='2026-01-01T00:06:00Z'),
    lambda g:g.update(issued_at='2026-01-01T00:03:00Z'),
    lambda g:g.update(cutoff='2026-01-01T01:00:00Z'),lambda g:g.update(max_bytes=0),
    lambda g:g['members'][0].update(revision=2),lambda g:g['members'][0].update(sha256='c'*64),
    lambda g:g['members'].append(copy.deepcopy(g['members'][0])),
])
def test_wrong_grant_rejected(bundle,change):
    g,kw=grant_args(bundle);change(g)
    with pytest.raises((ValueError,PermissionError)):authorized_context(bundle,signed(g),**kw)

def test_unsigned_and_cross_tenant_graph_rejected(bundle):
    g,kw=grant_args(bundle);e=signed(g);e['mac']='0'*64
    with pytest.raises(PermissionError,match='SIGNATURE'):authorized_context(bundle,e,**kw)
    kw['seeds']=['SRC.1']
    with pytest.raises(PermissionError,match='ADMISSION'):authorized_context(bundle,signed(g),**kw)

def cell():return dict(page=1,table='T',row='R',column='C',token='1,234',unit='USD',period='2025',basis='nominal')

def test_page_token_cannot_replace_cell_alignment():
    a=[cell()];b=[dict(cell(),row='WRONG')];r=evaluate_cells(a,b,source_sha256='a'*64)
    assert r['missing_cells']==1 and r['exact_cells']==0 and r['status']=='NOT_QUALIFIED'

@pytest.mark.parametrize('field',['token','unit','period','basis'])
def test_critical_cell_fields_are_not_normalized_away(field):
    r=evaluate_cells([cell()],[dict(cell(),**{field:'changed'})],source_sha256='a'*64)
    assert r['critical_mismatches'][0]['fields']==[field]

def test_cell_match_without_independent_gold_not_qualified():
    a=[cell()];r=evaluate_cells(a,a,source_sha256='a'*64)
    assert r['exact_cells']==1 and r['status']=='NOT_QUALIFIED'
    g={'method':'independent_human','reviewer':'synthetic-reviewer','source_sha256':'a'*64,'expected_sha256':digest(a)}
    assert evaluate_cells(a,a,source_sha256='a'*64,trusted_gold=g)['status']=='QUALIFIED'
    g['method']='assistant'
    assert evaluate_cells(a,a,source_sha256='a'*64,trusted_gold=g)['status']=='NOT_QUALIFIED'
