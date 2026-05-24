# SQL Checks for mart_earthquakes_california

Этот документ содержит наборы SQL-запросов для проверки качества данных (data quality checks) в витрине `mart_earthquakes_california`.

---

## Connection & Structure

```sql
-- Check connection and table exists
SELECT table_name
FROM information_schema.tables
WHERE table_name = 'mart_earthquakes_california';
```

---

## Data Quality Checks

### Check 1: Table is not empty

```sql
SELECT COUNT(*) AS row_count FROM mart_earthquakes_california;
```

- **Expected:** > 0

### Check 2: Date range validation

```sql
SELECT MIN(date) AS first_date, MAX(date) AS last_date FROM mart_earthquakes_california;
```

- **Expected:** Reasonable date range for California earthquakes (e.g., no dates from the future or year 1970).

### Check 3: No NULLs in key columns

```sql
SELECT
    SUM(CASE WHEN date IS NULL THEN 1 ELSE 0 END) AS null_dates,
    SUM(CASE WHEN earthquake_count IS NULL THEN 1 ELSE 0 END) AS null_counts,
    SUM(CASE WHEN region_id IS NULL THEN 1 ELSE 0 END) AS null_regions,
    SUM(CASE WHEN region_name IS NULL THEN 1 ELSE 0 END) AS null_region_names
FROM mart_earthquakes_california;
```

- **Expected:** 0 for all columns.

### Check 4: No duplicate dates per region

```sql
SELECT date, region_id, COUNT(*) AS dup_count
FROM mart_earthquakes_california
GROUP BY date, region_id
HAVING COUNT(*) > 1;
```

- **Expected:** 0 rows (уникальность грануляции витрины).

### Check 5: Magnitude range validation

```sql
SELECT
    MIN(avg_magnitude) AS min_avg_mag,
    MAX(avg_magnitude) AS max_avg_mag,
    MIN(max_magnitude) AS min_max_mag,
    MAX(max_magnitude) AS max_max_mag
FROM mart_earthquakes_california;
```

- **Expected:** All magnitudes between -2.0 and 10.0 (микроземлетрясения могут быть отрицательными, но не более 10).

### Check 6: Earthquake count non-negative

```sql
SELECT MIN(earthquake_count) AS min_count FROM mart_earthquakes_california;
```

- **Expected:** >= 0

### Check 7: Deep events percentage sanity

```sql
SELECT
    AVG(deep_events_pct) AS avg_deep_pct,
    MIN(deep_events_pct) AS min_deep_pct,
    MAX(deep_events_pct) AS max_deep_pct
FROM mart_earthquakes_california
WHERE deep_events_pct IS NOT NULL;
```

- **Expected:** All values strictly between 0 and 100.

### Check 8: Rolling window sanity

```sql
SELECT COUNT(*) AS invalid_rolling_count
FROM mart_earthquakes_california
WHERE earthquake_count_7d < earthquake_count;
```

- **Expected:** 0 (сумма за 7 дней не может быть меньше значения за один текущий день).

### Check 9: Total earthquakes by month (Trend analysis)

```sql
SELECT
    EXTRACT(YEAR FROM date) AS year,
    EXTRACT(MONTH FROM date) AS month,
    SUM(earthquake_count) AS monthly_count
FROM mart_earthquakes_california
GROUP BY 1, 2
ORDER BY 1, 2;
```

- **Expected:** No sharp, unexpected drops to 0 across consecutive months (маркер падения пайплайна).

### Check 10: Logical consistency of magnitudes

```sql
SELECT COUNT(*) AS invalid_magnitude_logic
FROM mart_earthquakes_california
WHERE max_magnitude < avg_magnitude;
```

- **Expected:** 0 (максимальная магнитуда всегда больше или равна средней).
