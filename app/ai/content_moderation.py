BAD_WORDS = [
    "idiot", "stupid", "hate", "kill", 
    "sex", "nude", "scam", "fraud", "fuck", "shit",
]

SPAM_PATTERNS = ["buy now", "click here", "discount", "offer", "free free free"]

def moderate_content(text: str):
    """
    Returns:
    {
        "is_allowed": bool,
        "labels": [ ... ],
        "score": float   # 0 to 1 risk
    }
    """

    text = text.lower()
    labels = []
    score = 0

    # --- 1. Profanity detection ---
    if any(word in text for word in BAD_WORDS):
        score += 0.30
        labels.append("profanity")

    # --- 2. Spam detection ---
    for spam in SPAM_PATTERNS:
        if spam in text:
            score += 0.20
            labels.append("spam")

    # --- 3. NSFW or adult content ---
    if "sex" in text or "nude" in text:
        score += 0.40
        labels.append("adult")

    # --- 4. Violence ---
    if "kill" in text:
        score += 0.30
        labels.append("violence")

    # --- 5. All caps shouting ---
    if text.isupper() and len(text) > 10:
        score += 0.10
        labels.append("aggressive")

    # Finalize
    score = min(score, 1.0)

    return {
        "is_allowed": score < 0.75,
        "labels": labels,
        "score": score
    }
