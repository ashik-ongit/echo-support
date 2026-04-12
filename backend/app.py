# app.py — Main Flask application
# Integration Lead: Ashik
# Connects Hindsight memory + Groq LLM + frontend

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from groq import Groq
from hindsight_integration import save_to_memory, get_context, build_context_prompt

# Load .env variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# --- Groq Client ---
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Session ID — simple fixed ID for demo (can make dynamic later)
SESSION_ID = "demo_session_001"

# in-memory history store for /history endpoint
conversation_history = []


# ── 1. POST /chat ───────────────────────────────────────────
@app.route("/chat", methods=["POST"])
def chat():
    """Receive user message → Hindsight memory → Groq LLM → return reply."""
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400

        # Step 1: build context from Hindsight memory
        memory_context = build_context_prompt(SESSION_ID, num_messages=5)

        # Step 2: build messages for Groq
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful customer support AI assistant. "
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

        # Step 4: save to Hindsight memory
        save_to_memory(user_message, ai_reply, SESSION_ID)

        # Step 5: also save locally for /history
        conversation_history.append({"text": user_message, "sender": "user"})
        conversation_history.append({"text": ai_reply, "sender": "bot"})

        return jsonify({"reply": ai_reply}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── 2. GET /history ─────────────────────────────────────────
@app.route("/history", methods=["GET"])
def get_history():
    """Return conversation history."""
    return jsonify(conversation_history), 200


# ── 3. POST /reset ──────────────────────────────────────────
@app.route("/reset", methods=["POST"])
def reset_memory():
    """Clear conversation history."""
    conversation_history.clear()
    return jsonify({"message": "Memory cleared successfully"}), 200


# ── Run server ──────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)