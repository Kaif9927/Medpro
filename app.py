from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-super-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medpro.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    user_type = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(100), nullable=False)
    patient_email = db.Column(db.String(120), nullable=False)
    patient_phone = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    doctor_name = db.Column(db.String(100), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class UploadedFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# Symptom and disease lists
l1 = ['back_pain','constipation','abdominal_pain','diarrhoea','mild_fever','yellow_urine',
'yellowing_of_eyes','acute_liver_failure','fluid_overload','swelling_of_stomach',
'swelled_lymph_nodes','malaise','blurred_and_distorted_vision','phlegm','throat_irritation',
'redness_of_eyes','sinus_pressure','runny_nose','congestion','chest_pain','weakness_in_limbs',
'fast_heart_rate','pain_during_bowel_movements','pain_in_anal_region','bloody_stool',
'irritation_in_anus','neck_pain','dizziness','cramps','bruising','obesity','swollen_legs',
'swollen_blood_vessels','puffy_face_and_eyes','enlarged_thyroid','brittle_nails',
'swollen_extremeties','excessive_hunger','extra_marital_contacts','drying_and_tingling_lips',
'slurred_speech','knee_pain','hip_joint_pain','muscle_weakness','stiff_neck','swelling_joints',
'movement_stiffness','spinning_movements','loss_of_balance','unsteadiness',
'weakness_of_one_body_side','loss_of_smell','bladder_discomfort','foul_smell_of urine',
'continuous_feel_of_urine','passage_of_gases','internal_itching','toxic_look_(typhos)',
'depression','irritability','muscle_pain','altered_sensorium','red_spots_over_body','belly_pain',
'abnormal_menstruation','dischromic _patches','watering_from_eyes','increased_appetite','polyuria',
'family_history','mucoid_sputum','rusty_sputum','lack_of_concentration','visual_disturbances',
'receiving_blood_transfusion','receiving_unsterile_injections','coma','stomach_bleeding',
'distention_of_abdomen','history_of_alcohol_consumption','blood_in_sputum','prominent_veins_on_calf',
'palpitations','painful_walking','pus_filled_pimples','blackheads','scurring','skin_peeling',
'silver_like_dusting','small_dents_in_nails','inflammatory_nails','blister','red_sore_around_nose',
'yellow_crust_ooze']

disease = ['Fungal infection','Allergy','GERD','Chronic cholestasis','Drug Reaction',
'Peptic ulcer diseae','AIDS','Diabetes','Gastroenteritis','Bronchial Asthma','Hypertension',
'Migraine','Cervical spondylosis','Paralysis (brain hemorrhage)','Jaundice','Malaria',
'Chicken pox','Dengue','Typhoid','hepatitis A','Hepatitis B','Hepatitis C','Hepatitis D',
'Hepatitis E','Alcoholic hepatitis','Tuberculosis','Common Cold','Pneumonia',
'Dimorphic hemmorhoids(piles)','Heart attack','Varicose veins','Hypothyroidism',
'Hyperthyroidism','Hypoglycemia','Osteoarthristis','Arthritis',
'(vertigo) Paroymsal  Positional Vertigo','Acne','Urinary tract infection','Psoriasis',
'Impetigo']

# Load and train the ML model
def load_and_train_model():
    try:
        df = pd.read_csv("Training.csv")
        df['prognosis'] = df['prognosis'].str.strip()
        mapping = {disease_name: i for i, disease_name in enumerate(disease)}
        df['prognosis'] = df['prognosis'].map(mapping)
        X = df[l1]
        y = df['prognosis']
        clf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        clf_model.fit(X, y)
        return clf_model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

clf_model = load_and_train_model()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        print(f"Login attempt: username={username}")  # Debug line
        
        user = User.query.filter_by(username=username).first()
        
        if user:
            print(f"User found: {user.username}, is_active: {user.is_active}")  # Debug line
            if user.check_password(password) and user.is_active:
                login_user(user)
                flash('Login successful!', 'success')
                print("Login successful, redirecting to dashboard")  # Debug line
                return redirect(url_for('dashboard'))
            else:
                print("Password check failed or user inactive")  # Debug line
                flash('Invalid username or password', 'error')
        else:
            print("User not found")  # Debug line
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = 'B'  # Force regular user for public signup
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('signup.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('signup.html')
        
        user = User(username=username, email=email, user_type=user_type)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    files = UploadedFile.query.filter_by(user_id=current_user.id).order_by(UploadedFile.uploaded_at.desc()).all()
    appointments = Appointment.query.filter_by(user_id=current_user.id).order_by(Appointment.appointment_date.desc()).limit(5).all()
    return render_template('dashboard.html', files=files, appointments=appointments)

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        file_record = UploadedFile(
            filename=unique_filename,
            original_filename=filename,
            file_size=os.path.getsize(file_path),
            user_id=current_user.id
        )
        db.session.add(file_record)
        db.session.commit()
        
        flash('File uploaded successfully!', 'success')
        return jsonify({'message': 'File uploaded successfully', 'filename': unique_filename})
    
    return jsonify({'error': 'Upload failed'}), 400

@app.route('/files')
@login_required
def list_files():
    files = UploadedFile.query.filter_by(user_id=current_user.id).order_by(UploadedFile.uploaded_at.desc()).all()
    return jsonify([{
        'id': f.id,
        'filename': f.filename,
        'original_filename': f.original_filename,
        'file_size': f.file_size,
        'uploaded_at': f.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
    } for f in files])

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    file_record = UploadedFile.query.filter_by(filename=filename, user_id=current_user.id).first()
    if file_record:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    return 'File not found', 404

@app.route('/delete/<int:file_id>', methods=['POST'])
@login_required
def delete_file(file_id):
    file_record = UploadedFile.query.get_or_404(file_id)
    
    if file_record.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_record.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    db.session.delete(file_record)
    db.session.commit()
    
    flash('File deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/symptom-checker', methods=['GET', 'POST'])
def public_symptom_checker():
    """Public symptom checker - no login required"""
    if request.method == 'POST':
        symptoms = [request.form.get(f"symptom{i}") for i in range(1, 6)]
        symptoms = [s for s in symptoms if s and s != 'None']
        
        if not symptoms:
            flash('Please select at least one symptom', 'error')
            return render_template('public_symptom_checker.html', symptoms=l1)
        
        input_vector = [0] * len(l1)
        for symptom in symptoms:
            if symptom in l1:
                index = l1.index(symptom)
                input_vector[index] = 1
        
        if clf_model:
            prediction_proba = clf_model.predict_proba([input_vector])[0]
            prediction_index = clf_model.predict([input_vector])[0]
            prediction = disease[prediction_index]
            confidence = max(prediction_proba) * 100
            
            return render_template('public_symptom_checker.html', 
                                symptoms=l1, 
                                prediction=prediction, 
                                confidence=confidence,
                                selected_symptoms=symptoms)
        else:
            flash('Prediction model not available', 'error')
    
    return render_template('public_symptom_checker.html', symptoms=l1)

@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    if request.method == 'POST':
        symptoms = [request.form.get(f"symptom{i}") for i in range(1, 6)]
        symptoms = [s for s in symptoms if s and s != 'None']
        
        if not symptoms:
            flash('Please select at least one symptom', 'error')
            return render_template('predict.html', symptoms=l1)
        
        input_vector = [0] * len(l1)
        for symptom in symptoms:
            if symptom in l1:
                index = l1.index(symptom)
                input_vector[index] = 1
        
        if clf_model:
            prediction_proba = clf_model.predict_proba([input_vector])[0]
            prediction_index = clf_model.predict([input_vector])[0]
            prediction = disease[prediction_index]
            confidence = max(prediction_proba) * 100
            
            return render_template('predict.html', 
                                symptoms=l1, 
                                prediction=prediction, 
                                confidence=confidence,
                                selected_symptoms=symptoms)
        else:
            flash('Prediction model not available', 'error')
    
    return render_template('predict.html', symptoms=l1)

@app.route('/appointment', methods=['GET', 'POST'])
@login_required
def appointment():
    if request.method == 'POST':
        appointment_data = Appointment(
            patient_name=request.form.get('name'),
            patient_email=request.form.get('email'),
            patient_phone=request.form.get('phone'),
            department=request.form.get('department'),
            doctor_name=request.form.get('doctor'),
            appointment_date=datetime.strptime(request.form.get('date'), '%Y-%m-%d'),
            message=request.form.get('message'),
            user_id=current_user.id
        )
        
        db.session.add(appointment_data)
        db.session.commit()
        
        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('appointment.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/doctors')
def doctors():
    return render_template('doctors.html')

@app.route('/departments')
def departments():
    return render_template('departments.html')

# Admin routes
@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.user_type != 'A':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get statistics
    total_users = User.query.count()
    total_appointments = Appointment.query.count()
    total_files = UploadedFile.query.count()
    user_b_count = User.query.filter_by(user_type='B').count()
    
    # Get recent users
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    
    # Get pending User B accounts (if any approval system is needed)
    pending_users = User.query.filter_by(user_type='B').all()
    
    return render_template('admin.html', 
                         total_users=total_users,
                         total_appointments=total_appointments,
                         total_files=total_files,
                         user_b_count=user_b_count,
                         recent_users=recent_users,
                         pending_users=pending_users)

@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.user_type != 'A':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/add_user', methods=['GET', 'POST'])
@login_required
def admin_add_user():
    if current_user.user_type != 'A':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()
        
        if existing_user:
            flash('Username already exists!', 'error')
        elif existing_email:
            flash('Email already exists!', 'error')
        else:
            new_user = User(
                username=username,
                email=email,
                user_type=user_type
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash(f'User {username} created successfully!', 'success')
            return redirect(url_for('admin_users'))
    
    return render_template('admin_add_user.html')

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    if current_user.user_type != 'A':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        flash('Cannot delete your own account!', 'error')
        return redirect(url_for('admin_users'))
    
    # Delete user's files and appointments
    UploadedFile.query.filter_by(user_id=user_id).delete()
    Appointment.query.filter_by(user_id=user_id).delete()
    
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.username} deleted successfully!', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/symptom_checker')
@login_required
def admin_symptom_checker():
    if current_user.user_type != 'A':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('admin_symptom_checker.html')

@app.route('/debug/users')
def debug_users():
    """Debug route to check users in database"""
    users = User.query.all()
    result = []
    for user in users:
        result.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'user_type': user.user_type,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat() if user.created_at else None
        })
    return {'users': result, 'count': len(result)}

def create_tables():
    with app.app_context():
        db.create_all()
        
        # Check if admin user already exists by username or email
        admin_user = User.query.filter_by(username='admin').first()
        admin_email = User.query.filter_by(email='admin@medpro.com').first()
        
        print(f"Admin user check: username exists={admin_user is not None}, email exists={admin_email is not None}")
        
        if not admin_user and not admin_email:
            admin = User(username='admin', email='admin@medpro.com', user_type='A')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: username=admin, password=admin123")
        else:
            print("Admin user already exists, skipping creation")
            if admin_user:
                print(f"Existing admin user: username={admin_user.username}, email={admin_user.email}, is_active={admin_user.is_active}")

if __name__ == '__main__':
    create_tables()
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)
