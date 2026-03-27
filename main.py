# -*- coding: utf-8 -*-
import json

from rich.prompt import Prompt

from config import base_url, auth, headers, layer_name_quickresto, console
from core.create_client import create_client
from core.delete_customer import delete_customer
from core.get_all_clients import get_all_clients
from core.get_client_phone import get_customer_by_phone
from core.get_full_client_info import get_full_client_info
from core.update_customer_bonus import update_customer_bonus


# Импортируем только функцию, но не вызываем напрямую из get_full_client_info
# чтобы избежать циклических импортов

# https://quickresto.ru/api/


def run_get_all_clients():
    result = get_all_clients()
    console.print(f"[green]Всего клиентов: {len(result)}[/green]")


def run_update_customer_bonus():
    customer_id = int(Prompt.ask("Введите customer_id"))
    amount = float(Prompt.ask("Введите количество бонусов"))
    customer_phone = Prompt.ask("Введите номер телефона")
    result = update_customer_bonus(customer_id, amount, customer_phone)
    if result:
        console.print_json(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        console.print("[red]Ошибка при обновлении бонусов[/red]")


def run_delete_customer():
    customer_id = int(Prompt.ask("Введите customer_id для удаления"))
    result = delete_customer(customer_id, base_url, auth, headers)
    if result:
        console.print_json(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        console.print("[red]Ошибка при удалении клиента[/red]")


def run_get_full_client_info():
    client_id = int(Prompt.ask("Введите client_id"))
    result = get_full_client_info(client_id, base_url, auth, headers)
    if result:
        console.print_json(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        console.print("[red]Клиент не найден[/red]")


def run_create_client():
    name_customer = Prompt.ask("Введите имя клиента")
    phone_customer = Prompt.ask("Введите номер телефона")
    result = create_client(name_customer, phone_customer, base_url, auth, headers)
    if result:
        console.print_json(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        console.print("[red]Ошибка при создании клиента[/red]")


def run_get_customer_by_phone():
    phone_number = Prompt.ask("Введите номер телефона")
    result = get_customer_by_phone(layer_name_quickresto, phone_number, auth, headers)
    if result:
        console.print_json(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        console.print("[red]Клиент не найден[/red]")


def main():
    menu_items = [
        ("get_all_clients", "Получить всех клиентов", run_get_all_clients),
        ("update_customer_bonus", "Обновить бонусы клиента", run_update_customer_bonus),
        ("delete_customer", "Удалить клиента", run_delete_customer),
        ("get_full_client_info", "Получить полную информацию о клиенте", run_get_full_client_info),
        ("create_client", "Создать нового клиента", run_create_client),
        ("get_customer_by_phone", "Найти клиента по телефону", run_get_customer_by_phone),
    ]

    while True:
        console.clear()
        console.print("[bold cyan]Меню тестирования функций[/bold cyan]\n")

        for i, (_, desc, _) in enumerate(menu_items, 1):
            console.print(f"  [yellow]{i}.[/yellow] {desc}")

        console.print(f"\n  [yellow]0.[/yellow] Выход")

        choice = Prompt.ask(
            "\n[bold]Выберите пункт меню[/bold]",
            choices=[str(i) for i in range(len(menu_items) + 1)],
            show_choices=False,
        )

        if choice == "0":
            break

        idx = int(choice) - 1
        if 0 <= idx < len(menu_items):
            console.clear()
            _, _, func = menu_items[idx]
            try:
                func()
            except Exception as e:
                console.print(f"[red]Ошибка: {e}[/red]")

            console.input("\n[dim]Нажмите Enter для продолжения...[/dim]")


if __name__ == "__main__":
    main()
