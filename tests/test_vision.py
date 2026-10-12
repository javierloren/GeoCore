from geocore.vision.roboflow import rescale_predictions_to_original


def test_rescale_predictions_to_original():
    pred = {
        "predictions": [
            {
                "x": 10,
                "y": 20,
                "width": 30,
                "height": 40,
                "points": [{"x": 1, "y": 2}, {"x": 3, "y": 4}],
            }
        ]
    }

    out = rescale_predictions_to_original(pred, sx=2, sy=3, orig_w=200, orig_h=300)

    item = out["predictions"][0]
    assert item["x"] == 20
    assert item["y"] == 60
    assert item["width"] == 60
    assert item["height"] == 120
    assert item["points"] == [{"x": 2, "y": 6}, {"x": 6, "y": 12}]
    assert out["image"] == {"width": 200, "height": 300}
