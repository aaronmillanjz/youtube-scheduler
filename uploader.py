from googleapiclient.http import MediaFileUpload
from service import Create_Service
from scheduler import next_schedule_time, find_latest_date
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

CLIENT_SECRET_FILE = 'client_secret.json'
API_NAME = 'youtube'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
current_scheduled_time = []
        
service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, scopes=["https://www.googleapis.com/auth/youtube.readonly"])

credentials = flow.run_local_server(port=8080)
youtube = build("youtube", "v3", credentials=credentials)

# Retrieve channel information
channel_response = youtube.channels().list(
    mine=True,
    part='contentDetails'
).execute()

# Extract the upload playlist ID from the channel response
uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

# Now use this ID to get videos from the 'uploads' playlist
playlistitems_response = youtube.playlistItems().list(
    playlistId=uploads_playlist_id,
    part="snippet,contentDetails",
    maxResults=25
).execute()

# Process the playlist items as needed

for item in playlistitems_response['items']:
    video_id = item['contentDetails']['videoId']
    video_response = youtube.videos().list(
        part="snippet,contentDetails,status",
        id=video_id
    ).execute()

    #Get Last Scheduled Video
    status = video_response['items'][0]['status'] 
    if status['privacyStatus'] == 'private' and 'publishAt' in status:
        #print(f"Title: {video['snippet']['title']}")
        #print(f"Scheduled Time: {status['publishAt']}")
        current_scheduled_time.append(status['publishAt'])
        print(current_scheduled_time)
    
video_title = input("Enter the video title: ")
video_tags = input("Enter the video tags (comma-separated): ").split(',')

#upload_date_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
upload_date_time = next_schedule_time(find_latest_date(current_scheduled_time))
print(upload_date_time)
request_body = {
    'id': video_id,
    'snippet': {
        'categoryId': 24,
        'title': video_title,
        'description': '',
        'tags': video_tags
    },
    'status': {
        'privacyStatus': 'private',
        'publishAt': upload_date_time,
        'selfDeclaredMadeForKids': False,
    }
}
mediaFile = MediaFileUpload('to_upload/ditch.mp4',
                            chunksize=1024*1024, resumable=True)

response_upload = service.videos().insert(
    part='snippet,status',
    body=request_body,
    media_body=mediaFile
)


response = None
while response is None:
    status, response = response_upload.next_chunk()
    if status:
        print("Uploaded %d%%." % int(status.progress() * 100))

print("Upload Complete!")
