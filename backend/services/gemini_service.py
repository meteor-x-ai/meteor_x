import os, json

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
