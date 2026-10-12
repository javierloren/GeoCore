# GeoCore Roadmap

This roadmap is intentionally staged. GeoCore should grow into a suite, but the
first releases must produce a complete workflow instead of many unfinished
menus.

## Phase 0: Repository Foundation

Status: started.

- Create the public project structure.
- Define mission, scope, roadmap, license, and contribution rules.
- Keep `RQD_MVP_V0` as the reference prototype until migration.
- Decide the initial technical architecture.

## Phase 1: GeoCore Core Logger Prototype

Target outcome:

`Project -> Borehole -> Core Box -> Recovery/RQD -> Borehole Log -> PDF`

Features:

- Project manager.
- Borehole manager.
- Collar data: ID, coordinates, elevation, azimuth, inclination, date, contractor,
  equipment, groundwater, final depth.
- Lithology intervals.
- Core runs.
- Core box photo upload.
- RQD calculation migrated from `RQD_MVP_V0`.
- Core recovery calculation.
- Manual review and correction.
- Borehole log preview.
- PDF export.
- CSV/Excel export.

This is the first release that can genuinely help a student or engineer produce
a professional deliverable.

## Phase 2: Desktop Foundation

Target outcome:

`GeoCore Desktop -> Local project -> Borehole Manager -> Log Viewer`

Features:

- Desktop shell using Python + PySide6/Qt.
- Project tree similar in spirit to QGIS.
- Local project storage with SQLite/JSON first.
- Reuse of the same `geocore` Python package used by Streamlit.
- Open/save project workflow.
- Foundation for a future `.geocore` project format.

Streamlit remains the prototype/demo interface. Desktop becomes the main product
direction once the core data model and logging workflow are stable.

## Phase 3: Rock Mechanics

Features:

- RMR.
- Q-System.
- GSI.
- Discontinuity logging.
- Fracture frequency.
- UCS and point load inputs.
- Transparent calculation sheets and report sections.

## Phase 4: Soil, SPT, CPT, and Laboratory Data

Features:

- Soil logging.
- USCS classification helper.
- SPT entry and corrections.
- CPT data import and basic plots.
- Laboratory samples and tests.
- Grain size, Atterberg limits, moisture, density, strength, consolidation.

## Phase 5: Maps, Sections, and Interoperability

Features:

- GIS map of boreholes.
- GeoJSON import/export.
- AGS import/export.
- Cross sections between boreholes.
- Stratigraphic correlation tools.
- Project-level reports.

## Phase 6: Slope Stability

Features:

- SSAP-inspired limit equilibrium workflows.
- Geometry editor.
- Soil/rock layers.
- Piezometric line.
- Loads and supports.
- Circular and non-circular slip surfaces.
- Factor of safety reports.
- Verification examples against published/manual calculations.

This module must be treated carefully because wrong results can affect safety.
It needs strong validation before being presented as engineering software.

## Phase 7: Plugin Platform and Advanced Suite

Possible future modules:

- Settlement calculations.
- Shallow and deep foundations.
- Bearing capacity.
- Retaining walls.
- Rock wedge/toppling checks.
- Simple 3D borehole visualization.
- Cloud collaboration.
- Plugin API and plugin manager.
- Packaged installers for Windows, Linux, and macOS.

