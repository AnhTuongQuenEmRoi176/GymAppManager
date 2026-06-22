"""Simple in-memory app state to hold current user for session-wide checks."""
current_user = None


def set_current_user(user):
    global current_user
    current_user = user


def get_current_user():
    return current_user


def is_admin():
    user = get_current_user()
    try:
        return bool(user and user.role and user.role.name == 'admin')
    except Exception:
        return False
