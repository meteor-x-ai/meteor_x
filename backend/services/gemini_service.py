import os, json, random

try:
    import google.generativeai as genai
except ImportError:
    genai = None

model = None
if genai:
    api_key = os.environ.get('GEMINI_API_KEY')
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash-lite')
        except Exception:
            model = None

def generate_from_prompt(prompt: str):
    if not model:
        return {"data": f"Fake response for prompt: {prompt}"}
    try:
        response = model.generate_content(prompt)
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            return {"data": response.text}
    except Exception as e:
        print(f"Error during generation: {e}")
        return {"data": f"Error generating response for prompt: {prompt}"}


def generate_random_meteor():
    prompt = """
    Create a realistic random meteor with physical parameters based on known meteorites.

    Parameters to generate:
    - mass: mass in kg (0.1 to 1,000,000 kg, smaller values more common)
    - speed: atmospheric entry speed in m/s (11,000-72,000 m/s)
    - angle: entry angle to horizon in degrees (15-90°)
    - latitude: impact latitude (-90 to 90)
    - longitude: impact longitude (-180 to 180)
    - type: meteor type ("STONY", "IRON", "STONY_IRON") - stony most common
    - weather: weather conditions ("CLEAR", "RAIN", "SNOW", "STORM")
    - material: material ("STONE", "IRON", "MIXED") - must match type

    Type-Material mapping:
    STONY -> STONE
    IRON -> IRON  
    STONY_IRON -> MIXED

    Return ONLY JSON format:
    {
        "mass": number,
        "speed": number,
        "angle": number,
        "latitude": number,
        "longitude": number,
        "type": "string",
        "weather": "string",
        "material": "string"
    }
    """
    
    if not model:
        return create_fallback_meteor()
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean markdown formatting if present
        if response_text.startswith('```'):
            lines = response_text.split('\n')
            json_lines = []
            in_json = False
            for line in lines:
                if line.startswith('```'):
                    in_json = not in_json
                    continue
                if in_json:
                    json_lines.append(line)
            response_text = '\n'.join(json_lines)
        
        meteor_data = json.loads(response_text)
        
        if is_valid_meteor(meteor_data):
            return meteor_data
        else:
            print("Generated data failed validation, using fallback")
            return create_fallback_meteor()
            
    except (json.JSONDecodeError, Exception) as e:
        print(f"Error generating meteor with AI: {e}")
        return create_fallback_meteor()


def create_fallback_meteor():
    meteor_type_chance = random.random()
    if meteor_type_chance < 0.86:
        meteor_type, material = "STONY", "STONE"
    elif meteor_type_chance < 0.94:
        meteor_type, material = "IRON", "IRON"
    else:
        meteor_type, material = "STONY_IRON", "MIXED"
    
    weather_chance = random.random()
    if weather_chance < 0.7:
        weather = "CLEAR"
    elif weather_chance < 0.85:
        weather = "RAIN"
    elif weather_chance < 0.95:
        weather = "SNOW"
    else:
        weather = "STORM"
    
    # Logarithmic distribution for mass (smaller values more common)
    mass_log = random.uniform(-1, 6)
    mass = 10 ** mass_log
    
    return {
        "mass": round(mass, 2),
        "speed": random.randint(11000, 72000),
        "angle": random.randint(15, 90),
        "latitude": round(random.uniform(-90, 90), 6),
        "longitude": round(random.uniform(-180, 180), 6),
        "type": meteor_type,
        "weather": weather,
        "material": material
    }


def is_valid_meteor(data):
    try:
        required_fields = ["mass", "speed", "angle", "latitude", "longitude", "type", "weather", "material"]
        if not all(field in data for field in required_fields):
            return False
        
        if not (0.1 <= data["mass"] <= 1000000):
            return False
        if not (11000 <= data["speed"] <= 72000):
            return False
        if not (15 <= data["angle"] <= 90):
            return False
        if not (-90 <= data["latitude"] <= 90):
            return False
        if not (-180 <= data["longitude"] <= 180):
            return False
        
        valid_types = ["STONY", "IRON", "STONY_IRON"]
        valid_weathers = ["CLEAR", "RAIN", "SNOW", "STORM"]
        valid_materials = ["STONE", "IRON", "MIXED"]
        
        if data["type"] not in valid_types:
            return False
        if data["weather"] not in valid_weathers:
            return False
        if data["material"] not in valid_materials:
            return False
        
        type_material_map = {
            "STONY": "STONE",
            "IRON": "IRON",
            "STONY_IRON": "MIXED"
        }
        if data["material"] != type_material_map[data["type"]]:
            return False
        
        return True
        
    except (KeyError, TypeError, ValueError):
        return False
