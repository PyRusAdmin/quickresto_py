# -*- coding: utf-8 -*-
import requests
from loguru import logger


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
