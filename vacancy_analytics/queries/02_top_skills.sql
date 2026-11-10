-- title: Самые востребованные навыки (доля вакансий, где навык упомянут)
SELECT
    s.name AS skill,
    COUNT(*) AS vacancies,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM vacancies), 1) AS share_pct
FROM vacancy_skills vs
JOIN skills s ON s.id = vs.skill_id
GROUP BY s.id
ORDER BY vacancies DESC, skill
LIMIT 15;
