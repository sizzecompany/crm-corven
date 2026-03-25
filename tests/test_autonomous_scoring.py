from types import SimpleNamespace

from app.services.scoring_service import compute_score


def test_compute_score_hot():
    q = SimpleNamespace(urgency="high", age=35, has_dependents=True, city="SP", plan_type="family")
    score, reason = compute_score(q)
    assert score == 90
    assert "Hot lead" in reason


def test_compute_score_cold():
    q = SimpleNamespace(urgency="low", age=None, has_dependents=False, city=None, plan_type=None)
    score, _ = compute_score(q)
    assert score == 30
