"""Запуск SQL-запросов из папки queries/ и оформление результатов."""
from __future__ import annotations

import sqlite3
from pathlib import Path

QUERIES_DIR = Path(__file__).parent / "queries"


def load_queries() -> list[tuple[str, str]]:
    """Возвращает [(заголовок, sql)] в порядке имён файлов."""
    result = []
    for path in sorted(QUERIES_DIR.glob("*.sql")):
        sql = path.read_text(encoding="utf-8")
        first = sql.splitlines()[0]
        title = first.removeprefix("-- title:").strip() if first.startswith("-- title:") else path.stem
        result.append((title, sql))
    return result


def load_queries_by_name() -> list[tuple[str, str]]:
    """Возвращает [(имя файла без .sql, sql)]; удобно для тестов."""
    return [(p.stem, p.read_text(encoding="utf-8")) for p in sorted(QUERIES_DIR.glob("*.sql"))]


def run_query(conn: sqlite3.Connection, sql: str) -> tuple[list[str], list[tuple]]:
    cur = conn.execute(sql)
    columns = [d[0] for d in cur.description]
    return columns, [tuple(row) for row in cur.fetchall()]


def format_table(columns: list[str], rows: list[tuple]) -> str:
    if not rows:
        return "(нет данных)"
    cells = [[("" if v is None else f"{v:,}".replace(",", " ") if isinstance(v, int) else str(v))
              for v in row] for row in rows]
    widths = [max(len(c), *(len(r[i]) for r in cells)) for i, c in enumerate(columns)]
    line = lambda items: "  ".join(s.ljust(w) for s, w in zip(items, widths)).rstrip()
    sep = "  ".join("-" * w for w in widths)
    return "\n".join([line(columns), sep, *(line(r) for r in cells)])


def build_report(conn: sqlite3.Connection) -> str:
    parts = []
    for i, (title, sql) in enumerate(load_queries(), start=1):
        columns, rows = run_query(conn, sql)
        parts.append(f"{i}. {title}\n\n{format_table(columns, rows)}")
    return "\n\n".join(parts) + "\n"


def save_skills_chart(conn: sqlite3.Connection, path: str | Path) -> bool:
    """Рисует график топ-навыков. Нужен matplotlib; без него возвращает False."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return False

    _, sql = load_queries()[1]
    _, rows = run_query(conn, sql)
    skills = [r[0] for r in rows][::-1]
    shares = [r[2] for r in rows][::-1]

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.barh(skills, shares, color="#2f5d50")
    ax.set_xlabel("Доля вакансий, %")
    ax.set_title("Топ навыков в вакансиях (демо-данные)")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return True
