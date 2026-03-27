# -*- coding: utf-8 -*-
import json

import requests
from loguru import logger

from config.config import console, base_url, auth, headers


# Убираем импорт из main.py чтобы избежать циклической зависимости
# base_url, auth, headers будут передаваться как параметры


def get_full_client_info(client_id, base_url, auth, headers):
    """
    Возвращает полную информацию об одном конкретном пользователе (клиенте)

    :param client_id: ID клиента
    :param base_url: базовый URL
    :param auth: аутентификация
    :param headers: заголовки
    :return: полную информацию об одном конкретном пользователе (клиенте)
    """
    url = f"{base_url}/read"

    query_params = {
        "moduleName": "crm.customer",
        "className": "ru.edgex.quickresto.modules.crm.customer.CrmCustomer",
        "objectId": client_id,  # ← objectId идёт в params, не в body
    }

    try:
        response = requests.get(
            url,
            params=query_params,
            auth=auth,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    except Exception as e:
        logger.exception(f"❌ Ошибка при чтении клиента {client_id}: {e}")
        return None


def print_client_info():
    result = get_full_client_info(client_id=7677, base_url=base_url, auth=auth, headers=headers)

    if not result:
        logger.error("Клиент не найден")
        return

    if result:
        console.print_json(json.dumps(result, indent=2, ensure_ascii=False))

    # Личные данные
    id_client = result.get('id')
    first_name = result.get('firstName', '—')
    middle_name = result.get('middleName', '—')
    last_name = result.get('lastName', '—')
    date_of_birth = result.get('dateOfBirth', '—')
    create_time = result.get('createTime', '—')

    # Телефон
    contacts = result.get('contactMethods', [])
    phone_number = contacts[0].get('value') if contacts else '—'

    # Бонусный счёт
    accounts = result.get('accounts', [])
    if accounts:
        account_balance = accounts[0].get('accountBalance', {})
        bonus_ledger = account_balance.get('ledger', 0)  # общий
        bonus_available = account_balance.get('available', 0)  # доступно
    else:
        bonus_ledger = bonus_available = 0

    # Накопительный баланс
    accumulation = result.get('accumulationBalance', {})
    accum_ledger = accumulation.get('ledger', 0)

    logger.info(f"ID:              {id_client}")
    logger.info(f"Имя:             {first_name} {middle_name} {last_name}")
    logger.info(f"Дата рождения:   {date_of_birth}")
    logger.info(f"Телефон:         {phone_number}")
    logger.info(f"Создан:          {create_time}")
    logger.info(f"Бонусы (всего):  {bonus_ledger}")
    logger.info(f"Бонусы (доступно): {bonus_available}")
    logger.info(f"Накопительный:   {accum_ledger}")


if __name__ == "__main__":
    print_client_info()
