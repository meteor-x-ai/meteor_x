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

