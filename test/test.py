# -*- coding: utf-8 -*-
import json
from unittest.mock import Mock

import pytest
import requests

from core.update_customer_bonus import update_customer_bonus, print_update_customer_bonus


# ─────────────────────────────────────────────────────────────
# ФИКСТУРЫ
# ─────────────────────────────────────────────────────────────
@pytest.fixture
def mock_logger(mocker):
    """Фикстура для мока logger"""
    return mocker.patch("update_customer_bonus.logger")


@pytest.fixture
def mock_requests_post(mocker):
    """Фикстура для мока requests.post"""
    return mocker.patch("update_customer_bonus.requests.post")


@pytest.fixture
def mock_console(mocker):
    """Фикстура для мока console"""
    return mocker.patch("update_customer_bonus.console")


@pytest.fixture
def mock_json_module(mocker):
    """Фикстура для мока json.dumps"""
    return mocker.patch("update_customer_bonus.json.dumps")


@pytest.fixture
def mock_print(mocker):
    """Фикстура для мока встроенной функции print"""
    return mocker.patch("update_customer_bonus.print")


@pytest.fixture
def valid_response_mock():
    """Создаёт мок успешного ответа от API"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": "success",
        "data": {
            "customer_id": 7678,
            "bonus_balance": 150.0
        }
    }
    mock_response.raise_for_status = Mock()  # Не выбрасывает исключение
    return mock_response


# ─────────────────────────────────────────────────────────────
# ТЕСТЫ ДЛЯ update_customer_bonus
# ─────────────────────────────────────────────────────────────
class TestUpdateCustomerBonus:

    def test_success_response(self, mock_requests_post, mock_logger, valid_response_mock):
        """✅ Успешный ответ от API"""
        mock_requests_post.return_value = valid_response_mock

        result = update_customer_bonus(
            customer_id=7678,
            amount=100.0,
            customer_phone='79493531398'
        )

        # Проверяем результат
        assert result is not None
        assert result["status"] == "success"
        assert result["data"]["bonus_balance"] == 150.0

        # Проверяем, что запрос был сделан с правильными параметрами
        mock_requests_post.assert_called_once()
        call_kwargs = mock_requests_post.call_args[1]
        assert call_kwargs["json"]["customerToken"]["key"] == '79493531398'
        assert call_kwargs["json"]["amount"] == 100.0

        # Проверяем логирование
        mock_logger.info.assert_called_with("Редактирование бонусных балов для клиента 7678")

    @pytest.mark.parametrize("status_code,error_text", [
        (400, "Bad Request — неверные данные"),
        (401, "Unauthorized — ошибка авторизации"),
        (403, "Forbidden — доступ запрещён"),
        (404, "Not Found — клиент не найден"),
        (500, "Internal Server Error — ошибка сервера"),
    ])
    def test_http_errors(self, mock_requests_post, mock_logger, valid_response_mock, status_code, error_text):
        """❌ Различные HTTP-ошибки от API"""
        # Настраиваем мок для выброса HTTPError
        mock_requests_post.return_value.raise_for_status.side_effect = requests.HTTPError(error_text)
        mock_requests_post.return_value.status_code = status_code
        mock_requests_post.return_value.json.return_value = {"error": error_text}

        result = update_customer_bonus(
            customer_id=7678,
            amount=100.0,
            customer_phone='79493531398'
        )

        # Функция должна вернуть None при ошибке
        assert result is None
        # Ошибка должна быть залогирована
        mock_logger.exception.assert_called_once()

    def test_timeout_error(self, mock_requests_post, mock_logger):
        """❌ Таймаут запроса"""
        mock_requests_post.side_effect = requests.Timeout("Request timed out after 30 seconds")

        result = update_customer_bonus(
            customer_id=7678,
            amount=100.0,
            customer_phone='79493531398'
        )

        assert result is None
        mock_logger.exception.assert_called_once()
        # Проверяем, что исключение действительно было Timeout
        call_args = mock_logger.exception.call_args[0][0]
        assert isinstance(call_args, requests.Timeout)

    def test_connection_error(self, mock_requests_post, mock_logger):
        """❌ Ошибка соединения (сеть недоступна)"""
        mock_requests_post.side_effect = requests.ConnectionError("Failed to establish connection")

        result = update_customer_bonus(
            customer_id=7678,
            amount=100.0,
            customer_phone='79493531398'
        )

        assert result is None
        mock_logger.exception.assert_called_once()

    def test_json_decode_error(self, mock_requests_post, mock_logger):
        """❌ API вернул невалидный JSON"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        # Имитируем ошибку парсинга JSON
        mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "doc", 0)
        mock_requests_post.return_value = mock_response

        result = update_customer_bonus(
            customer_id=7678,
            amount=100.0,
            customer_phone='79493531398'
        )

        assert result is None
        mock_logger.exception.assert_called_once()

    def test_invalid_phone_format(self, mock_requests_post, mock_logger):
        """⚠️ Тест с невалидным форматом телефона (проверяет, что запрос уходит как есть)"""
        # Примечание: валидацию телефона нужно добавить в саму функцию,
        # если вы хотите отлавливать такие ошибки до запроса
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("400 Invalid phone")
        mock_response.status_code = 400
        mock_requests_post.return_value = mock_response

        result = update_customer_bonus(
            customer_id=7678,
            amount=100.0,
            customer_phone='invalid-phone!'  # Некорректный формат
        )

        # Проверяем, что в запросе ушёл именно этот номер
        call_kwargs = mock_requests_post.call_args[1]
        assert call_kwargs["json"]["customerToken"]["key"] == 'invalid-phone!'
        assert result is None


