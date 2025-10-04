from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
from services.gemini_service import generate_from_prompt
import bcrypt
import json
import uuid
import os

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)

cred = credentials.Certificate("firebase-adminsdk.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Path to the meteors data file
data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'meteors.json')

@app.route('/api/meteors', methods=['GET'])
def get_meteors():
    try:
        with open(data_path, 'r') as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/prompt', methods=['GET'])
def prompt_handler():
    prompt = request.args.get('prompt')
    if not prompt:
        return jsonify({"error": "Prompt is missing"}), 400
    if len(prompt) > 100:
        return jsonify({"error": "Prompt cannot exceed 100 characters"}), 400

    try:
        result = generate_from_prompt(prompt)
        if result is None:
            return jsonify({"error": "Failed to generate data."}), 500
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/auth', methods=['GET'])
def is_user_logged_in():
    user_id = request.cookies.get("userId")
    if not user_id:
        return False

    user_ref = db.collection("users").document(user_id)
    if not user_ref.get().exists:
        return False

    return True

@app.route('/api/signup', methods=['POST'])
def register_user():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "bad request"}), 400

        users_ref = db.collection("users")
        query = users_ref.where("username", "==", username).stream()
        if any(query):
            return jsonify({"error": "Username already exists"}), 400

        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        user_id = str(uuid.uuid4())

        users_ref.document(user_id).set({
            "username": username,
            "password": hashed_pw.decode(),
            "createdAt": firestore.SERVER_TIMESTAMP
        })

        resp = make_response(jsonify({"status": "success", "userId": user_id}))
        resp.set_cookie("userId", user_id, httponly=True)
        return resp
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login_user():
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        users_ref = db.collection("users")
        query = users_ref.where("username", "==", username).stream()

        user_doc = None
        for doc in query:
            user_doc = doc
            break

        if not user_doc:
            return jsonify({"error": "User not found"}), 404

        user_data = user_doc.to_dict()
        hashed_pw = user_data.get("password").encode("utf-8")

        if bcrypt.checkpw(password.encode("utf-8"), hashed_pw):
            resp = make_response(jsonify({"status": "success", "userId": user_doc.id}))
            resp.set_cookie("userId", user_doc.id, httponly=True)
            return resp
        else:
            return jsonify({"error": "Invalid password"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
