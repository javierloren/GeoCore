from geocore.models import Borehole, CoreRun, LithologyInterval, Project


def demo_project() -> Project:
    bh_01 = Borehole(
        borehole_id="BH-01",
        x=725431.0,
        y=4378211.0,
        z=132.4,
        final_depth_m=18.0,
        groundwater_depth_m=4.3,
        lithology=[
            LithologyInterval(0.0, 1.6, "Fill", "Sandy gravel fill with brick fragments."),
            LithologyInterval(1.6, 5.2, "Clay", "Brown silty clay, firm to stiff."),
            LithologyInterval(5.2, 9.0, "Weathered granite", "Highly weathered granite, fractured."),
            LithologyInterval(9.0, 18.0, "Granite", "Fresh to slightly weathered granite."),
        ],
        core_runs=[
            CoreRun(5.2, 6.7, 1.18, 38.0, validated=True),
            CoreRun(6.7, 8.2, 1.32, 52.0, validated=True),
            CoreRun(8.2, 9.7, 1.41, 68.0, validated=True),
            CoreRun(9.7, 11.2, 1.46, 84.0, validated=False),
        ],
    )
    bh_02 = Borehole(
        borehole_id="BH-02",
        x=725512.0,
        y=4378276.0,
        z=129.8,
        final_depth_m=15.0,
        groundwater_depth_m=3.9,
        lithology=[
            LithologyInterval(0.0, 2.1, "Fill", "Heterogeneous fill."),
            LithologyInterval(2.1, 6.4, "Sand", "Medium dense silty sand."),
            LithologyInterval(6.4, 15.0, "Weathered granite", "Weathered granite with frequent joints."),
        ],
        core_runs=[
            CoreRun(6.4, 7.9, 1.05, 31.0, validated=True),
            CoreRun(7.9, 9.4, 1.24, 46.0, validated=False),
            CoreRun(9.4, 10.9, 1.30, 58.0, validated=False),
        ],
    )
    return Project(
        name="Demo geotechnical campaign",
        client="Open education project",
        location="Example site",
        coordinate_reference_system="EPSG:25830",
        notes="Demo data used to design the GeoCore workbench.",
        boreholes=[bh_01, bh_02],
    )

