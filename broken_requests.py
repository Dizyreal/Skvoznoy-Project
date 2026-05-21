import requests

url = "https://httpbin.org/delay/10"
#url = "https://httpbin.org/status/404"
#url = "https://httpbin.org/html"


try:
    response = requests.get(url, timeout=3)
    
    response.raise_for_status() #4xx or 5xx
    
    try:
        data = response.json()
        
        if "url" in data:
            print("Успех! Полученный URL:", data["url"])
        else:
            print("Ошибка: В ответе сервера отсутствует ключ 'url'.")
            
    except requests.exceptions.JSONDecodeError:
        print("[ОШИБКА ФОРМАТА]: Сервер вернул ответ, но он не является валидным JSON.")

except requests.exceptions.Timeout:
    print("[ОШИБКА ТАЙМАУТА]: Сервер отвечал слишком долго (превышено ограничение в 3 секунды).")

except requests.exceptions.HTTPError as http_err:
    print(f"[ОШИБКА СТАТУСА]: Сервер вернул ошибочный HTTP-код: {http_err.response.status_code}")

except requests.exceptions.RequestException as net_err:
    print(f"[ОШИБКА СЕТИ]: Проблемы с интернет-соединением или DNS: {net_err}")
