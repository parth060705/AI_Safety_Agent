import re
import time
import csv
from collections import defaultdict

# ==================================================
# BOT DETECTION LISTS (Loaded from CSV)
# ==================================================

BOT_PHRASES = set()
EMOJI_SPAM = set()

def load_bot_csv():
    """Safely load bot detection phrases & emojis."""
    path = "app/csv/bot_moderation.csv"

    try:
        with open(path, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(
                filter(lambda row: row.strip() and not row.startswith("#"), file)
            )

            for row in reader:
                category = row.get("category")
                word = row.get("word")

                if not category or not word:
                    continue

                category = category.strip().lower()
                word = word.strip().lower()

                if category == "bot_phrase":
                    BOT_PHRASES.add(word)

                elif category == "emoji_spam":
                    EMOJI_SPAM.add(word)

    except FileNotFoundError:
        print(f"[ERROR] CSV not found: {path}")
    except Exception as e:
        print(f"[ERROR] CSV load failed: {e}")

# Load CSV immediately
load_bot_csv()


# ==================================================
# USER MESSAGE SPEED DATA
# ==================================================

USER_ACTIVITY = defaultdict(list)

def record_message(user_id: str):
    """Track timestamps of messages, detect bots sending too fast."""
    now = time.time()
    USER_ACTIVITY[user_id].append(now)

    if len(USER_ACTIVITY[user_id]) > 10:
        USER_ACTIVITY[user_id] = USER_ACTIVITY[user_id][-10:]


def is_sending_too_fast(user_id: str) -> bool:
    """Detect if 5+ messages within 3 seconds."""
    timestamps = USER_ACTIVITY[user_id]
    if len(timestamps) < 5:
        return False

    return (timestamps[-1] - timestamps[0]) < 3


# ==================================================
# TEXT CHECKS
# ==================================================

def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9\s]", " ", text.lower())


def detect_repetitive_pattern(text: str) -> bool:
    return bool(re.search(r"(.)\1{6,}", text))


def detect_emoji_spam(text: str) -> bool:
    for emoji in EMOJI_SPAM:
        if text.count(emoji) >= 5:
            return True
    return False


def detect_bot_phrases(normalized: str) -> bool:
    return any(phrase in normalized for phrase in BOT_PHRASES)


# ==================================================
# MAIN BOT DETECTION ENGINE
# ==================================================

def bot_detector(user_id: str, text: str):
    """Returns bot detection result."""

    raw = text
    normalized = normalize(text)

    score = 0.0
    labels = []

    # Speed detection
    record_message(user_id)
    if is_sending_too_fast(user_id):
        score += 0.40
        labels.append("bot_speed")

    # Repetitive spam
    if detect_repetitive_pattern(raw):
        score += 0.30
        labels.append("repetitive_text")

    # Emoji spam
    if detect_emoji_spam(raw):
        score += 0.25
        labels.append("emoji_spam")

    # Message contains known bot phrases
    if detect_bot_phrases(normalized):
        score += 0.35
        labels.append("bot_phrase")

    # All caps
    if raw.isupper() and len(raw) > 8:
        score += 0.10
        labels.append("all_caps")

    score = min(score, 1.0)

    # Final decision
    if score >= 0.40:
        return {
            "is_bot": True,
            "action": "flag",
            "score": score,
            "labels": labels
        }

    return {
        "is_bot": False,
        "action": "allow",
        "score": score,
        "labels": labels
    }
