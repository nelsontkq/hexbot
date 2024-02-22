from fastapi.testclient import TestClient
from app.main import app  # Import your FastAPI app
from unittest.mock import patch

client = TestClient(app)

def test_twitter_oauth_flow():
    with patch('tweepy.OAuth1UserHandler.get_authorization_url') as mock_auth_url:
        mock_auth_url.return_value = "https://mocked.url"
        response = client.get("/twitter")
        assert response.status_code == 200
        assert "https://mocked.url" in response.json()["url"]

def test_youtube_subscription_verification():
    # Simulating YouTube's subscription verification request
    response = client.post("/youtube/hook", data={
        'hub.mode': 'subscribe',
        'hub.challenge': 'test_challenge'
    })
    assert response.status_code == 200
    assert response.content == b'test_challenge'

def test_youtube_notification_handling():
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
    response = client.post("/youtube/hook", data=xml_data, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Received"}
