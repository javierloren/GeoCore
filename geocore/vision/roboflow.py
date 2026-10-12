from __future__ import annotations

import base64
import io
from typing import Any


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


def roboflow_outline_infer(
    image_bytes: bytes,
    dataset_slug: str,
    version: int,
    api_key: str,
    confidence: int = 35,
    overlap: int = 30,
    max_w: int = 1600,
    jpeg_quality: int = 85,
) -> dict[str, Any]:
    url = f"https://outline.roboflow.com/{dataset_slug}/{version}"
    attempts = [
        (max_w, jpeg_quality),
        (1400, min(jpeg_quality, 80)),
        (1200, min(jpeg_quality, 75)),
        (1000, min(jpeg_quality, 70)),
    ]
    last_err = None

    for width, quality in attempts:
        infer_bytes, orig_w, orig_h, inf_w, inf_h = prepare_image_for_inference(
            image_bytes,
            width,
            quality,
        )
        img_b64 = base64.b64encode(infer_bytes).decode("utf-8")

        try:
            import requests

            response = requests.post(
                url,
                params={
                    "api_key": api_key,
                    "confidence": confidence,
                    "overlap": overlap,
                },
                data=img_b64,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=60,
            )
            if response.status_code == 413:
                last_err = RuntimeError("Image too large. Retrying with stronger compression.")
                continue

            response.raise_for_status()
            sx = orig_w / float(inf_w)
            sy = orig_h / float(inf_h)
            return rescale_predictions_to_original(response.json(), sx, sy, orig_w, orig_h)
        except Exception as exc:
            last_err = exc
            response = getattr(exc, "response", None)
            if response is not None and 400 <= response.status_code < 500 and response.status_code != 413:
                break

    raise RuntimeError("Inference could not be completed.") from last_err
