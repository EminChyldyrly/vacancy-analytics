-- title: Доля удалённых вакансий по месяцам (месяцы, где минимум 20 вакансий)
-- Неполные месяцы с малой выборкой отсекаем: по 4 вакансиям процент ничего не говорит.
SELECT
    strftime('%Y-%m', published_at) AS month,
    COUNT(*) AS vacancies,
    SUM(remote) AS remote_vacancies,
    ROUND(100.0 * SUM(remote) / COUNT(*), 1) AS remote_pct
FROM vacancies
GROUP BY month
HAVING COUNT(*) >= 20
ORDER BY month;
