# -*- coding: utf-8 -*-
import json

import requests
from loguru import logger

from config.config import console, layer_name_quickresto, auth, headers


def update_customer_bonus(layer_name_quickresto: str, customer_id: int, amount: float, customer_phone: str, auth,
                          headers):
    """
    Редактирование бонусных балов для клиента. Для изменения бонусных балов, требуется ID клиента в QuickResto и номер
    телефона клиента, котрый в базе данных QuickResto. Для получения ID клиента и номера телефона клиента,
    требуется можно использовать метод get_customer_by_phone.

    :param layer_name_quickresto: название слоя QuickResto
    :param customer_id: идентификатор клиента в QuickResto
    :param amount: количество бонусных балов для клиента в QuickResto
    :param customer_phone: номер телефона клиента в QuickResto
    :param auth: аутентификация
    :param headers: заголовки
    :return: результат выполнения запроса в формате JSON
    """
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

        response = requests.post(url, json=body, auth=auth, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()

    except Exception as e:
        logger.exception(e)


def print_update_customer_bonus():
    """Редактирование клиента"""
    from config.config import layer_name_quickresto, auth, headers

    result = update_customer_bonus(
        layer_name_quickresto=layer_name_quickresto,
        customer_id=7678,
        amount=0,
        customer_phone='79493531398',
        auth=auth,
        headers=headers
    )

    if result:
        console.print_json(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Функция вернула None — смотри логи ошибок")


if __name__ == "__main__":
    print_update_customer_bonus()
