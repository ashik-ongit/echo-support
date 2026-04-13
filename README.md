🤖 AI Agents That Learn Using Hindsight

Most AI systems today forget you the moment the conversation ends.
They respond, but they don’t **remember**, **learn**, or **grow with you**.

Our goal is to change that.

We are building AI agents that don’t just answer questions — they understand people over time. By using *hindsight memory*,
the system reflects on past conversations, learns user preferences, and adapts its behavior to feel more natural, personal, and human.

This transforms AI from a tool into something closer to a **thoughtful assistant that evolves with you**.


💡 Project Overview

This project is a memory-powered AI chat system designed to:

* 🧠 Remember past conversations using Hindsight Cloud
* 🔁 Use previous interactions to build meaningful context
* 🎯 Learn user preferences (tone, style, needs)
* 💬 Deliver more personalized, human-like responses
* 🎨 Provide a clean, premium chat experience inspired by Apple design

Instead of starting from zero every time, this AI **builds a relationship with the user over time**.


⚙️ Setup Instructions

1. Clone the Repository

```bash
git clone <your-repo-link>
cd project
```

2. Install Required Dependencies

```bash
pip install requests
```

3. Configure API Access

* Open `hindsight_integration.py`
* Replace:

```python
API_KEY = "YOUR_API_KEY"
```

with your actual Hindsight API key.


▶️ How to Run the Project

### Step 1: Start Backend Server

(Example using Flask)

```bash
python app.py
```

### Step 2: Open Frontend

* Open `index.html` in your browser
* Start chatting with the AI

---

🔄 How It Works (Simple Flow)

1. User sends a message
2. AI generates a response
3. Conversation is stored in memory (Hindsight)
4. Future responses use past context
5. AI gradually learns and adapts to the user


❤️ What Makes This Special

* Remembers conversations like a human would
* Learns preferences instead of being re-trained
* Creates a more natural and engaging experience
* Moves AI from “stateless” → “relationship-based”
