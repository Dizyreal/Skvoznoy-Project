# Data Contract

## 1. Информация

- **Источник:** USGS Earthquake Hazards Program (Геологическая служба США)
- **Тема:** Землетрясения в регионе Калифорния (USA)
- **Тип источника:** `usgs_earthquake` (внешнее географическое API)
- **URL:** `https://earthquake.usgs.gov/fdsnws/event/1/query`
- **HTTP-метод:** `GET`

## 2. Параметры запроса (Query Parameters)

| Параметр       | Тип    | Обязательный | Значение                                                     | Описание                                     |
| -------------- | ------ | ------------ | ------------------------------------------------------------ | -------------------------------------------- |
| `format`       | string | Да           | `geojson`                                                    | Формат сериализации геоданных                |
| `minmagnitude` | float  | Да           | `2.5`                                                        | Нижний порог магнитуды для фильтрации        |
| `minlatitude`  | float  | Да           | `32.0`                                                       | Южная граница bounding box региона US_CA     |
| `maxlatitude`  | float  | Да           | `42.0`                                                       | Северная граница bounding box региона US_CA  |
| `minlongitude` | float  | Да           | `-125.0`                                                     | Западная граница bounding box региона US_CA  |
| `maxlongitude` | float  | Да           | `-114.0`                                                     | Восточная граница bounding box региона US_CA |
| `starttime`    | string | Да           | Дата начала выборки в формате YYYY-MM-DD (последние 90 дней) |
| `endtime`      | string | Да           | Дата конца выборки в формате YYYY-MM-DD                      |

## 3. Регламент, ограничения и технические нюансы

- **Частота загрузки:** Раз в сутки по расписанию (скрипт `extract.py` стягивает скользящее окно за последние 90 дней для учета возможных корректировок данных задним числом).
- **Сетевой уровень:** Обязательный `timeout=5` секунд для предотвращения зависания потока при перегрузке серверов USGS.
- **Специфика формата:** Ответ приходит в формате GeoJSON. На этапе экстракции сырой файл пишется "как есть" (со структурой `features`, внутри которой лежат `properties` и `geometry`). Поля `starttime` и `endtime` рассчитываются скриптом динамически от текущей даты.
- **Аномалии данных (Notes):** Поле `depth_km` (в GeoJSON это третья координата в массиве `geometry.coordinates`) может принимать отрицательные значения. Это не баг, а особенность фиксации сейсмографами толчков выше уровня моря (например, в горах). На этапе Data Quality это нужно обрабатывать отдельно, а не просто дропать.

## 4. Raw слой (data/raw/)

| Поле       | Тип    | Описание                                                       |
| ---------- | ------ | -------------------------------------------------------------- |
| `type`     | string | Тип GeoJSON объекта ("FeatureCollection")                      |
| `metadata` | object | Метаданные запроса (generated, url, title, status, api, count) |
| `features` | array  | Массив событий землетрясений                                   |
| `bbox`     | array  | Bounding box всех событий                                      |

## 5. Normalized слой (data/normalized/)

### Зерно таблицы

Одна строка = одно событие землетрясения

### Схема таблицы: earthquakes

| Поле               | Тип        | Nullable | Описание                                                   |
| ------------------ | ---------- | -------- | ---------------------------------------------------------- |
| `event_id`         | object     | No       | Уникальный идентификатор события                           |
| `magnitude`        | float64    | Yes      | Магнитуда землетрясения                                    |
| `magnitude_type`   | object     | Yes      | Тип магнитуды (ml, mw, md, mlr и др.)                      |
| `place`            | object     | Yes      | Текстовое описание местоположения                          |
| `time`             | datetime64 | No       | Время события                                              |
| `updated`          | datetime64 | Yes      | Время последнего обновления данных                         |
| `url`              | object     | Yes      | Ссылка на страницу события на USGS                         |
| `felt`             | float64    | Yes      | Количество отчетов о ощутимости                            |
| `cdi`              | float64    | Yes      | Community Decimal Intensity (0-10)                         |
| `mmi`              | float64    | Yes      | Modified Mercalli Intensity (0-10)                         |
| `alert`            | object     | Yes      | Уровень оповещения (green/yellow/orange/red)               |
| `status`           | object     | Yes      | Статус обработки (automatic/reviewed)                      |
| `tsunami`          | int64      | Yes      | Флаг цунами (0 или 1)                                      |
| `significance`     | float64    | Yes      | Значимость события (0-1000)                                |
| `net`              | object     | Yes      | Идентификатор сейсмологической сети                        |
| `num_stations`     | float64    | Yes      | Количество станций, зафиксировавших событие                |
| `min_distance_deg` | float64    | Yes      | Минимальное расстояние до станции в градусах               |
| `rms`              | float64    | Yes      | Среднеквадратичная остаточная ошибка                       |
| `azimuthal_gap`    | float64    | Yes      | Наибольший азимутальный разрыв в покрытии станциями        |
| `latitude`         | float64    | No       | Широта эпицентра                                           |
| `longitude`        | float64    | No       | Долгота эпицентра                                          |
| `depth_km`         | float64    | Yes      | Глубина события в километрах (может быть отрицательной)    |
| `event_type`       | object     | Yes      | Тип сейсмического события (earthquake, quarry blast и др.) |
| `title`            | object     | Yes      | Заголовок события                                          |
| `time_year`        | int64      | No       | Год из времени события                                     |
| `time_month`       | int64      | No       | Месяц из времени события                                   |
| `time_day`         | int64      | No       | День из времени события                                    |
| `time_hour`        | int64      | No       | Час из времени события                                     |

### Шаги очистки (normalization)

1. **Приведение типов:** Числовые поля (mag, depth_km, felt, sig, nst, dmin, rms, gap) приведены к numeric с заменой ошибок на NaN
2. **Преобразование времени:** Поля time и updated конвертированы из unix timestamp (ms) в datetime
3. **Заполнение пропусков:** felt и tsunami заполнены 0 вместо NaN (отсутствие данных = отсутствие события)
4. **Добавление признаков:** Извлечены компоненты времени (год, месяц, день, час) для агрегаций
5. **Переименование колонок:** Приведены к человеко-читаемым названиям

### Источник полей в raw JSON

| normalized поле  | raw JSON путь                         |
| ---------------- | ------------------------------------- |
| `event_id`       | `features[*].id`                      |
| `magnitude`      | `features[*].properties.mag`          |
| `magnitude_type` | `features[*].properties.magType`      |
| `place`          | `features[*].properties.place`        |
| `time`           | `features[*].properties.time`         |
| `updated`        | `features[*].properties.updated`      |
| `latitude`       | `features[*].geometry.coordinates[1]` |
| `longitude`      | `features[*].geometry.coordinates[0]` |
| `depth_km`       | `features[*].geometry.coordinates[2]` |

## Data Quality Rules

### Normalized layer

- `event_id` - уникальный, не NULL
- `magnitude` - диапазон 0-10
- `depth_km` - может быть отрицательным (специфика USGS)
- `time` - не NULL, корректный timestamp

### Mart layer

- `date` - уникальный, не NULL
- `earthquake_count` - положительное число, не NULL
- `avg_magnitude` - диапазон 0-10
- `max_magnitude` - диапазон 0-10
