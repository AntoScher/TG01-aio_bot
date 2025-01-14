from googleapiclient.discovery import build
import os

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

request = youtube.search().list(
    q='painter zverev',
    part='snippet',
    maxResults=1
)
response = request.execute()
print(response)
