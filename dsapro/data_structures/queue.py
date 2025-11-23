# data_structures/queue.py
from collections import deque
from typing import Optional, List

class AppointmentQueue:
    def __init__(self):
        self.q = deque()

    def enqueue(self, patient_id: int):
        self.q.append(patient_id)

    def dequeue(self) -> Optional[int]:
        return self.q.popleft() if self.q else None

    def peek(self) -> Optional[int]:
        return self.q[0] if self.q else None

    def is_empty(self) -> bool:
        return len(self.q) == 0

    def to_list(self) -> List[int]:
        return list(self.q)

    def load_from_list(self, arr: List[int]):
        self.q = deque(arr)