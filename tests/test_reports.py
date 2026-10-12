from geocore.reports import borehole_report_html
from geocore.sample_data import demo_project


def test_borehole_report_html_contains_project_and_log():
    project = demo_project()
    report = borehole_report_html(project, project.boreholes[0])

    assert "GeoCore Borehole Report" in report
    assert project.name in report
    assert project.boreholes[0].borehole_id in report
    assert "<svg" in report
    assert "Core Runs" in report
