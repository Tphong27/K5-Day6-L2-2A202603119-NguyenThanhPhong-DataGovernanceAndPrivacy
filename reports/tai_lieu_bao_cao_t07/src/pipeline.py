import json
from pathlib import Path

from .detector import detect


def run_pipeline(model, source, output_dir=None, confidence=0.25, device=None, label_map=None, allowed_labels=('face', 'plate')):
    frames = list(detect(model, source, confidence, device, label_map, allowed_labels))
    if output_dir is not None:
        destination = Path(output_dir)
        destination.mkdir(parents=True, exist_ok=True)
        for frame in frames:
            path = destination / (Path(frame['source']).stem + '.json')
            path.write_text(json.dumps(frame['detections'], ensure_ascii=False, indent=2), encoding='utf-8')
    return {
        'stage': 'detect',
        'frames': frames,
        'frame_count': len(frames),
        'detection_count': sum(len(frame['detections']) for frame in frames),
    }
