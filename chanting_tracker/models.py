from dataclasses import dataclass
from typing import Optional


@dataclass
class Devotee:
    id: Optional[int] = None
    name: str = ""
    phone: str = ""
    email: str = ""
    is_active: int = 1
    notes: str = ""


@dataclass
class Report:
    id: Optional[int] = None
    devotee_id: int = 0
    report_date: str = ""
    japa_count: int = 0
    chanting_hours: float = 0.0
    spiritual_notes: str = ""
    submitted_at: str = ""