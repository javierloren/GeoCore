from __future__ import annotations

import html

from geocore.models import Borehole, LithologyInterval


LITHOLOGY_COLORS = {
    "fill": "#c8ad7f",
    "clay": "#c87b9b",
    "sand": "#e5c84c",
    "gravel": "#d59d45",
    "weathered granite": "#92b47c",
    "granite": "#8fb8c9",
}


def _lithology_color(interval: LithologyInterval) -> str:
    name = interval.lithology.lower()
    for key, color in LITHOLOGY_COLORS.items():
        if key in name:
            return color
    return "#d5d8dc"


def borehole_log_svg(borehole: Borehole, height: int = 660) -> str:
    depth = borehole.final_depth_m or _max_logged_depth(borehole)
    depth = max(depth, 1.0)
    top = 58
    bottom = 36
    plot_h = height - top - bottom
    scale = plot_h / depth

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 {height}" role="img">',
        '<rect width="760" height="100%" fill="#ffffff"/>',
        '<text x="18" y="24" font-size="15" font-family="Arial" font-weight="700" fill="#1f2937">',
        html.escape(borehole.borehole_id),
        "</text>",
        '<text x="18" y="43" font-size="11" font-family="Arial" fill="#4b5563">',
        f"Depth {depth:.1f} m",
        "</text>",
        _header("Depth", 22),
        _header("Lithology", 92),
        _header("Description", 220),
        _header("Recovery", 520),
        _header("RQD", 630),
        f'<rect x="16" y="{top}" width="720" height="{plot_h}" fill="none" stroke="#1f2937" stroke-width="1"/>',
        _vline(78, top, plot_h),
        _vline(206, top, plot_h),
        _vline(506, top, plot_h),
        _vline(616, top, plot_h),
    ]

    tick_step = 1.0 if depth <= 25 else 2.0
    tick = 0.0
    while tick <= depth + 0.001:
        y = top + tick * scale
        parts.append(f'<line x1="16" y1="{y:.1f}" x2="736" y2="{y:.1f}" stroke="#e5e7eb" stroke-width="0.8"/>')
        parts.append(f'<text x="50" y="{y + 3:.1f}" font-size="9" font-family="Arial" text-anchor="middle" fill="#374151">{tick:g}</text>')
        tick += tick_step

    for interval in borehole.lithology:
        start = max(0.0, interval.from_m)
        end = min(depth, interval.to_m)
        if end <= start:
            continue
        y = top + start * scale
        h = max(8.0, (end - start) * scale)
        color = _lithology_color(interval)
        label = html.escape(interval.lithology)
        description = html.escape(interval.description)
        parts.extend(
            [
                f'<rect x="78" y="{y:.1f}" width="128" height="{h:.1f}" fill="{color}" stroke="#1f2937" stroke-width="0.7"/>',
                f'<text x="84" y="{y + 15:.1f}" font-size="10" font-family="Arial" fill="#111827">{label}</text>',
                f'<text x="216" y="{y + 15:.1f}" font-size="10" font-family="Arial" fill="#111827">{description[:64]}</text>',
                f'<line x1="16" y1="{y:.1f}" x2="736" y2="{y:.1f}" stroke="#1f2937" stroke-width="0.7"/>',
            ]
        )

    for run in borehole.core_runs:
        start = max(0.0, run.from_m)
        end = min(depth, run.to_m)
        if end <= start:
            continue
        y = top + start * scale
        h = max(8.0, (end - start) * scale)
        rec = run.recovery_percent
        rqd = run.rqd_percent
        if rec is not None:
            bar_w = max(0.0, min(1.0, rec / 100.0)) * 88
            parts.append(f'<rect x="516" y="{y + 3:.1f}" width="{bar_w:.1f}" height="{max(4.0, h - 6):.1f}" fill="#2f7d6d"/>')
            parts.append(f'<text x="560" y="{y + 15:.1f}" font-size="9" font-family="Arial" text-anchor="middle" fill="#111827">{rec:.0f}%</text>')
        if rqd is not None:
            bar_w = max(0.0, min(1.0, rqd / 100.0)) * 88
            parts.append(f'<rect x="626" y="{y + 3:.1f}" width="{bar_w:.1f}" height="{max(4.0, h - 6):.1f}" fill="#5f6fb1"/>')
            parts.append(f'<text x="670" y="{y + 15:.1f}" font-size="9" font-family="Arial" text-anchor="middle" fill="#111827">{rqd:.0f}%</text>')

    if borehole.groundwater_depth_m is not None:
        y = top + borehole.groundwater_depth_m * scale
        parts.append(f'<line x1="16" y1="{y:.1f}" x2="736" y2="{y:.1f}" stroke="#2563eb" stroke-width="1.6" stroke-dasharray="5 4"/>')
        parts.append(f'<text x="704" y="{y - 5:.1f}" font-size="10" font-family="Arial" text-anchor="end" fill="#1d4ed8">GW {borehole.groundwater_depth_m:.1f} m</text>')

    parts.append("</svg>")
    return "".join(parts)


def _max_logged_depth(borehole: Borehole) -> float:
    values = [0.0]
    values.extend(interval.to_m for interval in borehole.lithology)
    values.extend(run.to_m for run in borehole.core_runs)
    return max(values)


def _header(label: str, x: int) -> str:
    return f'<text x="{x}" y="54" font-size="10" font-family="Arial" font-weight="700" fill="#374151">{html.escape(label)}</text>'


def _vline(x: int, top: int, plot_h: int) -> str:
    return f'<line x1="{x}" y1="{top}" x2="{x}" y2="{top + plot_h}" stroke="#1f2937" stroke-width="1"/>'

