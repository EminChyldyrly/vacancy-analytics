"""Сбор реальных вакансий через открытое API hh.ru (только стандартная библиотека).

ВАЖНО: этот модуль написан по документации API, но в среде разработки не
запускался (там нет доступа в интернет). Перед использованием проверьте на
небольшом числе страниц; формат ответа и правила доступа API могут меняться.
Документация: https://api.hh.ru/openapi/redoc
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from typing import Iterator

from .skills import extract_skills

API_URL = "https://api.hh.ru/vacancies"
DEFAULT_USER_AGENT = "vacancy-analytics/0.1 (portfolio project)"


def fetch_page(text: str, page: int, per_page: int = 100, area: int | None = None,
               user_agent: str = DEFAULT_USER_AGENT) -> dict:
    params = {"text": text, "page": page, "per_page": per_page}
    if area is not None:
        params["area"] = area
    req = urllib.request.Request(
        f"{API_URL}?{urllib.parse.urlencode(params)}",
        headers={"User-Agent": user_agent},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def normalize(item: dict) -> dict:
    """Приводит элемент ответа API к формату db.insert_vacancies."""
    salary = item.get("salary") or {}
    snippet = item.get("snippet") or {}
    text = " ".join(filter(None, [
        item.get("name"), snippet.get("requirement"), snippet.get("responsibility"),
    ]))
    schedule = (item.get("schedule") or {}).get("id")
    work_formats = [f.get("id") for f in item.get("work_format") or []]
    return {
        "id": item["id"],
        "title": item.get("name", ""),
        "employer": (item.get("employer") or {}).get("name") or "Не указан",
        "city": (item.get("area") or {}).get("name"),
        "salary_from": salary.get("from"),
        "salary_to": salary.get("to"),
        "currency": salary.get("currency"),
        "experience": (item.get("experience") or {}).get("name"),
        "remote": schedule == "remote" or "REMOTE" in work_formats,
        "published_at": (item.get("published_at") or "")[:10],
        "url": item.get("alternate_url"),
        "skills": extract_skills(text),
    }


def fetch(text: str, pages: int = 3, area: int | None = None, delay: float = 0.5,
          user_agent: str = DEFAULT_USER_AGENT) -> Iterator[dict]:
    """Постранично собирает вакансии по поисковому запросу."""
    for page in range(pages):
        data = fetch_page(text, page, area=area, user_agent=user_agent)
        for item in data.get("items", []):
            yield normalize(item)
        if page + 1 >= data.get("pages", 0):
            break
        time.sleep(delay)  # не нагружаем API
