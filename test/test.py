# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

from update_customer_bonus import print_update_customer_bonus


class TestPrintUpdateCustomerBonus(unittest.TestCase):

    @patch('update_customer_bonus.update_customer_bonus')
    @patch('update_customer_bonus.console')
    @patch('update_customer_bonus.json')
    def test_print_update_customer_bonus_with_result(self, mock_json, mock_console, mock_update_customer_bonus):
        # Организуем мок-результат и настраиваем возвращаемые значения моков
        mock_result = {"status": "success", "data": {}}  # Пример успешного ответа от функции обновления бонуса
        mock_update_customer_bonus.return_value = mock_result  # Мокаем возвращаемое значение функции update_customer_bonus
        mock_json.dumps.return_value = '{"status": "success", "data": {}}'  # Мокаем результат сериализации в JSON

        # Вызываем тестируемую функцию
        print_update_customer_bonus()

        # Проверяем, что функция update_customer_bonus была вызвана один раз с правильными аргументами
        mock_update_customer_bonus.assert_called_once_with(customer_id=7678, amount=0, customer_phone='79493531398')
        # Проверяем, что json.dumps был вызван один раз с ожидаемыми параметрами
        mock_json.dumps.assert_called_once_with(mock_result, indent=2, ensure_ascii=False)
        # Проверяем, что console.print_json был вызван один раз с сериализованным JSON-объектом
        mock_console.print_json.assert_called_once_with('{"status": "success", "data": {}}')

    @patch('update_customer_bonus.update_customer_bonus')
    @patch('update_customer_bonus.print')
    def test_print_update_customer_bonus_no_result(self, mock_print, mock_update_customer_bonus):
        # Настраиваем мок, чтобы функция вернула None
        mock_update_customer_bonus.return_value = None

        # Вызываем тестируемую функцию
        print_update_customer_bonus()

        # Проверяем, что функция update_customer_bonus была вызвана один раз с правильными аргументами
        mock_update_customer_bonus.assert_called_once_with(customer_id=7678, amount=0, customer_phone='79493531398')
        # Проверяем, что была вызвана функция print с соответствующим сообщением об ошибке
        mock_print.assert_called_once_with("Функция вернула None — смотри логи ошибок")


if __name__ == '__main__':
    unittest.main()
