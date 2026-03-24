# -*- coding: utf-8 -*-
import json

import requests
from loguru import logger

from main import base_url, auth, headers


def create_client(name_customer, phone_customer, BASE_URL, auth, headers):
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
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.exception(e)


def main():
    """Пример использования функции create_client"""
    client = create_client(
        name_customer='Виталий',
        phone_customer='79493531398',
        BASE_URL=base_url,
        auth=auth,
        headers=headers
    )
    if client:
        print(json.dumps(client, indent=2, ensure_ascii=False))
    print(100 * "#")


if __name__ == "__main__":
    main()
