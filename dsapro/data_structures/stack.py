# data_structures/stack.py
from typing import List, Tuple, Optional

# Undo stack actions:
# ("add", patient_dict) -> remove this patient on undo
# ("delete", patient_dict) -> re-add this patient on undo
# ("update", old_patient_dict, new_patient_dict) -> revert to old on undo
# ("appointment_add", patient_id) -> remove last appointment

class UndoStack:
    def __init__(self):
        self.stack: List = []

    def push(self, item):
        self.stack.append(item)

    def pop(self):
        return self.stack.pop() if self.stack else None

    def undo(self, patients_linked_list, patient_tree, appointments_queue):
        if not self.stack:
            print("Nothing to undo.")
            return
        action = self.pop()
        typ = action[0]

        if typ == "add":
            patient_dict = action[1]
            pid = patient_dict["patient_id"]
            removed = patients_linked_list.delete_by_id(pid)
            if removed:
                # also remove from tree
                patient_tree.remove(patient_dict["doctor"], pid)
            print(f"Undo: removed patient ID {pid}")

        elif typ == "delete":
            patient_dict = action[1]
            from patient import Patient
            p = Patient(**patient_dict)
            patients_linked_list.insert_end(p)
            patient_tree.insert(p.doctor, patient_dict)
            print(f"Undo: restored patient ID {p.patient_id}")

        elif typ == "update":
            old = action[1]
            pid = old["patient_id"]
            patients_linked_list.update_by_id(pid,
                                             name=old["name"],
                                             age=int(old["age"]),
                                             disease=old["disease"],
                                             doctor=old["doctor"])
            # For simplicity, rebuild tree entries by deleting then re-inserting
            patient_tree.rebuild_from_list(patients_linked_list.to_list())
            print(f"Undo: reverted update for patient ID {pid}")

        elif typ == "appointment_add":
            pid = action[1]
            # remove last occurrence of pid in queue (reverse search)
            lst = appointments_queue.to_list()
            if pid in lst:
                # remove last occurrence
                for i in range(len(lst)-1, -1, -1):
                    if lst[i] == pid:
                        lst.pop(i)
                        break
                appointments_queue.load_from_list(lst)
                print(f"Undo: removed appointment for patient ID {pid}")

        else:
            print("Unknown undo action.")