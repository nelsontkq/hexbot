

from app.config import Settings
import tweepy

from app.db import TwitterUser


def get_twitter_client(config: Settings, user: TwitterUser) -> tweepy.Client:
    api = tweepy.Client(
        consumer_key=config.twitter_api_key,
        consumer_secret=config.twitter_api_key_secret,
        access_token=user.access_token,
        access_token_secret=user.access_token_secret
    )
    return api


async def process_youtube(title: str, link: str, config: Settings, user: TwitterUser):
    # Initialize Twitter client
    api = get_twitter_client(config, user)

    # Post tweet
    try:
        api.create_tweet(text=f"""🚨 New Video 🚨

Check out my latest video over on YouTube
                         
{link}

Hex 👋

#mtgmkm #mtgkarlov #mtg""")
        print("Tweet posted successfully.")
    except Exception as e:
        print("Error in posting tweet:", e)