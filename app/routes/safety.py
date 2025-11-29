from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Import AI modules
from app.ai.fraud_detector import detect_fraud
from app.ai.bot_detector import detect_bot
from app.ai.content_moderation import moderate_content


router = APIRouter()

# ----------- Request Models -----------

class SafetyCheckRequest(BaseModel):
    user_id: int | None = None
    message: str | None = None
    listing_title: str | None = None
    listing_description: str | None = None
    ip_address: str | None = None


# ----------- Endpoints -----------

@router.post("/check-content")
def check_content(request: SafetyCheckRequest):
    """
    Runs AI content moderation on user message or listing.
    """
    text = request.message or request.listing_description or ""
    result = moderate_content(text)

    return {
        "status": "ok",
        "moderation_result": result
    }


@router.post("/check-fraud")
def check_fraud(request: SafetyCheckRequest):
    """
    Checks for suspicious listing or user fraud patterns.
    """
    fraud_score = detect_fraud(
        user_id=request.user_id,
        title=request.listing_title,
        description=request.listing_description,
        ip=request.ip_address
    )

    return {
        "status": "ok",
        "fraud_score": fraud_score,
        "is_fraud": fraud_score > 0.75
    }


@router.post("/check-bot")
def check_bot(request: SafetyCheckRequest):
    """
    Detects if the user behavior looks like a bot.
    """
    bot_result = detect_bot(
        user_id=request.user_id,
        message=request.message,
        ip=request.ip_address
    )

    return {
        "status": "ok",
        "bot_result": bot_result,
        "is_bot": bot_result.get("score", 0) > 0.8
    }


@router.post("/full-scan")
def full_scan(request: SafetyCheckRequest):
    """
    Runs all AI detectors (fraud, bot, content moderation).
    """

    text = request.message or request.listing_description or ""

    mod = moderate_content(text)
    fraud = detect_fraud(request.user_id, request.listing_title, request.listing_description, request.ip_address)
    bot = detect_bot(request.user_id, request.message, request.ip_address)

    return {
        "status": "ok",
        "moderation": mod,
        "fraud_score": fraud,
        "is_fraud": fraud > 0.75,
        "bot_result": bot,
        "is_bot": bot.get("score", 0) > 0.8
    }
