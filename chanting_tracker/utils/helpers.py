from datetime import date, timedelta
from typing import List


def get_last_7_dates() -> List[str]:
    today = date.today()
    return [(today - timedelta(days=i)).isoformat() for i in range(6, -1, -1)]


def format_count(value: int) -> str:
    return str(value)


def safe_float(value) -> float:
    try:
        return float(value)
    except:
        return 0.0