"""T07 schema and bbox contract tests; no detector or instructor GT required."""

import pandas as pd
import pytest

from src.t07_contract import validate_candidates, validate_final_regions


@pytest.fixture
def images():
    return pd.DataFrame([
        {"image_id": "img_a", "path": "images/a.png", "width": 640,
         "height": 360, "split": "dev"},
        {"image_id": "img_b", "path": "images/b.png", "width": 80,
         "height": 60, "split": "eval"},
    ])


@pytest.fixture
def candidates():
    return pd.DataFrame([
        {"region_id": "a_face", "image_id": "img_a", "type": "face",
         "x": 10, "y": 20, "w": 30, "h": 40, "confidence": 0.8,
         "score": 0.2, "reason": "low confidence", "slice": "type=face",
         "path": "images/a.png"},
        {"region_id": "b_plate", "image_id": "img_b", "type": "plate",
         "x": 5, "y": 10, "w": 40, "h": 15, "confidence": 0.6,
         "score": 0.7, "reason": "small region", "slice": "type=plate",
         "path": "images/b.png"},
    ])


@pytest.fixture(params=[validate_candidates, validate_final_regions],
                ids=["candidates", "final_regions"])
def validate(request):
    return request.param


def test_valid_regions_preserve_data_and_do_not_mutate_input(validate, candidates, images):
    before = candidates.copy(deep=True)
    result = validate(candidates, images)
    pd.testing.assert_frame_equal(result, before)
    pd.testing.assert_frame_equal(candidates, before)
    assert result is not candidates


@pytest.mark.parametrize("column", [
    "region_id", "image_id", "type", "x", "y", "w", "h",
    "confidence", "score", "reason", "slice", "path",
])
def test_candidates_reject_missing_columns(column, candidates, images):
    with pytest.raises(ValueError, match=rf"missing required columns.*{column}"):
        validate_candidates(candidates.drop(columns=column), images)


@pytest.mark.parametrize("column", ["image_id", "x", "y", "w", "h"])
def test_final_regions_reject_missing_columns(column, candidates, images):
    with pytest.raises(ValueError, match=rf"missing required columns.*{column}"):
        validate_final_regions(candidates.drop(columns=column), images)


def test_final_regions_accept_minimum_export_schema(candidates, images):
    regions = candidates[["image_id", "x", "y", "w", "h"]].copy()
    pd.testing.assert_frame_equal(validate_final_regions(regions, images), regions)


@pytest.mark.parametrize("box", [
    {"x": 0, "y": 0, "w": 1, "h": 1},
    {"x": 79, "y": 59, "w": 1, "h": 1},
    {"x": 0, "y": 0, "w": 80, "h": 60},
])
def test_bbox_can_touch_image_edges(validate, candidates, images, box):
    # img_b is deliberately smaller than the standard 640x360 fixture.
    for column, value in box.items():
        candidates.loc[1, column] = value
    result = validate(candidates, images)
    assert result.loc[1, ["x", "y", "w", "h"]].tolist() == list(box.values())


@pytest.mark.parametrize("column,value", [
    ("x", -1), ("y", -1),
    ("w", 0), ("h", 0), ("w", -1), ("h", -1),
    ("x", 41), ("y", 46),  # right/bottom edge exceeds img_b by one pixel
    ("w", 76), ("h", 51),
])
def test_invalid_bbox_is_rejected(validate, candidates, images, column, value):
    candidates.loc[1, column] = value
    with pytest.raises(ValueError, match="invalid boxes"):
        validate(candidates, images)


@pytest.mark.parametrize("column", ["x", "y", "w", "h"])
@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_non_finite_bbox_is_rejected(validate, candidates, images, column, value):
    candidates[column] = candidates[column].astype(float)
    candidates.loc[1, column] = value
    with pytest.raises(ValueError, match="non-finite box coordinates"):
        validate(candidates, images)


def test_non_numeric_bbox_is_rejected(validate, candidates, images):
    candidates["x"] = candidates["x"].astype(object)
    candidates.loc[1, "x"] = "not-a-coordinate"
    with pytest.raises(ValueError, match="non-finite box coordinates"):
        validate(candidates, images)


def test_unknown_image_is_rejected(validate, candidates, images):
    candidates.loc[1, "image_id"] = "missing_image"
    with pytest.raises(ValueError, match="invalid boxes"):
        validate(candidates, images)


def test_empty_regions_are_valid_with_schema(validate, candidates, images):
    empty = candidates.iloc[:0].copy()
    result = validate(empty, images)
    assert result.empty
    assert list(result.columns) == list(empty.columns)


def test_bbox_validation_preserves_non_default_index(validate, candidates, images):
    candidates.index = [10, 30]
    result = validate(candidates, images)
    assert result.index.tolist() == [10, 30]
    candidates.loc[30, "x"] = -1
    with pytest.raises(ValueError, match="invalid boxes"):
        validate(candidates, images)
