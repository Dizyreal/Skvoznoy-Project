# Data Quality Rules

**Таблица:** `mart_earthquakes`  
**Реализация:** `src/week8/dq.py` — класс `DQChecker`  
**Отчёт:** `data/dq_report.json` (перезаписывается после каждого DAG Run)

---

## Проверки

| № | Название | Метод DQChecker | Слой | Критичность | Описание |
|---|----------|-----------------|------|-------------|----------|
| 1 | Table not empty | `check_not_empty()` | mart | **FAIL** | Таблица не должна быть пустой — если 0 строк, пайплайн упал |
| 2 | No NULLs in `date` | `check_not_null('date')` | mart | **FAIL** | Дата — первичный ключ, NULL недопустим |
| 3 | No NULLs in `earthquake_count` | `check_not_null('earthquake_count')` | mart | **FAIL** | Ключевая метрика не может быть NULL |
| 4 | Unique `date` | `check_unique('date')` | mart | **FAIL** | Одна строка = один день, дубли нарушают гранулярность |
| 5 | Magnitude range [0, 10] | `check_range('max_magnitude', 0, 10)` | mart | **FAIL** | Магнитуда вне диапазона — признак ошибки парсинга |
| 6 | Positive `earthquake_count` | `check_positive('earthquake_count')` | mart | **FAIL** | Количество событий не может быть ≤ 0 |

---

## Поведение при FAIL

- DQ Gate стоит **до** шага `load` в Airflow DAG
- При любом FAIL: DAG прерывается (`sys.exit(1)`), данные **не записываются** в PostgreSQL
- Airflow помечает DAG Run как `failed`, доступен retry

## Поведение при WARNING

- Пайплайн продолжается
- В `dq_report.json` проставляется статус `WARNING`
- Требует ручной проверки

---

## Business Key

`date` — уникальный идентификатор строки витрины. Используется как PK при idempotent-загрузке (`DELETE WHERE date = X` + `INSERT`).

---

## Пример отчёта dq_report.json

```json
{
  "timestamp": "2026-05-24T22:14:43",
  "table": "mart_earthquakes",
  "rows": 86,
  "checks": [
    {"name": "Table not empty",            "status": "PASS", "message": "Rows: 86"},
    {"name": "No NULLs in date",           "status": "PASS", "message": "Null count: 0"},
    {"name": "No NULLs in earthquake_count","status": "PASS", "message": "Null count: 0"},
    {"name": "Unique date",                "status": "PASS", "message": "Duplicates: 0"},
    {"name": "Range for max_magnitude",    "status": "PASS", "message": "Values out of range [0,10]: 0"},
    {"name": "Positive earthquake_count",  "status": "PASS", "message": "Non-positive count: 0"}
  ],
  "summary": {"total": 6, "pass": 6, "fail": 0, "warning": 0}
}
```
