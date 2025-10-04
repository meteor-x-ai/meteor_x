import os, json
import google.generativeai as genai

model = None
try:
    genai.configure(api_key=os.environ['GEMINI_API_KEY'])
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
except KeyError:
    print("Error: GEMINI_API_KEY environment variable not set. Please get your key from Google AI Studio at https://aistudio.google.com/app/apikey and set it as an environment variable.")

def generate_from_prompt(prompt: str):
    if not model:
        raise RuntimeError("Model not initialized. Check API key.")
    
    try:
        response = model.generate_content(prompt)
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            return {"data": response.text}
    except Exception as e:
        print(f"Error during generation: {e}")
        return None
