from geocore.models import CoreRun


def test_core_run_recovery_percent():
    run = CoreRun(from_m=10.0, to_m=11.5, recovered_length_m=1.2)

    assert run.run_length_m == 1.5
    assert run.recovery_percent == 80.0


def test_core_run_recovery_is_none_for_missing_recovered_length():
    run = CoreRun(from_m=10.0, to_m=11.5)

    assert run.recovery_percent is None

