# data_structures/linked_list.py
from patient import Patient
from typing import Optional, List

class Node:
    def __init__(self, patient: Patient):
        self.patient = patient
        self.next = None

class LinkedList:
    def __init__(self):
        self.head: Optional[Node] = None

    def insert_end(self, patient: Patient):
        new_node = Node(patient)
        if not self.head:
            self.head = new_node
            return
        temp = self.head
        while temp.next:
            temp = temp.next
        temp.next = new_node

    def display(self):
        temp = self.head
        if not temp:
            print("No patients registered.")
            return
        print("\nAll Patients:")
        print("-" * 60)
        while temp:
            p = temp.patient
            print(f"ID: {p.patient_id} | Name: {p.name} | Age: {p.age} | Disease: {p.disease} | Doctor: {p.doctor} | Registered: {p.registered_at}")
            temp = temp.next
        print("-" * 60)

    def find_by_id(self, pid: int) -> Optional[Patient]:
        temp = self.head
        while temp:
            if temp.patient.patient_id == pid:
                return temp.patient
            temp = temp.next
        return None

    def delete_by_id(self, pid: int) -> Optional[Patient]:
        prev = None
        curr = self.head
        while curr:
            if curr.patient.patient_id == pid:
                if prev:
                    prev.next = curr.next
                else:
                    self.head = curr.next
                return curr.patient
            prev = curr
            curr = curr.next
        return None

    def update_by_id(self, pid: int, **kwargs) -> bool:
        temp = self.head
        while temp:
            if temp.patient.patient_id == pid:
                for k, v in kwargs.items():
                    if hasattr(temp.patient, k):
                        setattr(temp.patient, k, v)
                return True
            temp = temp.next
        return False

    def to_list(self) -> List[dict]:
        arr = []
        temp = self.head
        while temp:
            arr.append(temp.patient.to_dict())
            temp = temp.next
        return arr

    def load_from_list(self, patients: List[dict]):
        self.head = None
        for d in patients:
            p = Patient(**d)
            self.insert_end(p)

    def get_max_id(self) -> int:
        m = 0
        temp = self.head
        while temp:
            if temp.patient.patient_id > m:
                m = temp.patient.patient_id
            temp = temp.next
        return m
