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

def generate_from_prompt(user_prompt: str):
    if not model:
        return {"data": f"Fake response for prompt: {user_prompt}"}

    prompt = f"""
    GENERATE A REALISTIC RANDOM METEOR WITH PHYSICAL PARAMETERS BASED ON KNOWN METEORITES.
    
    !!! IMPORTANT INSTRUCTIONS – READ CAREFULLY !!!
    
    1. YOU MUST OUTPUT STRICTLY ONE JSON OBJECT WITH THIS EXACT FORMAT:
       {{
           "data": {{
               "mass": float,
               "speed": float,
               "angle": float,
               "type": string,
               "weather": string,
               "material": string
           }}
       }}
    
    2. DO NOT USE MARKDOWN, DO NOT USE CODE BLOCKS, DO NOT WRITE ANY TEXT, COMMENTS, OR EXPLANATIONS.
    
    3. DATA RULES:
    - mass: float, kg, range [0.1–1,000,000], smaller values more common
    - speed: float, m/s, range [11,000–72,000]
    - angle: float, degrees, range [15–90]
    - type: one of ["Stony", "Iron", "Stony-Iron"] (STONY most common)
    - weather: one of ["Clear", "Rain", "Snow", "Storm"]
    - material must match type:
      STONE -> "Stone"
      IRON -> "Iron"
      MIXED -> "Mixed"
    
    OUTPUT EXAMPLE (RAW JSON ONLY, STRICTLY):
    {{
    "data": {{
        "mass": 850000.0,
        "speed": 55000.0,
        "angle": 35.0,
        "type": "Stony",
        "weather": "Clear",
        "material": "Stone"
        }}
    }}
    
    USER PROMPT: {user_prompt}
    """

    try:
        return model.generate_content(prompt).text
    except Exception as e:
        print(f"Error during generation: {e}")
        return {"data": f"Error generating response for prompt: {prompt}"}

def generate_random_meteor():
    prompt = ''

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


def calculate_casualties(meteor_data):
    if not model:
        raise Exception("Gemini AI model not available. Cannot calculate casualties without AI.")

    prompt = f"""
    You are a scientific expert calculating realistic meteor impact casualties. Analyze the exact coordinates and meteor properties.

    METEOR IMPACT DATA:
    Location: {meteor_data.get('latitude', 0)}°N, {meteor_data.get('longitude', 0)}°E
    Mass: {meteor_data.get('mass', 0)} kg
    Speed: {meteor_data.get('speed', 0)} m/s  
    Angle: {meteor_data.get('angle', 0)}°
    Type: {meteor_data.get('type', 'Unknown')} ({meteor_data.get('material', 'Unknown')})
    Weather: {meteor_data.get('weather', 'Clear')}

    ANALYSIS STEPS:
    1. LOCATION CHECK: What is at coordinates {meteor_data.get('latitude', 0)}, {meteor_data.get('longitude', 0)}?
       - Ocean/Sea? → Very low casualties (0-100)
       - Remote land/desert/mountains? → Low casualties (0-1,000) 
       - Rural/farmland? → Medium casualties (100-10,000)
       - City outskirts? → High casualties (1,000-100,000)
       - Major city center? → Very high casualties (10,000-1,000,000+)

    2. IMPACT ENERGY: Mass {meteor_data.get('mass', 0)}kg at {meteor_data.get('speed', 0)}m/s
       - <1000kg: Local damage only
       - 1000-10000kg: City block damage  
       - 10000-100000kg: Several km radius damage
       - >100000kg: Regional catastrophe

    3. SECONDARY EFFECTS:
       - Ocean impact near coast: Tsunami casualties
       - Weather {meteor_data.get('weather', 'Clear')}: Affects evacuation

    Calculate realistic casualties considering the EXACT location and meteor size.
    Return ONLY the number. Examples:
    - Pacific Ocean: 0
    - Sahara Desert: 12  
    - Rural Kansas: 2400
    - Paris suburbs: 45000
    - Manhattan center: 850000
    """

    try:
        response = model.generate_content(prompt)
        casualties_text = response.text.strip()

        casualties = int(''.join(filter(str.isdigit, casualties_text)))

        if casualties > 100000000:
            casualties = 100000000
        elif casualties < 0:
            casualties = 0

        print(f"AI calculated casualties for coordinates ({meteor_data.get('latitude')}, {meteor_data.get('longitude')}): {casualties}")
        return casualties

    except Exception as e:
        print(f"Error calculating casualties with AI: {e}")
        raise Exception(f"Failed to calculate casualties using AI: {str(e)}")


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

        print(f"Error calculating casualties with AI: {e}")
        raise Exception(f"Failed to calculate casualties using AI: {str(e)}")


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
