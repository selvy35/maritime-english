import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Vocabulary, UserProgress, WarmUpHistory
from config import SECRET_KEY, DATABASE_NAME
import uuid
from gtts import gTTS
from utils import delete_file_later

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, 'database')
os.makedirs(DATABASE_DIR, exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(DATABASE_DIR, DATABASE_NAME)}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
@login_required
def home():
    units = [
        {"id": 1, "title": "Basic Maritime Vocabulary"},
        {"id": 2, "title": "Ship Anatomy and Equipment"},
        {"id": 3, "title": "Navigation Terms"},
        {"id": 4, "title": "Safety and Emergency Phrases"},
        {"id": 5, "title": "Radio Communication"},
        {"id": 6, "title": "Maritime Commands and Instructions"}
    ]
    return render_template('home.html', units=units)

@app.route('/unit')
def unit_list():
    units = [
        {"id": 1, "title": "Basic Maritime Vocabulary"},
        {"id": 2, "title": "Ship Anatomy and Equipment"},
        {"id": 3, "title": "Navigation Terms"},
        {"id": 4, "title": "Safety and Emergency Phrases"},
        {"id": 5, "title": "Radio Communication"},
        {"id": 6, "title": "Maritime Commands and Instructions"}
    ]
    return render_template('home.html', units=units)  # Gunakan template home.html untuk /unit

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Username or email already exists.')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!')
            return redirect(url_for('home'))  # Redirect ke /home setelah login
        else:
            flash('Invalid email or password.')
    return render_template('login.html')

@app.route('/unit/<int:unit_id>/<section>')
@login_required
def learning_unit(unit_id, section): 
    valid_sections = ['warm_up', 'input_material', 'noticing', 'control_practice', 'guided_practice', 'authentic_task', 'assesment']
    if section not in valid_sections:
        flash('Invalid section.')
        return redirect(url_for('index'))
    
    vocabularies = Vocabulary.query.filter_by(unit=unit_id).all()
    progress = None
    if current_user.is_authenticated:
        progress = UserProgress.query.filter_by(user_id=current_user.id, unit=unit_id, section=section).first()
    
    return render_template(f'unit_{unit_id}/{section}.html', unit_id=unit_id, vocabularies=vocabularies, progress=progress)

@app.route('/complete_section/<int:unit_id>/<section>', methods=['POST'])
@login_required
def complete_section(unit_id, section): 
    if current_user.is_authenticated:
        progress = UserProgress.query.filter_by(user_id=current_user.id, unit=unit_id, section=section).first()
        score = request.form.get('score', 0, type=int)
        if not progress:
            progress = UserProgress(user_id=current_user.id, unit=unit_id, section=section, completed=True, score=score)
            db.session.add(progress)
        else:
            progress.completed = True
            progress.score = score
        db.session.commit()
    
    flash(f'{section.replace("_", " ").title()} completed! Great job, {current_user.username}!')
    return redirect(url_for('learning_unit', unit_id=unit_id, section=section))

@app.route('/unit/<int:unit_id>/warm_up', methods=['GET'])
@login_required
def warm_up(unit_id):
    progress = UserProgress.query.filter_by(user_id=current_user.id, unit=unit_id, section='warm_up').first()
    return render_template(f'unit_{unit_id}/warm_up.html', unit_id=unit_id, progress=progress)

@app.route("/warmup_history_batch", methods=["POST"])
@login_required
def warmup_history_batch():
    data = request.json
    unit = data.get("unit", 1)
    history_list = data.get("history", [])

    for h in history_list:
        history = WarmUpHistory(
            user_id=current_user.id,
            unit=unit,
            question=h.get("question"),
            correct_answer=h.get("correct_answer"),
            user_answer=h.get("user_answer"),
            is_correct=h.get("is_correct", False)
        )
        db.session.add(history)

    db.session.commit()
    return {"status": "saved", "count": len(history_list)}

@app.route("/speak", methods=["POST"])
def tts():
    text = request.json.get("text")
    if not text:
        return "No text provided", 400

    audio_dir = os.path.join(app.root_path, "static", "audio")
    os.makedirs(audio_dir, exist_ok=True)

    filename = f"{uuid.uuid4()}.mp3"
    filepath = os.path.join(audio_dir, filename)

    tts = gTTS(text)
    tts.save(filepath)

    delete_file_later(filepath, delay=10)

    return {"url": url_for("static", filename=f"audio/{filename}")}

def init_db():
    # bisa menggunakan json untuk init databasenya
    with app.app_context():
        db.create_all()
        if not Vocabulary.query.filter_by(unit=1).first():
            vocabularies = [
                Vocabulary(unit=1, word="Port", meaning="Pelabuhan (sisi kiri kapal)", example="The ship is docked on the port side.", ipa="/pɔːrt/", image="img/port.jpg"),
                Vocabulary(unit=1, word="Starboard", meaning="Sisi kanan kapal", example="Turn the ship to starboard.", ipa="/ˈstɑːrbərd/", image="img/starboard.jpg"),
                Vocabulary(unit=1, word="Bow", meaning="Haluan (depan kapal)", example="The bow of the ship faces the horizon.", ipa="/baʊ/", image="img/bow.jpg"),
                Vocabulary(unit=1, word="Stern", meaning="Buritan (belakang kapal)", example="The lifeboat is stored at the stern.", ipa="/stɜːrn/", image="img/stern.jpg")
            ]
            db.session.bulk_save_objects(vocabularies)
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)