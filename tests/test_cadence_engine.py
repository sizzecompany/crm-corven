from types import SimpleNamespace

from app.cadence.engine import step_payload


def test_cadence_steps_intervals():
    lead = SimpleNamespace(name="Ana")
    content, next_run = step_payload(0, lead)
    assert content == "cadence_d0"
    assert next_run is not None


def test_cadence_finishes_after_last_step():
    lead = SimpleNamespace(name="Ana")
    content, next_run = step_payload(999, lead)
    assert content == ""
    assert next_run is None
