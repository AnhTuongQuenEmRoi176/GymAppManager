import re
from datetime import datetime

PHONE_RE = re.compile(r"^(0|\+84)[0-9]{8,10}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_phone(phone):
    return phone.replace(" ", "").replace("-", "").strip()


def validate_required(value, label):
    if not value or not value.strip():
        return f"{label} không được để trống"
    return None


def validate_phone(phone, required=True):
    phone = normalize_phone(phone)
    if not phone:
        return "SĐT không được để trống" if required else None
    if not PHONE_RE.match(phone):
        return "SĐT phải bắt đầu bằng 0 hoặc +84 và có 9-11 chữ số"
    return None


def validate_email(email, required=False):
    email = (email or "").strip()
    if not email:
        return "Email không được để trống" if required else None
    if not EMAIL_RE.match(email):
        return "Email không đúng định dạng"
    return None


def parse_iso_date(value, label, required=False):
    value = (value or "").strip()
    if not value:
        if required:
            raise ValueError(f"{label} không được để trống")
        return None
    try:
        return datetime.fromisoformat(value).date()
    except Exception as exc:
        raise ValueError(f"{label} phải theo định dạng YYYY-MM-DD") from exc


def parse_money(value, label, required=False):
    value = (value or "").strip()
    if not value:
        if required:
            raise ValueError(f"{label} không được để trống")
        return 0.0
    try:
        amount = float(value.replace(",", ""))
    except Exception as exc:
        raise ValueError(f"{label} phải là số") from exc
    if amount < 0:
        raise ValueError(f"{label} không được âm")
    return amount
