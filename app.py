from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Database setup
DATABASE = 'hospital.db'

def init_db():
    """Initialize the database with patients table."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            patient_id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            date_of_birth DATE NOT NULL,
            gender TEXT NOT NULL,
            blood_type TEXT,
            marital_status TEXT,
            phone TEXT NOT NULL,
            email TEXT,
            address TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            zip_code TEXT NOT NULL,
            emergency_name TEXT NOT NULL,
            emergency_relation TEXT NOT NULL,
            emergency_phone TEXT NOT NULL,
            primary_doctor TEXT,
            insurance_provider TEXT,
            policy_number TEXT,
            allergies TEXT,
            medications TEXT,
            medical_history TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    """Home page with dashboard."""
    conn = get_db_connection()
    
    # Get statistics
    total_patients = conn.execute('SELECT COUNT(*) FROM patients').fetchone()[0]
    
    # Get recent patients (last 5)
    recent_patients = conn.execute(
        'SELECT first_name, last_name, created_at FROM patients ORDER BY created_at DESC LIMIT 5'
    ).fetchall()
    
    conn.close()
    
    return render_template('home.html', 
                         total_patients=total_patients,
                         recent_patients=recent_patients)

@app.route('/patient_form', methods=['GET', 'POST'])
def patient_form():
    """Patient registration form."""
    if request.method == 'POST':
        try:
            # Get form data
            patient_data = {
                'patient_id': request.form['patient_id'],
                'first_name': request.form['firstName'],
                'last_name': request.form['lastName'],
                'date_of_birth': request.form['dateOfBirth'],
                'gender': request.form['gender'],
                'blood_type': request.form.get('bloodType', ''),
                'marital_status': request.form.get('maritalStatus', ''),
                'phone': request.form['phone'],
                'email': request.form.get('email', ''),
                'address': request.form['address'],
                'city': request.form['city'],
                'state': request.form['state'],
                'zip_code': request.form['zipCode'],
                'emergency_name': request.form['emergencyName'],
                'emergency_relation': request.form['emergencyRelation'],
                'emergency_phone': request.form['emergencyPhone'],
                'primary_doctor': request.form.get('primaryDoctor', ''),
                'insurance_provider': request.form.get('insuranceProvider', ''),
                'policy_number': request.form.get('policyNumber', ''),
                'allergies': request.form.get('allergies', ''),
                'medications': request.form.get('medications', ''),
                'medical_history': request.form.get('medicalHistory', '')
            }
            
            # Validate required fields
            required_fields = ['patient_id','first_name', 'last_name', 'date_of_birth', 'gender', 
                             'phone', 'address', 'city', 'state', 'zip_code',
                             'emergency_name', 'emergency_relation', 'emergency_phone']
            
            for field in required_fields:
                if not patient_data[field]:
                    error_msg = f'Please fill in the {field.replace("_", " ").title()} field.'
                    return render_template('patient_form.html', error=error_msg)
            
            # Check if patient ID already exists
            conn = get_db_connection()
            existing_patient = conn.execute('SELECT patient_id FROM patients WHERE patient_id = ?', 
                                          (patient_data['patient_id'],)).fetchone()
            
            if existing_patient:
                conn.close()
                error_msg = f'Patient ID {patient_data["patient_id"]} already exists. Please use a different ID.'
                return render_template('patient_form.html', error=error_msg)
            
            # Insert into database
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO patients (
                    patient_id, first_name, last_name, date_of_birth, gender, blood_type, 
                    marital_status, phone, email, address, city, state, zip_code,
                    emergency_name, emergency_relation, emergency_phone,
                    primary_doctor, insurance_provider, policy_number,
                    allergies, medications, medical_history
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                patient_data['patient_id'], patient_data['first_name'], patient_data['last_name'], 
                patient_data['date_of_birth'], patient_data['gender'],
                patient_data['blood_type'], patient_data['marital_status'],
                patient_data['phone'], patient_data['email'],
                patient_data['address'], patient_data['city'],
                patient_data['state'], patient_data['zip_code'],
                patient_data['emergency_name'], patient_data['emergency_relation'],
                patient_data['emergency_phone'], patient_data['primary_doctor'],
                patient_data['insurance_provider'], patient_data['policy_number'],
                patient_data['allergies'], patient_data['medications'],
                patient_data['medical_history']
            ))
            
            conn.commit()
            conn.close()
            
            success_msg = f'Patient {patient_data["first_name"]} {patient_data["last_name"]} has been successfully added!'
            return render_template('patient_form.html', success=success_msg)
            
        except sqlite3.IntegrityError as e:
            error_msg = f'Database error: Patient ID might already exist or data format is invalid.'
            return render_template('patient_form.html', error=error_msg)
        except Exception as e:
            error_msg = f'Error adding patient: {str(e)}'
            return render_template('patient_form.html', error=error_msg)
    
    return render_template('patient_form.html')

@app.route('/patients')
def view_patients():
    """View all patients."""
    conn = get_db_connection()
    patients = conn.execute(
        'SELECT * FROM patients ORDER BY created_at DESC'
    ).fetchall()
    conn.close()
    
    return render_template('patients.html', patients=patients)
    
application = app

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)
