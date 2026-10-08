import streamlit as st
import streamlit.components.v1 as components

from geocore.reports.borehole_log import borehole_log_svg
from geocore.sample_data import demo_project


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
          <div class="gc-module"><strong>Core Logging</strong><span>Core box photographs, recovery, RQD, discontinuity review.</span><small>Next</small></div>
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
    st.info("The next implementation step is migrating the RQD vision workflow from RQD_MVP_V0 into this module.")


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
elif module == "Log Viewer":
    log_viewer(project)
elif module == "Analysis Center":
    analysis_center()
else:
    reports_center()

