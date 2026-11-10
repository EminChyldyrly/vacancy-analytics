-- title: Зарплата в вакансиях с SQL и без (корреляция, а не причинно-следственная связь)
WITH flagged AS (
    SELECT
        v.salary_mid,
        EXISTS (
            SELECT 1
            FROM vacancy_skills vs
            JOIN skills s ON s.id = vs.skill_id
            WHERE vs.vacancy_id = v.id AND s.name = 'SQL'
        ) AS has_sql
    FROM v_vacancy_salary v
    WHERE v.salary_mid IS NOT NULL
)
SELECT
    CASE has_sql WHEN 1 THEN 'с SQL' ELSE 'без SQL' END AS group_name,
    COUNT(*) AS vacancies,
    CAST(AVG(salary_mid) AS INTEGER) AS avg_salary
FROM flagged
GROUP BY has_sql
ORDER BY has_sql DESC;
