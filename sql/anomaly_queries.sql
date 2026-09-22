USE steel_energy;

-- Highest energy observations for operational review
SELECT
    date,
    Usage_kWh,
    Load_Type,
    Day_of_week,
    WeekStatus
FROM energy_data
ORDER BY Usage_kWh DESC
LIMIT 20;

-- Highest energy observations by hour
SELECT
    HOUR(date) AS hour_of_day,
    COUNT(*) AS high_usage_observations,
    ROUND(AVG(Usage_kWh), 2) AS average_energy_kwh,
    ROUND(MAX(Usage_kWh), 2) AS peak_energy_kwh
FROM energy_data
GROUP BY HOUR(date)
ORDER BY average_energy_kwh DESC;
