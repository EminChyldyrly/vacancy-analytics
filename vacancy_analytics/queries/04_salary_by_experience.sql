-- title: Зарплата по требуемому опыту
SELECT
    experience,
    COUNT(*) AS vacancies_with_salary,
    CAST(AVG(salary_mid) AS INTEGER) AS avg_salary,
    CAST(MIN(salary_mid) AS INTEGER) AS min_salary,
    CAST(MAX(salary_mid) AS INTEGER) AS max_salary
FROM v_vacancy_salary
WHERE salary_mid IS NOT NULL AND experience IS NOT NULL
GROUP BY experience
ORDER BY avg_salary;
