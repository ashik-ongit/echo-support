"""
hindsight_integration.py
Hindsight Cloud API integration for memory storage, retrieval, and preference learning.
Branch: ashi-branch | Author: adhiragul
"""

import os
import json
import requests
from datetime import datetime
from typing import Optional

# ─── Configuration ────────────────────────────────────────────────────────────

HINDSIGHT_API_BASE = "https://api.hindsight.vectorize.io/v1"
HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY", "")
PROMO_CODE = "MEMHACK409"

HEADERS = {
    "Authorization": f"Bearer {HINDSIGHT_API_KEY}",
    "Content-Type": "application/json",
    "X-Promo-Code": PROMO_CODE,
}


# ─── Core Functions ───────────────────────────────────────────────────────────


def save_to_memory(user_message: str, ai_response: str, session_id: str) -> dict:
    """
    Save a conversation turn to Hindsight Cloud memory.

    Args:
        user_message (str): The message sent by the user.
        ai_response  (str): The AI's reply to that message.
        session_id   (str): Unique identifier for the user/session.

    Returns:
        dict: API response payload, or an error dict on failure.

    Example:
        >>> result = save_to_memory("My order is late", "I'm sorry to hear that...", "user_42")
        >>> print(result.get("id"))  # memory entry ID
    """
    payload = {
        "session_id": session_id,
        "messages": [
            {"role": "user",      "content": user_message},
            {"role": "assistant", "content": ai_response},
        ],
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "metadata": {
            "source": "customer_support_chat",
            "promo":  PROMO_CODE,
        },
    }

    try:
        response = requests.post(
            f"{HINDSIGHT_API_BASE}/memories",
            headers=HEADERS,
            json=payload,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as exc:
        return {"error": str(exc), "saved": False}


def get_context(session_id: str, num_messages: int = 5) -> list[dict]:
    """
    Retrieve the last N conversation turns for a session from Hindsight Cloud.

    Args:
        session_id   (str): Unique identifier for the user/session.
        num_messages (int): How many recent message pairs to fetch (default: 5).

    Returns:
        list[dict]: Ordered list of message dicts, each with 'role' and 'content'.
                    Returns an empty list on failure.

    Example:
        >>> history = get_context("user_42", num_messages=3)
        >>> for msg in history:
        ...     print(msg["role"], ":", msg["content"])
    """
    params = {
        "session_id": session_id,
        "limit": num_messages,
        "order": "desc",  # newest first, we'll reverse below
    }

    try:
        response = requests.get(
            f"{HINDSIGHT_API_BASE}/memories",
            headers=HEADERS,
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        # Flatten paired messages into a flat list, oldest-first
        messages = []
        for entry in reversed(data.get("memories", [])):
            messages.extend(entry.get("messages", []))

        return messages

    except requests.exceptions.RequestException as exc:
        print(f"[Hindsight] get_context error: {exc}")
        return []


def get_learned_preferences(session_id: str) -> dict:
    """
    Extract learned user preferences and behavioural patterns from stored memory.

    Hindsight Cloud analyses past conversations and returns structured insights
    such as preferred tone, common topics, sentiment trends, and recurring issues.

    Args:
        session_id (str): Unique identifier for the user/session.

    Returns:
        dict: Preference/pattern data, e.g.:
              {
                "preferred_tone":   "formal",
                "common_topics":    ["shipping", "returns"],
                "sentiment_trend":  "frustrated → satisfied",
                "language":         "en",
                "custom_notes":     ["prefers bullet-point answers"]
              }
              Returns an empty dict on failure.

    Example:
        >>> prefs = get_learned_preferences("user_42")
        >>> if prefs.get("preferred_tone") == "formal":
        ...     system_prompt += " Respond formally."
    """
    try:
        response = requests.get(
            f"{HINDSIGHT_API_BASE}/insights/{session_id}",
            headers=HEADERS,
            timeout=10,
        )
        response.raise_for_status()
        return response.json().get("preferences", {})

    except requests.exceptions.RequestException as exc:
        print(f"[Hindsight] get_learned_preferences error: {exc}")
        return {}


# ─── Helper: build full prompt context ────────────────────────────────────────


def build_context_prompt(session_id: str, num_messages: int = 5) -> str:
    """
    Convenience helper that combines get_context() and get_learned_preferences()
    into a ready-to-use system-prompt string for the AI model.

    Args:
        session_id   (str): Unique identifier for the user/session.
        num_messages (int): Recent messages to include.

    Returns:
        str: A formatted context block to prepend to your system prompt.
    """
    history = get_context(session_id, num_messages)
    prefs   = get_learned_preferences(session_id)

    lines = ["=== Conversation Memory ==="]

    if prefs:
        lines.append(f"User preferences: {json.dumps(prefs, ensure_ascii=False)}")

    if history:
        lines.append("Recent history:")
        for msg in history:
            role    = msg.get("role", "unknown").capitalize()
            content = msg.get("content", "")
            lines.append(f"  {role}: {content}")
    else:
        lines.append("No prior history found.")

    lines.append("===========================")
    return "\n".join(lines)
