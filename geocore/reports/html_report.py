from __future__ import annotations

import html

from geocore.models import Borehole, Project
from geocore.reports.borehole_log import borehole_log_svg


def borehole_report_html(project: Project, borehole: Borehole) -> str:
    title = f"{project.name} - {borehole.borehole_id}"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{_esc(title)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; color: #1f2937; margin: 28px; }}
    h1 {{ font-size: 22px; margin: 0 0 4px; }}
    h2 {{ font-size: 15px; margin: 22px 0 8px; }}
    .muted {{ color: #667085; }}
    .meta {{ display: grid; grid-template-columns: repeat(4, 1fr); border: 1px solid #111827; border-bottom: 0; margin-top: 16px; }}
    .meta div {{ min-height: 42px; border-right: 1px solid #111827; border-bottom: 1px solid #111827; padding: 6px; }}
    .meta div:nth-child(4n) {{ border-right: 0; }}
    .meta strong {{ display: block; font-size: 10px; text-transform: uppercase; }}
    .meta span {{ font-size: 12px; }}
    table {{ width: 100%; border-collapse: collapse; table-layout: fixed; }}
    th, td {{ border: 1px solid #111827; padding: 5px; font-size: 10px; vertical-align: top; word-wrap: break-word; }}
    th {{ background: #eef2f5; text-transform: uppercase; }}
    .log {{ border: 1px solid #cfd6df; margin-top: 10px; }}
    @media print {{ body {{ margin: 14mm; }} }}
  </style>
</head>
<body>
  <h1>GeoCore Borehole Report</h1>
  <p class="muted">{_esc(title)}</p>
  <section class="meta">
    {_meta("Project", project.name)}
    {_meta("Client", project.client)}
    {_meta("Location", project.location)}
    {_meta("CRS", project.coordinate_reference_system)}
    {_meta("Borehole", borehole.borehole_id)}
    {_meta("X", borehole.x)}
    {_meta("Y", borehole.y)}
    {_meta("Z", borehole.z)}
    {_meta("Final depth", _fmt_m(borehole.final_depth_m))}
    {_meta("Groundwater", _fmt_m(borehole.groundwater_depth_m))}
    {_meta("Average recovery", _fmt_percent(borehole.average_recovery_percent))}
    {_meta("Average RQD", _fmt_percent(borehole.average_rqd_percent))}
  </section>

  <h2>Borehole Log</h2>
  <div class="log">{borehole_log_svg(borehole)}</div>

  <h2>Lithology</h2>
  {_lithology_table(borehole)}

  <h2>Core Runs</h2>
  {_core_runs_table(borehole)}
</body>
</html>
"""


def _lithology_table(borehole: Borehole) -> str:
    rows = [
        "<tr><th>From (m)</th><th>To (m)</th><th>Lithology</th><th>Description</th><th>Weathering</th><th>Strength</th></tr>"
    ]
    for interval in borehole.lithology:
        rows.append(
            "<tr>"
            f"<td>{interval.from_m:.2f}</td>"
            f"<td>{interval.to_m:.2f}</td>"
            f"<td>{_esc(interval.lithology)}</td>"
            f"<td>{_esc(interval.description)}</td>"
            f"<td>{_esc(interval.weathering)}</td>"
            f"<td>{_esc(interval.strength)}</td>"
            "</tr>"
        )
    return f"<table>{''.join(rows)}</table>"


def _core_runs_table(borehole: Borehole) -> str:
    rows = [
        "<tr><th>From (m)</th><th>To (m)</th><th>Run length (m)</th><th>Recovered (m)</th><th>Recovery (%)</th><th>RQD (%)</th><th>Validated</th></tr>"
    ]
    for run in borehole.core_runs:
        rows.append(
            "<tr>"
            f"<td>{run.from_m:.2f}</td>"
            f"<td>{run.to_m:.2f}</td>"
            f"<td>{run.run_length_m:.2f}</td>"
            f"<td>{'' if run.recovered_length_m is None else f'{run.recovered_length_m:.2f}'}</td>"
            f"<td>{_fmt_percent(run.recovery_percent)}</td>"
            f"<td>{_fmt_percent(run.rqd_percent)}</td>"
            f"<td>{'Yes' if run.validated else 'No'}</td>"
            "</tr>"
        )
    return f"<table>{''.join(rows)}</table>"


def _meta(label: str, value: object) -> str:
    return f"<div><strong>{_esc(label)}</strong><span>{_esc(value)}</span></div>"


def _fmt_m(value: float | None) -> str:
    return "" if value is None else f"{value:.2f} m"


def _fmt_percent(value: float | None) -> str:
    return "" if value is None else f"{value:.1f}%"


def _esc(value: object) -> str:
    return html.escape("" if value is None else str(value))
