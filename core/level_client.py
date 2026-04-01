# -*- coding: utf-8 -*-
import json
import requests
from requests.auth import HTTPBasicAuth
from loguru import logger
from collections import Counter
import time

from config.config import layer_name_quickresto, username_quickresto, password_quickresto

BASE_URL = f"https://{layer_name_quickresto}.quickresto.ru/platform/online/api"
auth = HTTPBasicAuth(username_quickresto, password_quickresto)
headers = {"Content-Type": "application/json"}

# ── Уровни ────────────────────────────────────────────────────────────────────

LEVELS = [
    {"name": "Black", "min_amount": 60000},
    {"name": "Gold", "min_amount": 30000},
    {"name": "Silver", "min_amount": 10000},
    {"name": "Bronze", "min_amount": 0},
]


def get_level(accumulation: float) -> str:
    for level in LEVELS:
        if accumulation >= level["min_amount"]:
            return level["name"]
    return "Bronze"


# ── Загрузка всех клиентов ────────────────────────────────────────────────────


def get_all_clients_full() -> list:
    """Загружает полные данные всех клиентов через /api/read"""

    # Шаг 1 — получаем только ID через /api/list
    all_ids = []
    limit, offset = 500, 0

    logger.info("Загружаю список ID клиентов...")
    while True:
        response = requests.get(
            f"{BASE_URL}/list",
            params={
                "moduleName": "crm.customer",
                "className": "ru.edgex.quickresto.modules.crm.customer.CrmCustomer"
            },
            json={"limit": limit, "offset": offset},
            auth=auth, headers=headers, timeout=30
        )
        response.raise_for_status()
        batch = response.json()
        if not batch:
            break
        all_ids.extend([c["id"] for c in batch if c.get("id")])
        offset += limit
        if len(batch) < limit:
            break

    logger.info(f"Найдено ID: {len(all_ids)}")

    # Шаг 2 — для каждого ID запрашиваем полные данные
    full_clients = []
    errors = 0

    for i, client_id in enumerate(all_ids):
        try:
            response = requests.get(
                f"{BASE_URL}/read",
                params={
                    "moduleName": "crm.customer",
                    "className": "ru.edgex.quickresto.modules.crm.customer.CrmCustomer",
                    "objectId": client_id
                },
                auth=auth, headers=headers, timeout=30
            )
            response.raise_for_status()
            full_clients.append(response.json())

            # Прогресс каждые 100 клиентов
            if (i + 1) % 100 == 0:
                logger.info(f"Обработано: {i + 1}/{len(all_ids)}")

            # Пауза чтобы не перегружать сервер
            time.sleep(0.1)

        except Exception as e:
            logger.warning(f"Ошибка для ID {client_id}: {e}")
            errors += 1
            continue

    logger.info(f"Готово. Загружено: {len(full_clients)}, ошибок: {errors}")
    return full_clients


def get_all_clients() -> list:
    all_clients = []
    limit = 500
    offset = 0

    logger.info("Начинаю загрузку клиентов...")

    while True:
        response = requests.get(
            f"{BASE_URL}/list",
            params={
                "moduleName": "crm.customer",
                "className": "ru.edgex.quickresto.modules.crm.customer.CrmCustomer"
            },
            json={"limit": limit, "offset": offset},
            auth=auth,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        batch = response.json()

        if not batch:
            break

        all_clients.extend(batch)
        logger.info(f"Загружено: {len(all_clients)}...")
        offset += limit

        if len(batch) < limit:
            break

    return all_clients


# ── Обработка ─────────────────────────────────────────────────────────────────

def analyze_clients():
    clients = get_all_clients_full()
    logger.info(f"Всего клиентов: {len(clients)}")

    result = []

    for client in clients:
        # Личные данные
        client_id = client.get("id")
        first_name = client.get("firstName", "—")
        last_name = client.get("lastName", "—")

        # Телефон
        contacts = client.get("contactMethods", [])
        phone = contacts[0].get("value") if contacts else "—"

        # Накопительный баланс — основа для уровня
        accumulation = client.get("accumulationBalance", {})
        accum_amount = accumulation.get("ledger", 0) if isinstance(accumulation, dict) else 0

        # Бонусный счёт
        accounts = client.get("accounts", [])
        bonus = accounts[0].get("accountBalance", {}).get("ledger", 0) if accounts else 0

        # Уровень
        level = get_level(accum_amount)

        result.append({
            "id": client_id,
            "name": f"{first_name} {last_name}".strip(),
            "phone": phone,
            "accumulation": accum_amount,
            "bonus": bonus,
            "level": level,
        })

    # Сортируем по накопленной сумме — лучшие клиенты вверху
    result.sort(key=lambda x: x["accumulation"], reverse=True)

    return result


# ── Вывод ─────────────────────────────────────────────────────────────────────

def print_report(data: list):
    print("\n" + "=" * 75)
    print(f"{'ID':<7} | {'Имя':<25} | {'Телефон':<15} | {'Накоп.':<10} | {'Бонусы':<8} | Уровень")
    print("-" * 75)

    for c in data:
        print(
            f"{c['id']:<7} | "
            f"{c['name']:<25} | "
            f"{c['phone']:<15} | "
            f"{c['accumulation']:<10.1f} | "
            f"{c['bonus']:<8.1f} | "
            f"{c['level']}"
        )

    # Статистика по уровням
    level_counts = Counter(c["level"] for c in data)
    print("\n" + "=" * 75)
    print("📊 Распределение по уровням:")
    for level in ["Black", "Gold", "Silver", "Bronze"]:
        count = level_counts.get(level, 0)
        percent = count / len(data) * 100 if data else 0
        print(f"  {level:<8}: {count:>5} клиентов ({percent:.1f}%)")
    print("=" * 75)


if __name__ == "__main__":
    data = analyze_clients()
    print_report(data)

    # Сохраняем в JSON для дальнейшей работы
    with open("clients_levels.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info("Результат сохранён в clients_levels.json")
