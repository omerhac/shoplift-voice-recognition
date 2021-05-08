from flask import Flask, render_template
import base64
from transcribe_file import transcribe_streaming
import os
from credentials import retrieve_credentials
import eventlet
import eventlet.wsgi
import socketio

# init app
app = Flask(__name__)
socket_ = socketio.Server()

# set speech to text google API credentials
retrieve_credentials.get_secret()  # dump api key to json
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'credentials/stt-api-creds.json'


@app.route('/')
def index():
    return render_template('client_side.html')


@app.route('/stream')
def index_stream():
    return render_template('client_side_streaming.html')


@socket_.on('connect')
def handle_connect(sid, environ):
    print(f'Connected! {sid}')


@socket_.on('message-transcribe')
def transcribe_message(sid, message):
    """Receive audio message to transcribe, send transcription back to frontend"""
    print('Got message!')

    # get base64 encoded data
    data_blob = message['audio']['dataURL'].split(',')[-1]
    data_blob = base64.b64decode(data_blob)  # decode to binary
    transcript = transcribe_streaming(data_blob)  # use google speech to transcribe data

    # emit results to frontend
    socket_.emit('results', transcript + '\r\n')


@socket_.on('stream')
def transcribe_stream(sid, stream):
    print('Got stream')
    print(stream)


if __name__ == '__main__':
    app = socketio.Middleware(socket_, app)
    eventlet.wsgi.server(eventlet.wrap_ssl(eventlet.listen(('', 8000)),
                                           certfile='myCA.pem',
                                           keyfile='myCA.key'), app)
