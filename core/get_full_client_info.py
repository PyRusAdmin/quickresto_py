# -*- coding: utf-8 -*-
import requests
from loguru import logger


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
