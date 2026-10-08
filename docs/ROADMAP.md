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

## Phase 1: GeoCore Core Logger

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

## Phase 2: Rock Mechanics

Features:

- RMR.
- Q-System.
- GSI.
- Discontinuity logging.
- Fracture frequency.
- UCS and point load inputs.
- Transparent calculation sheets and report sections.

## Phase 3: Soil, SPT, CPT, and Laboratory Data

Features:

- Soil logging.
- USCS classification helper.
- SPT entry and corrections.
- CPT data import and basic plots.
- Laboratory samples and tests.
- Grain size, Atterberg limits, moisture, density, strength, consolidation.

## Phase 4: Maps, Sections, and Interoperability

Features:

- GIS map of boreholes.
- GeoJSON import/export.
- AGS import/export.
- Cross sections between boreholes.
- Stratigraphic correlation tools.
- Project-level reports.

## Phase 5: Slope Stability

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

## Phase 6: Advanced Suite

Possible future modules:

- Settlement calculations.
- Shallow and deep foundations.
- Bearing capacity.
- Retaining walls.
- Rock wedge/toppling checks.
- Simple 3D borehole visualization.
- Cloud collaboration.
- Desktop/local packaged app.

