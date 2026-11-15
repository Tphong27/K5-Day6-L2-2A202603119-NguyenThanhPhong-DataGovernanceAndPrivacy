"""Evaluate T07 against internal CVAT labels, with reproducible QA evidence.

Run only after baseline and PoC inference. This module is never imported by
the production pipeline and does not replace the instructor's official GT.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

from src.common.io import git_sha
from src.common.report import MetricResult, compare_runs, write_metrics
from src.metrics.detection import pii_miss_rate
from src.metrics.tracks import eval_t07
from src.t07_contract import load_images, validate_final_regions


def wilson(k: int, n: int) -> tuple[float | None, float | None]:
    if not n:
        return None, None
    z = 1.959963984540054
    center = (k / n + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt((k / n) * (1 - k / n) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, center - half), min(1.0, center + half)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input', type=Path, default=Path('fixtures/t07_redaction'))
    ap.add_argument('--labels', type=Path, default=Path('reports/gold/t07_cvat_coco.json'))
    ap.add_argument('--baseline', type=Path, default=Path('out/baseline/redactions.csv'))
    ap.add_argument('--poc', type=Path, default=Path('out/poc/redactions.csv'))
    ap.add_argument('--output', type=Path, default=Path('reports/t07_qa'))
    ap.add_argument('--metrics-dir', type=Path, default=Path('reports'))
    ap.add_argument('--evaluation-dir', type=Path, default=Path('out/t07_internal_eval'))
    ap.add_argument('--split', choices=['dev', 'eval'], default='eval')
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--bootstrap', type=int, default=2000)
    a = ap.parse_args(argv)
    if a.bootstrap <= 0:
        ap.error('--bootstrap must be positive')
    images = load_images(a.input)
    coco = json.loads(a.labels.read_text(encoding='utf-8'))
    image_ids = {r['id']: Path(r['file_name']).stem for r in coco['images']}
    categories = {r['id']: r['name'] for r in coco['categories']}
    splits = images.set_index('image_id').split.to_dict()
    rows = []
    for ann in coco['annotations']:
        iid = image_ids[ann['image_id']]
        x, y, w, h = ann['bbox']
        rows.append(dict(image_id=iid, region_id=f"cvat:{ann['id']}",
                         type=categories[ann['category_id']], x=x, y=y, w=w, h=h,
                         split=splits[iid], condition='unknown', must_redact=1))
    gt = validate_final_regions(pd.DataFrame(rows), images)
    if not set(gt.type).issubset({'face', 'plate'}):
        raise ValueError('Unknown CVAT category')
    selected_gt = gt[gt.split == a.split]
    if selected_gt.empty:
        raise ValueError('No labeled regions in the selected split')
    for directory in [a.output, a.metrics_dir, a.evaluation_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    images.to_csv(a.evaluation_dir / 'images.csv', index=False)
    gt_path = a.evaluation_dir / 'gt_regions.csv'
    gt.to_csv(gt_path, index=False)
    sizes = {r.image_id: (int(r.height), int(r.width)) for r in images.itertuples()}
    pool = sorted(images.loc[images.split == a.split, 'image_id'])
    config = dict(split=a.split, min_coverage=0.9, max_over_redaction=0.3)
    runs = [('baseline', a.baseline), ('poc', a.poc)]
    blur_all = a.baseline.with_name('redactions_blur_all.csv')
    if blur_all.exists():
        runs.append(('blur_all', blur_all))
    all_regions, all_slices, bootstraps = [], [], []
    for name, pred in runs:
        red = validate_final_regions(pd.read_csv(pred), images)
        red = red[red.image_id.isin(pool)]
        regions = pii_miss_rate(selected_gt, red, sizes, 0.9)['regions']
        regions['run'] = name
        area = regions.w * regions.h
        regions['size'] = np.where(area < 1024, 'small', np.where(area < 9216, 'medium', 'large'))
        all_regions.append(regions)
        evaluated = eval_t07(gt_path, pred, config)
        groups = [('all', regions)]
        for column in ['type', 'condition']:
            groups.extend((f'{column}={value}', sub) for value, sub in regions.groupby(column))
        groups.extend((f'size={value}', regions[regions['size'] == value])
                      for value in ['small', 'medium', 'large'])
        for label, sub in groups:
            n, missed = len(sub), int(sub.missed.sum())
            low, high = wilson(missed, n)
            all_slices.append(dict(run=name, slice=label, n_regions=n, n_missed=missed,
                                   miss_rate=missed / n if n else None,
                                   wilson95_low=low, wilson95_high=high,
                                   mean_coverage=float(sub.coverage.mean()) if n else None))
            if label.startswith('size='):
                evaluated.metrics.append(MetricResult(
                    name='PII Miss Rate', value=missed / n if n else None,
                    direction='lower', unit='fraction', numerator=missed,
                    denominator=n, n=n, slice=label))
        per_image = regions.groupby('image_id').missed.agg(['sum', 'count']).reindex(pool, fill_value=0)
        indices = np.random.default_rng(a.seed).integers(0, len(pool), size=(a.bootstrap, len(pool)))
        numerators = per_image['sum'].to_numpy()[indices].sum(axis=1)
        denominators = per_image['count'].to_numpy()[indices].sum(axis=1)
        valid = denominators > 0
        rates = numerators[valid] / denominators[valid]
        bootstraps.append(dict(run=name, n_bootstrap=a.bootstrap, n_valid=int(valid.sum()), seed=a.seed,
                               image_bootstrap95_low=float(np.quantile(rates, 0.025)) if len(rates) else None,
                               image_bootstrap95_high=float(np.quantile(rates, 0.975)) if len(rates) else None))
        info_path = pred.with_name('run_info.json')
        info = json.loads(info_path.read_text(encoding='utf-8')) if info_path.exists() else {}
        stats = info.get('stats', {})
        review = stats.get('review', {})
        reviewed = name == 'poc' and review.get('n_reviewed', 0) > 0 and review.get('pending', 1) == 0
        count = stats.get('n_images', stats.get('n_items'))
        runtime = info.get('runtime_seconds') if name != 'blur_all' else None
        run_name = ('poc_reviewed' if reviewed else 'poc_prereview') if name == 'poc' else name
        write_metrics(a.metrics_dir / f'metrics_{name}.json', run_name, 't07', evaluated.metrics,
                      seed=info.get('seed', a.seed), config=config, runtime_seconds=runtime,
                      n_items=count if runtime is not None else None,
                      extra=dict(evaluation_status='INTERNAL_CVAT_NOT_OFFICIAL',
                                 labels=str(a.labels), labels_sha256=sha256(a.labels),
                                 predictions=str(pred), predictions_sha256=sha256(pred),
                                 inference_git_sha=info.get('git_sha'), inference_config_hash=info.get('config_hash'),
                                 human_review_completed=reviewed, review=review, notes=evaluated.notes,
                                 limitations=['CVAT labels incomplete, potentially duplicate or incorrect',
                                              'condition=unknown; no condition labels invented',
                                              'Runtime is whole-pipeline time over all input images',
                                              'Separate blur-all runtime not measured'],
                                 runtime_image_count=count, reporting_git_sha=git_sha()))
    pd.concat(all_regions).to_csv(a.output / 'per_region_coverage.csv', index=False)
    pd.DataFrame(all_slices).to_csv(a.output / 'slices_with_ci.csv', index=False)
    (a.output / 'image_bootstrap_ci.json').write_text(json.dumps(bootstraps, indent=2), encoding='utf-8')
    table = compare_runs(a.metrics_dir / 'metrics_baseline.json', a.metrics_dir / 'metrics_poc.json')
    (a.metrics_dir / 'table1_baseline_vs_poc.md').write_text(
        '> INTERNAL CVAT EVALUATION ONLY. Check run_name/review status; not official GT.\n\n' + table + '\n',
        encoding='utf-8')
    evidence = a.output / 'evidence'
    evidence.mkdir(exist_ok=True)
    predictions = pd.read_csv(a.poc)
    poc_regions = next(r for r in all_regions if r.run.iloc[0] == 'poc')
    # Two observed plate failures; keep the suspected face label error separate.
    cases = poc_regions[(poc_regions.type == 'plate') & (poc_regions.missed == 1)]
    cases = cases.sort_values(['coverage', 'image_id', 'region_id']).drop_duplicates('image_id').head(2)
    suspect = poc_regions[(poc_regions.image_id == 'pii_03') & (poc_regions.region_id == 'cvat:14')]
    sections = ['# T07 internal failure evidence', '',
                'Green = CVAT reference; orange = predicted redaction. Labels are incomplete/unverified.', '',
                'Root-cause hypotheses below are not confirmed by intermediate detector traces.', '']
    for label, frame in [('Plate detection case', cases), ('Suspected label-quality issue', suspect)]:
        for r in frame.itertuples():
            row = images.set_index('image_id').loc[r.image_id]
            image = Image.open(a.input / row.path).convert('RGB')
            draw = ImageDraw.Draw(image)
            boxes = predictions[predictions.image_id == r.image_id]
            for b in boxes.itertuples():
                draw.rectangle([b.x, b.y, b.x + b.w, b.y + b.h], outline='orange', width=2)
            draw.rectangle([r.x, r.y, r.x + r.w, r.y + r.h], outline='lime', width=3)
            filename = f'{r.type}_{r.image_id}_{r.region_id.replace(":", "_")}.png'
            image.save(evidence / filename)
            sections += [f'## {label}: {r.image_id}, {r.region_id}', '',
                         f'- Split: {a.split}; type: {r.type}; CVAT bbox: {[r.x, r.y, r.w, r.h]}.',
                         f'- Coverage={r.coverage:.8f}; threshold=0.9; predicted boxes on image={len(boxes)}.']
            if label.startswith('Suspected'):
                sections += ['- Visual inspection places the reference face box on clothing. Verify the annotation; do not claim a real face was missed.',
                             '- This annotation is NOT silently removed or corrected in metric calculation.']
            else:
                sections += ['- Observed: predicted redactions do not cover the labeled plate sufficiently.',
                             '- Hypothesis: edge/shape heuristics or candidate filters fail for this region; exact rejecting stage is not traced.',
                             '- Next step: inspect intermediate detections and analogous dev cases; do not tune on eval.']
            sections += [f'![Evidence](evidence/{filename})', '']
    (a.output / 'failure_analysis.md').write_text('\n'.join(sections), encoding='utf-8')
    print(f'Generated {len(all_slices)} slice rows for {len(runs)} runs.')
    print(f'Internal CVAT metrics: {a.metrics_dir}; slices/evidence: {a.output}')


if __name__ == '__main__':
    main()
