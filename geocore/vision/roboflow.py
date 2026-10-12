from __future__ import annotations

import base64
import io
import time
from typing import Any


class RoboflowInferenceError(RuntimeError):
    pass


def prepare_image_for_inference(
    image_bytes: bytes,
    max_w: int,
    jpeg_quality: int,
) -> tuple[bytes, int, int, int, int]:
    from PIL import Image

    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    orig_w, orig_h = image.size

    scale = min(1.0, max_w / float(orig_w))
    if scale < 1.0:
        image = image.resize((int(orig_w * scale), int(orig_h * scale)), Image.LANCZOS)

    inf_w, inf_h = image.size

    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=jpeg_quality, optimize=True)
    return buf.getvalue(), orig_w, orig_h, inf_w, inf_h


def rescale_predictions_to_original(
    pred: dict[str, Any],
    sx: float,
    sy: float,
    orig_w: int,
    orig_h: int,
) -> dict[str, Any]:
    for item in pred.get("predictions", []):
        points = item.get("points")
        if isinstance(points, list):
            for point in points:
                if isinstance(point, dict):
                    if "x" in point:
                        point["x"] = float(point["x"]) * sx
                    if "y" in point:
                        point["y"] = float(point["y"]) * sy

        if "x" in item:
            item["x"] = float(item["x"]) * sx
        if "y" in item:
            item["y"] = float(item["y"]) * sy
        if "width" in item:
            item["width"] = float(item["width"]) * sx
        if "height" in item:
            item["height"] = float(item["height"]) * sy

    pred["image"] = {"width": orig_w, "height": orig_h}
    return pred


def roboflow_workflow_infer(
    image_bytes: bytes,
    workspace_name: str,
    workflow_id: str,
    api_key: str,
    parameters: dict[str, Any] | None = None,
    timeout: int = 60,
    retries: int = 2,
) -> dict[str, Any]:
    img_b64 = base64.b64encode(image_bytes).decode("utf-8")
    payload = {
        "inputs": {"image": {"type": "base64", "value": img_b64}},
        "parameters": parameters or {},
    }
    url = f"https://serverless.roboflow.com/{workspace_name}/workflows/{workflow_id}"
    last_err = None

    for attempt in range(retries + 1):
        try:
            import requests

            response = requests.post(
                url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                timeout=timeout,
            )
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            last_err = exc
            if attempt < retries:
                time.sleep(0.5 * (2**attempt))

    raise RoboflowInferenceError("Roboflow workflow inference failed.") from last_err


def extract_first_predictions(response: Any) -> list[dict[str, Any]]:
    found = _find_prediction_lists(response)
    return found[0] if found else []


def _find_prediction_lists(value: Any) -> list[list[dict[str, Any]]]:
    if isinstance(value, dict):
        matches = []
        predictions = value.get("predictions")
        if _looks_like_predictions(predictions):
            matches.append(predictions)
        for child in value.values():
            matches.extend(_find_prediction_lists(child))
        return matches
    if isinstance(value, list):
        matches = []
        for item in value:
            matches.extend(_find_prediction_lists(item))
        return matches
    return []


def _looks_like_predictions(value: Any) -> bool:
    return (
        isinstance(value, list)
        and all(isinstance(item, dict) for item in value)
        and any("points" in item or "x" in item or "width" in item for item in value)
    )
