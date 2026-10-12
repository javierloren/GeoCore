from geocore.calculations.rqd import (
    classify_rqd,
    compute_rqd_by_intervals,
    compute_rqd_from_piece_lengths,
)


def _rect(cls, x1, y1, x2, y2):
    return {
        "class": cls,
        "points": [
            {"x": x1, "y": y1},
            {"x": x2, "y": y1},
            {"x": x2, "y": y2},
            {"x": x1, "y": y2},
        ],
    }


def test_classify_rqd_boundaries():
    assert classify_rqd(24.9) == "very poor (<25)"
    assert classify_rqd(25.0) == "poor (25-50)"
    assert classify_rqd(50.0) == "fair (50-75)"
    assert classify_rqd(75.0) == "good (75-90)"
    assert classify_rqd(90.0) == "excellent (90-100)"


def test_compute_rqd_by_intervals_for_single_lane():
    result = compute_rqd_by_intervals(
        predictions=[
            _rect("roca sana", 0, 0, 60, 10),
            _rect("roca sana", 70, 0, 100, 10),
        ],
        block_points_xy=[(0, 5), (100, 5)],
        img_w=100,
        img_h=10,
        n_lanes=1,
        lane_length_cm=100,
        threshold_cm=10,
        orientation="L2R",
    )

    assert result["overall"]["RQD_%"] == 90.0
    assert result["overall"]["quality"] == "excellent (90-100)"
    assert result["intervals"][0]["intact_length_cm"] == 90.0


def test_compute_rqd_requires_two_core_blocks():
    result = compute_rqd_by_intervals(
        predictions=[_rect("roca sana", 0, 0, 100, 10)],
        block_points_xy=[(0, 5)],
        img_w=100,
        img_h=10,
        n_lanes=1,
        lane_length_cm=100,
        threshold_cm=10,
        orientation="L2R",
    )

    assert "error" in result


def test_compute_rqd_from_piece_lengths():
    result = compute_rqd_from_piece_lengths(100.0, [8.0, 12.0, 25.0, 5.0, 30.0])

    assert result["overall"]["RQD_%"] == 67.0
    assert result["overall"]["intact_length_cm"] == 67.0


def test_compute_rqd_from_piece_lengths_rejects_impossible_input():
    result = compute_rqd_from_piece_lengths(100.0, [60.0, 60.0])

    assert "error" in result
