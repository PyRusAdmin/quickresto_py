# -*- coding: utf-8 -*-
import os

from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
from rich.console import Console

console = Console()

# Загружаем переменные из файла .env (override=True переопределяет системные переменные)

'''
Если в системе Windows уже установлена переменная с таким же именем (например, USERNAME часто занято именем 
пользователя компьютера), этот флаг заставит Python взять значение именно из файла, а не из системы.
'''
load_dotenv(
    override=True  # Переопределение значений для существующих ключей (что бы случайно не взять занятое имя)
)

# Достаем данные из окружения
layer_name_quickresto: str = os.getenv("LAYER_NAME_QUICKRESTO")  # Извлекаем значение из .env файла
username_quickresto: str = os.getenv("USERNAME_QUICKRESTO")  # Извлекаем значение из .env файла
password_quickresto: str = os.getenv("PASSWORD_QUICKRESTO")  # Извлекаем значение из .env файла

'''
HTTPBasicAuth: Quick Resto использует стандартную проверку «Логин:Пароль», зашифрованную в заголовке запроса.
BASE_URL: Автоматически подставляет имя «облака» (layer) в адрес запроса (username равное layer).
'''

base_url = f"https://{layer_name_quickresto}.quickresto.ru/platform/online/api"
auth = HTTPBasicAuth(username_quickresto, password_quickresto)
headers = {"Content-Type": "application/json"}
