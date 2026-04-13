import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from groq import Groq
from hindsight_integration import save_to_memory, build_context_prompt

load_dotenv()
app = Flask(__name__)
CORS(app)

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
SESSION_ID = "demo_session_001"
conversation_history = []


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()
        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400

        memory_context = build_context_prompt(SESSION_ID, num_messages=5)

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Echo, a smart customer support AI. "
                        "Use this memory context:\n" + memory_context + "\n\n"
                        "After your reply, on a NEW LINE write exactly:\n"
                        "MEMORY: <one short emoji + fact to remember, max 8 words, or SKIP if nothing important>"
                    )
                },
                {"role": "user", "content": user_message}
            ],
            max_tokens=1100,
            temperature=0.7
        )

        full = response.choices[0].message.content.strip()

        if "MEMORY:" in full:
            parts = full.rsplit("MEMORY:", 1)
            ai_reply = parts[0].strip()
            memory = parts[1].strip()
            if memory == "SKIP":
                memory = None
        else:
            ai_reply = full
            memory = None

        save_to_memory(user_message, ai_reply, SESSION_ID)
        conversation_history.append({"text": user_message, "sender": "user"})
        conversation_history.append({"text": ai_reply, "sender": "bot"})

        return jsonify({"reply": ai_reply, "memory": memory}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/history", methods=["GET"])
def get_history():
    return jsonify(conversation_history), 200


@app.route("/reset", methods=["POST"])
def reset_memory():
    conversation_history.clear()
    return jsonify({"message": "Memory cleared successfully"}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)