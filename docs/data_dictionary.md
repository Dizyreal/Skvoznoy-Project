# Data Dictionary - Earthquakes California

## Overview

Daily aggregated earthquake data for California region (US_CA). Data source: USGS Earthquake API with magnitude >= 2.5.

## Columns Description

### date

**Business meaning:** Calendar date of aggregation  
**Format:** YYYY-MM-DD  
**Example:** 2026-05-24  
**Note:** One row per date, no gaps

### earthquake_count

**Business meaning:** Number of earthquakes that occurred on this date  
**Unit:** Count of events  
**Example:** 15  
**Note:** Includes all events with magnitude >= 2.5

### avg_magnitude

**Business meaning:** Average magnitude of all earthquakes on this date  
**Unit:** Magnitude (0-10 scale)  
**Example:** 2.8  
**Note:** NULL if no events

### max_magnitude / min_magnitude

**Business meaning:** Highest/lowest magnitude on this date  
**Unit:** Magnitude (0-10 scale)  
**Example:** 4.2  
**Note:** Useful for identifying significant events

### avg_depth_km / max_depth_km

**Business meaning:** Average/maximum depth of earthquakes  
**Unit:** Kilometers (km)  
**Example:** 12.5  
**Note:** Negative values possible (above sea level events)

### avg_magnitude_7d

**Business meaning:** 7-day rolling average of daily average magnitudes  
**Unit:** Magnitude (0-10 scale)  
**Example:** 2.9  
**Note:** Smooths daily noise, shows trends

### earthquake_count_7d

**Business meaning:** 7-day rolling sum of earthquake counts  
**Unit:** Count of events  
**Example:** 87  
**Note:** Identifies active periods

### deep_events_count / deep_events_pct

**Business meaning:** Count/percentage of events with depth > 70 km  
**Unit:** Count / Percent  
**Example:** 3 / 20.0  
**Note:** Deep events are less common in California

### year / month / week / day_of_week

**Business meaning:** Temporal components extracted from date  
**Unit:** Integer values  
**Note:** Used for seasonal and weekly analysis

### region_id / region_name

**Business meaning:** Geographic region identifier and name  
**Value:** US_CA / Калифорния (USA)  
**Note:** Fixed for this variant

## Example Row

| date       | earthquake_count | avg_magnitude | max_magnitude | avg_depth_km |
| ---------- | ---------------- | ------------- | ------------- | ------------ |
| 2026-05-24 | 12               | 2.9           | 4.2           | 15.3         |

## Usage Notes

- Use `date` as primary key for joins
- For time series, sort by `date`
- For weekly trends, use `avg_magnitude_7d` or `earthquake_count_7d`
- For seasonal analysis, use `month` and `year`
