-- title: Медианная зарплата по городам (города, где есть минимум 5 вакансий с зарплатой)
-- В SQLite нет функции MEDIAN, поэтому берём центральные строки через оконные функции.
WITH ranked AS (
    SELECT
        city,
        salary_mid,
        ROW_NUMBER() OVER (PARTITION BY city ORDER BY salary_mid) AS rn,
        COUNT(*)     OVER (PARTITION BY city)                     AS cnt
    FROM v_vacancy_salary
    WHERE salary_mid IS NOT NULL
)
SELECT
    city,
    cnt AS vacancies,
    CAST(AVG(salary_mid) AS INTEGER) AS median_salary
FROM ranked
WHERE rn IN ((cnt + 1) / 2, (cnt + 2) / 2)
GROUP BY city, cnt
HAVING cnt >= 5
ORDER BY median_salary DESC;
