from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.models import ModerationQueue, Artwork, Comment, Review, ArtistReview
from app.ai.content_moderation import moderate_content


MODEL_MAPPING = {
    "artworks": Artwork,
    "comments": Comment,
    "reviews": Review,
    "artist_reviews": ArtistReview
}


def extract_text(item, content_obj):
    """Extracts text depending on table type."""
    if item.table_name == "artworks":
        title = getattr(content_obj, "title", "") or ""
        description = getattr(content_obj, "description", "") or ""
        tags = getattr(content_obj, "tags", []) or []
        return f"{title} {description} {' '.join(tags)}"

    # Comments
    if item.table_name == "comments":
        return getattr(content_obj, "content", "") or ""

    # Reviews + Artist Reviews
    if item.table_name in ["reviews", "artist_reviews"]:
        return getattr(content_obj, "comment", "") or ""

    return ""


def process_moderation_queue():
    """Reads pending moderation items, evaluates them, updates DB."""
    db: Session = SessionLocal()

    try:
        pending_items = db.query(ModerationQueue).filter_by(checked=False).all()
        print(f"🔍 Pending moderation items: {pending_items}")

        if not pending_items:
            print("✔ No moderation items.")
            return

        for item in pending_items:

            # 1️⃣ Determine model
            ModelClass = MODEL_MAPPING.get(item.table_name)
            if not ModelClass:
                print(f"⚠️ Unknown table: {item.table_name}")
                item.checked = True
                db.commit()
                continue

            # 2️⃣ Fetch content row
            content_obj = db.query(ModelClass).filter_by(id=item.content_id).first()
            if not content_obj:
                print(f"❌ Content not found: {item.table_name}/{item.content_id}")
                item.checked = True
                db.commit()
                continue

            # 3️⃣ Extract text properly
            text_to_check = extract_text(item, content_obj)

            # 4️⃣ Run moderation
            result = moderate_content(text_to_check)
            print(f"🧠 Moderation result → {item.table_name}/{item.content_id}: {result}")

            # 5️⃣ Update content status based on moderation action
            content_obj.status = result["action"]  # allow / review / block

            # 6️⃣ Mark queue record as processed
            item.checked = True

            db.commit()

    finally:
        db.close()
