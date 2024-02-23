import asyncio
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

import pytest
from sqlmodel import SQLModel
from app.config import settings
from app.db import engine
from app.main import app  # Import your FastAPI app

@pytest.fixture(scope="module")
def client():
    SQLModel.metadata.create_all(engine)

    with TestClient(app) as client:
        yield client

    # Teardown: Drop tables
    SQLModel.metadata.drop_all(engine)
        
        

def test_youtube_invalid_verify_token(client: TestClient):
    # Simulating YouTube's subscription verification request
    response = client.get("/youtube/hook", params={
        'hub.mode': 'subscribe',
        'hub.challenge': 'test_challenge',
        'hub.verify_token': 'test_token',
        'hub.lease_seconds': '864000',
        'hub.topic': 'test_topic',
    })
    assert response.status_code == 403

@patch('app.config.settings.youtube_verify_token', 'test_token')
def test_youtube_valid_verify_token(client: TestClient):
    response = client.get("/youtube/hook", params={
        'hub.mode': 'subscribe',
        'hub.challenge': 'test_challenge',
        'hub.verify_token': 'test_token',
        'hub.lease_seconds': '864000',
        'hub.topic': 'test_topic',
    })
    assert response.status_code == 200
    assert response.text == 'test_challenge'

def test_youtube_notification_handling(client: TestClient):
    # Simulating a YouTube notification
    xml_data = """
    <feed xmlns:yt="http://www.youtube.com/xml/schemas/2015"
            xmlns="http://www.w3.org/2005/Atom">
    <link rel="hub" href="https://pubsubhubbub.appspot.com"/>
    <link rel="self" href="https://www.youtube.com/xml/feeds/videos.xml?channel_id=CHANNEL_ID"/>
    <title>YouTube video feed</title>
    <updated>2015-04-01T19:05:24.552394234+00:00</updated>
    <entry>
        <id>yt:video:VIDEO_ID</id>
        <yt:videoId>VIDEO_ID</yt:videoId>
        <yt:channelId>CHANNEL_ID</yt:channelId>
        <title>Video title</title>
        <link rel="alternate" href="http://www.youtube.com/watch?v=VIDEO_ID"/>
        <author>
        <name>Channel title</name>
        <uri>http://www.youtube.com/channel/CHANNEL_ID</uri>
        </author>
        <published>2015-03-06T21:40:57+00:00</published>
        <updated>2015-03-09T19:05:24.552394234+00:00</updated>
    </entry>
    </feed>
    """
    headers = {'content-type': 'application/atom+xml'}
    response = client.post("/youtube/hook", content=xml_data, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Received"}


@patch('app.main.get_user')
@patch('aiohttp.ClientSession.post')
def test_youtube_resubscribe_user_found(mock_post, mock_get_user, client: TestClient):
        # Mock the response from YouTube
    mock_resp = MagicMock()
    mock_resp.status = 200  # Set to the expected status code
    mock_resp.text = MagicMock(return_value=asyncio.Future())
    mock_resp.text.return_value.set_result('Success')  # Set the expected response text
    mock_post.return_value.__aenter__.return_value = mock_resp
    mock_user = MagicMock()
    mock_user.hub_topic = 'test_topic'
    mock_get_user.return_value = mock_user

    # Test
    response = client.post("/youtube/resubscribe")
    assert response.status_code == 200
    assert response.json() == {"message": "Resubscribed"}


@patch('app.main.get_user')
@patch('aiohttp.ClientSession.post')
def test_youtube_resubscribe_user_not_found(mock_post, mock_get_user, client: TestClient):
        # Mock the response from YouTube
    mock_resp = MagicMock()
    mock_resp.status = 200  # Set to the expected status code
    mock_resp.text = MagicMock(return_value=asyncio.Future())
    mock_resp.text.return_value.set_result('Success')  # Set the expected response text
    mock_post.return_value.__aenter__.return_value = mock_resp
    mock_user = MagicMock()
    mock_user.hub_topic = 'test_topic'
    mock_get_user.return_value = None
    response = client.post("/youtube/resubscribe")
    assert response.status_code == 200
    assert response.json() == {"message": "User not found"}