from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routes import safety   # You can add/remove as needed
# from app.routes import users, safety, listings   # You can add/remove as needed
from app.utils.schedulers_utils import start_scheduler

app = FastAPI(
    title="Social Marketplace AI Safety Agent",
    description="Fraud detection, content moderation, and bot detection AI service.",
    version="1.0.0"
)

# ---------------------------
# CORS (Allow mobile apps / web)
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Root endpoint
# ---------------------------
@app.get("/")
def home():
    return {"message": "AI Safety Agent is running."}


# Start scheduled moderation checks
start_scheduler()

# ---------------------------
# Routers (modular API)
# ---------------------------
# app.include_router(users.router, prefix="/users", tags=["Users"])
# app.include_router(listings.router, prefix="/listings", tags=["Listings"])
app.include_router(safety.router, prefix="/safety", tags=["AI Safety"])

