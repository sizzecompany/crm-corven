from __future__ import annotations

from jinja2 import Environment, StrictUndefined


env = Environment(undefined=StrictUndefined, autoescape=False)


def render_template(template: str, context: dict) -> str:
    return env.from_string(template).render(**context)
