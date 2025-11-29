import re

# --- Word lists (expand later) ---
PROFANITY = ["fuck", "shit", "idiot", "stupid", "bitch", "asshole"]
HATE_SPEECH = ["hate", "racist", "terrorist", "nazi"]
VIOLENCE = ["kill", "murder", "attack", "blood"]
NSFW_WORDS = ["sex", "nude", "porn", "boobs", "dick", "pussy"]
SCAM_WORDS = ["urgent sale", "cheap price", "crypto only", "advance payment", "send payment"]
SPAM_WORDS = ["buy now", "free offer", "click here", "discount", "special deal"]

EMOJI_NSFW = ["🍑", "🍆", "😈"]
EMOJI_VIOLENCE = ["🔪", "🗡️", "💣"]

def moderate_content(text: str):
    """
    Returns a structured moderation result:
    {
        'allowed': True/False,
        'action': 'allow'/'review'/'block',
        'labels': [...],
        'score': 0-1
    }
    """

    text_l = text.lower()
    score = 0.0
    labels = []

    # --- 1. Profanity ---
    if any(w in text_l for w in PROFANITY):
        score += 0.30
        labels.append("profanity")

    # --- 2. Hate speech ---
    if any(w in text_l for w in HATE_SPEECH):
        score += 0.40
        labels.append("hate_speech")

    # --- 3. Violence ---
    if any(w in text_l for w in VIOLENCE):
        score += 0.35
        labels.append("violence")

    # --- 4. NSFW / Sexual ---
    if any(w in text_l for w in NSFW_WORDS):
        score += 0.45
        labels.append("nsfw")

    if any(e in text for e in EMOJI_NSFW):
        score += 0.25
        labels.append("nsfw_emoji")

    # --- 5. Scam / Fraud ---
    if any(w in text_l for w in SCAM_WORDS):
        score += 0.30
        labels.append("scam")

    # --- 6. Spam ---
    if any(w in text_l for w in SPAM_WORDS):
        score += 0.20
        labels.append("spam")

    # --- 7. All caps shouting ---
    if text.isupper() and len(text) > 10:
        score += 0.10
        labels.append("aggressive")

    # --- 8. Repeated characters (spam) ---
    if re.search(r"(.)\1{4,}", text):
        score += 0.20
        labels.append("spam_repetition")

    # --- Final score ---
    score = min(score, 1.0)

    # --- Decision ---
    if score >= 0.75:
        action = "block"
        allowed = False
    elif 0.40 <= score < 0.75:
        action = "review"
        allowed = False
    else:
        action = "allow"
        allowed = True

    return {
        "allowed": allowed,
        "action": action,
        "labels": labels,
        "score": score
    }
