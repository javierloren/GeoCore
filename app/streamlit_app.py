import hashlib
import io

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, ImageDraw
from streamlit_image_coordinates import streamlit_image_coordinates

from geocore.calculations import compute_rqd_by_intervals, compute_rqd_from_piece_lengths
from geocore.reports.borehole_log import borehole_log_svg
from geocore.sample_data import demo_project
from geocore.vision import roboflow_outline_infer


DEFAULT_ROBOFLOW_DATASET_SLUG = "software-szwke"
DEFAULT_ROBOFLOW_MODEL_VERSION = 3
DEFAULT_ROBOFLOW_CONFIDENCE = 35
DEFAULT_ROBOFLOW_OVERLAP = 30


st.set_page_config(page_title="GeoCore", layout="wide")


def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --gc-ink: #1f2937;
            --gc-muted: #667085;
            --gc-border: #cfd6df;
            --gc-ribbon: #e9edf2;
            --gc-teal: #2f7d6d;
            --gc-violet: #5f6fb1;
        }
        .block-container {
            padding-top: 1rem;
            padding-bottom: 2rem;
            max-width: 1500px;
        }
        h1, h2, h3 {
            letter-spacing: 0;
        }
        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid var(--gc-border);
            border-radius: 6px;
            padding: 0.65rem 0.8rem;
        }
        section[data-testid="stSidebar"] {
            background: #eef2f5;
            border-right: 1px solid var(--gc-border);
        }
        .gc-titlebar {
            border: 1px solid var(--gc-border);
            border-radius: 6px;
            padding: 0.7rem 0.9rem;
            background: linear-gradient(180deg, #ffffff, #f6f8fb);
            margin-bottom: 0.65rem;
        }
        .gc-titlebar h1 {
            margin: 0;
            font-size: 1.35rem;
            color: var(--gc-ink);
        }
        .gc-titlebar p {
            margin: 0.15rem 0 0;
            color: var(--gc-muted);
            font-size: 0.9rem;
        }
        .gc-ribbon {
            display: grid;
            grid-template-columns: repeat(6, minmax(110px, 1fr));
            gap: 0.4rem;
            border: 1px solid var(--gc-border);
            border-radius: 6px;
            background: var(--gc-ribbon);
            padding: 0.45rem;
            margin-bottom: 0.8rem;
        }
        .gc-ribbon-item {
            background: #ffffff;
            border: 1px solid #d8dee6;
            border-radius: 5px;
            padding: 0.45rem 0.55rem;
            min-height: 54px;
        }
        .gc-ribbon-item strong {
            display: block;
            color: var(--gc-ink);
            font-size: 0.82rem;
            line-height: 1.1;
        }
        .gc-ribbon-item span {
            color: var(--gc-muted);
            font-size: 0.72rem;
        }
        .gc-panel {
            border: 1px solid var(--gc-border);
            border-radius: 6px;
            background: #ffffff;
            padding: 0.85rem;
        }
        .gc-panel-title {
            margin: 0 0 0.55rem;
            font-size: 0.95rem;
            font-weight: 700;
            color: var(--gc-ink);
        }
        .gc-status {
            display: flex;
            gap: 0.45rem;
            flex-wrap: wrap;
            margin-top: 0.45rem;
        }
        .gc-tag {
            border: 1px solid #d8dee6;
            border-radius: 999px;
            padding: 0.14rem 0.55rem;
            background: #ffffff;
            color: #344054;
            font-size: 0.75rem;
        }
        .gc-module-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.65rem;
        }
        .gc-module {
            border: 1px solid var(--gc-border);
            border-left: 4px solid var(--gc-teal);
            border-radius: 6px;
            padding: 0.75rem;
            background: #ffffff;
            min-height: 96px;
        }
        .gc-module strong {
            display: block;
            color: var(--gc-ink);
            font-size: 0.93rem;
        }
        .gc-module span {
            display: block;
            color: var(--gc-muted);
            margin-top: 0.2rem;
            font-size: 0.8rem;
        }
        .gc-module small {
            display: inline-block;
            margin-top: 0.55rem;
            color: #ffffff;
            background: var(--gc-violet);
            border-radius: 4px;
            padding: 0.1rem 0.35rem;
            font-size: 0.7rem;
        }
        @media (max-width: 900px) {
            .gc-ribbon,
            .gc-module-grid {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def titlebar() -> None:
    st.markdown(
        """
        <div class="gc-titlebar">
          <h1>GeoCore Workbench</h1>
          <p>Open-source geotechnical suite for boreholes, logs, reports, rock mechanics, and slope stability.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def ribbon() -> None:
    items = [
        ("New Borehole", "Create collar and drilling record"),
        ("Import Data", "CSV, Excel, AGS planned"),
        ("Core Box Vision", "RQD and recovery workflow"),
        ("Build Log", "Preview professional borehole log"),
        ("Export Report", "PDF workflow planned"),
        ("Validate", "Traceable calculation checks"),
    ]
    html = '<div class="gc-ribbon">'
    for title, caption in items:
        html += f'<div class="gc-ribbon-item"><strong>{title}</strong><span>{caption}</span></div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def project_dashboard(project) -> None:
    cols = st.columns(4)
    boreholes = project.boreholes
    total_depth = sum((bh.final_depth_m or 0.0) for bh in boreholes)
    avg_rqd_values = [bh.average_rqd_percent for bh in boreholes if bh.average_rqd_percent is not None]
    avg_rqd = sum(avg_rqd_values) / len(avg_rqd_values) if avg_rqd_values else None
    cols[0].metric("Boreholes", len(boreholes))
    cols[1].metric("Total drilled depth", f"{total_depth:.1f} m")
    cols[2].metric("Average RQD", "-" if avg_rqd is None else f"{avg_rqd:.0f}%")
    cols[3].metric("Reports", "0 ready")

    st.markdown("#### Suite Modules")
    st.markdown(
        """
        <div class="gc-module-grid">
          <div class="gc-module"><strong>Borehole Manager</strong><span>Collars, surveys, lithology, groundwater, samples, runs.</span><small>Active</small></div>
          <div class="gc-module"><strong>Core Box Vision</strong><span>Upload core photographs, review segmentation, calculate RQD.</span><small>Active</small></div>
          <div class="gc-module"><strong>Log Designer</strong><span>Professional borehole logs with tracks and templates.</span><small>Started</small></div>
          <div class="gc-module"><strong>Rock Mechanics</strong><span>RMR, Q-System, GSI, fracture frequency and UCS inputs.</span><small>Planned</small></div>
          <div class="gc-module"><strong>Slope Stability</strong><span>SSAP-style limit equilibrium workflows and validation cases.</span><small>Planned</small></div>
          <div class="gc-module"><strong>Stereonet Tools</strong><span>Dips-style discontinuity sets, poles, great circles and kinematic checks.</span><small>Planned</small></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def borehole_manager(project) -> None:
    rows = []
    for bh in project.boreholes:
        rows.append(
            {
                "ID": bh.borehole_id,
                "X": bh.x,
                "Y": bh.y,
                "Z": bh.z,
                "Final depth (m)": bh.final_depth_m,
                "GW (m)": bh.groundwater_depth_m,
                "Avg recovery (%)": _fmt_percent(bh.average_recovery_percent),
                "Avg RQD (%)": _fmt_percent(bh.average_rqd_percent),
            }
        )
    st.markdown('<div class="gc-panel"><p class="gc-panel-title">Borehole database</p>', unsafe_allow_html=True)
    st.data_editor(rows, use_container_width=True, hide_index=True, num_rows="dynamic")
    st.markdown("</div>", unsafe_allow_html=True)


def core_logging(project) -> None:
    borehole = select_borehole(project)
    st.markdown("#### Core Runs")
    rows = [
        {
            "From (m)": run.from_m,
            "To (m)": run.to_m,
            "Run length (m)": run.run_length_m,
            "Recovered (m)": run.recovered_length_m,
            "Recovery (%)": _fmt_percent(run.recovery_percent),
            "RQD (%)": run.rqd_percent,
            "Validated": run.validated,
        }
        for run in borehole.core_runs
    ]
    st.data_editor(rows, use_container_width=True, hide_index=True, num_rows="dynamic")

    st.markdown("#### Manual RQD Calculator")
    c1, c2, c3 = st.columns([0.18, 0.18, 0.64])
    run_length_cm = c1.number_input("Run length (cm)", min_value=1.0, value=150.0, step=1.0)
    threshold_cm = c2.number_input("Threshold (cm)", min_value=1.0, value=10.0, step=1.0)
    pieces_text = c3.text_input("Intact pieces (cm)", value="8, 12, 25, 5, 30")
    pieces = _parse_float_list(pieces_text)
    if pieces is None:
        st.warning("Use comma-separated numeric lengths, for example: 8, 12, 25, 5, 30")
    else:
        result = compute_rqd_from_piece_lengths(run_length_cm, pieces, threshold_cm)
        if "error" in result:
            st.warning(result["error"])
        else:
            overall = result["overall"]
            m1, m2, m3 = st.columns(3)
            m1.metric("RQD", f'{overall["RQD_%"]:.1f}%')
            m2.metric("Intact >= threshold", f'{overall["intact_length_cm"]:.1f} cm')
            m3.metric("Quality", overall["quality"])
            st.dataframe(result["intervals"], use_container_width=True, hide_index=True)

    st.markdown("#### Core Box Vision")
    core_box_vision_panel()


def core_box_vision_panel() -> None:
    _init_core_box_state()

    api_key = st.secrets.get("ROBOFLOW_API_KEY", "")
    dataset_slug = (st.secrets.get("ROBOFLOW_DATASET_SLUG", DEFAULT_ROBOFLOW_DATASET_SLUG) or "").strip()
    version = int(st.secrets.get("ROBOFLOW_MODEL_VERSION", DEFAULT_ROBOFLOW_MODEL_VERSION))
    confidence = int(st.secrets.get("ROBOFLOW_CONFIDENCE", DEFAULT_ROBOFLOW_CONFIDENCE))
    overlap = int(st.secrets.get("ROBOFLOW_OVERLAP", DEFAULT_ROBOFLOW_OVERLAP))

    config_cols = st.columns([0.16, 0.16, 0.16, 0.16, 0.36])
    orientation_ui = config_cols[0].selectbox("Orientation", ["L->R", "R->L"])
    n_lanes = config_cols[1].number_input("Rows", min_value=1, max_value=8, value=4, step=1)
    lane_length_cm = config_cols[2].number_input("Row length (cm)", min_value=10.0, value=60.0, step=1.0)
    threshold_cm = config_cols[3].number_input("RQD threshold (cm)", min_value=1.0, value=10.0, step=1.0)
    uploaded = config_cols[4].file_uploader("Core box photo", type=["jpg", "jpeg", "png"])
    st.caption(f"Roboflow model: `{dataset_slug}/{version}` | Confidence: {confidence}% | Overlap: {overlap}%")

    if uploaded is not None:
        image_bytes = uploaded.getvalue()
        image_hash = hashlib.sha256(image_bytes).hexdigest()
        if st.session_state.corebox_image_hash != image_hash:
            st.session_state.corebox_image_hash = image_hash
            st.session_state.corebox_image_bytes = image_bytes
            st.session_state.corebox_points = []
            st.session_state.corebox_last_click = None
            st.session_state.corebox_click_key += 1
            st.session_state.corebox_result = None

    if st.session_state.corebox_image_bytes is None:
        st.info("Upload a core box photograph to calculate RQD from image segmentation.")
        return

    image_bytes = st.session_state.corebox_image_bytes
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img_w, img_h = image.size

    left, right = st.columns([0.58, 0.42])
    with left:
        st.caption("Click the center of each core block/taco that defines the calculation intervals.")
        display, scale = _display_image_with_points(image, st.session_state.corebox_points)
        coords = streamlit_image_coordinates(
            display,
            key=f"corebox_clicks_{st.session_state.corebox_click_key}",
            width=display.size[0],
        )
        if coords and "x" in coords and "y" in coords:
            x_orig = float(coords["x"]) / scale
            y_orig = float(coords["y"]) / scale
            sig = (round(x_orig, 1), round(y_orig, 1))
            if sig != st.session_state.corebox_last_click:
                st.session_state.corebox_points.append((x_orig, y_orig))
                st.session_state.corebox_last_click = sig
                st.rerun()

        c1, c2, c3 = st.columns([0.2, 0.2, 0.6])
        c1.write(f"Blocks: **{len(st.session_state.corebox_points)}**")
        if c2.button("Undo", disabled=not st.session_state.corebox_points, use_container_width=True):
            st.session_state.corebox_points.pop()
            st.session_state.corebox_click_key += 1
            st.session_state.corebox_result = None
            st.rerun()
        if c3.button("Clear selected blocks", disabled=not st.session_state.corebox_points, use_container_width=True):
            st.session_state.corebox_points = []
            st.session_state.corebox_click_key += 1
            st.session_state.corebox_result = None
            st.rerun()

    with right:
        if not api_key:
            st.warning("Roboflow API key is missing. Add ROBOFLOW_API_KEY to Streamlit secrets to process uploaded photos.")
            return

        pred = _get_or_run_inference(image_bytes, dataset_slug, version, api_key, confidence, overlap)
        predictions = pred.get("predictions", []) if pred else []
        st.image(_overlay_predictions(image, predictions), caption="Segmentation overlay", use_container_width=True)

        can_calc = len(st.session_state.corebox_points) >= 2 and len(predictions) > 0
        if st.button("Calculate image RQD", type="primary", disabled=not can_calc, use_container_width=True):
            st.session_state.corebox_result = compute_rqd_by_intervals(
                predictions=predictions,
                block_points_xy=st.session_state.corebox_points,
                img_w=img_w,
                img_h=img_h,
                n_lanes=int(n_lanes),
                lane_length_cm=float(lane_length_cm),
                threshold_cm=float(threshold_cm),
                orientation="L2R" if orientation_ui.startswith("L") else "R2L",
            )

        if st.session_state.corebox_result:
            result = st.session_state.corebox_result
            if "error" in result:
                st.warning(result["error"])
            else:
                overall = result["overall"]
                st.metric("Image RQD", f'{overall["RQD_%"]:.1f}%', help=overall["quality"])
                st.caption(
                    f'Denominator: {overall["denom_cm"]} cm | Intact >= {threshold_cm:.0f} cm: {overall["intact_length_cm"]} cm'
                )
                st.dataframe(result["intervals"], use_container_width=True, hide_index=True)


def log_viewer(project) -> None:
    borehole = select_borehole(project)
    left, right = st.columns([0.62, 0.38])
    with left:
        st.markdown("#### Borehole Log Preview")
        components.html(borehole_log_svg(borehole), height=700, scrolling=False)
    with right:
        st.markdown("#### Lithology Intervals")
        st.dataframe(
            [
                {
                    "From": interval.from_m,
                    "To": interval.to_m,
                    "Lithology": interval.lithology,
                    "Description": interval.description,
                }
                for interval in borehole.lithology
            ],
            use_container_width=True,
            hide_index=True,
        )
        st.markdown("#### Report Tracks")
        st.checkbox("Depth scale", value=True)
        st.checkbox("Lithology", value=True)
        st.checkbox("Description", value=True)
        st.checkbox("Recovery", value=True)
        st.checkbox("RQD", value=True)
        st.checkbox("Groundwater", value=True)


def analysis_center() -> None:
    st.markdown("#### Engineering Analysis Center")
    st.markdown(
        """
        <div class="gc-module-grid">
          <div class="gc-module"><strong>RMR</strong><span>Uses RQD, UCS, spacing, discontinuity condition and groundwater.</span><small>Planned</small></div>
          <div class="gc-module"><strong>Q-System</strong><span>RQD/Jn, Jr/Ja, Jw/SRF with transparent calculation report.</span><small>Planned</small></div>
          <div class="gc-module"><strong>GSI</strong><span>Guided visual classification and chart-based support.</span><small>Planned</small></div>
          <div class="gc-module"><strong>Slope Stability</strong><span>Limit equilibrium geometry, layers, water and slip surfaces.</span><small>Planned</small></div>
          <div class="gc-module"><strong>Stereonet</strong><span>Dips-style structural geology plotting and kinematic checks.</span><small>Planned</small></div>
          <div class="gc-module"><strong>SPT/CPT</strong><span>In-situ testing tables, corrections and depth plots.</span><small>Planned</small></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def reports_center() -> None:
    st.markdown("#### Reports and Exports")
    st.write("Planned deliverables for V1.0:")
    st.table(
        [
            {"Output": "Borehole PDF", "Status": "Next", "Content": "Header, log, RQD/recovery, photos, notes"},
            {"Output": "Project PDF", "Status": "Planned", "Content": "All boreholes, summary tables, annexes"},
            {"Output": "CSV/Excel", "Status": "Planned", "Content": "Project, boreholes, lithology, runs, tests"},
            {"Output": "AGS", "Status": "Future", "Content": "Professional geotechnical interchange"},
            {"Output": "GeoJSON", "Status": "Future", "Content": "Borehole map data"},
        ]
    )


def select_borehole(project):
    selected_id = st.selectbox("Active borehole", [bh.borehole_id for bh in project.boreholes])
    return next(bh for bh in project.boreholes if bh.borehole_id == selected_id)


def _fmt_percent(value: float | None) -> str:
    return "-" if value is None else f"{value:.0f}"


def _parse_float_list(value: str) -> list[float] | None:
    try:
        return [float(item.strip().replace(",", ".")) for item in value.replace(";", ",").split(",") if item.strip()]
    except ValueError:
        return None


def _init_core_box_state() -> None:
    defaults = {
        "corebox_image_bytes": None,
        "corebox_image_hash": None,
        "corebox_points": [],
        "corebox_last_click": None,
        "corebox_click_key": 0,
        "corebox_pred_cache": None,
        "corebox_pred_cache_key": None,
        "corebox_result": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _display_image_with_points(image: Image.Image, points: list[tuple[float, float]]) -> tuple[Image.Image, float]:
    base_max_w = 950
    scale = min(1.0, base_max_w / float(image.size[0]))
    display = image.resize((int(image.size[0] * scale), int(image.size[1] * scale)), Image.LANCZOS)
    draw = ImageDraw.Draw(display)
    for idx, (x0, y0) in enumerate(points, start=1):
        x, y = x0 * scale, y0 * scale
        draw.ellipse((x - 8, y - 8, x + 8, y + 8), outline="lime", width=3)
        draw.text((x + 10, y - 10), str(idx), fill="lime")
    return display, scale


def _get_or_run_inference(
    image_bytes: bytes,
    dataset_slug: str,
    version: int,
    api_key: str,
    confidence: int,
    overlap: int,
) -> dict:
    cache_key = (hashlib.sha256(image_bytes).hexdigest(), dataset_slug, version, confidence, overlap)
    if st.session_state.corebox_pred_cache_key == cache_key:
        return st.session_state.corebox_pred_cache

    try:
        with st.spinner("Processing image..."):
            pred = roboflow_outline_infer(
                image_bytes=image_bytes,
                dataset_slug=dataset_slug,
                version=version,
                api_key=api_key,
                confidence=confidence,
                overlap=overlap,
            )
    except Exception:
        st.error("The image could not be processed. Check Roboflow secrets and try again.")
        pred = {"predictions": []}

    st.session_state.corebox_pred_cache = pred
    st.session_state.corebox_pred_cache_key = cache_key
    return pred


def _overlay_predictions(image: Image.Image, predictions: list[dict]) -> Image.Image:
    overlay = image.copy()
    draw = ImageDraw.Draw(overlay)
    color_map = {
        "roca sana": "magenta",
        "roca_sana": "magenta",
        "rocasana": "magenta",
        "fracturas": "red",
        "fractura": "red",
        "suelo": "cyan",
        "soil": "cyan",
    }
    for prediction in predictions:
        pts = prediction.get("points", [])
        cls = (prediction.get("class") or "").strip().lower()
        poly = [(point["x"], point["y"]) for point in pts if "x" in point and "y" in point]
        if len(poly) >= 3:
            draw.polygon(poly, outline=color_map.get(cls, "yellow"), width=2)
    return overlay


inject_css()

if "project" not in st.session_state:
    st.session_state.project = demo_project()

project = st.session_state.project

with st.sidebar:
    st.markdown("### GeoCore")
    st.caption("Project workspace")
    module = st.radio(
        "Module",
        [
            "Project Dashboard",
            "Borehole Manager",
            "Core Logging",
            "Core Box Vision",
            "Log Viewer",
            "Analysis Center",
            "Reports",
        ],
    )
    st.markdown("---")
    st.text_input("Project", value=project.name)
    st.text_input("Client", value=project.client)
    st.text_input("CRS", value=project.coordinate_reference_system)
    st.markdown(
        '<div class="gc-status"><span class="gc-tag">Local demo data</span><span class="gc-tag">V0.1 workbench</span></div>',
        unsafe_allow_html=True,
    )

titlebar()
ribbon()

if module == "Project Dashboard":
    project_dashboard(project)
elif module == "Borehole Manager":
    borehole_manager(project)
elif module == "Core Logging":
    core_logging(project)
elif module == "Core Box Vision":
    st.markdown("#### Core Box Vision")
    core_box_vision_panel()
elif module == "Log Viewer":
    log_viewer(project)
elif module == "Analysis Center":
    analysis_center()
else:
    reports_center()

