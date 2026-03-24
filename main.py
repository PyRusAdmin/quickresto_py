# -*- coding: utf-8 -*-
import json
import os

import requests
from dotenv import load_dotenv
from loguru import logger
from requests.auth import HTTPBasicAuth
from rich.console import Console

console = Console()

# https://quickresto.ru/api/

# Загружаем переменные из файла .env (override=True переопределяет системные переменные)

'''
Если в системе Windows уже установлена переменная с таким же именем (например, USERNAME часто занято именем 
пользователя компьютера), этот флаг заставит Python взять значение именно из файла, а не из системы.
'''
load_dotenv(
    override=True  # Переопределение значений для существующих ключей (что бы случайно не взять занятое имя)
)

# Достаем данные из окружения
layer_name_quickresto: str = os.getenv("LAYER_NAME_QUICKRESTO")  # Извлекаем значение из .env файла
username_quickresto: str = os.getenv("USERNAME_QUICKRESTO")  # Извлекаем значение из .env файла
password_quickresto: str = os.getenv("PASSWORD_QUICKRESTO")  # Извлекаем значение из .env файла

'''
HTTPBasicAuth: Quick Resto использует стандартную проверку «Логин:Пароль», зашифрованную в заголовке запроса.
BASE_URL: Автоматически подставляет имя «облака» (layer) в адрес запроса (username равное layer).
'''

BASE_URL = f"https://{layer_name_quickresto}.quickresto.ru/platform/online/api"
auth = HTTPBasicAuth(username_quickresto, password_quickresto)
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


def get_full_client_info(client_id):
    """Возвращает полную информацию об одном конкретном пользователе (клиенте)"""
    url = f"{BASE_URL}/read"

    query_params = {
        "moduleName": "crm.customer",
        "className": "ru.edgex.quickresto.modules.crm.customer.CrmCustomer",
        "objectId": client_id,  # ← objectId идёт в params, не в body
    }

    try:
        response = requests.get(
            url,
            params=query_params,
            # json=payload,
            auth=auth,
            headers=HEADERS,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    except Exception as e:
        print(f"❌ Ошибка при чтении клиента {client_id}: {e}")
        return None


def create_client(name_customer, phone_customer):
    """Создание нового клиента"""
    try:
        url = f"{BASE_URL}/create"

        query_params = {
            "moduleName": "crm.customer",
            "className": "ru.edgex.quickresto.modules.crm.customer.CrmCustomer"
        }

        body = {
            "firstName": name_customer,
            "contactMethods": [
                {
                    "type": "phoneNumber",
                    "value": phone_customer
                }
            ]
        }

        # post - отправка запроса
        # get - получение данных

        response = requests.post(
            url,
            params=query_params,
            json=body,
            auth=auth,
            headers=HEADERS,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.exception(e)


def update_customer_bonus(customer_id: int, amount: float, customer_phone):
    """Редактирование бонусных балов для клиента"""
    try:
        logger.info(f"Редактирование бонусных балов для клиента {customer_id}")

        url = f"https://{layer_name_quickresto}.quickresto.ru/platform/online/bonuses/creditHold"

        body = {
            "customerToken": {
                "type": "phone",  # ← тип токена: телефон
                "entry": "manual",  # ← способ ввода: вручную
                "key": customer_phone  # ← сам номер телефона
            },
            "accountType": {
                "accountGuid": "bonus_account_type-1"  # ← из данных клиента
            },
            "amount": amount
        }

        response = requests.post(url, json=body, auth=auth, headers=HEADERS, timeout=30)
        response.raise_for_status()
        return response.json()

    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":

    """получение всех клиентов"""

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

    print(100 * "#")

    """Получение клиента по ID"""

    client = get_full_client_info(7677)  # подставь реальный ID
    if client:
        print(json.dumps(client, indent=2, ensure_ascii=False))

    print(100 * "#")

    """Создание нового клиента"""

    client = create_client('Виталий', '79493531398')
    if client:
        print(json.dumps(client, indent=2, ensure_ascii=False))

    print(100 * "#")

    """Получение клиента по номеру телефона"""

    # client = get_client_phone('79493531398')  # подставь реальный номер
    #
    # if client:
    #     print(json.dumps(client, indent=2, ensure_ascii=False))
    #
    #     console.print_json(json.dumps(client, indent=2, ensure_ascii=False))

    """Редактирование клиента"""

    result = update_customer_bonus(7678, 0, '79493531398')

    if result:
        console.print_json(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Функция вернула None — смотри логи ошибок")

    """Получение клиента по ID"""

    client = get_full_client_info(7678)

    if not client:
        logger.error("Клиент не найден")
    else:
        # Личные данные
        name = client.get('firstName', '—')
        surname = client.get('lastName', '—')
        guid = client.get('customerGuid', '—')

        # Телефон
        contacts = client.get('contactMethods', [])
        phone = contacts[0].get('value') if contacts else '—'

        # Баланс
        accounts = client.get('accounts', [])
        if accounts:
            balance = accounts[0].get('accountBalance', {})
            ledger = balance.get('ledger', 0)
            available = balance.get('available', 0)
        else:
            ledger = available = 0

        logger.info(f"Клиент:    {name} {surname}")
        logger.info(f"Телефон:   {phone}")
        logger.info(f"GUID:      {guid}")
        logger.info(f"Баланс:    {ledger} (доступно: {available})")
