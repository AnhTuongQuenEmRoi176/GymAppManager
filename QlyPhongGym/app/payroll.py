PT_SESSION_RATE = 50000
DEFAULT_RECEPTIONIST_SALARY = 0


def calculate_trainer_salary(base_salary, session_count, session_rate=PT_SESSION_RATE):
    base = float(base_salary or 0)
    count = int(session_count or 0)
    rate = float(session_rate or 0)
    return base + count * rate


def salary_token(employee_type, employee_id):
    return f"payroll:{employee_type}:{employee_id}"
