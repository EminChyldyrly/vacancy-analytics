PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS employers (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS vacancies (
    id           TEXT PRIMARY KEY,
    title        TEXT NOT NULL,
    employer_id  INTEGER NOT NULL REFERENCES employers(id),
    city         TEXT,
    salary_from  INTEGER,
    salary_to    INTEGER,
    currency     TEXT,
    experience   TEXT,
    remote       INTEGER NOT NULL DEFAULT 0 CHECK (remote IN (0, 1)),
    published_at TEXT NOT NULL,          -- YYYY-MM-DD
    url          TEXT
);

CREATE TABLE IF NOT EXISTS skills (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS vacancy_skills (
    vacancy_id TEXT    NOT NULL REFERENCES vacancies(id) ON DELETE CASCADE,
    skill_id   INTEGER NOT NULL REFERENCES skills(id),
    PRIMARY KEY (vacancy_id, skill_id)
);

CREATE INDEX IF NOT EXISTS idx_vacancies_city      ON vacancies(city);
CREATE INDEX IF NOT EXISTS idx_vacancies_published ON vacancies(published_at);
CREATE INDEX IF NOT EXISTS idx_vs_skill            ON vacancy_skills(skill_id);

-- Вакансии с зарплатой, приведённой к одному числу (salary_mid).
-- Берём середину вилки, а если указана одна граница, то её.
-- Зарплаты не в рублях исключаем (salary_mid = NULL), чтобы не смешивать валюты.
DROP VIEW IF EXISTS v_vacancy_salary;
CREATE VIEW v_vacancy_salary AS
SELECT
    v.*,
    e.name AS employer,
    CASE
        WHEN v.currency IS NOT NULL AND v.currency <> 'RUR' THEN NULL
        WHEN v.salary_from IS NOT NULL AND v.salary_to IS NOT NULL
            THEN (v.salary_from + v.salary_to) / 2.0
        WHEN v.salary_from IS NOT NULL THEN v.salary_from
        WHEN v.salary_to   IS NOT NULL THEN v.salary_to
    END AS salary_mid
FROM vacancies v
JOIN employers e ON e.id = v.employer_id;
