import re
from datetime import datetime

def detect_bot(user_id: int | None, message: str | None, ip: str | None):
    """
    Returns bot detection information:
    { "score": float, "reason": "string" }
    """

    score = 0.0
    reason = []

    # --- 1. Repetition detection ---
    if message:
        if len(set(message.split())) <= 2:  # e.g. "hello hello hello"
            score += 0.40
            reason.append("Repeated words")

        if message.isupper():
            score += 0.20
            reason.append("Excessive capitalization")

        if re.search(r"(.)\1{4,}", message):  # e.g. "hellooooo"
            score += 0.15
            reason.append("Character spam")

    # --- 2. IP pattern detection ---
    if ip and (ip.startswith("172.") or ip.startswith("192.168.")):
        score += 0.10
        reason.append("Private/hidden IP pattern")

    # --- 3. Very short time between messages (simulated) ---
    # Normally you'd check last message timestamps from database.
    # Here we simulate a probability.
    from random import random
    if random() > 0.85:
        score += 0.15
        reason.append("Unusually fast messaging behavior")

    return {
        "score": min(score, 1.0),
        "reason": ", ".join(reason) or "Normal activity"
    }
