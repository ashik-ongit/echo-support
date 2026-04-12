# app.py — Main Flask application
# Integration Lead: Ashik
# Connects Hindsight memory + Groq LLM + frontend

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from groq import Groq
from hindsight import HindsightClient  # adjust to your Hindsight package

# Load .env variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # allows frontend to connect

# --- API Clients ---
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
hindsight_client = HindsightClient(api_key=os.getenv("HINDSIGHT_API_KEY"))


# ── 1. POST /chat ──────────────────────────────────────────
@app.route("/chat", methods=["POST"])
def chat():
    """Receive user message → Hindsight memory → Groq LLM → return reply."""
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400

        # Step 1: get memory context from Hindsight
        memory_context = hindsight_client.get_context(user_message)

        # Step 2: build messages for Groq
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful AI assistant. "
                    "Use the memory context below to personalise your response:\n"
                    f"{memory_context}"
                )
            },
            {"role": "user", "content": user_message}
        ]

        # Step 3: call Groq LLM
        response = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages,
            max_tokens=1024,
            temperature=0.7
        )
        ai_reply = response.choices[0].message.content

        # Step 4: save exchange to Hindsight
        hindsight_client.save_exchange(
            user_message=user_message,
            ai_response=ai_reply
        )

        return jsonify({"reply": ai_reply}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── 2. GET /history ────────────────────────────────────────
@app.route("/history", methods=["GET"])
def get_history():
    """Return full conversation history from Hindsight."""
    try:
        history = hindsight_client.get_history()
        return jsonify({"history": history}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── 3. POST /reset ─────────────────────────────────────────
@app.route("/reset", methods=["POST"])
def reset_memory():
    """Clear all conversation memory from Hindsight."""
    try:
        hindsight_client.clear_memory()
        return jsonify({"message": "Memory cleared successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Run server ─────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)