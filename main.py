from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, url_for, session
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import os
from flask import Flask, render_template, request
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier


# utils.py or at top of app.py
def load_or_create_aes_key(filename="aes.key"):
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            return f.read()
    key = get_random_bytes(16)
    with open(filename, "wb") as f:
        f.write(key)
    return key

AES_KEY = load_or_create_aes_key()

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "secret_key"  # Replace with a secure key

# --- AES Encryption Utilities ---
AES_KEY = load_or_create_aes_key()  # Use this line instead of generating new key

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

# Load data
df = pd.read_csv("Training.csv")
tr = pd.read_csv("Testing.csv")

# Clean & map diseases to numbers
df['prognosis'] = df['prognosis'].str.strip()
tr['prognosis'] = tr['prognosis'].str.strip()

mapping = {disease_name: i for i, disease_name in enumerate(disease)}

df['prognosis'] = df['prognosis'].map(mapping)
tr['prognosis'] = tr['prognosis'].map(mapping)

print("Training missing labels:", df['prognosis'].isnull().sum())
print("Testing missing labels:", tr['prognosis'].isnull().sum())

# Ensure no NaNs remain or your model will error
assert df['prognosis'].isnull().sum() == 0, "Training data has unmapped labels."
assert tr['prognosis'].isnull().sum() == 0, "Testing data has unmapped labels."

X = df[l1]
y = df['prognosis']

clf_model = RandomForestClassifier()
clf_model.fit(X, y)
def encrypt_password(plaintext):
    cipher = AES.new(AES_KEY, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode())
    return base64.b64encode(cipher.nonce + tag + ciphertext).decode()

def decrypt_password(encoded_data):
    decoded = base64.b64decode(encoded_data)
    nonce = decoded[:16]
    tag = decoded[16:32]
    ciphertext = decoded[32:]
    cipher = AES.new(AES_KEY, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag).decode()

# --- User Management ---
def load_users(file):
    users = {}
    if not os.path.exists(file):
        return users
    with open(file, "r") as f:
        for line in f:
            parts = line.strip().split(",", 1)  # split only on the first comma
            if len(parts) == 2:
                username, encrypted_password = parts
                users[username] = encrypted_password
            else:
                # Optional: log or skip the malformed line
                print(f"Skipping malformed line in {file}: {line.strip()}")
    return users


def save_user(file, username, password):
    encrypted = encrypt_password(password)
    with open(file, "a") as f:
        f.write(f"{username},{encrypted}\n")

# --- Routes ---
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users_A = load_users("users_A.txt")
        users_B = load_users("users_B.txt")

        if username in users_A:
            try:
                if decrypt_password(users_A[username]) == password:
                    session["user"] = username
                    return redirect(url_for("index"))
            except:
                return "Decryption failed. Possibly corrupt data."

        if username in users_B:
            try:
                if decrypt_password(users_B[username]) == password:
                    session["pending_user"] = username
                    return redirect(url_for("second_login"))
            except:
                return "Decryption failed. Possibly corrupt data."

        return "Invalid username or password. Please try again."

    return render_template("login.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Save as User A
        save_user("users_A.txt", username, password)
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/second-login', methods=['GET', 'POST'])
def second_login():
    if "pending_user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users_B = load_users("users_B.txt")
        if username in users_B:
            if username != session["pending_user"]:
                if decrypt_password(users_B[username]) == password:
                    session["user_B"] = session["pending_user"]
                    session.pop("pending_user")
                    return redirect(url_for("hidden_data"))
                else:
                    return "Incorrect password for User B."
            else:
                return "User B cannot be the same as the first user."
        else:
            return "User B not found. Use sign-up to create."
    return render_template("second_login.html")

@app.route("/index")
def index():
    if "user" in session:
        files = os.listdir(app.config['UPLOAD_FOLDER'])
        return render_template("index.html", files=files)
    return redirect(url_for("login"))

@app.route("/hidden-data")
def hidden_data():
    if "user_B" in session:
        return render_template("hidden_data.html")
    return redirect(url_for("login"))


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    return "File uploaded successfully!", 200

@app.route('/files', methods=['GET'])
def list_files():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return jsonify(files)

@app.route('/uploads/<filename>', methods=['GET'])
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return redirect(url_for('index'))
    return "File not found", 404

@app.route('/signup-user-b', methods=['GET', 'POST'])
def signup_user_b():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        save_user("users_B.txt", username, password)
        return redirect(url_for('login'))
    return render_template('signup_user_b.html')

if __name__ == '__main__':
    app.run(debug=True)
