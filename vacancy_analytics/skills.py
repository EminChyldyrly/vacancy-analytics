"""Извлечение навыков из текста вакансии по словарю шаблонов."""
from __future__ import annotations

import re

_PATTERNS: dict[str, str] = {
    "Python": r"python",
    "SQL": r"\bsql\b",
    "PostgreSQL": r"postgres(?:ql)?",
    "Excel": r"excel|эксель",
    "Pandas": r"pandas",
    "Go": r"(?-i:\bGo(?:lang)?\b)",  # с учётом регистра, чтобы не ловить английское «go»
    "C++": r"(?<!\w)c\+\+",
    "Docker": r"docker",
    "Git": r"\bgit\b",
    "Linux": r"linux",
    "Airflow": r"airflow",
    "Spark": r"\bspark\b",
    "ClickHouse": r"clickhouse",
    "Tableau": r"tableau",
    "Power BI": r"power\s?bi",
    "Django": r"django",
    "FastAPI": r"fastapi",
    "Kafka": r"kafka",
}

_COMPILED = {name: re.compile(p, re.IGNORECASE) for name, p in _PATTERNS.items()}

KNOWN_SKILLS = tuple(_PATTERNS)


def extract_skills(text: str) -> list[str]:
    """Возвращает отсортированный список найденных навыков."""
    if not text:
        return []
    return sorted(name for name, rx in _COMPILED.items() if rx.search(text))
