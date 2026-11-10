"""Работа с базой: подключение, схема, загрузка вакансий."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def connect(path: str | Path = "vacancies.db") -> sqlite3.Connection:
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))


def _get_or_create(conn: sqlite3.Connection, table: str, name: str) -> int:
    conn.execute(f"INSERT OR IGNORE INTO {table}(name) VALUES (?)", (name,))
    row = conn.execute(f"SELECT id FROM {table} WHERE name = ?", (name,)).fetchone()
    return row["id"]


def insert_vacancies(conn: sqlite3.Connection, vacancies: Iterable[dict]) -> int:
    """Загружает вакансии. Повторная загрузка той же вакансии (по id) её пропускает.

    Формат записи: id, title, employer, city, salary_from, salary_to, currency,
    experience, remote (bool), published_at (YYYY-MM-DD), url, skills (list[str]).
    Возвращает число реально добавленных вакансий.
    """
    added = 0
    with conn:
        for v in vacancies:
            employer_id = _get_or_create(conn, "employers", v["employer"])
            cur = conn.execute(
                """INSERT OR IGNORE INTO vacancies
                   (id, title, employer_id, city, salary_from, salary_to, currency,
                    experience, remote, published_at, url)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    str(v["id"]), v["title"], employer_id, v.get("city"),
                    v.get("salary_from"), v.get("salary_to"), v.get("currency"),
                    v.get("experience"), int(bool(v.get("remote"))),
                    v["published_at"], v.get("url"),
                ),
            )
            if cur.rowcount == 0:
                continue
            added += 1
            # sorted, чтобы id навыков не зависели от хеш-рандомизации set
            for skill in sorted(set(v.get("skills", []))):
                skill_id = _get_or_create(conn, "skills", skill)
                conn.execute(
                    "INSERT OR IGNORE INTO vacancy_skills(vacancy_id, skill_id) VALUES (?, ?)",
                    (str(v["id"]), skill_id),
                )
    return added
