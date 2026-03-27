# -*- coding: utf-8 -*-
import json

import requests
from loguru import logger

from config.config import console, base_url, auth, headers


def create_client(name_customer, phone_customer, base_url, auth, headers):
    """
    Создание нового клиента

    :param name_customer: имя клиента
    :param phone_customer: телефон клиента
    :param base_url: базовый URL
    :param auth: аутентификация
    :param headers: заголовки запроса
    :return: результат запроса
    """
    try:
        url = f"{base_url}/create"

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
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.exception(e)


def demo_create_client():
    """Пример использования функции create_client"""
    result = create_client(
        name_customer='Виталий',
        phone_customer='79493531398',
        base_url=base_url,
        auth=auth,
        headers=headers
    )

    if result:
        print(f"Клиент с телефоном 79493531398 уже существует")
        console.print_json(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    demo_create_client()
