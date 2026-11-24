import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def call_gemini(model, text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
    prompt = (
        "You are MMM Nexus AI, created by founder Murali Mohan. "
        "Answer clearly, warmly, and helpfully in the same language the user asks "
        "(Telugu, English, or Tenglish): " + text
    )
    res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=25)
    return res.json()

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "MMM Nexus Backend v1.0 is Live!"})

@app.route("/chat", methods=["POST"])
def chat():
    if not GEMINI_API_KEY:
        return jsonify({"error": "Server API Key missing"}), 500

    data = request.get_json() or {}
    text = data.get("message", "").strip()
    if not text:
        return jsonify({"error": "Empty message"}), 400

    try:
        result = call_gemini("gemini-3.5-flash-lite", text)
        if "error" in result:
            result = call_gemini("gemini-3.5-flash", text)

        reply = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text")
        if reply:
            return jsonify({"reply": reply})
        return jsonify({"error": result.get("error", {}).get("message", "Try again")}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
