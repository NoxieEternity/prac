"""Серверная проверка полей регистрации."""
import re

class RegistrationValidator:
    @staticmethod
    def validate(form):
        errors = {}
        login = form.get("login", "")
        password = form.get("password", "")
        full_name = form.get("full_name", "")
        phone = form.get("phone", "")
        email = form.get("email", "")
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{3,19}", login):
            errors["login"] = "От 4 до 20 символов: латинские буквы, цифры и _, первый символ — буква"
        if len(password) < 6:
            errors["password"] = "Пароль должен содержать не менее 6 символов"
        if len(full_name.split()) < 2 or not re.fullmatch(r"[А-Яа-яЁё -]+", full_name):
            errors["full_name"] = "Введите фамилию и имя русскими буквами"
        if not re.fullmatch(r"8\(\d{3}\)\d{3}-\d{2}-\d{2}", phone):
            errors["phone"] = "Формат: 8(900)123-45-67"
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            errors["email"] = "Введите корректный адрес электронной почты"
        return errors
