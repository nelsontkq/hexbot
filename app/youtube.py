import aiohttp
from app.config import settings


async def resubscribe(topic: str):
    print(f"Resubscribing to {topic}")
    async with aiohttp.ClientSession() as session:
        data = {
            "hub.callback": f"{settings.base_url}/youtube/hook",
            "hub.mode": "subscribe",
            "hub.topic": topic,
            "hub.verify": "async",
            "hub.verify_token": settings.youtube_verify_token,
        }
        print(data)
        async with session.post(
            "https://pubsubhubbub.appspot.com/subscribe",
            data=data,
        ) as resp:
            if resp.ok:
                print(f"Resubscribed to {topic}")
            else:
                raise Exception(
                    f"Failed to resubscribe to {topic} with status {resp.status}: {await resp.text()}"
                )
