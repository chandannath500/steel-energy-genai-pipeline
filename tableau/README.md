# Tableau Dashboard

Use the generated `data/processed/cleaned_energy_data.csv` or the MySQL `energy_data` table as the Tableau source.

## Recommended dashboard layout

### Executive KPI row

- Total Energy (kWh)
- Average Energy (kWh)
- Peak Energy (kWh)
- P95 Energy (kWh)
- Statistical Anomaly Count

### Visuals

- Energy consumption over time
- Daily energy consumption
- Average energy by hour
- Average energy by load type
- Energy vs power factor

### Filters

- Date
- Hour
- Load Type
- Week Status
- Day of Week

## Business questions

1. When does energy consumption peak?
2. Which load type has the highest average energy use?
3. Which periods contain statistical anomalies?
4. Is energy behavior different between weekdays and weekends?
5. What operating periods should be investigated further?
