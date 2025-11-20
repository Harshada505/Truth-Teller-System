from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import uuid
from extractAudio import extractAudio
from extractText import get_large_audio_transcription
from predict import predict_sentences
from extractYT import download_youtube_video_480p
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/truthteller'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

jwt = JWTManager(app)
db = SQLAlchemy(app)

# User model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

# Register route
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify(error="User already exists"), 409

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, email=email, password=hashed_password)

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify(message="User registered successfully"), 201
    except Exception as e:
        db.session.rollback()
        return jsonify(error=str(e)), 500

# Login route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify(error="Invalid credentials"), 401

# Profile route
@app.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user:
        return jsonify(id=user.id, username=user.username, email=user.email), 200
    else:
        return jsonify(error="User not found"), 404

# Upload configuration
app.config['UPLOAD_FOLDER'] = 'uploads/video/'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}

def is_allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Upload and predict route (local file)
@app.route('/predict', methods=['POST'])
def upload_video():
    try:
        if 'file' not in request.files:
            return jsonify(error="No file part in the request"), 400

        file = request.files['file']
        language = request.form.get("language", "en")

        if file.filename == '':
            return jsonify(error="No file selected"), 400

        if not is_allowed_file(file.filename):
            return jsonify(error="Invalid file type. Only video files are allowed"), 400

        base_name = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{base_name}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)

        try:
            file.save(file_path)
        except PermissionError:
            return jsonify(error="Permission denied while saving the video file."), 500

        eapath = extractAudio(unique_name, file_path)
        if not eapath:
            return jsonify(error="Audio extraction failed"), 500

        transArray = get_large_audio_transcription(eapath, language=language)

        test_records = [
            {
                "sentence_id": str(idx),
                "speaker_name": "",
                "speaker_role": "",
                "speech_title": "",
                "text": text,
                "url": ""
            }
            for idx, text in enumerate(transArray)
        ]

        predicted_results = predict_sentences(test_records)
        finalStatements = calculate_label_percentages(predicted_results)

        print("Done")
        return jsonify(
            message="Truth Classification successfully",
            filename=unique_name,
            finalStatements=finalStatements,
            predicted_results=predicted_results
        ), 200

    except Exception as e:
        print("Error occurred in /predict:", str(e))
        return jsonify(error="Server error: " + str(e)), 500

# YouTube prediction
@app.route('/predict/link', methods=['POST'])
def yt_video():
    try:
        data = request.get_json()
        video_url = data.get('url')
        language = data.get('language', "en")

        if not video_url:
            return jsonify({"error": "No URL provided"}), 400

        video_path, video_title = download_youtube_video_480p(video_url, "./uploads/YT")

        if not video_path or not video_title:
            return jsonify({"error": "Failed to download the video. Please check the URL and try again."}), 400

        eapath = extractAudio(video_title, video_path)
        transArray = get_large_audio_transcription(eapath, language=language)

        test_records = [
            {
                "sentence_id": str(idx),
                "speaker_name": "",
                "speaker_role": "",
                "speech_title": "",
                "text": text,
                "url": ""
            }
            for idx, text in enumerate(transArray)
        ]

        predicted_results = predict_sentences(test_records)
        finalStatements = calculate_label_percentages(predicted_results)

        print("Done")
        return jsonify(
            message="Truth Classification successfully",
            filename=video_title,
            finalStatements=finalStatements,
            predicted_results=predicted_results
        ), 200

    except Exception as e:
        print("Error occurred in /predict/link:", str(e))
        return jsonify(error="Server error: " + str(e)), 500

@app.errorhandler(413)
def file_too_large(e):
    return jsonify(error="File is too large. Maximum allowed size is 10 MB"), 413

def calculate_label_percentages(statements):
    counts = {"TRUE": 0, "FALSE": 0, "Neutral": 0}
    total = len(statements)

    for stmt in statements:
        label = stmt.get("predicted_label")
        if label in counts:
            counts[label] += 1

    return [{"label": k, "percentage": round((v / total) * 100, 2)} for k, v in counts.items()]

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
