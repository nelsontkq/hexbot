from apscheduler.schedulers.background import BackgroundScheduler
from app.db import get_users_to_resub, get_session
from app.youtube import resubscribe
import asyncio

scheduler = BackgroundScheduler()

def init_scheduler():
    scheduler.add_job(lambda: asyncio.run(check_subscriptions()), "interval", hours=24)
    scheduler.start()


async def check_subscriptions():
    resub_jobs = get_users_to_resub(get_session())

    for user in resub_jobs:
        try:
            await resubscribe(user.hub_topic)
        except Exception as e:
            print(f"Error resubscribing user {user.user}: {e}")
