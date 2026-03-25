# -*- coding: utf-8 -*-
import json

import requests
from loguru import logger

from config import console
from main import base_url, auth, headers


def get_full_client_info(client_id, base_url, auth, headers):
    """Возвращает полную информацию об одном конкретном пользователе (клиенте)"""
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
    """Получение клиента по ID"""

    result = get_full_client_info(client_id=7677, base_url=base_url, auth=auth, headers=headers)  # подставь реальный ID
    if result:
        console.print_json(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    print_client_info()
