# -*- coding: utf-8 -*-
import requests


def get_customer_by_phone(layer_name_quickresto, phone_number, auth, headers):
    """
    Возвращает информацию о клиенте по номеру телефона

    :param layer_name_quickresto: название слоя quickresto
    :param phone_number: номер телефона
    :param auth: авторизация в quickresto
    :param headers: заголовки запроса
    :return: информация о клиенте
    """
    url = f"https://{layer_name_quickresto}.quickresto.ru/platform/online/bonuses/filterCustomers"

    payload = {
        'search': phone_number,
        'typeList': ['customer'],
        'limit': 10,
        'offset': 0
    }
    response = requests.post(url, json=payload, auth=auth, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()
