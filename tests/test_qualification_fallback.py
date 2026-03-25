from app.agents.crew_orchestrator import deterministic_extract


def test_deterministic_age_extract():
    assert deterministic_extract("age", "Tenho 42 anos") == 42


def test_deterministic_plan_type_extract():
    assert deterministic_extract("plan_type", "Quero plano empresarial para meu CNPJ") == "business"


def test_deterministic_urgency_extract():
    assert deterministic_extract("urgency", "preciso urgente") == "high"
