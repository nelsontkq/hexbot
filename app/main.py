import datetime
from functools import lru_cache
from discord import HTTPException
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from app import bot
from app.config import settings
import xml.etree.ElementTree as ET
import tweepy

from app.db import get_user, init_db, create_update_user

app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) 

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    
# templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root():
    return Response(content="<h1>Youtube to Twitter</h1><a href=\"/twitter\">authenticate with Twitter</a>", media_type='text/html')

@app.get("/twitter")
async def twitter():
    auth = tweepy.OAuth1UserHandler(
        settings.twitter_api_key, settings.twitter_api_key_secret
    )
    try:
        # Get the authorization URL for the user to complete the OAuth flow
        redirect_url = auth.get_authorization_url()
        
        return RedirectResponse(url=redirect_url)
    except tweepy.TweepyException as e:
        print({"error": str(e)})

@app.get("/twitter/callback")
async def twitter_oauth(oauth_token: str, oauth_verifier: str):
    auth = tweepy.OAuth1UserHandler(
        settings.twitter_api_key, settings.twitter_api_key_secret
    )
    auth.request_token = {'oauth_token': oauth_token, 'oauth_token_secret': oauth_verifier}
    try:
        # Get the access token and access token secret
        auth.access_token, auth.access_token_secret = auth.get_access_token(oauth_verifier)
        
        create_update_user(settings.default_user, auth.access_token, auth.access_token_secret)
        return Response(content="<p>User updated successfully</p>", media_type='text/html')
    except tweepy.TweepyException as e:
        print({"error": str(e)})


# @app.get("/update_template")
# async def update_template():
#     return Response(content="<form method=\"post\"><input type=\"text\" name=\"template\" placeholder=\"Template\"><input type=\"submit\" value=\"Submit\"></form>", media_type='text/html')
@app.get("/youtube/hook")
async def youtube_hook(request: Request):
    # Extract the content type of the request
    content_type = request.headers.get('content-type')

    # YouTube sends a verification request with 'hub.challenge' parameter when you first set up the webhook
    # This block handles the verification of the subscription
    if 'application/x-www-form-urlencoded' in content_type:
        form_data = await request.form()
        hub_mode = form_data.get('hub.mode')
        hub_challenge = form_data.get('hub.challenge')
        print(form_data)
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
                published = entry.find('{http://www.w3.org/2005/Atom}published').text
                link = entry.find('{http://www.w3.org/2005/Atom}link').attrib['href']
                
                # if published greater than 12 hours ago, ignore
                published_iso_date = datetime.datetime.fromisoformat(published).replace(tzinfo=None)
                if (datetime.datetime.utcnow() - published_iso_date).total_seconds() > 43200:
                    print("Ignoring video published more than 12 hours ago")
                    continue
                
                await bot.process_youtube(title, link, published, settings, get_user(settings.default_user))

        except ET.ParseError:
            raise HTTPException(status_code=400, detail="Invalid XML format")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    return {"message": "Received"}