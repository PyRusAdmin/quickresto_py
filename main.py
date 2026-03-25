# -*- coding: utf-8 -*-

import requests
from loguru import logger

from get_client_phone import print_client_info


# Импортируем только функцию, но не вызываем напрямую из get_full_client_info
# чтобы избежать циклических импортов

# https://quickresto.ru/api/


def get_all_clients():
    """Получает данные о всех клиентах"""

    all_clients = []
    limit = 500  # Максимально рекомендуемый размер порции для Quick Resto
    offset = 0  # Это смещение. Сначала мы берем первых 500 (с 0-го по 499-го).

    print("🚀 Начинаю загрузку всех клиентов...")

    while True:  # Бесконечный цикл пока не соберет все данные (клиентов)
        url = f"{base_url}/list"
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
                headers=headers,
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

    """Получение клиента по номеру телефона. Номер телефона должен быть в формате 79991234567"""

    print_client_info(
        layer_name_quickresto=layer_name_quickresto,  # имя слоя QuickResto
        phone_number='79493531398',  # номер телефона посетителя
        auth=auth,  # авторизация
        headers=headers  # заголовки
    )

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
