from flask import Flask, request
import requests
import os
import re

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

def send_photo(chat_id, photo_url):
    url = TELEGRAM_API_URL + 'sendPhoto'
    payload = {
        'chat_id': chat_id,
        'photo': photo_url
    }
    requests.post(url, json=payload)

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.json

    if 'message' in update:
        chat_id = update['message']['chat']['id']
        text = update['message']['text']

        if text.lower() == '/start':
            send_message(chat_id, 'Welcome! Send me a message containing a valid photo link.')

        else:
            # Check if the text contains a valid URL
            url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            match = re.search(url_pattern, text)
            
            if match:
                photo_url = match.group()
                send_photo(chat_id, photo_url)
            else:
                send_message(chat_id, 'Not a valid link. Send a valid photo link.')

    return 'OK'

@app.route('/')
def index():
    return "The bot is running...."

if __name__ == '__main__':
    app.run(port=8080)
