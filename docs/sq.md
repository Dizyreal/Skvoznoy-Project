# Data Quality Rules

## Проверки для mart_earthquakes

| №   | Проверка                     | Слой | Критичность | Описание                                                |
| --- | ---------------------------- | ---- | ----------- | ------------------------------------------------------- |
| 1   | Table not empty              | mart | FAIL        | Таблица не должна быть пустой                           |
| 2   | No NULLs in date             | mart | FAIL        | Дата не может быть NULL                                 |
| 3   | No NULLs in earthquake_count | mart | FAIL        | Количество землетрясений не может быть NULL             |
| 4   | No NULLs in region_id        | mart | WARNING     | Регион может быть NULL только если данные не матчнулись |
| 5   | Unique date                  | mart | FAIL        | Каждая дата должна быть уникальной                      |
| 6   | Magnitude range 0-10         | mart | FAIL        | Магнитуда должна быть в диапазоне 0-10                  |
| 7   | Avg magnitude range 0-10     | mart | WARNING     | Средняя магнитуда должна быть в диапазоне 0-10          |
| 8   | Earthquake_count positive    | mart | FAIL        | Количество землетрясений должно быть > 0                |

## Business key

`date` - уникальный идентификатор строки витрины

## Отчет

Результаты проверок сохраняются в `data/dq_report.json`
