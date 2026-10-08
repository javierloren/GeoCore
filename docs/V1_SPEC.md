# GeoCore V1.0 Specification

## Goal

V1.0 must deliver a complete and useful workflow:

`Project -> Borehole -> Core Logging -> Recovery + RQD -> Borehole Log -> PDF`

## User Workflow

1. The user creates a project.
2. The user creates one or more boreholes.
3. The user enters collar and drilling metadata.
4. The user enters lithology intervals.
5. The user uploads core box photos.
6. GeoCore detects intact rock, fractures, and soil/no recovery where possible.
7. The user validates or corrects the interpreted data.
8. GeoCore calculates core recovery and RQD by run/interval.
9. GeoCore generates a borehole log.
10. GeoCore exports a PDF report and structured data.

## Required Data

### Project

- Project name.
- Client.
- Location.
- Coordinate reference system.
- Notes.

### Borehole

- Borehole ID.
- X, Y, Z.
- Final depth.
- Inclination.
- Azimuth.
- Start/end date.
- Contractor.
- Drilling method.
- Equipment.
- Groundwater observations.

### Lithology Interval

- From depth.
- To depth.
- Lithology.
- Description.
- Weathering.
- Strength.
- Color.
- Notes.

### Core Run

- From depth.
- To depth.
- Run length.
- Recovered length.
- Core recovery percent.
- RQD percent.
- Photo reference.
- User validation status.

### Report

- Borehole header.
- Lithology column.
- Recovery column.
- RQD column.
- Sample/SPT column where available.
- Groundwater markers.
- Notes.
- Core photo annex.

## V1 Exclusions

These are deliberately postponed:

- Full finite element analysis.
- Full 3D geological modeling.
- Multiuser permissions.
- Complex AGS round-trip validation.
- Production-grade slope stability.

They are important, but they should not block the first useful release.

