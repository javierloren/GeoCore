# Initial Architecture

GeoCore will start as a Streamlit application because the prototype already uses
Streamlit and it allows fast public deployment. The code must still be organized
as a normal Python package so that calculations, reporting, and data models can
be tested outside the UI.

## Proposed Structure

```text
geocore/
  app/
    streamlit_app.py
    pages/
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

Local SQLite/JSON persistence first. Later this can support PostgreSQL for a
public hosted instance.

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

## First Migration Target

The current `RQD_MVP_V0/app.py` should be split without changing behavior:

- Roboflow and image inference -> `vision`.
- RQD geometry/calculation -> `calculations.rqd`.
- Borehole form defaults -> `models` or `logging`.
- CSV/HTML/report generation -> `reports` and `exports`.
- Streamlit interface -> `app`.

The first migration is successful only if the current RQD workflow still works.

