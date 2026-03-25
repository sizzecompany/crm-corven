from app.services.simulator_service import estimate_plan


def test_estimate_plan_returns_cta_and_prices():
    result = estimate_plan(age=40, plan_type="family", has_dependents=True, urgency="high")
    assert len(result.tiers) == 3
    assert result.tiers[0]["monthly_price"] > 0
    assert "BASIC" in result.cta
