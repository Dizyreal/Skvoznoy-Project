from datetime import datetime, timedelta
import json
import os
import requests
import yaml


def extract_data(config_path="configs/variant_15.yml"):
    if not os.path.exists(config_path):
        print(f"[ERROR] Конфигурационный файл не найден по пути: {config_path}")
        return

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    variant_id = config.get("variant_id")
    source_type = config.get("source_type")

    api_config = config.get("api", {})
    base_url = api_config.get("base_url")
    method = api_config.get("method").upper()
    params = api_config.get("params", {})
    request_template = api_config.get("request_template", "")

    now = datetime.now()
    start_date = now - timedelta(days=90)

    params["starttime"] = start_date.strftime("%Y-%m-%d")
    params["endtime"] = now.strftime("%Y-%m-%d")

    if request_template:
        url = base_url.rstrip("/") + "/" + request_template.lstrip("/")
    else:
        url = base_url

    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=5)
        else:
            print(f"[ERROR] Метод {method} пока не поддерживается скриптом.")
            return

        response.raise_for_status()
        data = response.json()

    except requests.exceptions.Timeout:
        print("[ERROR] Превышено время ожидания ответа от сервера (5 сек).")
        return
    except requests.exceptions.HTTPError as http_err:
        print(
            f"[ERROR] Сервер вернул ошибку HTTP {http_err.response.status_code}"
        )
        return
    except requests.exceptions.JSONDecodeError:
        print("[ERROR] Ответ сервера не является валидным JSON-документом.")
        return
    except requests.exceptions.RequestException as net_err:
        print(f"[ERROR] Проблема с сетью или DNS: {net_err}")
        return

    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = os.path.join("data", "raw", f"variant_{variant_id}")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, f"{timestamp}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    data_size = len(data.get("features", [])) if "features" in data else 1

    print("\n--- [LOG SUCCESS] ---")
    print(f"Вариант: {variant_id}")
    print(f"Источник: {source_type}")
    print(f"URL: {response.url}")
    print(f"Статус ответа: {response.status_code}")
    print(f"Сохранено в: {output_path}")
    print(f"Получено {data_size} землетрясений(я) из GeoJSON")
    print("---------------------\n")


if __name__ == "__main__":
    extract_data()
