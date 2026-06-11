# Skvoznoy Project — Earthquake ETL Pipeline

Сквозной проект курса «Технологии программирования».
Вариант 15 — землетрясения в Калифорнии (USGS Earthquake API).

---

## Архитектура

```
USGS API
   │
   ▼
[Extract]  src/week6/extract.py      →  data/raw/variant_15/*.json
   │
   ▼
[Transform] src/week6/transform.py   →  data/mart/*.csv
   │
   ▼
[DQ Check]  src/week8/dq.py          →  data/dq_report.json
   │
   ▼
[Load]      src/week6/load.py        →  PostgreSQL (analytics.mart_earthquakes)
   │
   ▼
Metabase BI dashboard (localhost:3000)
```

**Оркестрация:** Apache Airflow 2.10.0 (DAG `etl_variant_15`)  
**БД:** PostgreSQL 16 (один инстанс для Airflow metadata и аналитики)  
**BI:** Metabase

---

## Быстрый старт

### Предварительные требования
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (запущен)
- Windows 10/11

### 1. Запустить весь стек одной командой

Дважды кликните **`start.bat`** в корне проекта (или запустите из cmd):

```cmd
start.bat
```

Скрипт последовательно:
1. Проверяет, что Docker Desktop работает
2. Поднимает PostgreSQL и создаёт базы данных
3. Инициализирует Airflow (при первом запуске ~2 минуты)
4. Запускает Airflow Webserver, Scheduler и Metabase

### 2. Доступные сервисы

| Сервис        | URL                        | Логин / Пароль           |
|---------------|----------------------------|--------------------------|
| Airflow UI    | http://localhost:8080      | `admin` / `admin`        |
| Metabase BI   | http://localhost:3000      | настраивается при первом входе |
| PostgreSQL    | `localhost:5432`           | см. таблицу ниже         |

**Базы данных:**

| База данных | Пользователь | Пароль     | Назначение               |
|-------------|--------------|------------|--------------------------|
| `analytics` | `student`    | `student_pw` | Данные о землетрясениях |
| `airflow`   | `airflow`    | `airflow`  | Метаданные Airflow       |

### 3. Остановить стек

```cmd
stop.bat
```

---

## Настройка Metabase (первый раз)

1. Откройте http://localhost:3000, создайте учётную запись администратора.
2. На шаге «Добавить данные» выберите PostgreSQL:
   - **Host:** `postgres` ← именно так, не `localhost` (Metabase внутри Docker)
   - **Port:** `5432`
   - **Database:** `analytics`
   - **User:** `student`
   - **Password:** `student_pw`
3. Таблица для анализа: `mart_earthquakes`

---

## Структура проекта

```
skvoznoy_project/
├── start.bat                  # Запустить весь стек
├── stop.bat                   # Остановить весь стек
├── docker-compose.yml         # Все сервисы (Postgres, Airflow, Metabase)
├── requirements.txt           # Python-зависимости (локальная разработка)
│
├── configs/
│   └── variant_15.yml         # Параметры USGS API (регион, bbox, magnitude)
│
├── dags/
│   └── etl_variant_15.py      # Airflow DAG: extract → transform → load → dq
│
├── src/
│   ├── week6/
│   │   ├── extract.py         # Загрузка данных из USGS API
│   │   ├── transform.py       # Нормализация + агрегация по дням
│   │   ├── load.py            # Запись в PostgreSQL
│   │   └── pipeline.py        # Локальный запуск (без Airflow)
│   ├── week8/
│   │   ├── dq.py              # DQChecker — проверки качества данных
│   │   └── dq_period.py       # DQ для конкретного периода
│   └── week9/
│       └── schema_check.py    # Проверка схемы таблиц в БД
│
├── notebooks/
│   ├── week3_eda.ipynb         # EDA — анализ сырых данных
│   ├── week4_mart.ipynb        # Построение mart-слоя
│   ├── week7_viz.ipynb         # Визуализации (matplotlib)
│   └── week13_ml.ipynb         # ML: предсказание активности
│
├── tests/
│   └── test_dq.py             # Unit-тесты DQChecker (pytest)
│
├── docs/
│   ├── Data_Contract.md       # Схемы raw / normalized / mart
│   ├── Implementation_Plan.md # Дизайн инкрементального пайплайна
│   └── data_dictionary.md     # Словарь данных
│
├── reference/
│   └── regions.csv            # Справочник регионов (для enrichment)
│
├── scripts/
│   ├── setup_env.bat          # Создать conda-окружение + установить зависимости
│   ├── smoke_test.py          # Проверка установленных зависимостей
│   ├── init_db.sql            # SQL-скрипт первичной инициализации БД
│   └── pipeline.bat           # Локальный запуск пайплайна (без Docker)
│
└── data/                      # Runtime-данные (в .gitignore)
    ├── raw/variant_15/        # Сырые JSON-ответы API
    ├── mart/                  # Агрегированные CSV-файлы
    ├── state/state.json       # Watermark последнего запуска
    └── dq_report.json         # Последний отчёт о качестве данных
```

