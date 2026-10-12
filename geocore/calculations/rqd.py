from __future__ import annotations

from typing import Any


INTACT_ROCK_CLASSES = {"roca sana", "roca_sana", "rocasana", "rock_sana", "rock sana"}
SOIL_CLASSES = {"suelo", "soil"}


def classify_rqd(rqd: float) -> str:
    if rqd < 25:
        return "very poor (<25)"
    if rqd < 50:
        return "poor (25-50)"
    if rqd < 75:
        return "fair (50-75)"
    if rqd < 90:
        return "good (75-90)"
    return "excellent (90-100)"


def poly_bounds(points: list[dict[str, Any]]) -> tuple[float, float, float, float]:
    xs = [p["x"] for p in points if "x" in p]
    ys = [p["y"] for p in points if "y" in p]
    return float(min(xs)), float(min(ys)), float(max(xs)), float(max(ys))


def poly_centroid(points: list[dict[str, Any]]) -> tuple[float, float]:
    xs = [p["x"] for p in points if "x" in p]
    ys = [p["y"] for p in points if "y" in p]
    return sum(xs) / len(xs), sum(ys) / len(ys)


def kmeans_1d(values: list[float], k: int, iters: int = 25) -> list[float]:
    vmin, vmax = min(values), max(values)
    centers = [vmin + (vmax - vmin) * i / max(1, k - 1) for i in range(k)]

    for _ in range(iters):
        labels = [_nearest_index(value, centers) for value in values]

        new_centers = []
        for i in range(k):
            cluster = [value for value, label in zip(values, labels) if label == i]
            new_centers.append(centers[i] if len(cluster) == 0 else sum(cluster) / len(cluster))

        if all(abs(a - b) < 1e-9 for a, b in zip(new_centers, centers)):
            break
        centers = new_centers

    return centers


def build_lane_model(
    predictions: list[dict[str, Any]],
    img_w: int,
    img_h: int,
    n_lanes: int,
) -> list[dict[str, float | None]]:
    ys = []
    bounds_all = []

    for prediction in predictions:
        pts = prediction.get("points", [])
        if not pts:
            continue
        x1, y1, x2, y2 = poly_bounds(pts)
        bounds_all.append((x1, y1, x2, y2))
        _, cy = poly_centroid(pts)
        ys.append(cy)

    if len(ys) >= n_lanes:
        centers_sorted = sorted(kmeans_1d(ys, n_lanes))
    else:
        centers_sorted = [(img_h * (2 * i + 1) / (2 * n_lanes)) for i in range(n_lanes)]

    lanes: list[dict[str, float | None]] = [
        {"center_y": float(center), "left_x": None, "right_x": None}
        for center in centers_sorted
    ]

    for prediction in predictions:
        pts = prediction.get("points", [])
        if not pts:
            continue
        x1, _, x2, _ = poly_bounds(pts)
        _, cy = poly_centroid(pts)
        lane_idx = assign_lane(cy, lanes)

        if lanes[lane_idx]["left_x"] is None:
            lanes[lane_idx]["left_x"] = float(x1)
            lanes[lane_idx]["right_x"] = float(x2)
        else:
            lanes[lane_idx]["left_x"] = float(min(lanes[lane_idx]["left_x"], x1))
            lanes[lane_idx]["right_x"] = float(max(lanes[lane_idx]["right_x"], x2))

    if bounds_all:
        gx1 = float(min(bounds[0] for bounds in bounds_all))
        gx2 = float(max(bounds[2] for bounds in bounds_all))
    else:
        gx1, gx2 = 0.0, float(img_w)

    for lane in lanes:
        if lane["left_x"] is None or lane["right_x"] is None or lane["right_x"] <= lane["left_x"]:
            lane["left_x"], lane["right_x"] = gx1, gx2

    return lanes


def run_distance_cm(
    lane_idx: int,
    x: float,
    lanes: list[dict[str, float | None]],
    lane_length_cm: float,
    orientation: str,
) -> float:
    left = float(lanes[lane_idx]["left_x"])
    right = float(lanes[lane_idx]["right_x"])
    width_px = max(1.0, right - left)

    xc = float(min(max(x, left), right))
    cm_per_px = lane_length_cm / width_px

    if orientation == "L2R":
        within = (xc - left) * cm_per_px
    else:
        within = (right - xc) * cm_per_px

    return lane_idx * lane_length_cm + within


def assign_lane(y: float, lanes: list[dict[str, float | None]]) -> int:
    return _nearest_index(y, [float(lane["center_y"]) for lane in lanes])


