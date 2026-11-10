"""Командная строка: demo / fetch / report."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import analysis, db, hh_client, sample_data


def _cmd_demo(args: argparse.Namespace) -> int:
    path = Path(args.db)
    if path.exists():
        path.unlink()
    conn = db.connect(path)
    db.init_db(conn)
    added = db.insert_vacancies(conn, sample_data.generate(n=args.n, seed=args.seed))
    print(f"Создана база {path} с {added} демо-вакансиями (данные синтетические).")
    return 0


def _cmd_fetch(args: argparse.Namespace) -> int:
    conn = db.connect(args.db)
    db.init_db(conn)
    try:
        added = db.insert_vacancies(
            conn, hh_client.fetch(args.text, pages=args.pages, area=args.area)
        )
    except OSError as exc:  # сеть, DNS, HTTP-ошибки
        print(f"Не удалось получить данные: {exc}", file=sys.stderr)
        return 1
    print(f"Добавлено новых вакансий: {added}")
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    path = Path(args.db)
    if not path.exists():
        print(f"Базы {path} нет. Сначала выполните `demo` или `fetch`.", file=sys.stderr)
        return 1
    conn = db.connect(path)
    print(analysis.build_report(conn))
    if args.chart:
        ok = analysis.save_skills_chart(conn, args.chart)
        print(f"График сохранён: {args.chart}" if ok else "matplotlib не установлен, график пропущен.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="vacancy_analytics", description=__doc__)
    parser.add_argument("--db", default="vacancies.db", help="путь к файлу SQLite")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("demo", help="создать базу из синтетических данных")
    p.add_argument("-n", type=int, default=600, help="число вакансий")
    p.add_argument("--seed", type=int, default=42)
    p.set_defaults(func=_cmd_demo)

    p = sub.add_parser("fetch", help="загрузить вакансии с hh.ru")
    p.add_argument("text", help="поисковый запрос, например 'аналитик данных'")
    p.add_argument("--pages", type=int, default=3)
    p.add_argument("--area", type=int, default=None, help="id региона hh.ru (1 = Москва)")
    p.set_defaults(func=_cmd_fetch)

    p = sub.add_parser("report", help="вывести результаты всех запросов")
    p.add_argument("--chart", metavar="PNG", help="сохранить график топ-навыков")
    p.set_defaults(func=_cmd_report)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
