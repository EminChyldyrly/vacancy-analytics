-- title: Средняя зарплата по навыкам (навыки минимум в 10 вакансиях с зарплатой)
SELECT
    s.name AS skill,
    COUNT(*) AS vacancies_with_salary,
    CAST(AVG(v.salary_mid) AS INTEGER) AS avg_salary
FROM vacancy_skills vs
JOIN skills s ON s.id = vs.skill_id
JOIN v_vacancy_salary v ON v.id = vs.vacancy_id
WHERE v.salary_mid IS NOT NULL
GROUP BY s.id
HAVING COUNT(*) >= 10
ORDER BY avg_salary DESC;
