-- title: Работодатели с наибольшим числом вакансий
SELECT
    e.name AS employer,
    COUNT(*) AS vacancies,
    CAST(AVG(v.salary_mid) AS INTEGER) AS avg_salary
FROM v_vacancy_salary v
JOIN employers e ON e.id = v.employer_id
GROUP BY e.id
ORDER BY vacancies DESC, employer
LIMIT 10;
