import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "MMM Nexus Backend is Live!"})

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_msg = data.get("message", "")
        image_base64 = data.get("image", None)
        mime_type = data.get("mimeType", "image/jpeg")

        if not user_msg and not image_base64:
            return jsonify({"error": "Empty message"}), 400

        parts = []
        if user_msg:
            parts.append({"text": user_msg})
        else:
            parts.append({"text": "Analyze this image in detail."})

        if image_base64:
            parts.append({
                "inline_data": {
                    "mime_type": mime_type,
                    "data": image_base64
                }
            })

        payload = {
            "systemInstruction": {
                "parts": [{
                    "text": "You are MMM Nexus AI, a smart, helpful personal AI assistant created by Murali Mohan. Reply clearly in the user's language (Telugu or English)."
                }]
            },
            "contents": [{"parts": parts}]
        }

        res = requests.post(GEMINI_URL, json=payload, timeout=30)
        res_data = res.json()

        if "candidates" in res_data:
            reply = res_data["candidates"][0]["content"]["parts"][0]["text"]
            return jsonify({"reply": reply})
        else:
            err_msg = res_data.get("error", {}).get("message", "AI response error")
            return jsonify({"error": err_msg}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
        
