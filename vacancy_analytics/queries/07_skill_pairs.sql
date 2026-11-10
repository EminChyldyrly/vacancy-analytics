-- title: Какие навыки чаще всего требуются вместе (пары)
-- MIN/MAX от двух строк дают пару в алфавитном порядке независимо от id навыков.
SELECT
    MIN(a.name, b.name) AS skill_a,
    MAX(a.name, b.name) AS skill_b,
    COUNT(*) AS together
FROM vacancy_skills x
JOIN vacancy_skills y ON y.vacancy_id = x.vacancy_id AND x.skill_id < y.skill_id
JOIN skills a ON a.id = x.skill_id
JOIN skills b ON b.id = y.skill_id
GROUP BY x.skill_id, y.skill_id
ORDER BY together DESC, skill_a, skill_b
LIMIT 10;