---

## Схема данных

Подробно: [docs/Data_Contract.md](docs/Data_Contract.md)

**Слои:**
- **Raw** (`data/raw/`) — JSON-ответы USGS, один файл на запрос
- **Normalized** — одна строка = одно событие (`event_id` PK)
- **Mart** (`mart_earthquakes`) — одна строка = один день (`date` PK)

**Ключевые колонки mart:**

| Колонка               | Тип    | Описание                          |
|-----------------------|--------|-----------------------------------|
| `date`                | date   | Дата (PK)                         |
| `earthquake_count`    | int    | Количество землетрясений за день  |
| `avg_magnitude`       | float  | Средняя магнитуда                 |
| `max_magnitude`       | float  | Максимальная магнитуда            |
| `avg_magnitude_7d`    | float  | 7-дневная скользящая средняя      |
| `earthquake_count_7d` | float  | 7-дневное скользящее суммирование |
| `deep_events_pct`     | float  | Доля глубоких событий (> 70 км)   |
| `region_id`           | string | Код региона (`US_CA`)             |

---

## Локальная разработка (без Docker)

### Установка окружения

```cmd
cd scripts
setup_env.bat
```

Создаёт conda-окружение `my_project_env` (Python 3.10) и устанавливает все зависимости.

### Запуск пайплайна вручную

```cmd
# Полный прогон (из корня проекта)
conda run -n my_project_env python -m src.week6.pipeline --mode full

# Инкрементальный прогон
conda run -n my_project_env python -m src.week6.pipeline --mode incremental
```

### Тесты

```cmd
conda run -n my_project_env pytest tests/ -v
```

---

## Airflow DAG: `etl_variant_15`

Расписание: каждые 5 минут (`*/5 * * * *`)

```
start → extract → transform → load → dq → end
```

| Шаг         | Описание                                              |
|-------------|-------------------------------------------------------|
| `extract`   | Запрос к USGS API, сохранение JSON в `data/raw/`      |
| `transform` | Нормализация + агрегация по дням, сохранение CSV      |
| `load`      | Запись mart-таблицы в PostgreSQL (`replace` режим)    |
| `dq`        | Проверки качества: not null, unique, range; JSON-отчёт |

---

## ML-модуль (Week 13)

Ноутбук [notebooks/week13_ml.ipynb](notebooks/week13_ml.ipynb):
- Целевая переменная: `earthquake_count` следующего дня
- Модель: линейная регрессия (scikit-learn)
- Признаки: лаговые значения (lag-1..7), скользящие средние
- Метрики и сохранённые предсказания: `docs/ml/`

---

## Переменные окружения

Все пароли и настройки вынесены в `docker-compose.yml`.
Для продакшн-использования замените значения по умолчанию через `.env` файл:

```env
POSTGRES_PASSWORD=your_strong_password
AIRFLOW__WEBSERVER__SECRET_KEY=your_secret_key
```

---

*Автор: Евгасьев Дмитрий Олегович, вариант 15*
