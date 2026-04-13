import os
import json
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

MEMORY_FILE = "memories.json"

def load_memories():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_memories(memories):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memories, f)

local_memories = load_memories()


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()
        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400

        memory_context = build_context_prompt(SESSION_ID, num_messages=5)

        # inject local memories directly so AI actually sees them
        local_memory_str = "\n".join(local_memories) if local_memories else "No memories yet."

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Echo, a smart customer support AI with memory. "
                        "You MUST use these memories in every reply — never say you don't know the user:\n"
                        + local_memory_str + "\n\n"
                        "Hindsight context:\n" + memory_context + "\n\n"
                        "After your reply add a new line with:\n"
                        "MEMORY: \n"
                        "ALWAYS extract something. Even for greetings extract like: "
                        "'👋 User started a new conversation' or '👤 User said hi'. "
                        "Never write SKIP. Always write a memory fact."
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
        else:
            ai_reply = full
            memory = None

        save_to_memory(user_message, ai_reply, SESSION_ID)

        if memory and memory not in local_memories:
            local_memories.append(memory)
            save_memories(local_memories)

        conversation_history.append({"text": user_message, "sender": "user"})
        conversation_history.append({"text": ai_reply, "sender": "bot"})

        return jsonify({"reply": ai_reply, "memory": memory}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/welcome", methods=["GET"])
def welcome():
    try:
        if not local_memories:
            return jsonify({"message": None}), 200

        context = "\n".join(local_memories)

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Echo, a smart support AI with memory. "
                        "Based on these memories about a returning user, "
                        "generate a SHORT warm welcome back message under 20 words. "
                        "Mention their name or issue if you know it. "
                        "Example: 'Welcome back Ashik! I remember your order issue. How can I help today?' "
                        "Only return the message, nothing else."
                    )
                },
                {"role": "user", "content": f"Memories:\n{context}"}
            ],
            max_tokens=60,
            temperature=0.7
        )
        message = response.choices[0].message.content.strip()
        return jsonify({"message": message}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/memories", methods=["GET"])
def get_memories():
    return jsonify({"memories": local_memories}), 200


@app.route("/history", methods=["GET"])
def get_history():
    return jsonify(conversation_history), 200


@app.route("/reset", methods=["POST"])
def reset_memory():
    conversation_history.clear()
    local_memories.clear()
    save_memories([])
    return jsonify({"message": "Memory cleared successfully"}), 200
//hi 

if __name__ == "__main__":
    app.run(debug=True, port=5000)