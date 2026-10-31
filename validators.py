# Валидация данных перед отправкой в БД
import datetime
import re

def validate_not_empty(value, field_name):
    if not value or value.strip() == "":
        raise ValueError(f"Поле '{field_name}' не может быть пустым.")

def validate_length(value, field_name, max_len):
    if len(value) > max_len:
        raise ValueError(f"Поле '{field_name}' не должно превышать {max_len} символов.")

def validate_email(email):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValueError("Некорректный формат email.")

def validate_date(date_str, field_name):
    try:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        if date_obj > datetime.date.today():
            raise ValueError(f"Дата '{field_name}' не может быть в будущем.")
        return date_obj
    except ValueError:
        raise ValueError(f"Дата '{field_name}' должна быть в формате ГГГГ-ММ-ДД и не быть в будущем.")

def validate_choice(value, field_name, choices):
    if value not in choices:
        raise ValueError(f"Поле '{field_name}' должно быть одним из: {', '.join(choices)}.")
