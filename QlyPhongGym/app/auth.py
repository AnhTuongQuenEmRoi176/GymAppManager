import bcrypt
from itsdangerous import URLSafeTimedSerializer
import os

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret')


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def generate_reset_token(email: str) -> str:
    s = URLSafeTimedSerializer(SECRET_KEY)
    return s.dumps(email)


def verify_reset_token(token: str, max_age=3600):
    s = URLSafeTimedSerializer(SECRET_KEY)
    try:
        return s.loads(token, max_age=max_age)
    except Exception:
        return None
