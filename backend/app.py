from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import firebase_admin
from flask_socketio import SocketIO, join_room, emit
from firebase_admin import credentials, firestore
from services.gemini_service import generate_from_prompt, generate_random_meteor as ai_generate_meteor
import bcrypt
import random
import string
import json
import uuid
import os

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)

cred = credentials.Certificate("firebase-adminsdk.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'meteors.json')

# auth endpoints

@app.route('/api/test/login', methods=['POST'])
def test_login():
    test_user_id = "test-user-123"
    resp = make_response(jsonify({"status": "success", "userId": test_user_id}))
    resp.set_cookie("userId", test_user_id, httponly=True)
    return resp

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

# game endpoints

@app.route('/api/coop/create', methods=['POST'])
def create_room():
    user_id = request.cookies.get('userId')
    
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    room_code = generate_room_code()
    room_id = str(uuid.uuid4())

    db.collection("rooms").document(room_id).set({
        "code": room_code,
        "users": [user_id],
        "status": "waiting",
        "createdAt": firestore.SERVER_TIMESTAMP
    })

    return jsonify({"roomId": room_id, "code": room_code})

@app.route('/api/coop/join', methods=['POST'])
def join_room_http():
    user_id = request.cookies.get("userId")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    code = data.get("code")
    if not code:
        return jsonify({"error": "Room code is required"}), 400

    rooms_ref = db.collection("rooms")
    query = rooms_ref \
        .where("code", "==", code) \
        .where("status", "==", "waiting") \
        .stream()

    room_doc = None
    for doc in query:
        room_data = doc.to_dict()
        if len(room_data["users"]) < 4:
            room_doc = doc
            break

    if not room_doc:
        return jsonify({"error": "Room not found"}), 404

    room_data = room_doc.to_dict()
    if user_id not in room_data["users"]:
        room_data["users"].append(user_id)
        rooms_ref.document(room_doc.id).update({"users": room_data["users"]})

    return jsonify({"roomId": room_doc.id, "users": room_data["users"]})


def generate_room_code(length=4):
    return ''.join(random.choices(string.digits, k=length))

def generate_random_meteor():
    return ai_generate_meteor()

def validate_card_choice(card, meteor):
    if not meteor:
        return card in ["BUNKER", "EVACUATION"]
    
    mass = meteor.get("mass", 0)
    speed = meteor.get("speed", 0)
    weather = meteor.get("weather", "CLEAR")
    meteor_type = meteor.get("type", "STONY")

    if mass > 100000:
        return card == "BUNKER"
    if weather == "STORM":
        return card == "BUNKER"
    if meteor_type == "IRON" and mass > 10000:
        return card == "BUNKER"
    if speed > 50000:
        return card == "EVACUATION"
    if weather in ["RAIN", "SNOW"]:
        return card == "BUNKER"
    if mass < 1000:
        return card in ["EVACUATION", "IGNORE"]
    return card in ["BUNKER", "EVACUATION"]

# socket handlers

@socketio.on('connect')
def handle_connect():
    emit("socket_connected", {"message": "Connected to socket"})

@socketio.on('disconnect')
def handle_disconnect():
    pass

@socketio.on('join_lobby')
def handle_join_lobby(data):
    user_id = request.cookies.get('userId')
    
    if not user_id:
        emit("error", {"message": "Not authenticated"}, to=request.sid)
        return

    room_code = generate_room_code()
    room_id = str(uuid.uuid4())
    
    try:
        db.collection("rooms").document(room_id).set({
            "code": room_code,
            "users": [user_id],
            "status": "waiting",
            "createdAt": firestore.SERVER_TIMESTAMP,
            "game_state": {
                "hp": 3,
                "current_meteor": None,
                "user_positions": {}
            }
        })
        
        join_room(room_id)
        username = user_id
        
        emit("room_created", {
            "roomId": room_id, 
            "code": room_code
        }, to=request.sid)
        
        emit("room_changed", {
            "userId": user_id,
            "username": username,
            "type": "USER_ADDED"
        }, room=room_id)
        
    except Exception as e:
        emit("error", {"message": f"Server error: {str(e)}"}, to=request.sid)

@socketio.on('join_existing_room')
def handle_join_existing_room(data):
    user_id = request.cookies.get('userId')
    room_code = data.get('code')
    
    if not user_id:
        emit("error", {"message": "Not authenticated"}, to=request.sid)
        return
    
    if not room_code:
        emit("error", {"message": "Room code required"}, to=request.sid)
        return

    try:
        rooms_ref = db.collection("rooms")
        query = rooms_ref.where("code", "==", room_code).where("status", "==", "waiting").stream()
        
        room_doc = None
        for doc in query:
            room_data = doc.to_dict()
            if len(room_data["users"]) < 4:
                room_doc = doc
                break
        
        if not room_doc:
            emit("error", {"message": "Room not found or full"}, to=request.sid)
            return
        
        room_data = room_doc.to_dict()
        room_id = room_doc.id
        
        if user_id not in room_data["users"]:
            room_data["users"].append(user_id)
            db.collection("rooms").document(room_id).update({"users": room_data["users"]})
        
        join_room(room_id)
        username = user_id
        
        emit("room_joined", {
            "roomId": room_id,
            "code": room_code,
            "users": room_data["users"]
        }, to=request.sid)
        
        emit("room_changed", {
            "userId": user_id,
            "username": username,
            "type": "USER_ADDED",
            "total_users": len(room_data["users"])
        }, room=room_id)
        
    except Exception as e:
        emit("error", {"message": f"Server error: {str(e)}"}, to=request.sid)

@socketio.on('start_game')
def handle_start_game(data):
    user_id = request.cookies.get('userId')
    room_id = data.get('roomId')
    
    if not user_id:
        emit("error", {"message": "Not authenticated"}, to=request.sid)
        return
    
    if not room_id:
        emit("error", {"message": "Room ID required"}, to=request.sid)
        return

    try:
        room_doc = db.collection("rooms").document(room_id).get()
        if not room_doc.exists:
            emit("error", {"message": "Room not found"}, to=request.sid)
            return

        room_data = room_doc.to_dict()
        
        if len(room_data["users"]) != 4:
            emit("error", {"message": f"Need 4 players to start game. Current: {len(room_data['users'])}"}, to=request.sid)
            return
        
        db.collection("rooms").document(room_id).update({"status": "playing"})
        emit("game_redirect", {"message": "Game starting!"}, room=room_id)
        
    except Exception as e:
        emit("error", {"message": f"Server error: {str(e)}"}, to=request.sid)

@socketio.on('join_game')
def handle_join_game(data):
    user_id = request.cookies.get('userId')
    room_id = data.get('roomId')
    user_list = data.get('userList', [])
    
    if not user_id:
        emit("error", {"message": "Not authenticated"}, to=request.sid)
        return
    
    if not room_id:
        emit("error", {"message": "Room ID required"}, to=request.sid)
        return

    try:
        room_doc = db.collection("rooms").document(room_id).get()
        if not room_doc.exists:
            emit("error", {"message": "Room not found"}, to=request.sid)
            return

        room_data = room_doc.to_dict()
        game_state = room_data.get("game_state", {})
        user_positions = game_state.get("user_positions", {})
        
        if user_id not in user_positions:
            user_positions[user_id] = len(user_positions) + 1
        
        user_number = user_positions[user_id]
        meteor = generate_random_meteor()
        
        game_state["user_positions"] = user_positions
        game_state["current_meteor"] = meteor
        
        db.collection("rooms").document(room_id).update({"game_state": game_state})
        
        if len(user_positions) == 4:
            emit("game_started", {
                "message": "All players joined!",
                "user_positions": user_positions
            }, room=room_id)
        
        emit("game_joined", {
            "userNumber": user_number,
            "meteor": meteor,
            "totalUsers": len(user_positions)
        }, to=request.sid)
        
    except Exception as e:
        emit("error", {"message": f"Server error: {str(e)}"}, to=request.sid)

@socketio.on('card_chosen')
def handle_card_chosen(data):
    user_id = request.cookies.get('userId')
    room_id = data.get('roomId')
    chosen_card = data.get('card')
    meteor_data = data.get('meteor')
    
    if not user_id:
        emit("error", {"message": "Not authenticated"}, to=request.sid)
        return
    
    if not room_id or not chosen_card:
        emit("error", {"message": "Room ID and card choice required"}, to=request.sid)
        return

    try:
        room_doc = db.collection("rooms").document(room_id).get()
        if not room_doc.exists:
            emit("error", {"message": "Room not found"}, to=request.sid)
            return

        room_data = room_doc.to_dict()
        game_state = room_data.get("game_state", {})
        current_hp = game_state.get("hp", 3)
        current_meteor = game_state.get("current_meteor", {})
        
        is_correct_choice = validate_card_choice(chosen_card, current_meteor)
        
        if not is_correct_choice:
            current_hp -= 1
        
        game_state["hp"] = current_hp
        
        if current_hp <= 0:
            game_state["status"] = "ended"
            db.collection("rooms").document(room_id).update({
                "status": "ended",
                "game_state": game_state
            })
            
            emit("GAME_ENDED", {
                "message": "Game Over! No lives remaining.",
                "final_hp": current_hp
            }, room=room_id)
        else:
            new_meteor = generate_random_meteor()
            game_state["current_meteor"] = new_meteor
            
            db.collection("rooms").document(room_id).update({"game_state": game_state})
            
            emit("round_result", {
                "chosen_card": chosen_card,
                "was_correct": is_correct_choice,
                "current_hp": current_hp,
                "new_meteor": new_meteor,
                "message": "Correct choice!" if is_correct_choice else "Wrong choice! -1 HP"
            }, room=room_id)
        
    except Exception as e:
        emit("error", {"message": f"Server error: {str(e)}"}, to=request.sid)


if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)