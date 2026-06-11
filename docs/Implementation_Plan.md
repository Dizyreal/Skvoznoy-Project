# Implementation Plan

**Project:** SKVOZNOY_PROJECT — Earthquake ETL Pipeline  
**Variant:** 15 — USGS Earthquakes, California  
**Last Updated:** 2026-06-11

---

## Архитектура пайплайна

```
USGS Earthquake API
        │
        ▼
  [Extract]           src/week6/extract.py
  Запрос к API        → data/raw/variant_15/<timestamp>.json
        │
        ▼
  [Transform]         src/week6/transform.py
  Нормализация        → data/mart/mart_<date>.csv
  + Агрегация по дням
  + Rolling metrics
        │
        ▼
  [DQ Gate]           src/week8/dq.py
  Проверки качества   → data/dq_report.json
  (блокирует Load     
   при FAIL)
        │
        ▼
  [Load]              src/week6/load.py
  Запись в            → PostgreSQL: analytics.mart_earthquakes
  PostgreSQL
```

**Оркестрация:** Apache Airflow 2.10.0, DAG `etl_variant_15`  
**Расписание:** каждую минуту (`* * * * *`)

---

## Слои данных

| Слой | Путь | Гранулярность | Формат |
|------|------|---------------|--------|
| Raw | `data/raw/variant_15/` | 1 файл = 1 API-запрос | JSON (GeoJSON) |
| Normalized | (in-memory) | 1 строка = 1 событие | DataFrame |
| Mart | `data/mart/` + PostgreSQL | 1 строка = 1 день | CSV + таблица |

---

## Режимы запуска пайплайна

### Full mode
```
python -m src.week6.pipeline --mode full
```
- Запрашивает последние 90 дней из API
- Полностью пересоздаёт mart-таблицу (`mode='replace'`)
- Обновляет `state.json` с новым watermark

### Incremental mode
```
python -m src.week6.pipeline --mode incremental
```
- Запрашивает данные начиная с `last_watermark` из `state.json`
- Добавляет только новые строки (`mode='append'`)
- Безопасен при повторном запуске (idempotent)

---

## Инкрементальность и идемпотентность

### Watermark

Хранится в `data/state/state.json`:

```json
{
  "last_watermark": "2026-05-25",
  "last_run": "2026-05-25T10:30:00",
  "mode": "incremental"
}
```

Обновляется **только после успешного** выполнения всех этапов.

### Idempotent Load

- `full`: `DELETE TABLE` + `INSERT` — повторный запуск полностью заменяет данные
- `incremental`: `DELETE WHERE date = period` + `INSERT` — удаляет старые данные за период перед вставкой
- Retry в Airflow безопасен: повторная попытка того же периода не создаёт дублей

### Backfill

Backfill безопасен: каждый DAG Run обрабатывает свой период независимо. Повторный запуск любого периода даёт тот же результат.

---

## DQ Gate

DQ-проверки запускаются **до** загрузки в PostgreSQL. Если хотя бы одна проверка возвращает FAIL — DAG прерывается и данные не записываются.

| Проверка | Критичность | При FAIL |
|----------|-------------|---------|
| Table not empty | FAIL | Stop pipeline |
| No NULLs in date | FAIL | Stop pipeline |
| No NULLs in earthquake_count | FAIL | Stop pipeline |
| Unique date (no duplicates) | FAIL | Stop pipeline |
| Magnitude range [0, 10] | FAIL | Stop pipeline |
| Earthquake count > 0 | FAIL | Stop pipeline |

Отчёт сохраняется в `data/dq_report.json` после каждого запуска.

---

## Airflow DAG: etl_variant_15

```
start → extract → transform → load → dq → end
```

| Шаг | Файл | Описание |
|-----|------|----------|
| `extract` | `src/week6/extract.py` | GET-запрос к USGS API, сохранение JSON |
| `transform` | `src/week6/transform.py` | Нормализация событий, агрегация по дням, rolling-метрики |
| `load` | `src/week6/load.py` | Запись mart CSV в таблицу `mart_earthquakes` |
| `dq` | `src/week8/dq.py` | 6 проверок качества, JSON-отчёт |

**Retry policy:** `retries=1` — одна автоматическая попытка при падении шага.

---

## Конфигурация источника

Файл `configs/variant_15.yml`:

```yaml
variant_id: 15
source_type: api
api:
  base_url: https://earthquake.usgs.gov/fdsnws/event/1
  method: GET
  params:
    format: geojson
    minmagnitude: 2.5
    minlatitude: 32
    maxlatitude: 42
    minlongitude: -125
    maxlongitude: -114
```

Регион: Калифорния (bbox: lat 32–42, lon –125 – –114)  
Фильтр: магнитуда ≥ 2.5  
Окно запроса: последние 90 дней от текущей даты

---

## Enrichment

Таблица `reference/regions.csv` используется для добавления колонок `region_id` и `region_name` к mart-данным на шаге transform.

---

## Инфраструктура (Docker)

| Сервис | Образ | Порт | Назначение |
|--------|-------|------|------------|
| postgres | postgres:16 | 5432 | Хранилище данных |
| airflow-webserver | apache/airflow:2.10.0 | 8080 | UI оркестратора |
| airflow-scheduler | apache/airflow:2.10.0 | — | Запуск DAG по расписанию |
| metabase | metabase/metabase:latest | 3000 | BI-дашборды |

Запуск всего стека: `start.bat`  
Остановка: `stop.bat`
