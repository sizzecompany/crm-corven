from __future__ import annotations

from dataclasses import dataclass
import json
import re

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.lead_qualification import LeadQualification, QualificationStatus

settings = get_settings()

try:
    from crewai import Agent, Crew, Process, Task
except Exception:  # pragma: no cover
    Agent = Crew = Process = Task = None


QUESTIONS = [
    ("age", "Qual sua idade?"),
    ("city", "Em qual cidade você mora?"),
    ("plan_type", "O plano é individual, familiar ou empresarial?"),
    ("urgency", "Você precisa contratar em qual urgência: alta, média ou baixa?"),
    ("has_dependents", "Você possui dependentes no plano? (sim/não)"),
]


@dataclass
class QualificationResult:
    field: str
    value: str | int | bool | None


class CrewQualifier:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def extract_field(self, field_name: str, latest_message: str, history: str) -> QualificationResult:
        deterministic = deterministic_extract(field_name, latest_message)
        if deterministic is not None:
            return QualificationResult(field=field_name, value=deterministic)

        if Agent and Crew and Task and Process:
            qualifier = Agent(
                role="Sales Qualifier",
                goal=f"Extract the field {field_name} from lead conversation",
                backstory="Especialista em qualificação de leads para planos de saúde.",
                memory=True,
                verbose=False,
            )
            extraction_task = Task(
                description=(
                    f"Histórico: {history}\nMensagem atual: {latest_message}\n"
                    f"Retorne JSON com chave {field_name} e valor extraído."
                ),
                expected_output=f'JSON: {{"{field_name}": "value"}}',
                agent=qualifier,
            )
            crew = Crew(agents=[qualifier], tasks=[extraction_task], process=Process.sequential, memory=True)
            output = crew.kickoff()
            raw = str(output)
        else:
            completion = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Extract structured data from Portuguese sales messages. Return strict JSON.",
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Field: {field_name}. Conversation: {history}\nLatest: {latest_message}. "
                            f"Return JSON only with {field_name}."
                        ),
                    },
                ],
                temperature=0,
            )
            raw = completion.choices[0].message.content or "{}"

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {field_name: None}

        value = data.get(field_name)
        if field_name == "age" and value is not None:
            try:
                value = int(value)
            except Exception:
                value = None
        if field_name == "has_dependents" and isinstance(value, str):
            value = value.strip().lower() in {"sim", "yes", "true", "1"}

        return QualificationResult(field=field_name, value=value)


def deterministic_extract(field_name: str, text: str) -> str | int | bool | None:
    clean = (text or "").strip().lower()
    if not clean:
        return None

    if field_name == "age":
        patterns = [
            r"(\d{2})\s*anos",
            r"tenho\s+(\d{2})",
            r"idade\s*[:=]?\s*(\d{2})",
        ]
        for pattern in patterns:
            m = re.search(pattern, clean)
            if m:
                age = int(m.group(1))
                if 10 <= age <= 99:
                    return age
        return None

    if field_name == "plan_type":
        if any(k in clean for k in ["empresarial", "empresa", "pj", "cnpj"]):
            return "business"
        if any(k in clean for k in ["familiar", "família", "dependente"]):
            return "family"
        if any(k in clean for k in ["individual", "só pra mim", "somente eu"]):
            return "individual"
        return None

    if field_name == "urgency":
        if any(k in clean for k in ["urgente", "hoje", "agora", "imediato"]):
            return "high"
        if any(k in clean for k in ["essa semana", "próxima semana", "rápido"]):
            return "medium"
        if any(k in clean for k in ["sem pressa", "depois", "mês que vem"]):
            return "low"
        return None

    if field_name == "has_dependents":
        if any(k in clean for k in ["tenho dependente", "meus filhos", "minha esposa", "sim"]):
            return True
        if any(k in clean for k in ["não tenho dependente", "nao tenho dependente", "não", "nao"]):
            return False
        return None

    if field_name == "city":
        city_patterns = [
            r"moro em ([a-zà-ú\\s]+)",
            r"cidade[:=]?\\s*([a-zà-ú\\s]+)",
        ]
        for pattern in city_patterns:
            m = re.search(pattern, clean)
            if m:
                city = m.group(1).strip().title()
                if 2 <= len(city) <= 120:
                    return city
        return None

    return None


async def apply_qualification_progress(
    db: AsyncSession,
    qualification: LeadQualification,
    latest_message: str,
    history: str,
) -> tuple[LeadQualification, str | None]:
    qualifier = CrewQualifier()
    if qualification.current_question_index >= len(QUESTIONS):
        qualification.status = QualificationStatus.QUALIFIED
        return qualification, None

    field_name, _ = QUESTIONS[qualification.current_question_index]
    result = await qualifier.extract_field(field_name, latest_message, history)

    if result.value is not None:
        setattr(qualification, result.field, result.value)
        qualification.current_question_index += 1

    if qualification.current_question_index >= len(QUESTIONS):
        qualification.status = QualificationStatus.QUALIFIED
        await db.flush()
        return qualification, None

    next_question = QUESTIONS[qualification.current_question_index][1]
    await db.flush()
    return qualification, next_question
