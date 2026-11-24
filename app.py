import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

SYSTEM_PROMPT = (
    "You are MMM Nexus AI, an intelligent, friendly, and helpful AI assistant created by your visionary founder, Murali Mohan. "
    "Always reply naturally in the user's language (Telugu, English, or Tenglish). "
    "Keep answers clear, accurate, and engaging."
)

TEXT_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.5-flash-lite"
]

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "MMM Nexus Backend Live", "creator": "Murali Mohan"})

@app.route("/chat", methods=["POST"])
def chat():
    if not GEMINI_API_KEY:
        return jsonify({"error": "GEMINI_API_KEY missing on server."}), 500

    data = request.get_json() or {}
    user_msg = data.get("message", "").strip()
    img_b64 = data.get("image")
    mime_type = data.get("mimeType", "image/jpeg")

    if not user_msg and not img_b64:
        return jsonify({"error": "Empty message"}), 400

    parts = []
    if img_b64:
        parts.append({"inline_data": {"mime_type": mime_type, "data": img_b64}})
    if user_msg:
        parts.append({"text": user_msg})

    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": parts}]
    }

    last_error = "Server busy, please try again."
    for model in TEXT_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        try:
            res = requests.post(url, json=payload, timeout=60)
            res_json = res.json()
            if res.status_code == 200 and "candidates" in res_json:
                reply = res_json["candidates"][0]["content"]["parts"][0]["text"]
                return jsonify({"reply": reply, "model": model})
            else:
                err_msg = res_json.get("error", {}).get("message", f"HTTP {res.status_code}")
                last_error = err_msg
        except Exception as e:
            last_error = str(e)

    return jsonify({"error": last_error}), 503

@app.route("/generate-image", methods=["POST"])
def generate_image():
    if not GEMINI_API_KEY:
        return jsonify({"error": "GEMINI_API_KEY missing on server."}), 500

    data = request.get_json() or {}
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={GEMINI_API_KEY}"
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {"sampleCount": 1}
    }

    try:
        res = requests.post(url, json=payload, timeout=60)
        res_json = res.json()
        if res.status_code == 200 and "predictions" in res_json:
            b64_img = res_json["predictions"][0]["bytesBase64Encoded"]
            return jsonify({"image": f"data:image/jpeg;base64,{b64_img}"})
        err_msg = res_json.get("error", {}).get("message", "Image generation failed")
        return jsonify({"error": err_msg}), res.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
