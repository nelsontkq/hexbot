import requests
from sqlmodel import Session
from app.config import Settings, settings
import tweepy

from app.db import TwitterUser, get_create_post, get_on_youtube_post


def get_twitter_client(config: Settings, user: TwitterUser) -> tweepy.Client:
    api = tweepy.Client(
        consumer_key=config.twitter_api_key,
        consumer_secret=config.twitter_api_key_secret,
        access_token=user.access_token,
        access_token_secret=user.access_token_secret
    )
    return api


async def process_youtube(session: Session, title: str, link: str, config: Settings, user: TwitterUser):
    # Initialize Twitter client
    api = get_twitter_client(config, user)
    _, is_newly_created = get_create_post(session, link)
    if not is_newly_created:
        print("Tweet already posted.")
        return
    post_text = get_on_youtube_post(session, title, link, settings.default_user)
    if not post_text:
        print("No post text saved.")
        return
    try:
        print(f"Posting youtube tweet...")
        response = api.create_tweet(text=post_text)
        try:
            if isinstance(response, requests.models.Response):
                print(f"{response.status_code}: {response.text}")
            elif isinstance(response, tweepy.Response):
                print(f"{response.data} {response.errors}")
            else:
                print(response)
        except Exception as e:
            print(e)
    except Exception as e:
        print("Error in posting tweet:", e)