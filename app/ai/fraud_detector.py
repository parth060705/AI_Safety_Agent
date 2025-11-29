import re
from datetime import datetime, timedelta

# Example risky keywords
RISKY_KEYWORDS = [
    "cheap price", "urgent sale", "send payment", "western union",
    "bank transfer only", "advance payment", "no returns", "crypto only"
]

def detect_fraud(user_id: int | None, title: str | None, description: str | None, ip: str | None):
    """
    Returns a fraud score between 0 and 1.
    Fraud score above 0.75 = high risk.
    """

    score = 0.0
    text = f"{title or ''} {description or ''}".lower()

    # --- 1. Keyword-based scam detection ---
    for keyword in RISKY_KEYWORDS:
        if keyword in text:
            score += 0.15

    # --- 2. Too-cheap pricing pattern (if number detected) ---
    match = re.search(r"\b\d{1,4}\b", text)
    if match:
        price = int(match.group())
        if price <= 50:
            score += 0.20

    # --- 3. Suspicious behavior from IP ---
    if ip and ip.startswith("10."):   # Example internal/proxy IP range
        score += 0.10

    # --- 4. Very short descriptions ---
    if description and len(description) < 20: 
        score += 0.10

    # --- 5. ALL CAPS title ---
    if title and title.isupper():
        score += 0.10

    # --- Final Score ---
    return min(score, 1.0)
