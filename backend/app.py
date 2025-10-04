from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import firebase_admin
from flask_socketio import SocketIO, join_room, emit
from firebase_admin import credentials, firestore
from services.gemini_service import generate_from_prompt
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

# Path to the meteors data file
data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'meteors.json')

def load_meteors():
    try:
        with open(data_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading meteors: {e}")
        return []

def generate_random_meteor():
    meteors = load_meteors()
    if not meteors:
        return None
    
    meteor = random.choice(meteors)
    game_meteor = {
        "id": random.randint(1000, 9999),
        "name": meteor["name"],
        "mass": meteor["mass"],
        "speed": meteor["speed"],
        "angle": meteor["angle"],
        "type": meteor["type"],
        "material": meteor["material"],
        "weather": meteor["weather"],
        "diameter": meteor["diameter"],
        "description": meteor["description"]
    }
    return game_meteor

def get_correct_card_for_meteor(meteor):
    if meteor["mass"] > 1e12:  # Very large meteor
        return "ROCKET"  # Launch rocket to deflect
    elif meteor["diameter"] > 1000:  # Large meteor
        return "EVACUATION"  # Evacuate the area
    elif meteor["speed"] > 25000:  # Very fast meteor
        return "BUNKER"  # Take shelter in bunker
    else:
        return "IGNORE"  # Small meteor

# test, test -- auth

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

# -------------------- GAME --------------------

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

def get_username_by_id(user_id):
    """Get username from Firebase by user ID"""
    try:
        user_doc = db.collection("users").document(user_id).get()
        if user_doc.exists:
            return user_doc.to_dict().get("username", "Unknown")
        return "Unknown"
    except Exception as e:
        print(f"Error getting username: {e}")
        return "Unknown"

def get_game_state(room_id):
    """Get game state from Firestore"""
    try:
        game_doc = db.collection("games").document(room_id).get()
        if game_doc.exists:
            return game_doc.to_dict()
        return None
    except Exception as e:
        print(f"Error getting game state: {e}")
        return None

def save_game_state(room_id, game_state):
    """Save game state to Firestore"""
    try:
        db.collection("games").document(room_id).set(game_state)
        return True
    except Exception as e:
        print(f"Error saving game state: {e}")
        return False

def update_game_state(room_id, updates):
    """Update specific fields in game state"""
    try:
        db.collection("games").document(room_id).update(updates)
        return True
    except Exception as e:
        print(f"Error updating game state: {e}")
        return False

def delete_game_state(room_id):
    """Delete game state from Firestore"""
    try:
        db.collection("games").document(room_id).delete()
        return True
    except Exception as e:
        print(f"Error deleting game state: {e}")
        return False

# -------------------- GAME SOCKET --------------------

# -------------------- GAME SOCKET --------------------

@socketio.on('join_lobby')
def handle_join_lobby(data):
    user_id = request.cookies.get('userId')
    if not user_id:
        emit("error", {"message": "Not authenticated"}, to=request.sid)
        return

    room_id = data.get('roomId')
    
    # If no roomId provided, create a new room
    if not room_id:
        room_code = generate_room_code()
        room_id = str(uuid.uuid4())
        
        # Create new room in Firebase
        db.collection("rooms").document(room_id).set({
            "code": room_code,
            "users": [user_id],
            "status": "waiting",
            "createdAt": firestore.SERVER_TIMESTAMP
        })
        
        # Join the socket room
        join_room(room_id)
        
        # Get username
        username = get_username_by_id(user_id)
        
        # Return room info to the creator
        emit("lobby_created", {
            "roomId": room_id,
            "code": room_code,
            "users": [user_id]
        }, to=request.sid)
        
        # Notify about user addition (even though it's just creator)
        emit("room_changed", {
            "userId": user_id,
            "username": username,
            "type": "USER_ADDED"
        }, room=room_id)
        
        return
    
    # Joining existing room
    join_room(room_id)
    
    # Get room from Firebase
    room_doc = db.collection("rooms").document(room_id).get()
    if not room_doc.exists:
        emit("error", {"message": "Room not found"}, to=request.sid)
        return
    
    room_data = room_doc.to_dict()
    
    # Check if room is still waiting and not full
    if room_data.get("status") != "waiting":
        emit("error", {"message": "Room is no longer accepting players"}, to=request.sid)
        return
    
    if len(room_data["users"]) >= 4:
        emit("error", {"message": "Room is full"}, to=request.sid)
        return
    
    # Add user to room if not already there
    if user_id not in room_data["users"]:
        room_data["users"].append(user_id)
        db.collection("rooms").document(room_id).update({"users": room_data["users"]})
        
        # Get username
        username = get_username_by_id(user_id)
        
        # Notify all users in room about new user
        emit("room_changed", {
            "userId": user_id,
            "username": username,
            "type": "USER_ADDED"
        }, room=room_id)
    
    # Send current room state to the joining user
    emit("lobby_joined", {
        "roomId": room_id,
        "code": room_data["code"],
        "users": room_data["users"]
    }, to=request.sid)

@socketio.on('start_game')
def handle_start_game(data):
    user_id = request.cookies.get('userId')
    room_id = data.get('roomId')
    
    if not room_id or not user_id:
        emit("error", {"message": "Invalid request"}, to=request.sid)
        return
    
    # Get room from Firebase
    room_doc = db.collection("rooms").document(room_id).get()
    if not room_doc.exists:
        emit("error", {"message": "Room not found"}, to=request.sid)
        return
    
    room_data = room_doc.to_dict()
    
    # Check if user is in the room
    if user_id not in room_data.get("users", []):
        emit("error", {"message": "User not in room"}, to=request.sid)
        return
    
    # Check room status
    if room_data.get("status") != "waiting":
        emit("error", {"message": "Game already started or ended"}, to=request.sid)
        return
    
    # Check if enough users (exactly 4)
    users = room_data.get("users", [])
    if len(users) != 4:
        emit("error", {"message": f"Need exactly 4 players to start. Currently: {len(users)}"}, to=request.sid)
        return
    
    # Update room status to "starting" in Firebase
    db.collection("rooms").document(room_id).update({"status": "starting"})
    
    # Send game_redirect to all users in the room
    emit("game_redirect", {
        "message": "Game is starting!",
        "roomId": room_id,
        "users": users
    }, room=room_id)

@socketio.on('leave_lobby')
def handle_leave_lobby(data):
    user_id = request.cookies.get('userId')
    room_id = data.get('roomId')
    
    if not room_id or not user_id:
        emit("error", {"message": "Invalid request"}, to=request.sid)
        return
    
    try:
        room_doc = db.collection("rooms").document(room_id).get()
        if not room_doc.exists:
            return
        
        room_data = room_doc.to_dict()
        if user_id not in room_data.get("users", []):
            return
        
        # Remove user from room
        updated_users = [uid for uid in room_data["users"] if uid != user_id]
        
        if len(updated_users) == 0:
            # Delete empty room
            db.collection("rooms").document(room_id).delete()
        else:
            # Update room with remaining users
            db.collection("rooms").document(room_id).update({"users": updated_users})
            
            # Get username for notification
            username = get_username_by_id(user_id)
            
            # Notify remaining users about user leaving
            emit("room_changed", {
                "userId": user_id,
                "username": username,
                "type": "USER_REMOVED"
            }, room=room_id)
        
        # Confirm to the leaving user
        emit("lobby_left", {"message": "Successfully left lobby"}, to=request.sid)
        
    except Exception as e:
        print(f"Error leaving lobby: {e}")
        emit("error", {"message": "Failed to leave lobby"}, to=request.sid)

@socketio.on('join_game')
def handle_join_game(data):
    """Handle game start when all players are ready"""
    user_id = request.cookies.get('userId')
    room_id = data.get('roomId')
    user_ids = data.get('userIds', [])
    
    if not room_id or not user_id:
        emit("error", {"message": "Invalid request"}, to=request.sid)
        return
    
    join_room(room_id)
    
    if len(user_ids) != 4:
        emit("error", {"message": "Game requires exactly 4 players"}, to=request.sid)
        return
    
    if user_id not in user_ids:
        emit("error", {"message": "User not in game"}, to=request.sid)
        return
    
    # Check if game state already exists in Firestore
    game_state = get_game_state(room_id)
    
    if not game_state:
        # Create new game state
        meteor = generate_random_meteor()
        if not meteor:
            emit("error", {"message": "Failed to generate meteor"}, to=request.sid)
            return
            
        game_state = {
            "users": user_ids,
            "player_hp": {uid: 3 for uid in user_ids},  # Everyone starts with 3 HP
            "current_meteor": meteor,
            "correct_card": get_correct_card_for_meteor(meteor),
            "status": "active",
            "round": 1,
            "created_at": firestore.SERVER_TIMESTAMP
        }
        
        # Save game state to Firestore
        if not save_game_state(room_id, game_state):
            emit("error", {"message": "Failed to save game state"}, to=request.sid)
            return
        
        # Update room status in database
        db.collection("rooms").document(room_id).update({"status": "active"})
        
        # Emit game_started to all players in the room
        emit("game_started", {
            "message": "Game has started!",
            "meteor": meteor,
            "round": 1
        }, room=room_id)
    
    # Return user's position in the list (0-indexed)
    try:
        user_position = user_ids.index(user_id)
        
        emit("player_info", {
            "position": user_position,
            "hp": game_state["player_hp"][user_id],
            "meteor": game_state["current_meteor"],
            "round": game_state["round"]
        }, to=request.sid)
        
    except ValueError:
        emit("error", {"message": "User not found in game"}, to=request.sid)

@socketio.on('card_chosen')
def handle_card_chosen(data):
    """Handle player card choice"""
    user_id = request.cookies.get('userId')
    room_id = data.get('roomId')
    chosen_card = data.get('card')
    
    if not room_id or not user_id or not chosen_card:
        emit("error", {"message": "Invalid request"}, to=request.sid)
        return
    
    # Get game state from Firestore
    game_state = get_game_state(room_id)
    if not game_state:
        emit("error", {"message": "Game not found"}, to=request.sid)
        return
    
    # Check if user is in the game
    if user_id not in game_state["users"]:
        emit("error", {"message": "User not in game"}, to=request.sid)
        return
    
    # Check if player is still alive
    if game_state["player_hp"][user_id] <= 0:
        emit("error", {"message": "Player is already eliminated"}, to=request.sid)
        return
    
    # Check if card choice is correct
    correct_card = game_state["correct_card"]
    is_correct = chosen_card == correct_card
    
    # Update HP if wrong choice
    if not is_correct:
        game_state["player_hp"][user_id] -= 1
    
    # Check how many lives left
    remaining_hp = game_state["player_hp"][user_id]
    
    # Check if any players are still alive
    alive_players = [uid for uid, hp in game_state["player_hp"].items() if hp > 0]
    
    if len(alive_players) == 0 or remaining_hp == 0:
        # Game over - all players dead or this player died
        game_state["status"] = "ended"
        
        # Save final game state and delete from games collection
        save_game_state(room_id, game_state)
        delete_game_state(room_id)
        
        # Update room status in database
        db.collection("rooms").document(room_id).update({"status": "ended"})
        
        emit("game_ended", {
            "message": "GAME_ENDED",
            "reason": "All players eliminated" if len(alive_players) == 0 else "You have been eliminated",
            "correct_card": correct_card,
            "chosen_card": chosen_card,
            "final_hp": game_state["player_hp"]
        }, room=room_id)
        
    else:
        # Game continues - generate new meteor for next round
        new_meteor = generate_random_meteor()
        if new_meteor:
            game_state["current_meteor"] = new_meteor
            game_state["correct_card"] = get_correct_card_for_meteor(new_meteor)
            game_state["round"] += 1
            
            # Save updated game state to Firestore
            if not save_game_state(room_id, game_state):
                emit("error", {"message": "Failed to save game state"}, room=room_id)
                return
            
            # Send game state update to all players
            emit("game_update", {
                "message": "Round continues",
                "was_correct": is_correct,
                "correct_card": correct_card,
                "chosen_card": chosen_card,
                "player_hp": game_state["player_hp"],
                "new_meteor": new_meteor,
                "round": game_state["round"],
                "alive_players": alive_players
            }, room=room_id)
        else:
            emit("error", {"message": "Failed to generate new meteor"}, room=room_id)


@socketio.on('disconnect')
def handle_disconnect():
    """Handle player disconnection"""
    user_id = request.cookies.get('userId')
    if not user_id:
        return
    
    # Clean up active games from Firestore
    try:
        games_ref = db.collection("games")
        active_games_docs = games_ref.where("status", "==", "active").stream()
        
        rooms_to_clean = []
        for game_doc in active_games_docs:
            game_data = game_doc.to_dict()
            room_id = game_doc.id
            
            if user_id in game_data.get("users", []):
                # Mark player as disconnected by setting HP to 0
                game_data["player_hp"][user_id] = 0
                
                # Check if game should end
                alive_players = [uid for uid, hp in game_data["player_hp"].items() if hp > 0]
                if len(alive_players) == 0:
                    rooms_to_clean.append(room_id)
                    game_data["status"] = "ended"
                    save_game_state(room_id, game_data)
                    
                    emit("game_ended", {
                        "message": "GAME_ENDED",
                        "reason": "Player disconnected - game terminated",
                        "final_hp": game_data["player_hp"]
                    }, room=room_id)
                else:
                    # Save updated game state
                    save_game_state(room_id, game_data)
                    
                    emit("game_update", {
                        "message": "Player disconnected",
                        "player_hp": game_data["player_hp"],
                        "alive_players": alive_players
                    }, room=room_id)
        
        # Clean up ended games
        for room_id in rooms_to_clean:
            delete_game_state(room_id)
            db.collection("rooms").document(room_id).update({"status": "ended"})
            
    except Exception as e:
        print(f"Error cleaning up active games: {e}")
    
    # Clean up waiting rooms (remove user from rooms in waiting state)
    try:
        rooms_ref = db.collection("rooms")
        waiting_rooms = rooms_ref.where("status", "==", "waiting").stream()
        
        for room_doc in waiting_rooms:
            room_data = room_doc.to_dict()
            if user_id in room_data.get("users", []):
                updated_users = [uid for uid in room_data["users"] if uid != user_id]
                
                if len(updated_users) == 0:
                    # Delete empty room
                    rooms_ref.document(room_doc.id).delete()
                else:
                    # Update room with remaining users
                    rooms_ref.document(room_doc.id).update({"users": updated_users})
                    
                    # Get username for notification
                    username = get_username_by_id(user_id)
                    
                    # Notify remaining users about user leaving
                    emit("room_changed", {
                        "userId": user_id,
                        "username": username,
                        "type": "USER_REMOVED"
                    }, room=room_doc.id)
                
                break  # User should only be in one waiting room
    except Exception as e:
        print(f"Error cleaning up waiting rooms: {e}")

@socketio.on('get_game_state')
def handle_get_game_state(data):
    """Get current game state for reconnecting players"""
    user_id = request.cookies.get('userId')
    room_id = data.get('roomId')
    
    if not room_id or not user_id:
        emit("error", {"message": "Invalid request"}, to=request.sid)
        return
    
    # Get game state from Firestore
    game_state = get_game_state(room_id)
    if not game_state:
        emit("error", {"message": "Game not found"}, to=request.sid)
        return
    
    if user_id not in game_state["users"]:
        emit("error", {"message": "User not in game"}, to=request.sid)
        return
    
    # Send current game state to the requesting player
    emit("game_state", {
        "hp": game_state["player_hp"][user_id],
        "meteor": game_state["current_meteor"],
        "round": game_state["round"],
        "status": game_state["status"],
        "alive_players": [uid for uid, hp in game_state["player_hp"].items() if hp > 0],
        "all_player_hp": game_state["player_hp"]
    }, to=request.sid)


if __name__ == '__main__':
    from flask_socketio import SocketIO

    socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)
