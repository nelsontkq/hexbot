from apscheduler.schedulers.background import BackgroundScheduler
from app.db import get_users_to_resub
from app.youtube import resubscribe

scheduler = BackgroundScheduler()

def init_scheduler():
    scheduler.add_job(check_subscriptions, "interval", hours=24)
    scheduler.start()


async def check_subscriptions():
    resub_jobs = get_users_to_resub()

    for user in resub_jobs:
        try:
            await resubscribe(user.hub_topic)
        except Exception as e:
            print(f"Error resubscribing user {user.user}: {e}")