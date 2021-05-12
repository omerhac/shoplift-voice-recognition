from quart import Quart, render_template, websocket
import json
from transcribe_file import transcribe_streaming
import os
from credentials import retrieve_credentials
import eventlet.wsgi
import socketio
from transcribe_stream import transcribe_stream
import asyncio
import random

# init app
app = Quart(__name__)

# set speech to text google API credentials
#retrieve_credentials.get_secret()  # dump api key to json  #TODO:change this!!!
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'credentials/stt-api-creds.json'

# init transcribe jobs queue's dict
jobs_dict = {}


@app.route('/')
async def index_stream():
    return await render_template('client_side_quart.html')


@app.route('/on_connect')
async def add_connection():
    # generate random user id
    user_id = random.randint(0, 100000)
    while user_id in jobs_dict:
        user_id = random.randint(0, 100000)

    user_id = str(user_id)
    # generate queue for user
    jobs_dict[user_id] = asyncio.Queue()

    print(f'user {user_id} connected')
    return user_id


@app.websocket('/stream')
async def stream_data():
    while True:
        data = await websocket.receive()
        data = json.loads(data)
        print(data['data'].encode('utf-8'))
        user_id = data['user_id']

        # check whether to keep the connection alive
        if data['type'] == 'message':
            if data['data'] == 'closeConnection':
                print(f'connection with {user_id} is closed')
                break  # close conneciton



if __name__ == '__main__':
    app.run()

