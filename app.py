from flask import Flask, render_template
import base64
from transcribe_file import transcribe_streaming
import os
from credentials import retrieve_credentials
import eventlet.wsgi
import socketio
from transcribe_stream import transcribe_stream
import asyncio
import threading

# init app
app = Flask(__name__)
socket_ = socketio.Server()

# set speech to text google API credentials
#retrieve_credentials.get_secret()  # dump api key to json  #TODO:change this!!!
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'credentials/stt-api-creds.json'

# init transcribe jobs queue's dict
jobs_dict = {}


@app.route('/')
def index():
    return render_template('client_side.html')


@socket_.on('connect')
def handle_connect(sid, environ):
    print(f'Connected! {sid}')


@socket_.on('open_stream')
def handle_stream_opening(sid):
    print(f'opened stream for {sid}')

    # add streams blob queue
    jobs_dict[sid] = asyncio.Queue()


async def process_stream(sid):
    q = jobs_dict[sid]
    while True:
        blob = await q.get()
        print(blob)


@socket_.on('message-transcribe')
def transcribe_message(sid, message):
    """Receive audio message to transcribe, send transcription back to frontend"""
    print(f'Got message! from {sid}')

    # get base64 encoded data
    data_blob = message['audio']['dataURL'].split(',')[-1]
    data_blob = base64.b64decode(data_blob)  # decode to binary
    transcript = transcribe_streaming(data_blob)  # use google speech to transcribe data

    # emit results to frontend
    socket_.emit('results', transcript + '\r\n')


if __name__ == '__main__':
    app = socketio.Middleware(socket_, app)
    # start event loop
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(eventlet.wsgi.server(eventlet.listen(('127.0.0.1', 5000)), app))

