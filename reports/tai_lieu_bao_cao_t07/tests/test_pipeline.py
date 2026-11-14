import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from src.pipeline import run_pipeline


class Model:
    def __init__(self, results):
        self.results = results
        self.arguments = None

    def predict(self, **arguments):
        self.arguments = arguments
        return iter(self.results)


class PipelineTests(unittest.TestCase):
    def test_success_maps_labels_filters_other_classes_and_writes_json(self):
        boxes = [
            SimpleNamespace(cls=[0], conf=[0.9], xyxy=[[10, 20, 30, 40]]),
            SimpleNamespace(cls=[1], conf=[0.8], xyxy=[[50, 60, 90, 75]]),
            SimpleNamespace(cls=[2], conf=[0.95], xyxy=[[1, 2, 100, 100]]),
        ]
        model = Model([SimpleNamespace(path='frame_0000.jpeg', names={0: 'face', 1: 'license_plate', 2: 'car'}, boxes=boxes)])
        with tempfile.TemporaryDirectory() as directory:
            result = run_pipeline(model, 'images', directory, label_map={'license_plate': 'plate'})
            saved = json.loads((Path(directory) / 'frame_0000.json').read_text())
        self.assertEqual(result['stage'], 'detect')
        self.assertEqual(result['detection_count'], 2)
        self.assertEqual([item['label'] for item in saved], ['face', 'plate'])
        self.assertEqual(saved[0]['points'], [10.0, 20.0, 30.0, 40.0])
        self.assertIsNone(model.arguments['device'])

    def test_edge_no_detections_remains_empty(self):
        model = Model([SimpleNamespace(path='empty.jpeg', names={0: 'face'}, boxes=[])])
        result = run_pipeline(model, 'images')
        self.assertEqual(result['frame_count'], 1)
        self.assertEqual(result['detection_count'], 0)
        self.assertEqual(result['frames'][0]['detections'], [])

    def test_failure_detector_error_is_not_reported_as_success(self):
        class BrokenModel:
            def predict(self, **arguments):
                raise RuntimeError('detector unavailable')
        with self.assertRaisesRegex(RuntimeError, 'detector unavailable'):
            run_pipeline(BrokenModel(), 'images')
