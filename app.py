from flask import Flask, request
import requests
import os
import re
import yt_dlp

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TOKEN}/'

app = Flask(__name__)

def send_message(chat_id, text):
    url = TELEGRAM_API_URL + 'sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    requests.post(url, json=payload)

def send_video(chat_id, video_path):
    url = TELEGRAM_API_URL + 'sendVideo'
    files = {'video': open(video_path, 'rb')}
    payload = {
        'chat_id': chat_id
    }
    requests.post(url, data=payload, files=files)

def download_video(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloaded_video.%(ext)s',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_path = ydl.prepare_filename(info_dict)
    return video_path

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.json

    if 'message' in update:
        chat_id = update['message']['chat']['id']
        text = update['message']['text']

        if text.lower() == '/start':
            send_message(chat_id, 'Welcome! Send me a message containing a valid video link.')

        else:
            # Check if the text contains a valid URL
            url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            match = re.search(url_pattern, text)
            
            if match:
                video_url = match.group()
                try:
                    video_path = download_video(video_url)
                    send_video(chat_id, video_path)
                    os.remove(video_path)  # Clean up after sending the video
                except Exception as e:
                    send_message(chat_id, f'Failed to download or send the video: {e}')
            else:
                send_message(chat_id, 'Not a valid link. Send a valid video link.')

    return 'OK'

@app.route('/')
def index():
    return "The bot is running..."

if __name__ == '__main__':
    app.run(port=8080)
