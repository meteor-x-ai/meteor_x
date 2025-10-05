import os
import uuid
import json
import bcrypt
import random
import string
import firebase_admin

from flask import Flask, request, jsonify, make_response
from dotenv import load_dotenv
from flask_cors import CORS
from flask_socketio import SocketIO, join_room, emit
from firebase_admin import credentials, firestore
from services.gemini_service import generate_from_prompt, calculate_casualties

load_dotenv()

app = Flask(__name__)
CORS(
    app,
    origins=["https://profound-faloodeh-f91fc7.netlify.app"],
    supports_credentials=True,
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"]
)

cred = credentials.Certificate("firebase-adminsdk.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'meteors.json')

# auth endpoints

@app.before_request
def handle_options():
    if request.method == "OPTIONS":
        resp = make_response()
        resp.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin")
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = request.headers.get(
            "Access-Control-Request-Headers", "Authorization, Content-Type"
        )
        resp.headers["Access-Control-Allow-Credentials"] = "true"
        return resp

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

@app.route('/api/prompt', methods=['GET'])
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

@app.route('/api/calculate-impact', methods=['POST'])
def calculate_meteor_impact():
    try:
        meteor_data = request.json

        if not meteor_data:
            return jsonify({"error": "Meteor data is required"}), 400

        #Validate
        required_fields = ['latitude', 'longitude', 'mass', 'speed', 'angle']
        missing_fields = [field for field in required_fields if field not in meteor_data]

        if missing_fields:
            return jsonify({
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        casualties = calculate_casualties(meteor_data)

        return jsonify({
            "success": True,
            "casualties": casualties,
            "meteor": meteor_data,
            "impact_location": {
                "latitude": meteor_data['latitude'],
                "longitude": meteor_data['longitude']
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"AI calculation failed: {str(e)}"
        }), 500

@app.route('/api/generate-meteor', methods=['GET'])
def generate_meteor():
    return jsonify(get_scenario_params())


@app.route('/api/validate-card', methods=['POST'])
def validate_card():
    try:
        data = request.json

        if not data:
            return jsonify({"error": "Request data is required"}), 400

        generated_scenario = data.get('generated_scenario')
        chosen_card = data.get('chosen_card')

        if generated_scenario is None or chosen_card is None:
            return jsonify({
                "error": "Both 'generated_scenario' and 'chosen_card' are required"
            }), 400

        if not isinstance(generated_scenario, int) or generated_scenario < 1 or generated_scenario > 360:
            return jsonify({
                "error": "generated_scenario must be an integer between 1 and 360"
            }), 400

        valid_cards = ["IGNORE", "EVACUATION", "BUNKER", "ROCKET"]
        if chosen_card not in valid_cards:
            return jsonify({
                "error": f"chosen_card must be one of: {', '.join(valid_cards)}"
            }), 400

        is_correct = validate_card_choice(generated_scenario, chosen_card)

        return jsonify({
            "success": True,
            "is_correct": is_correct,
            "generated_scenario": generated_scenario,
            "chosen_card": chosen_card
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Validation failed: {str(e)}"
        }), 500

@app.route('/api/room-admin/<room_code>', methods=['GET'])
def check_room_admin(room_code):
    try:
        user_id = request.cookies.get("userId")
        if not user_id:
            return jsonify({"error": "Not authenticated"}), 401

        if not room_code:
            return jsonify({"error": "room_code is required"}), 400

        #sistema poiska komnaty po kodu
        rooms_ref = db.collection("rooms")
        query = rooms_ref.where("code", "==", room_code).stream()

        room_doc = None
        for doc in query:
            room_doc = doc
            break

        if not room_doc:
            return jsonify({"error": "Room not found"}), 404

        room_data = room_doc.to_dict()
        creator_id = room_data.get("creator")
        users = room_data.get("users", [])
        game_state = room_data.get("game_state", {})
        user_cards = game_state.get("user_cards", {})

        is_admin = user_id == creator_id
        is_member = user_id in users
        can_start_game = (is_admin and
                          len(user_cards) == 4 and
                          not game_state.get("game_started", False) and
                          room_data.get("status") == "game_waiting")

        # sobiraem info o userah
        users_info = []
        for uid, card in user_cards.items():
            username = get_user_name(uid)
            users_info.append({
                "username": username or "Unknown",
                "id": uid,
                "card": card,
                "is_current_user": uid == user_id
            })

        return jsonify({
            "success": True,
            "admin": is_admin,
            "is_admin": is_admin,
            "is_member": is_member,
            "can_start_game": can_start_game,
            "room_code": room_code,
            "total_users": len(users),
            "total_game_users": len(user_cards),
            "status": room_data.get("status", "unknown"),
            "game_started": game_state.get("game_started", False),
            "users_info": users_info,
            "current_meteor": game_state.get("current_meteor") if game_state.get("game_started") else None
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to check room admin: {str(e)}"
        }), 500

@app.route('/api/auth', methods=['GET'])
def is_user_logged_in():
    user_id = request.cookies.get("userId")
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    user_ref = db.collection("users").document(user_id)
    doc = user_ref.get()
    if not doc.exists:
        return jsonify({"error": "User not found"}), 401

    user_data = doc.to_dict()
    username = user_data.get("username")

    return jsonify({"id": user_id, "username": username}), 200

@app.route('/api/signup', methods=['POST'])
def register_user():
    print(request.json)
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

def generate_room_code(length=4):
    return ''.join(random.choices(string.digits, k=length))

def generate_random_meteor():
    return get_scenario_params()

def get_scenario_params():
    speed_1 = 10
    speed_2 = 30
    speed_3 = 50
    speed_4 = 70
    
    distance_1 = 20
    distance_2 = 1000
    distance_3 = 4000
    distance_4 = 100000000
    distance_5 = 300000000
    
    weight_1 = 1
    weight_2 = 20000
    weight_3 = 40000
    weight_4 = 60000
    
    angle_1 = 1
    angle_2 = 30
    angle_3 = 60
    angle_4 = 90
    
    generated_scenario = random.randint(1, 360)
    
    block = ((generated_scenario - 1) // 120) + 1
    if block == 1:
        speed = random.randint(speed_1, speed_2)
    elif block == 2:
        speed = random.randint(speed_2 + 1, speed_3)
    else:
        speed = random.randint(speed_3 + 1, speed_4)
    
    local120 = ((generated_scenario - 1) % 120) + 1
    if 1 <= local120 <= 24:
        composition = "ICE"
    elif 25 <= local120 <= 48:
        composition = "ICE_STONE"
    elif 49 <= local120 <= 72:
        composition = "STONE"
    elif 73 <= local120 <= 96:
        composition = "STONE_IRON"
    else:
        composition = "IRON"
    
    local24 = ((generated_scenario - 1) % 24) + 1
    if 1 <= local24 <= 9:
        distance = random.randint(distance_1, distance_2)
    elif 10 <= local24 <= 18:
        distance = random.randint(distance_2 + 1, distance_3)
    else:
        distance = random.randint(distance_4, distance_5)
    
    group1_ranges = [
        (1,3), (10,12), (25,27), (34,36), (49,51), (58,60),
        (73,75), (82,84), (97,99), (106,108), (121,123), (130,132),
        (145,147), (154,156), (169,171), (178,180), (193,195), (202,204),
        (217,219), (226,228), (241,243), (250,252), (265,267), (274,276),
        (289,291), (298,300), (313,315), (322,324), (337,339), (346,348)
    ]
    group2_ranges = [
        (4,6), (13,15), (19,21), (28,30), (37,39), (43,45),
        (52,54), (61,63), (67,69), (76,78), (85,87), (91,93),
        (100,102), (109,111), (115,117), (124,126), (133,135), (139,141),
        (148,150), (157,159), (163,165), (172,174), (181,183), (187,189),
        (196,198), (205,207), (211,213), (220,222), (229,231), (235,237),
        (244,246), (253,255), (259,261), (268,270), (277,279), (283,285),
        (292,294), (301,303), (307,309), (316,318), (325,327), (331,333),
        (340,342), (349,351), (355,357)
    ]
    group3_ranges = [
        (7,9), (16,18), (22,24), (31,33), (40,42), (46,48),
        (55,57), (64,66), (70,72), (79,81), (88,90), (94,96),
        (103,105), (112,114), (118,120), (127,129), (136,138), (142,144),
        (151,153), (160,162), (166,168), (175,177), (184,186), (190,192),
        (199,201), (208,210), (214,216), (223,225), (232,234), (238,240),
        (247,249), (256,258), (262,264), (271,273), (280,282), (286,288),
        (295,297), (304,306), (310,312), (319,321), (328,330), (334,336),
        (343,345), (352,354), (358,360)
    ]
    
    def in_ranges(val, ranges_list):
        for start, end in ranges_list:
            if start <= val <= end:
                return True
        return False
    
    if in_ranges(generated_scenario, group1_ranges):
        weight = random.randint(weight_1, weight_2)
    elif in_ranges(generated_scenario, group2_ranges):
        weight = random.randint(weight_2 + 1, weight_3)
    else:
        weight = random.randint(weight_3 + 1, weight_4)
    
    local3 = generated_scenario % 3
    if local3 == 1:
        angle = random.randint(angle_1, angle_2)
    elif local3 == 2:
        angle = random.randint(angle_2 + 1, angle_3)
    else:
        angle = random.randint(angle_3 + 1, angle_4)
    
    return {
        "speed": speed,
        "composition": composition,
        "distance": distance,
        "weight": weight,
        "angle": angle,
        "generated_scenario": generated_scenario
    }

def validate_card_choice(generated_scenario, chosen_card):
    ignore_scenarios = {
        1, 2, 3, 4, 5, 6, 10, 11, 12, 13, 14, 15, 19, 20, 21, 25, 26, 27, 28, 29, 30, 34, 35, 36, 37, 38, 39, 43, 44, 45, 49, 50, 51, 52, 58, 59, 60, 61, 73, 74, 75, 76, 82, 83, 84, 85, 97, 98, 99, 100, 106, 107, 108, 109, 121, 122, 123, 124, 130, 131, 132, 133, 145, 146, 147, 148, 154, 155, 156, 157, 169, 170, 171, 172, 178, 179, 180, 181, 193, 194, 195, 196, 202, 203, 204, 205
    }
    evacuation_scenarios = {
        22, 23, 24, 46, 47, 48, 67, 68, 69, 70, 71, 72, 91, 92, 93, 94, 95, 96, 115, 116, 117, 118, 119, 120, 139, 140, 141, 142, 143, 144, 163, 164, 165, 166, 167, 168, 187, 188, 189, 190, 191, 192, 211, 212, 213, 214, 215, 216, 235, 236, 237, 238, 239, 240, 259, 260, 261, 262, 263, 264, 283, 284, 285, 286, 287, 288, 307, 308, 309, 310, 311, 312, 331, 332, 333, 334, 335, 336, 355, 356, 357, 358, 359, 360
    }
    bunker_scenarios = {
        7, 8, 9, 16, 17, 18, 31, 32, 33, 40, 41, 42, 53, 54, 55, 56, 57, 62, 63, 64, 65, 66, 77, 78, 86, 87, 88, 89, 90, 101, 102, 110, 111, 112, 113, 114, 136, 137, 138, 160, 161, 162, 184, 185, 186, 208, 209, 210, 220, 221, 229, 230, 232, 233, 234, 244, 245, 253, 254, 256, 257, 258, 268, 269, 277, 278, 280, 281, 282, 292, 293, 301, 302, 304, 305, 306, 316, 317, 325, 326, 328, 329, 330, 340, 341, 349, 350, 352, 353, 354
    }
    rocket_scenarios = {
        79, 80, 81, 103, 104, 105, 125, 126, 127, 128, 129, 134, 135, 149, 150, 151, 152, 153, 158, 159, 173, 174, 175, 176, 177, 182, 183, 197, 198, 199, 200, 201, 206, 207, 217, 218, 219, 222, 223, 224, 225, 226, 227, 228, 231, 241, 242, 243, 246, 247, 248, 249, 250, 251, 252, 255, 265, 266, 267, 270, 271, 272, 273, 274, 275, 276, 279, 289, 290, 291, 294, 295, 296, 297, 298, 299, 300, 303, 313, 314, 315, 318, 319, 320, 321, 322, 323, 324, 327, 337, 338, 339, 342, 343, 344, 345, 346, 347, 348, 351
    }
    
    if chosen_card == "IGNORE":
        return generated_scenario in ignore_scenarios
    elif chosen_card == "EVACUATION":
        return generated_scenario in evacuation_scenarios
    elif chosen_card == "BUNKER":
        return generated_scenario in bunker_scenarios
    elif chosen_card == "ROCKET":
        return generated_scenario in rocket_scenarios
    else:
        return False

def get_user_name(user_id):
    doc = db.collection("users").document(user_id).get()
    if doc.exists:
        username = doc.to_dict().get("username")
        return username
    else:
        return None

# socket handlers

@socketio.on('connect')
def handle_connect():
    emit("socket_connected", {"message": "Connected to socket"})

@socketio.on('disconnect')
def handle_disconnect():
    user_id = request.cookies.get('userId')
    if not user_id:
        return

    try:
        rooms_ref = db.collection("rooms")
        query = rooms_ref.where("users", "array_contains", user_id).where("status", "==", "waiting").stream()

        for room_doc in query:
            room_data = room_doc.to_dict()
            room_id = room_doc.id
            current_users = room_data.get("users", [])

            if user_id in current_users:
                current_users.remove(user_id)
                username = get_user_name(user_id)
                if current_users:
                    db.collection("rooms").document(room_id).update({"users": current_users})
                    socketio.emit("room_changed", {
                        "userId": user_id,
                        "username": username or "Unknown",
                        "type": "USER_REMOVED",
                        "total_users": len(current_users)
                    }, room=room_id)
                else:
                    db.collection("rooms").document(room_id).delete()
    except Exception as e:
        print(f"Error handling disconnect for user {user_id}: {str(e)}")

@socketio.on('join_room')
def handle_join_lobby(data=None):
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
            "creator": user_id, #dobavil admina
            "status": "waiting",
            "createdAt": firestore.SERVER_TIMESTAMP,
            "game_state": {
                "hp": 3,
                "current_meteor": None,
                "user_cards": {},
                "game_started": False
            }
        })

        join_room(room_id)
        username = get_user_name(user_id)

        if not username:
            emit("error", {"message": "Not user name"}, to=request.sid)
            return

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
        username = get_user_name(user_id)

        if not username:
            emit("error", {"message": "Not user name"}, to=request.sid)
            return

        users = []
        for user_id in room_data["users"]:
            db.collection("users").document(user_id)
            users.append({
                "id": user_id,
                "username": get_user_name(user_id) or "Unknown"
            })

        emit("room_joined", {
            "roomId": room_id,
            "code": room_code,
            "users": users
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

        db.collection("rooms").document(room_id).update({"status": "game_waiting"})
        emit("game_redirect", True, room=room_id)

    except Exception as e:
        emit("error", {"message": f"Server error: {str(e)}"}, to=request.sid)

@socketio.on('admin_start_game')
def handle_admin_start_game(data):
    user_id = request.cookies.get('userId')
    room_code = data.get('room_code')

    if not user_id:
        emit("error", {"message": "Not authenticated"}, to=request.sid)
        return

    if not room_code:
        emit("error", {"message": "Room code required"}, to=request.sid)
        return

    try:
        #sistema poiska komnaty po kodu
        rooms_ref = db.collection("rooms")
        query = rooms_ref.where("code", "==", room_code).stream()

        room_doc = None
        for doc in query:
            room_doc = doc
            break

        if not room_doc:
            emit("error", {"message": "Room not found"}, to=request.sid)
            return

        room_data = room_doc.to_dict()
        room_id = room_doc.id

        #user admin?????
        if user_id != room_data.get("creator"):
            emit("error", {"message": "Only room creator can start the game"}, to=request.sid)
            return

        game_state = room_data.get("game_state", {})
        user_cards = game_state.get("user_cards", {})

        #userov 4 ?????
        if len(user_cards) != 4:
            emit("error", {"message": f"Need 4 players to start game. Current: {len(user_cards)}"}, to=request.sid)
            return

        #game uzhe zapushena?????
        if game_state.get("game_started", False):
            emit("error", {"message": "Game already started"}, to=request.sid)
            return

        # generiruem meteor i nachinaem igru
        meteor = generate_random_meteor()
        game_state["current_meteor"] = meteor
        game_state["game_started"] = True

        db.collection("rooms").document(room_id).update({
            "status": "playing",
            "game_state": game_state
        })

        # sobiraem list o userah
        users = []
        for uid, card in user_cards.items():
            username = get_user_name(uid)
            users.append({
                "username": username or "Unknown",
                "id": uid,
                "card": card
            })

        #sendim vsem igrokam v komnate
        emit("game_ready", {
            "message": "Admin started the game! Let's play!",
            "users": users,
            "meteor": meteor
        }, room=room_id)

    except Exception as e:
        emit("error", {"message": f"Server error: {str(e)}"}, to=request.sid)

@socketio.on('join_game')
def handle_join_game(data):
    user_id = request.cookies.get('userId')
    room_code = data.get('roomCode')

    if not user_id:
        emit("error", {"message": "Not authenticated"}, to=request.sid)
        return

    if not room_code:
        emit("error", {"message": "Room Code required"}, to=request.sid)
        return

    try:
        rooms = (
            db.collection("rooms")
            .where("code", "==", room_code)
            .where("status", "in", ["playing", "game_waiting"])#find room with status playing or waiting
            .get()
        )

        if not rooms:
            emit("error", {"message": "Room not found"}, to=request.sid)
            return

        room_doc = rooms[0]
        room_id = room_doc.id
        room_data = room_doc.to_dict()

        join_room(room_id)

        game_state = room_data.get("game_state", {})
        user_cards = game_state.get("user_cards", {})

        if room_data.get("status") == "playing":
            emit("error", {"message": "Game already in progress"}, to=request.sid) #if game already started, ne razrishaem(do not allow)
            return

        available_cards = ["ROCKET", "IGNORE", "EVACUATION", "BUNKER"]

        if user_id not in user_cards: #add user card
            card_index = len(user_cards)
            if card_index < len(available_cards):
                user_cards[user_id] = available_cards[card_index]
            else:
                emit("error", {"message": "Game is full"}, to=request.sid)
                return

        user_cards[user_id] = available_cards[card_index]
        game_state["user_cards"] = user_cards

        if room_data.get("status") != "game_waiting": #update status
            db.collection("rooms").document(room_id).update({
                "status": "game_waiting",
                "game_state": game_state
            })
        else:
            db.collection("rooms").document(room_id).update({"game_state": game_state})

        users = []
        for uid, card in user_cards.items():
            username = get_user_name(uid)
            users.append({
                "username": username or "Unknown",
                "id": uid,
                "card": card
            })

        if len(user_cards) == 4 and not game_state.get("game_started", False):
            meteor = generate_random_meteor()
            game_state["current_meteor"] = meteor
            game_state["game_started"] = True

            db.collection("rooms").document(room_id).update({
                "status": "playing",
                "game_state": game_state
            })

            emit("game_ready", {
                "message": "All players ready! Game starting...",
                "users": users,
                "meteor": meteor
            }, room=room_id)

        elif len(user_cards) == 4 and game_state.get("game_started", False):
            emit("game_ready", {
                "message": "Game in progress! Welcome!",
                "users": users,
                "meteor": game_state.get("current_meteor")
            }, to=request.sid)

        else:
            emit("game_wait_room", {
                "message": f"Waiting for players... ({len(user_cards)}/4)",
                "users": users,
                "totalUsers": len(user_cards)
            }, room=room_id)

            emit("game_joined_waiting", {
                "userId": user_id,
                "users": users,
                "totalUsers": len(user_cards)
            }, to=request.sid)

    except Exception as e:
        emit("error", {"message": f"Server error: {str(e)}"}, to=request.sid)

@socketio.on('close_room')
def handle_close_room(data):
    user_id = request.cookies.get('userId')
    room_id = data.get('roomId')
  
    if not user_id:
        emit("error", {"message": "Not authenticated"}, to=request.sid)
        return
    if not room_id:
        emit("error", {"message": "Room ID required"}, to=request.sid)
        return # tut proverka id and return
    try:
        room_doc = db.collection("rooms").document(room_id).get()
        if not room_doc.exists:
            emit("error", {"message": "Room not found"}, to=request.sid)
            return
        room_data = room_doc.to_dict()
        creator_id = room_data.get("creator")
        if user_id != creator_id:
            emit("error", {"message": "Only room creator can close the room"}, to=request.sid)
            return
        emit("room_closed", {
            "message": "Room has been closed by the creator",
            "roomId": room_id
        }, room=room_id)

        db.collection("rooms").document(room_id).delete() #tut udelenie komnati
        
    except Exception as e:
        emit("error", {"message": f"Server error: {str(e)}"}, to=request.sid)

@socketio.on('leave_room')
def handle_leave_room(data):
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
        current_users = room_data.get("users", [])
        creator_id = room_data.get("creator") #dobavil admina

        if user_id not in current_users:
            emit("error", {"message": "You are not in this room"}, to=request.sid)
            return

        username = get_user_name(user_id)

        if user_id == creator_id: # if admin leaves, close the room
            emit("room_closed", {
                "message": f"Room closed - creator {username or 'Unknown'} left",
                "roomId": room_id
            }, room=room_id)
            db.collection("rooms").document(room_id).delete()
        else:
            current_users.remove(user_id)
            if current_users: # esle users ostalis, update room
                db.collection("rooms").document(room_id).update({"users": current_users})
                emit("room_changed", {
                    "userId": user_id,
                    "username": username or "Unknown",
                    "type": "USER_REMOVED",
                    "total_users": len(current_users)
                }, room=room_id)
            else:
                db.collection("rooms").document(room_id).delete()

        emit("room_left", {
            "message": "You have left the room",
            "roomId": room_id
        }, to=request.sid)
    except Exception as e:
        emit("error", {"message": f"Server error: {str(e)}"}, to=request.sid)

@socketio.on('remove_user')
def handle_remove_user(data):
    user_id = request.cookies.get('userId')
    room_id = data.get('roomId')
    target_user_id = data.get('targetUserId')

    if not user_id:
        emit("error", {"message": "Not authenticated"}, to=request.sid)
        return

    if not room_id or not target_user_id:
        emit("error", {"message": "Room ID and target user ID required"}, to=request.sid)
        return

    try:
        room_doc = db.collection("rooms").document(room_id).get()
        if not room_doc.exists:
            emit("error", {"message": "Room not found"}, to=request.sid)
            return

        room_data = room_doc.to_dict()
        current_users = room_data.get("users", [])

        if user_id not in current_users:
            emit("error", {"message": "You are not in this room"}, to=request.sid)
            return

        if target_user_id not in current_users:
            emit("error", {"message": "Target user not in room"}, to=request.sid)
            return

        if user_id == target_user_id:
            emit("error", {"message": "Cannot remove yourself"}, to=request.sid)
            return

        current_users.remove(target_user_id)
        target_username = get_user_name(target_user_id)
        db.collection("rooms").document(room_id).update({"users": current_users})
        emit("room_changed", {
            "userId": target_user_id,
            "username": target_username or "Unknown",
            "type": "USER_REMOVED",
            "total_users": len(current_users)
        }, room=room_id)

    except Exception as e:
        emit("error", {"message": f"Server error: {str(e)}"}, to=request.sid)

@socketio.on('card_chosen')
def handle_card_chosen(data):
    user_id = request.cookies.get('userId')
    room_id = data.get('roomId')
    chosen_card = data.get('card')

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
        generated_scenario = current_meteor.get("generated_scenario", 1)

        is_correct_choice = validate_card_choice(generated_scenario, chosen_card)

        if not is_correct_choice:
            current_hp -= 1

        game_state["hp"] = current_hp

        if current_hp <= 0:
            game_state["status"] = "ended"
            db.collection("rooms").document(room_id).update({
                "status": "ended",
                "game_state": game_state
            })

            emit("game_ended", {
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