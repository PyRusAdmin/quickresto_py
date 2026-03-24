# -*- coding: utf-8 -*-
import json

import requests


def get_client_phone(layer_name_quickresto, phone, auth, headers):
    """
    Возвращает информацию о клиенте по номеру телефона

    :param layer_name_quickresto: название слоя quickresto
    :param phone: номер телефона
    :param auth: авторизация в quickresto
    :param headers: заголовки запроса
    :return: информация о клиенте
    """
    url = f"https://{layer_name_quickresto}.quickresto.ru/platform/online/bonuses/filterCustomers"

    payload = {
        'search': phone,
        'typeList': ['customer'],
        'limit': 10,
        'offset': 0
    }
    response = requests.post(url, json=payload, auth=auth, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


"""Получение клиента по номеру телефона"""

client = get_client_phone('89142839779')  # подставь реальный номер

if client:
    print(json.dumps(client, indent=2, ensure_ascii=False))

    console.print_json(json.dumps(client, indent=2, ensure_ascii=False))

print(100 * "#")
