import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os

# Загружаем переменные из файла .env (override=True переопределяет системные переменные)

'''
Если в системе Windows уже установлена переменная с таким же именем (например, USERNAME часто занято именем 
пользователя компьютера), этот флаг заставит Python взять значение именно из файла, а не из системы.
'''
load_dotenv(
    override=True  # Переопределение значений для существующих ключей (что бы случайно не взять занятое имя)
)

# Достаем данные из окружения
LAYER_NAME: str = os.getenv("LAYER_NAME")  # Извлекаем значение из .env файла
USERNAME: str = os.getenv("USERNAME")  # Извлекаем значение из .env файла
PASSWORD: str = os.getenv("PASSWORD")  # Извлекаем значение из .env файла

'''
HTTPBasicAuth: Quick Resto использует стандартную проверку «Логин:Пароль», зашифрованную в заголовке запроса.
BASE_URL: Автоматически подставляет имя «облака» (layer) в адрес запроса (username равное layer).
'''

BASE_URL = f"https://{LAYER_NAME}.quickresto.ru/platform/online/api"
auth = HTTPBasicAuth(USERNAME, PASSWORD)
HEADERS = {"Content-Type": "application/json"}


def get_all_clients():
    """Получает данные о всех клиентах"""

    all_clients = []
    limit = 500  # Максимально рекомендуемый размер порции для Quick Resto
    offset = 0  # Это смещение. Сначала мы берем первых 500 (с 0-го по 499-го).

    print("🚀 Начинаю загрузку всех клиентов...")

    while True:  # Бесконечный цикл пока не соберет все данные (клиентов)
        url = f"{BASE_URL}/list"
        query_params = {
            "moduleName": "crm.customer",
            "className": "ru.edgex.quickresto.modules.crm.customer.CrmCustomer"
        }
        payload = {
            "limit": limit,
            "offset": offset
        }

        try:
            response = requests.get(
                url,
                params=query_params,
                json=payload,
                auth=auth,
                headers=HEADERS,
                timeout=30
            )
            response.raise_for_status()

            batch = response.json()

            if not batch:
                # Если сервер вернул пустой список, значит мы дошли до конца
                break

            all_clients.extend(batch)
            print(f"📥 Загружено: {len(all_clients)}...")

            # Увеличиваем offset для следующей "страницы"
            offset += limit

            # Если вернулось меньше, чем мы просили, значит это была последняя страница
            if len(batch) < limit:
                break

        except Exception as e:
            print(f"❌ Ошибка на смещении {offset}: {e}")
            break

    return all_clients


if __name__ == "__main__":
    all_data = get_all_clients()

    print("\n" + "=" * 50)
    print(f"✅ Итого получено клиентов: {len(all_data)}")
    print("=" * 50)

    # Выведем первые 10 для проверки
    if all_data:
        print(f"{'ID':<7} | {'Имя':<25} | {'Телефон':<15}")
        print("-" * 50)
        for c in all_data[:10]:
            name = f"{c.get('firstName', '')} {c.get('lastName', '')}".strip() or "---"
            phone = c.get('phoneNumber', '---')
            print(f"{c.get('id', 0):<7} | {name:<25} | {phone:<15}")

        if len(all_data) > 10:
            print(f"... и еще {len(all_data) - 10} клиентов")