def compute_rqd_by_intervals(
    predictions: list[dict[str, Any]],
    block_points_xy: list[tuple[float, float]],
    img_w: int,
    img_h: int,
    n_lanes: int,
    lane_length_cm: float,
    threshold_cm: float,
    orientation: str,
) -> dict[str, Any]:
    lanes = build_lane_model(predictions, img_w, img_h, n_lanes)

    blocks = []
    for x, y in block_points_xy:
        lane_idx = assign_lane(y, lanes)
        distance = run_distance_cm(lane_idx, x, lanes, lane_length_cm, orientation)
        blocks.append({"x": x, "y": y, "lane": lane_idx, "d": distance})

    blocks_sorted = sorted(blocks, key=lambda block: block["d"])
    if len(blocks_sorted) < 2:
        return {"error": "You need at least 2 core blocks to define an interval."}

    spans_intact = []
    spans_soil = []

    for prediction in predictions:
        cls = (prediction.get("class") or "").strip().lower()
        pts = prediction.get("points", [])
        if not pts:
            continue

        x1, _, x2, _ = poly_bounds(pts)
        _, cy = poly_centroid(pts)
        lane_idx = assign_lane(cy, lanes)

        d1 = run_distance_cm(lane_idx, x1, lanes, lane_length_cm, orientation)
        d2 = run_distance_cm(lane_idx, x2, lanes, lane_length_cm, orientation)
        a, b = (d1, d2) if d1 <= d2 else (d2, d1)

        if cls in INTACT_ROCK_CLASSES:
            spans_intact.append((a, b))
        elif cls in SOIL_CLASSES:
            spans_soil.append((a, b))

    intervals = []
    for i in range(len(blocks_sorted) - 1):
        t0 = blocks_sorted[i]["d"]
        t1 = blocks_sorted[i + 1]["d"]
        if t1 <= t0:
            continue
        denom = t1 - t0

        intact_length = sum(
            length
            for seg in spans_intact
            if (length := _intersect_len(seg, (t0, t1))) >= threshold_cm
        )
        rqd = 0.0 if denom <= 0 else (intact_length / denom) * 100.0

        soil_len = sum(_intersect_len(seg, (t0, t1)) for seg in spans_soil)
        soil_pct = 0.0 if denom <= 0 else (soil_len / denom) * 100.0

        notes = []
        if soil_pct >= 10:
            notes.append(f"Soil presence (~{soil_pct:.0f}%)")
        if rqd < 25:
            notes.append("Highly fractured rock / low quality (based on RQD)")

        intervals.append(
            {
                "interval": i + 1,
                "from_cm": round(t0, 1),
                "to_cm": round(t1, 1),
                "denom_cm": round(denom, 1),
                "intact_length_cm": round(intact_length, 1),
                "RQD_%": round(rqd, 1),
                "quality": classify_rqd(rqd),
                "notes": " | ".join(notes) if notes else "",
            }
        )

    overall_t0 = blocks_sorted[0]["d"]
    overall_t1 = blocks_sorted[-1]["d"]
    overall_denom = max(0.0, overall_t1 - overall_t0)
    overall_num = sum(
        length
        for seg in spans_intact
        if (length := _intersect_len(seg, (overall_t0, overall_t1))) >= threshold_cm
    )
    overall_rqd = 0.0 if overall_denom <= 0 else (overall_num / overall_denom) * 100.0

    return {
        "intervals": intervals,
        "overall": {
            "from_cm": round(overall_t0, 1),
            "to_cm": round(overall_t1, 1),
            "denom_cm": round(overall_denom, 1),
            "intact_length_cm": round(overall_num, 1),
            "RQD_%": round(overall_rqd, 1),
            "quality": classify_rqd(overall_rqd),
        },
    }


def compute_rqd_by_tramos(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return compute_rqd_by_intervals(*args, **kwargs)


def compute_rqd_from_piece_lengths(
    run_length_cm: float,
    intact_piece_lengths_cm: list[float],
    threshold_cm: float = 10.0,
) -> dict[str, Any]:
    if run_length_cm <= 0:
        return {"error": "Run length must be greater than zero."}
    if any(length < 0 for length in intact_piece_lengths_cm):
        return {"error": "Piece lengths cannot be negative."}
    if sum(intact_piece_lengths_cm) > run_length_cm:
        return {"error": "Piece lengths cannot exceed the run length."}

    predictions = [_rect_prediction("lane", 0.0, 0.0, run_length_cm, 10.0)]
    cursor = 0.0
    for length in intact_piece_lengths_cm:
        if length > 0:
            predictions.append(_rect_prediction("roca sana", cursor, 0.0, cursor + length, 10.0))
        cursor += length

    return compute_rqd_by_intervals(
        predictions=predictions,
        block_points_xy=[(0.0, 5.0), (run_length_cm, 5.0)],
        img_w=max(1, int(round(run_length_cm))),
        img_h=10,
        n_lanes=1,
        lane_length_cm=run_length_cm,
        threshold_cm=threshold_cm,
        orientation="L2R",
    )


def _intersect_len(seg: tuple[float, float], tramo: tuple[float, float]) -> float:
    a, b = seg
    t0, t1 = tramo
    return max(0.0, min(b, t1) - max(a, t0))


def _rect_prediction(cls: str, x1: float, y1: float, x2: float, y2: float) -> dict[str, Any]:
    return {
        "class": cls,
        "points": [
            {"x": x1, "y": y1},
            {"x": x2, "y": y1},
            {"x": x2, "y": y2},
            {"x": x1, "y": y2},
        ],
    }


def _nearest_index(value: float, candidates: list[float]) -> int:
    return min(range(len(candidates)), key=lambda i: abs(value - candidates[i]))
