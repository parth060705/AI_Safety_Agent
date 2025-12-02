
# import re

# # --------------------------------------------------
# # Word Lists
# # --------------------------------------------------

# PROFANITY = {
#     "fuck", "shit", "idiot", "stupid", "bitch", "asshole",
#     "damn", "bastard", "crap", "dumb", "idiotic", "slut", "whore",
#     "freak", "jerk","nigga", "moron", "ass", "prick", "douche", "twat"
# }

# HATE_SPEECH = {
#     "hate", "racist", "terrorist", "nazi",
#     "bigot", "xenophobe", "sexist", "homophobe", "islamophobe", "supremacist"
# }

# VIOLENCE = {
#     "kill", "murder", "attack", "blood",
#     "stab", "shoot", "burn", "destroy", "assault", "slaughter"
# }
# VIOLENCE_EMOJIS = {"🔪", "🗡️", "💣", "💥", "🔥", "⚔️"}

# NSFW_WORDS = {
#     "sex", "nude", "porn", "boobs", "dick", "pussy",
#     "cock", "tits", "hentai", "erotic", "fetish", "cum", "anal", "blowjob"
# }
# NSFW_EMOJIS = {"🍑", "🍆", "😈", "💦", "👅"}

# SCAM_WORDS = {
#     "urgent sale", "cheap price", "crypto only", "advance payment", "send payment",
#     "limited time offer", "win money", "get rich", "investment opportunity",
#     "pay upfront", "bank transfer only"
# }

# SPAM_PHRASES = {
#     "buy now", "free offer", "click here", "discount", "special deal",
#     "subscribe now", "share this", "act fast", "must watch", "exclusive deal"
# }

# # --------------------------------------------------
# # Helper Functions
# # --------------------------------------------------

# def normalize(text: str) -> str:
#     """Normalize: lowercase + remove symbols (f*ck → fuck)"""
#     text = text.lower()
#     return re.sub(r"[^a-z0-9\s]", " ", text)


# def word_match(text: str, words: set) -> bool:
#     """Match full tokens only — avoids false positives like 'assignment' → 'ass'"""
#     tokens = set(text.split())
#     return any(word in tokens for word in words)


# # --------------------------------------------------
# # Moderation Engine
# # --------------------------------------------------

# def moderate_content(text: str):
#     """Rule-based moderation system."""

#     raw_text = text
#     normalized = normalize(text)
#     score = 0.0
#     labels = []

#     # ---- Categories ----

#     if word_match(normalized, PROFANITY):
#         score += 0.30
#         labels.append("profanity")

#     if word_match(normalized, HATE_SPEECH):
#         score += 0.40
#         labels.append("hate_speech")

#     if word_match(normalized, VIOLENCE):
#         score += 0.35
#         labels.append("violence")

#     if any(e in raw_text for e in VIOLENCE_EMOJIS):
#         score += 0.20
#         labels.append("violence_emoji")

#     if word_match(normalized, NSFW_WORDS):
#         score += 0.45
#         labels.append("nsfw")

#     if any(e in raw_text for e in NSFW_EMOJIS):
#         score += 0.25
#         labels.append("nsfw_emoji")

#     for phrase in SCAM_WORDS:
#         if phrase in normalized:
#             score += 0.30
#             labels.append("scam")

#     for phrase in SPAM_PHRASES:
#         if phrase in normalized:
#             score += 0.20
#             labels.append("spam")

#     # ALL CAPS long messages → aggressive
#     if raw_text.isupper() and len(raw_text) > 10:
#         score += 0.10
#         labels.append("aggressive")

#     # Repeated characters → spam
#     if re.search(r"(.)\1{4,}", raw_text):
#         score += 0.20
#         labels.append("spam_repetition")

#     # Repeated emojis/symbols → spam
#     if re.search(r"([!?.🔥💦🍆🍑])\1{3,}", raw_text):
#         score += 0.15
#         labels.append("emoji_repetition")

#     # Cap score at 1.0
#     score = min(score, 1.0)

#     # ---- Decision ----
#     if score >= 0.10:
#         return {
#             "allowed": False,
#             "action": "block",
#             "labels": labels,
#             "score": score
#         }

#     return {
#         "allowed": True,
#         "action": "allow",
#         "labels": labels,
#         "score": score
#     }

import re
import csv

# --------------------------------------------------
# Word Lists (loaded dynamically from CSV)
# --------------------------------------------------

PROFANITY = set()
HATE_SPEECH = set()
VIOLENCE = set()
NSFW_WORDS = set()
SCAM_WORDS = set()
SPAM_PHRASES = set()

VIOLENCE_EMOJIS = {"🔪", "🗡️", "💣", "💥", "🔥", "⚔️"}
NSFW_EMOJIS = {"🍑", "🍆", "😈", "💦", "👅"}

# Load words from CSV
with open("app/csv/moderation_content.csv", newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        word = row['word'].strip().lower()
        category = row['category'].strip().lower()
        if category == "profanity":
            PROFANITY.add(word)
        elif category == "hate_speech":
            HATE_SPEECH.add(word)
        elif category == "violence":
            VIOLENCE.add(word)
        elif category == "nsfw":
            NSFW_WORDS.add(word)
        elif category == "scam":
            SCAM_WORDS.add(word)
        elif category == "spam":
            SPAM_PHRASES.add(word)

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

    # ALL CAPS long messages → aggressive
    if raw_text.isupper() and len(raw_text) > 10:
        score += 0.10
        labels.append("aggressive")

    # Repeated characters → spam
    if re.search(r"(.)\1{4,}", raw_text):
        score += 0.20
        labels.append("spam_repetition")

    # Repeated emojis/symbols → spam
    if re.search(r"([!?.🔥💦🍆🍑])\1{3,}", raw_text):
        score += 0.15
        labels.append("emoji_repetition")

    # Cap score at 1.0
    score = min(score, 1.0)

    # ---- Decision ----
    if score >= 0.10:
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
