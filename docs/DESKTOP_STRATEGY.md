# Desktop Strategy

GeoCore should become a downloadable desktop application, with Streamlit kept as
the prototype and demo environment.

## Why Desktop

- Users can keep confidential geotechnical data on their own computers.
- Images, borehole coordinates, laboratory results, and reports do not need to be
  uploaded to a server.
- Running computer vision locally avoids permanent GPU/server costs.
- The project can scale to many users without the maintainer paying for every
  calculation.
- Offline use matters for field, academic, and consulting workflows.

## Target Shape

```text
GeoCore
  GeoCore Desktop
    local projects
    SQLite/DuckDB
    images/PDFs/documents
    local models
  GeoCore Web
    demo
    teaching
    lightweight public workflows
  GeoCore Core
    models
    calculations
    reports
    imports/exports
    vision
  GeoCore Plugins
    RQD Vision
    Rock mass classification
    Slope stability
    Stereonet tools
    CPT/SPT
    Foundations
```

## Technology Direction

The preferred desktop path is Python + PySide6/Qt because it keeps GeoCore close
to the existing Python prototype and matches the kind of interface used by QGIS.

The core rule is that engineering logic belongs in the `geocore` package, not in
the UI. Streamlit, PySide6, scripts, and tests should all call the same core
models and calculations.

## Project Format

GeoCore should eventually support a local project format:

```text
Project_Name.geocore
  project.sqlite
  images/
  reports/
  imports/
  exports/
  models/
```

The first implementation can use an ordinary folder and SQLite database. A zipped
`.geocore` package can come later.

## Near-Term Rule

Do not rewrite the current Streamlit workbench into desktop yet. First extract
the reusable geotechnical core:

- Borehole data model.
- RQD and recovery calculations.
- Core photo analysis interface.
- Reports and borehole logs.
- Local storage.

Once those pieces are stable, the desktop UI can be added without rewriting the
engineering logic.
