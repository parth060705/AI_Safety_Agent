import re


# -------------------------
# Normalized Word Lists
# -------------------------

PROFANITY = {"fuck", "shit", "idiot", "stupid", "bitch", "asshole"}
HATE_SPEECH = {"hate", "racist", "terrorist", "nazi"}
VIOLENCE = {"kill", "murder", "attack", "blood"}
NSFW_WORDS = {"sex", "nude", "porn", "boobs", "dick", "pussy"}

SCAM_WORDS = {
    "urgent sale",
    "cheap price",
    "crypto only",
    "advance payment",
    "send payment"
}

SPAM_PHRASES = {"buy now", "free offer", "click here", "discount", "special deal"}

NSFW_EMOJIS = {"🍑", "🍆", "😈"}
VIOLENCE_EMOJIS = {"🔪", "🗡️", "💣"}


# -------------------------
# Helper Functions
# -------------------------

def normalize(text: str):
    """Normalizes text by removing symbols (f*ck → fuck)."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)  # remove symbols
    return text


def word_match(text, words):
    """Ensures only full-word matches (prevents 'assignment' → ass)."""
    tokens = text.split()
    return any(w in tokens for w in words)


# -------------------------
# Main Moderation Function
# -------------------------

def moderate_content(text: str):
    """Safely evaluates content using rule-based scoring."""

    raw_text = text
    text = normalize(text)
    score = 0.0
    labels = []

    # ---- Profanity ----
    if word_match(text, PROFANITY):
        score += 0.30
        labels.append("profanity")

    # ---- Hate Speech ----
    if word_match(text, HATE_SPEECH):
        score += 0.40
        labels.append("hate_speech")

    # ---- Violence ----
    if word_match(text, VIOLENCE):
        score += 0.35
        labels.append("violence")

    if any(e in raw_text for e in VIOLENCE_EMOJIS):
        score += 0.20
        labels.append("violence_emoji")

    # ---- NSFW ----
    if word_match(text, NSFW_WORDS):
        score += 0.45
        labels.append("nsfw")

    if any(e in raw_text for e in NSFW_EMOJIS):
        score += 0.25
        labels.append("nsfw_emoji")

    # ---- Scam detection ----
    for phrase in SCAM_WORDS:
        if phrase in text:
            score += 0.30
            labels.append("scam")

    # ---- Spam detection ----
    for phrase in SPAM_PHRASES:
        if phrase in text:
            score += 0.20
            labels.append("spam")

    # ---- ALL CAPS ----
    if raw_text.isupper() and len(raw_text) > 10:
        score += 0.10
        labels.append("aggressive")

    # ---- Character repetition (spammy) ----
    if re.search(r"(.)\1{4,}", raw_text):
        score += 0.20
        labels.append("spam_repetition")

    # Limit score
    score = min(score, 1.0)

    # ---- Final Decision ----
    if score >= 0.75:
        action = "block"
        allowed = False
    elif score >= 0.40:
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
