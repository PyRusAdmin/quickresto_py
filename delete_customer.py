# -*- coding: utf-8 -*-
import requests
from loguru import logger

from main import base_url, auth, headers


def delete_customer(customer_id: int, base_url, auth, headers):
    """
    Удаление клиента по ID

    :param customer_id: ID клиента
    :param base_url: базовый URL
    :param auth: аутентификация
    :param headers: заголовки
    """
    try:
        logger.info(f"Удаление клиента {customer_id}")

        url = f"{base_url}/remove"

        query_params = {
            "moduleName": "crm.customer",
            "className": "ru.edgex.quickresto.modules.crm.customer.CrmCustomer"
        }

        body = {
            "id": customer_id  # ← id в теле, не в params
        }

        response = requests.post(  # ← POST, не DELETE
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


"""Удаление клиента по ID"""

delete_customer(customer_id=7678, base_url=base_url, auth=auth, headers=headers)
