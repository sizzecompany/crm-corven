from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EstimateResult:
    tiers: list[dict]
    cta: str


def estimate_plan(*, age: int | None, plan_type: str | None, has_dependents: bool | None, urgency: str | None) -> EstimateResult:
    base = 220.0
    if age:
        base += max(age - 25, 0) * 4.5

    multiplier = 1.0
    if plan_type == "family":
        multiplier += 0.45
    elif plan_type == "business":
        multiplier += 0.30

    if has_dependents:
        multiplier += 0.20

    if urgency == "high":
        discount = 8.0
    elif urgency == "medium":
        discount = 5.0
    else:
        discount = 3.0

    monthly = round(base * multiplier * (1 - (discount / 100)), 2)

    tiers = [
        {
            "name": "Basic",
            "monthly_price": round(monthly * 0.85, 2),
            "coverage_summary": "Cobertura essencial com foco em custo-benefício.",
            "cta": "Quero o Basic",
        },
        {
            "name": "Standard",
            "monthly_price": monthly,
            "coverage_summary": "Equilíbrio entre rede de atendimento e preço.",
            "cta": "Quero o Standard",
        },
        {
            "name": "Premium",
            "monthly_price": round(monthly * 1.35, 2),
            "coverage_summary": "Rede ampliada e benefícios completos.",
            "cta": "Quero o Premium",
        },
    ]
    cta = "Responder BASIC, STANDARD ou PREMIUM para avançar com especialista."
    return EstimateResult(tiers=tiers, cta=cta)
