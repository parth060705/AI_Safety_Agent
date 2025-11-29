from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db

# Import AI modules
from app.ai.fraud_detector import detect_fraud
from app.ai.bot_detector import detect_bot
from app.ai.content_moderation import moderate_content

# Import models
from app.models.models import Comment, Review, Artwork

router = APIRouter()

# ----------- Request Models -----------

class SafetyCheckRequest(BaseModel):
    user_id: int | None = None
    message: str | None = None
    listing_title: str | None = None
    listing_description: str | None = None
    ip_address: str | None = None

class ModerationDBRequest(BaseModel):
    content_type: str  # comment | review | listing
    content_id: str    # uuid of the row


# ----------- Endpoints -----------

@router.post("/check-db-content")
def check_db_content(request: ModerationDBRequest, db: Session = Depends(get_db)):

    # -------- COMMENT MODERATION --------
    if request.content_type == "comment":
        comment = db.query(Comment).filter(Comment.id == request.content_id).first()
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        text = comment.content


    # -------- REVIEW MODERATION --------
    elif request.content_type == "review":
        review = db.query(Review).filter(Review.id == request.content_id).first()
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        text = review.comment or ""


    # -------- LISTING MODERATION --------
    elif request.content_type == "listing":
        listing = db.query(Artwork).filter(Artwork.id == request.content_id).first()
        if not listing:
            raise HTTPException(status_code=404, detail="Listing not found")

        # Combine all listing text fields for moderation
        text = (
            (listing.title or "") + " " +
            (listing.description or "") + " " +
            " ".join(listing.tags or [])
        )

    else:
        raise HTTPException(status_code=400, detail="Invalid content type")

    # Run moderation AI model
    result = moderate_content(text)

    return {
        "status": "ok",
        "content_type": request.content_type,
        "content_id": request.content_id,
        "input_text": text,
        "moderation_result": result
    }

# @router.post("/full-scan")
# def full_scan(request: SafetyCheckRequest):
#     """
#     Runs all AI detectors (fraud, bot, content moderation).
#     """

#     text = request.message or request.listing_description or ""

#     mod = moderate_content(text)
#     fraud = detect_fraud(request.user_id, request.listing_title, request.listing_description, request.ip_address)
#     bot = detect_bot(request.user_id, request.message, request.ip_address)

#     return {
#         "status": "ok",
#         "moderation": mod,
#         "fraud_score": fraud,
#         "is_fraud": fraud > 0.75,
#         "bot_result": bot,
#         "is_bot": bot.get("score", 0) > 0.8
#     }

#-------------------------------------------------------------
# @router.post("/check-fraud")
# def check_fraud(request: SafetyCheckRequest):
#     """
#     Checks for suspicious listing or user fraud patterns.
#     """
#     fraud_score = detect_fraud(
#         user_id=request.user_id,
#         title=request.listing_title,
#         description=request.listing_description,
#         ip=request.ip_address
#     )

#     return {
#         "status": "ok",
#         "fraud_score": fraud_score,
#         "is_fraud": fraud_score > 0.75
#     }


# @router.post("/check-bot")
# def check_bot(request: SafetyCheckRequest):
#     """
#     Detects if the user behavior looks like a bot.
#     """
#     bot_result = detect_bot(
#         user_id=request.user_id,
#         message=request.message,
#         ip=request.ip_address
#     )

#     return {
#         "status": "ok",
#         "bot_result": bot_result,
#         "is_bot": bot_result.get("score", 0) > 0.8
#     }


