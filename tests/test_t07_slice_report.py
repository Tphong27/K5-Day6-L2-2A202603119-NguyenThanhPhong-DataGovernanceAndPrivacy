"""Exercise the reporting CLI with independently known spatial results."""
import json

import pandas as pd
from PIL import Image

from tools.t07_slice_report import main


def test_internal_report_preserves_labels_and_reports_empty_slices(tmp_path):
    inputs = tmp_path / 'input'
    inputs.mkdir()
    Image.new('RGB', (20, 10)).save(inputs / 'a.png')
    pd.DataFrame([dict(image_id='a', path='a.png', width=20, height=10, split='eval')]).to_csv(
        inputs / 'images.csv', index=False)
    labels = tmp_path / 'cvat.json'
    labels.write_text(json.dumps(dict(
        images=[dict(id=1, file_name='a.png')],
        categories=[dict(id=1, name='face')],
        annotations=[dict(id=1, image_id=1, category_id=1, bbox=[1.25, 1.5, 2.5, 2.25])])),
        encoding='utf-8')
    before = labels.read_bytes()
    pred = tmp_path / 'pred.csv'
    pd.DataFrame([dict(image_id='a', x=1.25, y=1.5, w=2.5, h=2.25)]).to_csv(pred, index=False)
    output, metrics, evaluation = (tmp_path / name for name in ['report', 'metrics', 'evaluation'])
    main(['--input', str(inputs), '--labels', str(labels), '--baseline', str(pred),
          '--poc', str(pred), '--output', str(output), '--metrics-dir', str(metrics),
          '--evaluation-dir', str(evaluation), '--bootstrap', '20'])
    assert labels.read_bytes() == before
    converted = pd.read_csv(evaluation / 'gt_regions.csv').iloc[0]
    assert converted[['x', 'y', 'w', 'h']].tolist() == [1.25, 1.5, 2.5, 2.25]
    payload = json.loads((metrics / 'metrics_poc.json').read_text(encoding='utf-8'))
    assert payload['extra']['evaluation_status'] == 'INTERNAL_CVAT_NOT_OFFICIAL'
    assert payload['run_name'] == 'poc_prereview'
    assert next(m['value'] for m in payload['metrics'] if m['primary']) == 0
    assert next(m['value'] for m in payload['metrics'] if m['name'].startswith('Guardrail:')) == 1
    large = next(m for m in payload['metrics'] if m['slice'] == 'size=large')
    assert large['n'] == 0 and large['value'] is None
    assert (metrics / 'table1_baseline_vs_poc.md').read_text(encoding='utf-8').startswith('> INTERNAL')
    bootstrap = json.loads((output / 'image_bootstrap_ci.json').read_text(encoding='utf-8'))
    assert all(b['image_bootstrap95_low'] == b['image_bootstrap95_high'] == 0 for b in bootstrap)
