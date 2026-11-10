"""Генератор демонстрационных данных.

Данные СИНТЕТИЧЕСКИЕ: они нужны, чтобы проект запускался без интернета и
результаты были воспроизводимыми. Выводы по ним не описывают реальный рынок.
Для реальных данных используйте команду `fetch` (см. hh_client.py).
"""
from __future__ import annotations

import random
from datetime import date, timedelta

# роль -> (типичные навыки, базовая зарплата в рублях)
ROLES: dict[str, tuple[list[str], int]] = {
    "Аналитик данных": (["SQL", "Excel", "Python", "Tableau", "Power BI", "Pandas"], 110_000),
    "BI-аналитик": (["SQL", "Power BI", "Excel", "Tableau"], 120_000),
    "Python-разработчик": (["Python", "Django", "FastAPI", "PostgreSQL", "Docker", "Git"], 160_000),
    "Data Engineer": (["Python", "SQL", "Airflow", "Spark", "ClickHouse", "Docker"], 200_000),
    "Go-разработчик": (["Go", "PostgreSQL", "Docker", "Kafka", "Git", "Linux"], 190_000),
    "Преподаватель программирования": (["Python", "Git", "SQL"], 70_000),
}
CITIES = {
    "Москва": 1.25, "Санкт-Петербург": 1.10, "Екатеринбург": 0.90,
    "Новосибирск": 0.90, "Казань": 0.85,
}
EXPERIENCE = {
    "Нет опыта": 0.70,
    "От 1 года до 3 лет": 1.00,
    "От 3 до 6 лет": 1.40,
}
ALL_SKILLS = sorted({s for skills, _ in ROLES.values() for s in skills})


def generate(n: int = 600, seed: int = 42, today: date = date(2026, 10, 1)) -> list[dict]:
    rng = random.Random(seed)
    employers = [f"Работодатель {i:02d}" for i in range(1, 31)]
    roles = list(ROLES)
    out: list[dict] = []

    for i in range(1, n + 1):
        role = rng.choice(roles)
        typical, base = ROLES[role]
        skills = set(rng.sample(typical, k=rng.randint(min(3, len(typical)), min(5, len(typical)))))
        if rng.random() < 0.25:
            skills.add(rng.choice(ALL_SKILLS))

        city = rng.choices(list(CITIES), weights=[40, 25, 12, 12, 11])[0]
        exp = rng.choices(list(EXPERIENCE), weights=[25, 50, 25])[0]
        remote = rng.random() < 0.35
        mid = base * CITIES[city] * EXPERIENCE[exp] * rng.lognormvariate(0, 0.15)
        mid = round(mid / 5000) * 5000

        salary_from = salary_to = None
        r = rng.random()
        if r < 0.15:
            pass  # зарплата не указана
        elif r < 0.75:
            salary_from, salary_to = round(mid * 0.85 / 5000) * 5000, round(mid * 1.15 / 5000) * 5000
        elif r < 0.92:
            salary_from = round(mid * 0.9 / 5000) * 5000
        else:
            salary_to = round(mid * 1.1 / 5000) * 5000

        out.append({
            "id": f"demo-{i:04d}",
            "title": role,
            "employer": rng.choice(employers),
            "city": city,
            "salary_from": salary_from,
            "salary_to": salary_to,
            "currency": "RUR" if (salary_from or salary_to) else None,
            "experience": exp,
            "remote": remote,
            "published_at": (today - timedelta(days=rng.randint(0, 180))).isoformat(),
            "url": None,
            "skills": sorted(skills),
        })
    return out
