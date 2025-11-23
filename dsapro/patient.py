# patient.py
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class Patient:
    patient_id: int
    name: str
    age: int
    disease: str
    doctor: str
    registered_at: str = None

    def __post_init__(self):
        if not self.registered_at:
            self.registered_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return asdict(self)