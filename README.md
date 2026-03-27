# QuickResto API

Библиотека для работы с API QuickResto (клиенты, бонусы).

## Установка

1. Скопировать `.env.example` в `.env` и заполнить данные:
    ```
    LAYER_NAME_QUICKRESTO=your_layer
    USERNAME_QUICKRESTO=your_login
    PASSWORD_QUICKRESTO=your_password
    ```

2. Установить зависимости:

    ```bash
    pip install -r requirements.txt
    ```

## Использование

Запустить главное меню:

```bash
python main.py
```

## Функции

### get_all_clients

Получить всех клиентов.

```python
from config.config import base_url, auth, headers
from core.get_all_clients import get_all_clients

clients = get_all_clients(base_url, auth, headers)
```

### get_full_client_info

Получить полную информацию о клиенте по ID.

```python
from config.config import base_url, auth, headers
from core.get_full_client_info import get_full_client_info

client = get_full_client_info(client_id=12345, base_url=base_url, auth=auth, headers=headers)
```

### create_client

Создать нового клиента.

```python
from config.config import base_url, auth, headers
from core.create_client import create_client

result = create_client(
    name_customer='Иван',
    phone_customer='79000000000',
    base_url=base_url,
    auth=auth,
    headers=headers
)
```

### delete_customer

Удалить клиента по ID.

```python
from config.config import base_url, auth, headers
from core.delete_customer import delete_customer

result = delete_customer(customer_id=12345, base_url=base_url, auth=auth, headers=headers)
```

### get_customer_by_phone

Найти клиента по номеру телефона.

```python
from config.config import layer_name_quickresto, auth, headers
from core.get_client_phone import get_customer_by_phone

result = get_customer_by_phone(
    layer_name_quickresto='your_layer',
    phone_number='79000000000',
    auth=auth,
    headers=headers
)
```

### update_customer_bonus

Обновить бонусные баллы клиента.

```python
from config.config import layer_name_quickresto, auth, headers
from core.update_customer_bonus import update_customer_bonus

result = update_customer_bonus(
    layer_name_quickresto='your_layer',
    customer_id=12345,
    amount=100,
    customer_phone='79000000000',
    auth=auth,
    headers=headers
)
```
