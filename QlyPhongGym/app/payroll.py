PT_SESSION_RATE = 50000


def calculate_trainer_salary(base_salary, session_count, session_rate=PT_SESSION_RATE):
    base = float(base_salary or 0)
    count = int(session_count or 0)
    rate = float(session_rate or 0)
    return base + count * rate
