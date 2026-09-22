USE steel_energy;

-- Core energy KPIs
SELECT
    ROUND(SUM(Usage_kWh), 2) AS total_energy_kwh,
    ROUND(AVG(Usage_kWh), 2) AS average_energy_kwh,
    ROUND(MIN(Usage_kWh), 2) AS minimum_energy_kwh,
    ROUND(MAX(Usage_kWh), 2) AS peak_energy_kwh
FROM energy_data;

-- Distribution statistics
SELECT
    COUNT(*) AS observations,
    ROUND(AVG(Usage_kWh), 2) AS mean_usage_kwh,
    ROUND(STDDEV_SAMP(Usage_kWh), 2) AS std_usage_kwh
FROM energy_data;

-- Daily energy profile
SELECT
    DATE(date) AS energy_date,
    ROUND(SUM(Usage_kWh), 2) AS total_energy_kwh,
    ROUND(AVG(Usage_kWh), 2) AS average_energy_kwh,
    ROUND(MAX(Usage_kWh), 2) AS peak_energy_kwh
FROM energy_data
GROUP BY DATE(date)
ORDER BY energy_date;

-- Hourly profile
SELECT
    HOUR(date) AS hour_of_day,
    ROUND(AVG(Usage_kWh), 2) AS average_energy_kwh,
    ROUND(MAX(Usage_kWh), 2) AS peak_energy_kwh
FROM energy_data
GROUP BY HOUR(date)
ORDER BY hour_of_day;

-- Load-type comparison
SELECT
    Load_Type,
    ROUND(AVG(Usage_kWh), 2) AS average_energy_kwh,
    ROUND(SUM(Usage_kWh), 2) AS total_energy_kwh,
    ROUND(MAX(Usage_kWh), 2) AS peak_energy_kwh,
    COUNT(*) AS observations
FROM energy_data
GROUP BY Load_Type
ORDER BY average_energy_kwh DESC;
