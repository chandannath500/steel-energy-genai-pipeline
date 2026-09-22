CREATE DATABASE IF NOT EXISTS steel_energy;
USE steel_energy;

CREATE TABLE IF NOT EXISTS energy_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    date DATETIME NOT NULL,
    Usage_kWh DOUBLE NOT NULL,
    Lagging_Current_Reactive_Power_kVarh DOUBLE,
    Leading_Current_Reactive_Power_kVarh DOUBLE,
    CO2tCO2 DOUBLE,
    Lagging_Current_Power_Factor DOUBLE,
    Leading_Current_Power_Factor DOUBLE,
    NSM BIGINT,
    WeekStatus VARCHAR(50),
    Day_of_week VARCHAR(50),
    Load_Type VARCHAR(50)
);
