# Initial Architecture

GeoCore will start as a Streamlit application because the prototype already uses
Streamlit and it allows fast public deployment. The final product direction is a
downloadable desktop application, likely Python + PySide6/Qt, with Streamlit kept
as a prototype/demo interface.

The code must therefore be organized as a normal Python package so calculations,
reporting, imports, exports, storage, and computer vision can be tested outside
any UI and reused by both Streamlit and the future desktop application.

## Proposed Structure

```text
geocore/
  app/
    streamlit_app.py
    pages/
  desktop/
    main.py
  geocore/
    models/
    storage/
    vision/
    logging/
    calculations/
    reports/
    exports/
  tests/
  docs/
```

## Modules

`models`

Core data structures: project, borehole, lithology interval, core run, sample,
test, groundwater record, discontinuity, and report metadata.

`storage`

Local SQLite/JSON persistence first. Later this can support a `.geocore` project
container and optional PostgreSQL for hosted/demo instances.

`vision`

Image preparation, Roboflow/local model integration, segmentation results, and
manual correction workflows.

`logging`

Soil and rock logging workflows, including lithology intervals, core runs,
samples, and discontinuities.

`calculations`

RQD, core recovery, RMR, Q-System, GSI, SPT corrections, slope stability, and
other engineering calculations.

`reports`

Borehole logs and PDF reports.

`exports`

CSV, Excel, GeoJSON, AGS, and other open formats.

## Desktop Direction

GeoCore Desktop should eventually become the main product:

- Python + PySide6/Qt interface.
- Local project files, with SQLite/DuckDB and project folders or zipped
  `.geocore` packages.
- Local images, PDFs, imported data, and model assets.
- Local computer vision inference where possible.
- No mandatory server dependency.
- Future plugin API for specialist modules.

Streamlit remains useful while the geotechnical core is still moving quickly.
The rule is simple: no engineering calculation should depend on `st.session_state`
or Streamlit widgets.

## First Migration Target

The current `RQD_MVP_V0/app.py` should be split without changing behavior:

- Roboflow and image inference -> `vision`.
- RQD geometry/calculation -> `calculations.rqd`.
- Borehole form defaults -> `models` or `logging`.
- CSV/HTML/report generation -> `reports` and `exports`.
- Streamlit interface -> `app`.

The first migration is successful only if the current RQD workflow still works.

