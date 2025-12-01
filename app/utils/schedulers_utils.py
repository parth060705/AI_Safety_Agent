from apscheduler.schedulers.background import BackgroundScheduler
from app.crud.safety_crud import process_moderation_queue

scheduler = BackgroundScheduler()

def start_scheduler():
    """
    Starts the background scheduler that runs every 10 hours.
    """
    # scheduler.add_job(process_moderation_queue, "interval", hours=2)
    scheduler.add_job(process_moderation_queue, "interval", seconds=10) 
    scheduler.start()
    print("🔄 AI Safety Scheduler Started (runs every 10 sec)")
