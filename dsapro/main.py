# main.py
import os
import csv
from patient import Patient
from data_structures.linked_list import LinkedList
from data_structures.queue import AppointmentQueue
from data_structures.stack import UndoStack
from data_structures.tree import PatientTree
from billing import calculate_bill

DATA_DIR = "data"
PATIENTS_FILE = os.path.join(DATA_DIR, "patients.csv")
APPTS_FILE = os.path.join(DATA_DIR, "appointments.csv")

def ensure_data_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(PATIENTS_FILE):
        with open(PATIENTS_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["patient_id","name","age","disease","doctor","registered_at"])
            writer.writeheader()
    if not os.path.exists(APPTS_FILE):
        with open(APPTS_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["patient_id"])  # header

def save_patients(linked_list: LinkedList):
    arr = linked_list.to_list()
    with open(PATIENTS_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["patient_id","name","age","disease","doctor","registered_at"])
        writer.writeheader()
        for d in arr:
            writer.writerow(d)

def load_patients(linked_list: LinkedList):
    arr = []
    try:
        with open(PATIENTS_FILE, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row and row["patient_id"]:
                    row["patient_id"] = int(row["patient_id"])
                    row["age"] = int(row["age"])
                    arr.append(row)
    except FileNotFoundError:
        return
    linked_list.load_from_list(arr)

def save_appointments(appts: AppointmentQueue):
    lst = appts.to_list()
    with open(APPTS_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["patient_id"])
        for pid in lst:
            writer.writerow([pid])

def load_appointments(appts: AppointmentQueue):
    arr = []
    try:
        with open(APPTS_FILE, newline="") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                if row:
                    arr.append(int(row[0]))
    except FileNotFoundError:
        return
    appts.load_from_list(arr)

def next_id(linked_list: LinkedList):
    m = linked_list.get_max_id()
    return m + 1

def register_patient(linked_list: LinkedList, tree: PatientTree, undo_stack: UndoStack):
    try:
        name = input("Enter patient name: ").strip()
        age = int(input("Enter age: ").strip())
        disease = input("Enter disease: ").strip()
        doctor = input("Enter assigned doctor: ").strip()
    except Exception as e:
        print("Invalid input. Registration cancelled.")
        return

    pid = next_id(linked_list)
    p = Patient(patient_id=pid, name=name, age=age, disease=disease, doctor=doctor)
    linked_list.insert_end(p)
    tree.insert(doctor, p.to_dict())
    undo_stack.push(("add", p.to_dict()))
    print(f"✅ Patient registered with ID {p.patient_id}")

def view_patients(linked_list: LinkedList):
    linked_list.display()
    def view_patients(linked_list: LinkedList):
        print("DEBUG: displaying patients...")   
    linked_list.display()
    
       

def schedule_appointment(appts: AppointmentQueue, linked_list: LinkedList, undo_stack: UndoStack):
    try:
        pid = int(input("Enter patient ID to schedule appointment: ").strip())
    except:
        print("Invalid ID.")
        return
    patient = linked_list.find_by_id(pid)
    if not patient:
        print("Patient ID not found.")
        return
    appts.enqueue(pid)
    undo_stack.push(("appointment_add", pid))
    print(f"Appointment scheduled for {patient.name} (ID {pid})")

def next_appointment(appts: AppointmentQueue, linked_list: LinkedList):
    pid = appts.dequeue()
    if pid is None:
        print("No appointments.")
        return
    p = linked_list.find_by_id(pid)
    if p:
        print(f"➡️ Next appointment: {p.name} (ID {pid}), Doctor: {p.doctor}")
        # quick billing demo
        base = float(input("Enter base fee for billing (or 0): ") or 0)
        tests = float(input("Tests cost (or 0): ") or 0)
        meds = float(input("Medicine cost (or 0): ") or 0)
        total = calculate_bill(base, tests, meds)
        print(f"Total bill: {total}")
    else:
        print(f"Patient ID {pid} not found in records.")

def search_by_doctor(tree: PatientTree):
    doc = input("Enter doctor's name to search patients: ").strip()
    res = tree.search(doc)
    if not res:
        print("No patients found for this doctor.")
        return
    print(f"Patients under Dr. {doc}:")
    for p in res:
        print(f"ID: {p['patient_id']} | Name: {p['name']} | Age: {p['age']} | Disease: {p['disease']} | Registered: {p['registered_at']}")

def delete_patient(linked_list: LinkedList, tree: PatientTree, undo_stack: UndoStack):
    try:
        pid = int(input("Enter patient ID to delete: ").strip())
    except:
        print("Invalid ID.")
        return
    patient = linked_list.find_by_id(pid)
    if not patient:
        print("ID not found.")
        return
    # store for undo
    undo_stack.push(("delete", patient.to_dict()))
    removed = linked_list.delete_by_id(pid)
    tree.remove(removed.doctor, pid)
    print(f"Patient ID {pid} deleted.")

def update_patient(linked_list: LinkedList, tree: PatientTree, undo_stack: UndoStack):
    try:
        pid = int(input("Enter patient ID to update: ").strip())
    except:
        print("Invalid ID.")
        return
    p = linked_list.find_by_id(pid)
    if not p:
        print("Patient not found.")
        return
    old = p.to_dict()
    print("Press enter to keep current value.")
    name = input(f"Name [{p.name}]: ").strip() or p.name
    age_in = input(f"Age [{p.age}]: ").strip()
    age = int(age_in) if age_in else p.age
    disease = input(f"Disease [{p.disease}]: ").strip() or p.disease
    doctor = input(f"Doctor [{p.doctor}]: ").strip() or p.doctor

    linked_list.update_by_id(pid, name=name, age=age, disease=disease, doctor=doctor)
    # rebuild tree safely
    tree.rebuild_from_list(linked_list.to_list())
    undo_stack.push(("update", old))
    print("Patient updated.")

    

def undo_action(undo_stack: UndoStack, linked_list: LinkedList, tree: PatientTree, appts: AppointmentQueue):
    undo_stack.undo(linked_list, tree, appts)

   


def save_all(linked_list: LinkedList, appts: AppointmentQueue):
    save_patients(linked_list)
    save_appointments(appts)
    print("Data saved to disk.")

def load_all(linked_list: LinkedList, tree: PatientTree, appts: AppointmentQueue):
    load_patients(linked_list)
    tree.rebuild_from_list(linked_list.to_list())
    load_appointments(appts)

def main():
    ensure_data_files()
    patients = LinkedList()
    appointments = AppointmentQueue()
    undo_stack = UndoStack()
    patient_tree = PatientTree()

    load_all(patients, patient_tree, appointments)

    while True:
        print("\n---  Patient Management System ---")
        print("1. Register Patient")
        print("2. View All Patients")
        print("3. Schedule Appointment")
        print("4. Next Appointment (serve)")
        print("5. Search Patients by Doctor")
        print("6. Update Patient")
        print("7. Delete Patient")
        print("8. Undo Last Action")
        print("9. Save Data")
        print("0. Exit")
        choice = input("Choice: ").strip()

        if choice == "1":
            register_patient(patients, patient_tree, undo_stack)
        elif choice == "2":
            view_patients(patients)
        elif choice == "3":
            schedule_appointment(appointments, patients, undo_stack)
        elif choice == "4":
            next_appointment(appointments, patients)
        elif choice == "5":
            search_by_doctor(patient_tree)
        elif choice == "6":
            update_patient(patients, patient_tree, undo_stack)
        elif choice == "7":
            delete_patient(patients, patient_tree, undo_stack)
        elif choice == "8":
            undo_action(undo_stack, patients, patient_tree, appointments)
        elif choice == "9":
            save_all(patients, appointments)
        elif choice == "0":
            save_all(patients, appointments)
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
