# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from main import (
    Patient, LinkedList, AppointmentQueue, UndoStack, PatientTree,
    register_patient, view_patients, schedule_appointment, next_appointment,
    search_by_doctor, delete_patient, update_patient, undo_action,
    save_all, load_all, calculate_bill
)
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "super-secret-key-CHANGE-ME"

# --- Global in-memory data structures ---
patients_ll = LinkedList()
appointments_q = AppointmentQueue()
undo_stack = UndoStack()
patient_tree = PatientTree()

# Load on startup
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR) 
load_all(patients_ll, patient_tree, appointments_q)


# Helper to refresh session undo state
def sync_undo_stack():
    session['undo_stack'] = list(undo_stack.stack)
  # simple list for session


@app.context_processor
def inject_now():
    return {'now': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}


@app.route('/')
def index():
    return render_template('index.html')




@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # Get and validate fields
            # Get and validate fields
            name = request.form.get('name', '').strip()
            age_str = request.form.get('age', '').strip()
            disease = request.form.get('disease', '').strip()
            doctor = request.form.get('doctor', '').strip()


            # Check for empty fields
            if not name or not age_str or not disease or not doctor:
                flash("All fields are required.", "danger")
                return redirect(url_for('register'))

            # Validate age conversion
            try:
                age = int(age_str)
                if age <= 0:
                    raise ValueError
            except ValueError:
                flash("Age must be a positive number.", "danger")
                return redirect(url_for('register'))

            # Create new patient
            pid = patients_ll.get_max_id() + 1
            p = Patient(patient_id=pid, name=name, age=age, disease=disease, doctor=doctor)

            # Add to structures
            patients_ll.insert_end(p)
            patient_tree.insert(doctor, p.to_dict())
            undo_stack.push(("add", p.to_dict()))
            sync_undo_stack()

            flash(f"Patient registered with ID {pid}", "success")
            return redirect(url_for('view_patients_route'))

        except Exception as e:
            # Print real error for debugging
            print("Registration error:", e)
            flash("An unexpected error occurred while registering patient.", "danger")

    return render_template('register.html')



@app.route('/patients')
def view_patients_route():
    patient_list = patients_ll.to_list()
    return render_template('view.html', patients=patient_list)


@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    if request.method == 'POST':
        try:
            pid = int(request.form['patient_id'])
            patient = patients_ll.find_by_id(pid)
            if not patient:
                flash("Patient ID not found.", "danger")
            else:
                appointments_q.enqueue(pid)
                undo_stack.push(("appointment_add", pid))
                sync_undo_stack()
                flash(f"Appointment scheduled for {patient.name} (ID {pid})", "success")
                return redirect(url_for('view_patients_route'))
        except:
            flash("Invalid patient ID.", "danger")

    # Show only registered patients for dropdown
    patient_list = patients_ll.to_list()
    return render_template('schedule.html', patients=patient_list)


@app.route('/next', methods=['GET', 'POST'])
def next_appt():
    pid = appointments_q.peek()  # get first patient in queue (but don’t remove yet)
    patient = patients_ll.find_by_id(pid) if pid else None
    bill = None

    # --- Handle bill calculation ---
    if request.method == 'POST' and patient:
        try:
            base = float(request.form.get('base', 0))
            tests = float(request.form.get('tests', 0))
            meds = float(request.form.get('meds', 0))
            bill = calculate_bill(base, tests, meds)
        except Exception as e:
            flash("Error calculating bill. Please check inputs.", "danger")
            print("Billing error:", e)

    # --- Serve & dequeue patient ---
    if request.args.get('serve') == '1' and pid:
        served_pid = appointments_q.dequeue()
        served_patient = patients_ll.find_by_id(served_pid)
        flash(f"Served: {served_patient.name} (ID {served_pid})", "success")
        # reset bill after serving patient
        bill = None
        return redirect(url_for('next_appt'))

    # --- Handle case when queue is empty ---
    if not patient:
        flash("No pending appointments.", "info")

    return render_template('next.html', patient=patient, bill=bill)


@app.route('/search', methods=['GET', 'POST'])
def search():
    results = []
    if request.method == 'POST':
        doctor = request.form['doctor'].strip()
        results = patient_tree.search(doctor)
        if not results:
            flash("No patients found for this doctor.", "info")

    return render_template('search.html', results=results)


@app.route('/update/<int:pid>', methods=['GET', 'POST'])
def update(pid):
    patient = patients_ll.find_by_id(pid)
    if not patient:
        flash("Patient not found.", "danger")
        return redirect(url_for('view_patients_route'))

    if request.method == 'POST':
        old = patient.to_dict()
        name = request.form['name'].strip() or patient.name
        age = int(request.form['age']) if request.form['age'].strip() else patient.age
        disease = request.form['disease'].strip() or patient.disease
        doctor = request.form['doctor'].strip() or patient.doctor

        patients_ll.update_by_id(pid, name=name, age=age, disease=disease, doctor=doctor)
        patient_tree.rebuild_from_list(patients_ll.to_list())
        undo_stack.push(("update", old))
        sync_undo_stack()
        flash("Patient updated successfully.", "success")
        return redirect(url_for('view_patients_route'))

    return render_template('update.html', patient=patient.to_dict())


@app.route('/delete/<int:pid>', methods=['POST'])
def delete(pid):
    patient = patients_ll.find_by_id(pid)
    if not patient:
        flash("Patient not found.", "danger")
    else:
        undo_stack.push(("delete", patient.to_dict()))
        patients_ll.delete_by_id(pid)
        patient_tree.remove(patient.doctor, pid)
        sync_undo_stack()
        flash(f"Patient ID {pid} deleted.", "success")
    return redirect(url_for('view_patients_route'))


@app.route('/undo')
def undo():
    if undo_stack.is_empty():
        flash("Nothing to undo.", "info")
    else:
        undo_action(undo_stack, patients_ll, patient_tree, appointments_q)
        sync_undo_stack()
        flash("Last action undone.", "success")
    return redirect(request.referrer or url_for('index'))


@app.route('/save')
def save():
    save_all(patients_ll, appointments_q)
    flash("All data saved to disk.", "success")
    return redirect(url_for('index'))


if __name__ == '__main__':
    # Use 0.0.0.0 to allow external access (e.g., Docker, VM)
    app.run(host='0.0.0.0', port=5000, debug=True)