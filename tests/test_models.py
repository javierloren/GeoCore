from geocore.models import Borehole, CoreRun


def test_core_run_recovery_percent():
    run = CoreRun(from_m=10.0, to_m=11.5, recovered_length_m=1.2)

    assert run.run_length_m == 1.5
    assert run.recovery_percent == 80.0


def test_core_run_recovery_is_none_for_missing_recovered_length():
    run = CoreRun(from_m=10.0, to_m=11.5)

    assert run.recovery_percent is None


def test_borehole_average_values_ignore_missing_runs():
    borehole = Borehole(
        borehole_id="BH-01",
        core_runs=[
            CoreRun(from_m=0.0, to_m=1.0, recovered_length_m=0.8, rqd_percent=60.0),
            CoreRun(from_m=1.0, to_m=2.0),
            CoreRun(from_m=2.0, to_m=3.0, recovered_length_m=1.0, rqd_percent=80.0),
        ],
    )

    assert borehole.average_recovery_percent == 90.0
    assert borehole.average_rqd_percent == 70.0