# ─────────────────────────────────────────────────────────────
# ТЕСТЫ ДЛЯ print_update_customer_bonus
# ─────────────────────────────────────────────────────────────
class TestPrintUpdateCustomerBonus:

    def test_print_success_result(
            self,
            mocker,
            mock_console,
            mock_json_module,
            mock_print
    ):
        """✅ Wrapper-функция выводит результат при успехе"""
        # Мокаем update_customer_bonus внутри модуля
        mock_update = mocker.patch(
            "update_customer_bonus.update_customer_bonus",
            return_value={"status": "ok", "balance": 200}
        )
        mock_json_module.return_value = '{"status": "ok", "balance": 200}'

        print_update_customer_bonus()

        # Проверяем вызов update_customer_bonus с дефолтными аргументами
        mock_update.assert_called_once_with(
            customer_id=7678,
            amount=0,
            customer_phone='79493531398'
        )
        # Проверяем сериализацию и вывод
        mock_json_module.assert_called_once_with(
            {"status": "ok", "balance": 200},
            indent=2,
            ensure_ascii=False
        )
        mock_console.print_json.assert_called_once_with('{"status": "ok", "balance": 200}')
        # print не должен вызываться при успехе
        mock_print.assert_not_called()

    def test_print_none_result(
            self,
            mocker,
            mock_console,
            mock_print
    ):
        """❌ Wrapper-функция выводит сообщение об ошибке, если результат None"""
        mock_update = mocker.patch(
            "update_customer_bonus.update_customer_bonus",
            return_value=None
        )

        print_update_customer_bonus()

        mock_update.assert_called_once()
        # console.print_json не должен вызываться
        mock_console.print_json.assert_not_called()
        # Должен быть вызван print с сообщением об ошибке
        mock_print.assert_called_once_with("Функция вернула None — смотри логи ошибок")


# ─────────────────────────────────────────────────────────────
# ИНТЕГРАЦИОННЫЙ ТЕСТ (опционально, требует реальных конфигов)
# ─────────────────────────────────────────────────────────────
@pytest.mark.integration
class TestUpdateCustomerBonusIntegration:
    """
    Интеграционные тесты — запускаются только с флагом --integration
    Пример: pytest --integration
    """

    def test_real_api_call_skipped_by_default(self):
        """Этот тест пропускается, если не указан флаг --integration"""
        pytest.skip("Интеграционный тест — требует реальных учётных данных API")

    # @pytest.mark.integration
    # def test_real_api_call(self):
    #     """Пример реального вызова (раскомментируйте для ручного тестирования)"""
    #     result = update_customer_bonus(
    #         customer_id=7678,
    #         amount=1.0,  # Минимальная сумма для теста
    #         customer_phone='79493531398'
    #     )
    #     assert result is not None
    #     assert "status" in result or "error" in result


# ─────────────────────────────────────────────────────────────
# КОНФИГУРАЦИЯ PYTEST (можно вынести в conftest.py)
# ─────────────────────────────────────────────────────────────
def pytest_addoption(parser):
    """Добавляет кастомный флаг --integration для запуска интеграционных тестов"""
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="Запускать интеграционные тесты с реальным API"
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: mark test as requiring real API connection"
    )


def pytest_collection_modifyitems(config, items):
    """Пропускает интеграционные тесты, если не указан флаг --integration"""
    if config.getoption("--integration"):
        return  # Запускаем все тесты
    # Пропускаем тесты с маркером @pytest.mark.integration
    skip_integration = pytest.mark.skip(reason="Требуется флаг --integration")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)
