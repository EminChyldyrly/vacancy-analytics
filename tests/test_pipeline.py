import statistics
import unittest

from vacancy_analytics import analysis, db, hh_client, sample_data
from vacancy_analytics.skills import extract_skills


def make_vacancy(i, city="Москва", salary_from=None, salary_to=None, currency="RUR",
                 skills=(), remote=False, month="2026-09"):
    return {
        "id": f"t{i}", "title": "Тест", "employer": "Работодатель",
        "city": city, "salary_from": salary_from, "salary_to": salary_to,
        "currency": currency if (salary_from or salary_to) else None,
        "experience": "От 1 года до 3 лет", "remote": remote,
        "published_at": f"{month}-15", "url": None, "skills": list(skills),
    }


def fresh_conn(test):
    conn = db.connect(":memory:")
    db.init_db(conn)
    test.addCleanup(conn.close)
    return conn


class SkillExtractionTests(unittest.TestCase):
    def test_finds_known_skills(self):
        text = "Требуется Python 3, знание SQL, PostgreSQL и Power BI. Будет плюсом Docker."
        self.assertEqual(
            extract_skills(text), ["Docker", "PostgreSQL", "Power BI", "Python", "SQL"]
        )

    def test_go_is_case_sensitive_and_cpp_is_found(self):
        self.assertEqual(extract_skills("we go to work"), [])
        self.assertEqual(extract_skills("Разработчик на Go или C++"), ["C++", "Go"])

    def test_mysql_is_not_sql(self):
        self.assertEqual(extract_skills("MySQL"), [])

    def test_empty(self):
        self.assertEqual(extract_skills(""), [])


class SalaryViewTests(unittest.TestCase):
    def test_salary_mid_rules(self):
        conn = fresh_conn(self)
        db.insert_vacancies(conn, [
            make_vacancy(1, salary_from=100_000, salary_to=200_000),  # середина
            make_vacancy(2, salary_from=90_000),                      # только от
            make_vacancy(3, salary_to=80_000),                        # только до
            make_vacancy(4),                                          # нет зарплаты
            make_vacancy(5, salary_from=3_000, currency="USD"),       # другая валюта
        ])
        rows = {r["id"]: r["salary_mid"]
                for r in conn.execute("SELECT id, salary_mid FROM v_vacancy_salary")}
        self.assertEqual(rows["t1"], 150_000)
        self.assertEqual(rows["t2"], 90_000)
        self.assertEqual(rows["t3"], 80_000)
        self.assertIsNone(rows["t4"])
        self.assertIsNone(rows["t5"])


class LoaderTests(unittest.TestCase):
    def test_reinsert_is_idempotent(self):
        conn = fresh_conn(self)
        data = [make_vacancy(1, skills=["SQL", "Python"])]
        self.assertEqual(db.insert_vacancies(conn, data), 1)
        self.assertEqual(db.insert_vacancies(conn, data), 0)
        count = conn.execute("SELECT COUNT(*) FROM vacancy_skills").fetchone()[0]
        self.assertEqual(count, 2)


class QueryTests(unittest.TestCase):
    def _median_query(self):
        return dict(analysis.load_queries_by_name())["01_median_salary_by_city"]

    def test_median_matches_statistics_module(self):
        conn = fresh_conn(self)
        odd = [60, 70, 80, 90, 200]    # медиана 80 (в тысячах)
        even = [50, 60, 70, 100, 110, 300]  # медиана 85
        vacancies = [make_vacancy(i, "Казань", salary_from=s * 1000) for i, s in enumerate(odd)]
        vacancies += [make_vacancy(100 + i, "Москва", salary_from=s * 1000) for i, s in enumerate(even)]
        db.insert_vacancies(conn, vacancies)

        _, rows = analysis.run_query(conn, self._median_query())
        result = {city: median for city, _, median in rows}
        self.assertEqual(result["Казань"], int(statistics.median(odd) * 1000))
        self.assertEqual(result["Москва"], int(statistics.median(even) * 1000))

    def test_median_skips_small_groups(self):
        conn = fresh_conn(self)
        db.insert_vacancies(conn, [make_vacancy(i, "Омск", salary_from=100_000) for i in range(4)])
        _, rows = analysis.run_query(conn, self._median_query())
        self.assertEqual(rows, [])

    def test_skill_pairs_counted_once(self):
        conn = fresh_conn(self)
        db.insert_vacancies(conn, [
            make_vacancy(1, skills=["SQL", "Python"]),
            make_vacancy(2, skills=["Python", "SQL", "Git"]),
        ])
        _, rows = analysis.run_query(conn, dict(analysis.load_queries_by_name())["07_skill_pairs"])
        top = rows[0]
        self.assertEqual((top[0], top[1], top[2]), ("Python", "SQL", 2))

    def test_all_queries_run_on_demo_data(self):
        conn = fresh_conn(self)
        db.insert_vacancies(conn, sample_data.generate(n=300))
        for title, sql in analysis.load_queries():
            columns, rows = analysis.run_query(conn, sql)
            self.assertTrue(columns, title)
            self.assertTrue(rows, f"запрос без результатов: {title}")


class SampleDataTests(unittest.TestCase):
    def test_deterministic(self):
        self.assertEqual(sample_data.generate(n=50, seed=1), sample_data.generate(n=50, seed=1))

    def test_demo_has_expected_patterns(self):
        conn = fresh_conn(self)
        db.insert_vacancies(conn, sample_data.generate(n=600))
        _, rows = analysis.run_query(conn, dict(analysis.load_queries_by_name())["04_salary_by_experience"])
        avg = {r[0]: r[2] for r in rows}
        self.assertLess(avg["Нет опыта"], avg["От 1 года до 3 лет"])
        self.assertLess(avg["От 1 года до 3 лет"], avg["От 3 до 6 лет"])


class HhNormalizeTests(unittest.TestCase):
    def test_normalize_item(self):
        item = {
            "id": "123", "name": "Аналитик данных (SQL)",
            "employer": {"name": "ООО Пример"}, "area": {"name": "Москва"},
            "salary": {"from": 100000, "to": None, "currency": "RUR"},
            "experience": {"name": "От 1 года до 3 лет"},
            "schedule": {"id": "remote"},
            "published_at": "2026-10-01T12:00:00+0300",
            "alternate_url": "https://hh.ru/vacancy/123",
            "snippet": {"requirement": "Знание Python и Excel", "responsibility": None},
        }
        v = hh_client.normalize(item)
        self.assertEqual(v["published_at"], "2026-10-01")
        self.assertTrue(v["remote"])
        self.assertEqual(v["skills"], ["Excel", "Python", "SQL"])
        self.assertEqual(v["salary_from"], 100000)

    def test_normalize_handles_missing_fields(self):
        v = hh_client.normalize({"id": "1", "name": "X"})
        self.assertEqual(v["employer"], "Не указан")
        self.assertIsNone(v["salary_from"])


if __name__ == "__main__":
    unittest.main()
