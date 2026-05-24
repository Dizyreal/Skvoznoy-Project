# Data Contract

**Project:** SKVOZNOY_PROJECT  
**Variant:** 15  
**Source:** USGS Earthquake API (California region)  
**Contract Version:** 1.0  
**Last Updated:** 2026-05-24

## Timezone

All timestamps are in **UTC**. No local time conversions applied.

## Granularity

- **Raw:** One file per API request
- **Normalized:** One row = one earthquake event
- **Mart:** One row = one calendar day

## Changelog

| Version | Date       | Change           | Reason        |
| ------- | ---------- | ---------------- | ------------- |
| 1.0     | 2026-05-24 | Initial contract | First release |

## Naming Rules

- All columns: `snake_case`
- Primary key: `event_id` (normalized), `date` (mart)
- Metrics: `avg_*`, `max_*`, `min_*`, `cnt_*`
- No abstract names like `value`, `metric1`

## Normalized Schema

| Column    | Type     | Nullable | Unit    | Description                  |
| --------- | -------- | -------- | ------- | ---------------------------- |
| event_id  | string   | No       | -       | Unique earthquake identifier |
| magnitude | float    | Yes      | -       | Earthquake magnitude (0-10)  |
| mag_type  | string   | Yes      | -       | Magnitude type (ml, mw, md)  |
| place     | string   | Yes      | -       | Textual location description |
| time      | datetime | No       | UTC     | Event occurrence time        |
| updated   | datetime | Yes      | UTC     | Last USGS update time        |
| felt      | int      | Yes      | count   | Number of felt reports       |
| tsunami   | int      | Yes      | flag    | Tsunami flag (0 or 1)        |
| latitude  | float    | No       | degrees | Epicenter latitude           |
| longitude | float    | No       | degrees | Epicenter longitude          |
| depth_km  | float    | Yes      | km      | Event depth                  |
| region_id | string   | No       | -       | Region code (US_CA)          |

## Mart Schema

| Column              | Type   | Nullable | Unit    | Description                 |
| ------------------- | ------ | -------- | ------- | --------------------------- |
| date                | date   | No       | -       | Calendar date (daily grain) |
| earthquake_count    | int    | No       | count   | Total earthquakes per day   |
| avg_magnitude       | float  | Yes      | -       | Average daily magnitude     |
| max_magnitude       | float  | Yes      | -       | Maximum daily magnitude     |
| min_magnitude       | float  | Yes      | -       | Minimum daily magnitude     |
| avg_depth_km        | float  | Yes      | km      | Average daily depth         |
| max_depth_km        | float  | Yes      | km      | Maximum daily depth         |
| avg_magnitude_7d    | float  | Yes      | -       | 7-day rolling avg magnitude |
| earthquake_count_7d | float  | Yes      | count   | 7-day rolling sum           |
| deep_events_count   | int    | Yes      | count   | Events with depth > 70 km   |
| deep_events_pct     | float  | Yes      | percent | Percentage of deep events   |
| year                | int    | No       | -       | Year extracted from date    |
| month               | int    | No       | -       | Month extracted from date   |
| week                | int    | No       | -       | Week number                 |
| day_of_week         | int    | No       | -       | Day of week (0=Monday)      |
| region_id           | string | No       | -       | Region code                 |
| region_name         | string | No       | -       | Human-readable region name  |

## Business Keys

- **Normalized:** `event_id`
- **Mart:** `date`

## Critical Rules

1. `date` must be unique in mart
2. `earthquake_count` must be > 0
3. `magnitude` must be between 0 and 10
4. `time` cannot be NULL
