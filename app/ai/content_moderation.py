import re

# --------------------------------------------------
# Word Lists
# --------------------------------------------------

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

SPAM_PHRASES = {
    "buy now",
    "free offer",
    "click here",
    "discount",
    "special deal"
}

NSFW_EMOJIS = {"🍑", "🍆", "😈"}
VIOLENCE_EMOJIS = {"🔪", "🗡️", "💣"}


# --------------------------------------------------
# Helper Functions
# --------------------------------------------------

def normalize(text: str) -> str:
    """Normalize: lowercase + remove symbols (f*ck → fuck)"""
    text = text.lower()
    return re.sub(r"[^a-z0-9\s]", " ", text)


def word_match(text: str, words: set) -> bool:
    """Match full tokens only — avoids false positives like 'assignment' → 'ass'"""
    tokens = set(text.split())
    return any(word in tokens for word in words)


# --------------------------------------------------
# Moderation Engine
# --------------------------------------------------

def moderate_content(text: str):
    """Rule-based moderation system."""

    raw_text = text
    normalized = normalize(text)
    score = 0.0
    labels = []

    # ---- Categories ----

    if word_match(normalized, PROFANITY):
        score += 0.30
        labels.append("profanity")

    if word_match(normalized, HATE_SPEECH):
        score += 0.40
        labels.append("hate_speech")

    if word_match(normalized, VIOLENCE):
        score += 0.35
        labels.append("violence")

    if any(e in raw_text for e in VIOLENCE_EMOJIS):
        score += 0.20
        labels.append("violence_emoji")

    if word_match(normalized, NSFW_WORDS):
        score += 0.45
        labels.append("nsfw")

    if any(e in raw_text for e in NSFW_EMOJIS):
        score += 0.25
        labels.append("nsfw_emoji")

    for phrase in SCAM_WORDS:
        if phrase in normalized:
            score += 0.30
            labels.append("scam")

    for phrase in SPAM_PHRASES:
        if phrase in normalized:
            score += 0.20
            labels.append("spam")

    if raw_text.isupper() and len(raw_text) > 10:
        score += 0.10
        labels.append("aggressive")

    if re.search(r"(.)\1{4,}", raw_text):
        score += 0.20
        labels.append("spam_repetition")

    score = min(score, 1.0)

    # ---- Decision ----
    if score >= 0.40:
        return {
            "allowed": False,
            "action": "block",
            "labels": labels,
            "score": score
        }

    return {
        "allowed": True,
        "action": "allow",
        "labels": labels,
        "score": score
    }
