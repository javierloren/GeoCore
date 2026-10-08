# GeoCore

GeoCore is an open-source geotechnical engineering suite in early development.
Its goal is to make professional geotechnical workflows accessible to students,
universities, small consultants, and practitioners who cannot afford expensive
commercial licenses.

The project starts from the ideas and prototype work in `RQD_MVP_V0`: image-based
RQD calculation from core box photographs, borehole registration, stratigraphic
columns, and report exports.

## Mission

Build a free, transparent, and extensible alternative for common geotechnical
workflows:

- Borehole and project management.
- Soil and rock logging.
- Core box image analysis.
- Core recovery and RQD calculation.
- Borehole log generation.
- Professional PDF reports.
- Rock mass classifications such as RMR, Q-System, and GSI.
- SPT/CPT and laboratory data management.
- GIS maps, cross sections, and interoperability.
- Slope stability and other geotechnical calculation modules.

GeoCore will not begin by trying to replace advanced finite element products.
The first target is the workflow covered by tools such as RSLog, LogPlot,
gINT/OpenGround, HoleBASE, RockWorks, and parts of Leapfrog Works: structured
geotechnical data, logs, reports, maps, and interpretation.

## Product Principle

GeoCore should be professional, but not opaque.

Every calculation must be traceable. The software can assist with AI, computer
vision, and automation, but the geologist or engineer must remain in control:

`AI suggests -> user validates -> GeoCore records and reports.`

## Current Status

This repository is the new project home. The original prototype is currently
kept outside this repository as `RQD_MVP_V0` and will be migrated carefully into
a modular architecture.

## Run Locally

```bash
python -m streamlit run app/streamlit_app.py
```

## First Milestone

The first usable release will focus on:

`Project -> Borehole -> Core Logging -> Recovery + RQD -> Borehole Log -> PDF`

This gives users a complete workflow from field/core-box data to a professional
deliverable.

## License

GeoCore is intended to be free and open source. See [LICENSE](LICENSE).
