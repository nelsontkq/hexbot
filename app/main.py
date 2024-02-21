from functools import lru_cache
from typing import Annotated, Union
from discord import HTTPException

from fastapi import Depends, FastAPI, Request, Response
from . import config, bot
import xml.etree.ElementTree as ET
import tweepy

app = FastAPI()


@lru_cache
def get_settings():
    return config.Settings()


@app.get("/twitter")
async def twitter(settings: config.Settings = Depends(get_settings)):
    auth = tweepy.OAuth1UserHandler(
        settings.twitter_api_key, settings.twitter_api_key_secret
    )
    try:
        # Get the authorization URL for the user to complete the OAuth flow
        redirect_url = auth.get_authorization_url()
        return {"url": redirect_url}
    except tweepy.TweepyException as e:
        return {"error": str(e)}

@app.get("/twitter/callback")
async def twitter_oauth(token: str, verifier: str, settings: config.Settings = Depends(get_settings)):
    auth = tweepy.OAuth1UserHandler(
        settings.twitter_api_key, settings.twitter_api_key_secret
    )
    auth.request_token = {'oauth_token': token, 'oauth_token_secret': verifier}
    try:
        # Get the access token and access token secret
        auth.access_token, auth.access_token_secret = auth.get_access_token(verifier)
        return {"access_token": auth.access_token, "access_token_secret": auth.access_token_secret}
    except tweepy.TweepyException as e:
        return {"error": str(e)}

@app.post("/youtube/hook")
async def youtube_hook(request: Request, settings: config.Settings = Depends(get_settings)):
    # Extract the content type of the request
    content_type = request.headers.get('content-type')

    # YouTube sends a verification request with 'hub.challenge' parameter when you first set up the webhook
    # This block handles the verification of the subscription
    if 'application/x-www-form-urlencoded' in content_type:
        form_data = await request.form()
        hub_mode = form_data.get('hub.mode')
        hub_challenge = form_data.get('hub.challenge')

        if hub_mode == 'subscribe' and hub_challenge:
            return Response(content=hub_challenge, media_type='text/plain')

    # Handling YouTube notification
    else:
        body = await request.body()
        try:
            # Parse the XML data
            root = ET.fromstring(body)

            # Extract data from the XML. Here's an example to get the video title and link.
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                title = entry.find('{http://www.w3.org/2005/Atom}title').text
                link = entry.find('{http://www.w3.org/2005/Atom}link').attrib['href']

                await bot.process_youtube(title, link, settings)

        except ET.ParseError:
            raise HTTPException(status_code=400, detail="Invalid XML format")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    return {"message": "Received"}