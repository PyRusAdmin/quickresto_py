import requests
from loguru import logger


def main():
    try:
        url = "https://[имя_аккаунта].quickresto.ru/api/v1/clients"
        headers = {
            "Authorization": "Bearer your_api_key_here",
            "Accept": "application/json"
        }
        params = {
            "limit": 50,
            "offset": 0
        }

        response = requests.get(url, headers=headers, params=params)
        print(response.json())
    except requests.exceptions.InvalidURL:
        logger.error("Неверный URL")


if __name__ == '__main__':
    main()
