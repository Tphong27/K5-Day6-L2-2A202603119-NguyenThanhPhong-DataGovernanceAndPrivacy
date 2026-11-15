"""T07 integration QA; synthetic review actions are test fixtures only."""
import hashlib,json,socket
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from src import pipeline
from src.common.context import RunContext
from src.common.review import AuditLog
from src.common.gt_guard import enable_gt_guard,disable_gt_guard,GroundTruthAccessError
from src.common.offline import enable_offline_guard,disable_offline_guard,NetworkBlockedError
from src.t07_contract import load_images,validate_final_regions
FX=Path('fixtures/t07_redaction').resolve()

def execute(out,reviewed=None):
    out.mkdir(parents=True,exist_ok=True)
    if reviewed is not None: reviewed.to_csv(out/'review_queue_reviewed.csv',index=False)
    ctx=RunContext('t07',FX,out,{'params':{'budget':15},'owner':'QA fixture'},42,np.random.default_rng(42),audit=AuditLog(out/'audit_log.jsonl'))
    enable_offline_guard(); enable_gt_guard()
    try: pipeline.run(ctx)
    finally: disable_gt_guard(); disable_offline_guard()
    return ctx

@pytest.fixture(scope='module')
def initial(tmp_path_factory): return execute(tmp_path_factory.mktemp('initial'))

def test_schema_geometry_export(initial):
    out=initial.output_dir
    regions=pd.read_csv(out/'redactions.csv')
    validate_final_regions(regions,load_images(FX))
    manifest=pd.read_csv(out/'redacted_images/export_manifest.csv')
    assert set(manifest.image_id)==set(load_images(FX).image_id)
    assert manifest.n_regions.sum()==len(regions)
    assert len(list((out/'redacted_images').glob('*.jpg')))==60

def test_seed42_deterministic(initial,tmp_path):
    other=execute(tmp_path/'repeat')
    for name in ['candidates.csv','review_queue.csv','redactions.csv']:
        pd.testing.assert_frame_equal(pd.read_csv(initial.output_dir/name),pd.read_csv(other.output_dir/name))
    first=json.loads((initial.output_dir/'decision.json').read_text())
    second=json.loads((other.output_dir/'decision.json').read_text())
    first.pop('ts',None); second.pop('ts',None)
    first.pop('evidence',None); second.pop('evidence',None)
    assert first==second

def test_queue_pending(initial):
    q=pd.read_csv(initial.output_dir/'review_queue.csv')
    assert 0<len(q)<=15 and q.item_id.is_unique
    assert initial.stats['review']['pending']==len(q)
    assert json.loads((initial.output_dir/'decision.json').read_text())['reason_code']=='REVIEW_PENDING'

def test_reject_edit_audit(initial,tmp_path):
    q=pd.read_csv(initial.output_dir/'review_queue.csv'); rejected,edited=q.item_id.iloc[:2]
    reviewed=q.iloc[:2].astype(object).fillna('')
    reviewed['reviewer_decision']=['reject','edit']
    reviewed['reviewer']='SYNTHETIC_TEST_ONLY'
    reviewed['review_note']='QA fixture, not human review'
    reviewed['override_value']=['',json.dumps(dict(type='face',x=1,y=2,w=10,h=12))]
    reviewed['reviewed_at']='2026-11-15T00:00:00Z'
    ctx=execute(tmp_path/'review',reviewed); final=pd.read_csv(ctx.output_dir/'redactions.csv')
    assert rejected not in set(final.region_id)
    assert final.set_index('region_id').loc[edited,['x','y','w','h']].tolist()==[1,2,10,12]
    events=[json.loads(line) for line in (ctx.output_dir/'audit_log.jsonl').read_text().splitlines()]
    for action,rid in [('review:reject',rejected),('review:edit',edited)]:
        event=next(e for e in events if e['action']==action and e['item_id']==rid)
        assert event['extra']['reviewer']=='SYNTHETIC_TEST_ONLY' and isinstance(event['before'],dict) and 'after' in event
        if action=='review:reject': assert event['after'] is None
        else: assert event['after']['x']==1
    assert ctx.stats['review']['pending']==len(q)-2

def test_inputs_unchanged(tmp_path):
    def hashes(): return {str(p.relative_to(FX)):hashlib.sha256(p.read_bytes()).hexdigest() for p in FX.rglob('*') if p.is_file()}
    before=hashes(); execute(tmp_path/'preserve'); assert hashes()==before

def test_network_guard():
    enable_offline_guard()
    try:
        with pytest.raises(NetworkBlockedError): socket.create_connection(('example.com',443))
    finally: disable_offline_guard()

def test_gt_guard():
    enable_gt_guard()
    try:
        with pytest.raises(GroundTruthAccessError): (FX/'gt/never_read.csv').read_text()
    finally: disable_gt_guard()

def test_pipeline_no_network_or_labels(tmp_path,monkeypatch):
    import builtins,io,sys
    original=builtins.open
    def checked(file,*args,**kwargs):
        if isinstance(file,(str,Path)):
            value=str(file).replace(chr(92),'/').lower()
            assert '/gt/' not in value and 'internal_cvat' not in value and '/reports/gold/' not in value
        return original(file,*args,**kwargs)
    def forbidden(*args,**kwargs): raise AssertionError('Network attempted')
    module=sys.modules[__name__]
    monkeypatch.setattr(module,'enable_gt_guard',lambda:None); monkeypatch.setattr(module,'enable_offline_guard',lambda:None)
    monkeypatch.setattr(builtins,'open',checked); monkeypatch.setattr(io,'open',checked)
    monkeypatch.setattr(socket.socket,'connect',forbidden); monkeypatch.setattr(socket,'create_connection',forbidden)
    execute(tmp_path/'guarded')
