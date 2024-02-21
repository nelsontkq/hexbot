

from app.config import Settings
import tweepy


def get_twitter_client(config: Settings) -> tweepy.Client:
    api = tweepy.Client(
        bearer_token=config.twitter_bearer_token,  
        # consumer_key=config.twitter_api_key,
        # consumer_secret=config.twitter_api_key_secret,
    )
    return api


async def process_youtube(title: str, link: str, config: Settings):
    # Initialize Twitter client
    api = get_twitter_client(config)

    # Create tweet content
    tweet_content = f"Received a new video: {title} - {link}"

    # Post tweet
    try:
        api.create_tweet(text=tweet_content)
        print("Tweet posted successfully.")
    except Exception as e:
        print("Error in posting tweet:", e)