"""
burning man 2021 project
numbers from: https://freemusicarchive.org/music/The_Conet_Project

"""
#!/usr/bin/env python
import atexit
import os
import random
import threading
import time
from time import sleep

import requests
from pydub import AudioSegment
from pydub.playback import play
from threading import Lock
from flask import Flask, render_template, session, request, \
    copy_current_request_context, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
SOUND_DIRECTORY = "./static/numbers"
"""
# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()
yourThread = threading.Thread()


def interrupt():
    global yourThread
    yourThread.cancel()

def player():
    # wait until web starts
    print("START PLAYER")
    time.sleep(5)
    while True:
        print("boink")
        play_next = random.choice(os.listdir(SOUND_DIRECTORY))
        requests.get("http://127.0.0.1:5000/emit/{}".format(play_next))
        print("Playing -> {}", play_next)
        time.sleep(500)


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(2)
        count += 1
        play_next = random.choice(os.listdir(SOUND_DIRECTORY))
        print("BACKGROUND FIRE")
        socketio.emit('my_response',
                      {'data': play_next, 'count': count, "playing": play_next},
                      namespace='/test')
        sound = AudioSegment.from_wav(SOUND_DIRECTORY + "/" + play_next)
        play(sound)
        socketio.sleep(5)


@app.route('/otr/<the_file>')
def otr(the_file):
    return send_from_directory('static', the_file)


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on('my_event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})


@socketio.on('my_broadcast_event', namespace='/test')
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)


@socketio.on('join', namespace='/test')
def join(message):
    join_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.on('leave', namespace='/test')
def leave(message):
    leave_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.on('close_room', namespace='/test')
def close(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                         'count': session['receive_count']},
         room=message['room'])
    close_room(message['room'])


@socketio.on('my_room_event', namespace='/test')
def send_room_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         room=message['room'])


@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    session['receive_count'] = session.get('receive_count', 0) + 1
    # for this emit we use a callback function
    # when the callback function is invoked we know that the message has been
    # received and it is safe to disconnect
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']},
         callback=can_disconnect)


@socketio.on('my_ping', namespace='/test')
def ping_pong():
    emit('my_pong')


@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    print("Launching background threads")
    print("player...")
    yourThread = threading.Thread(target=player)
    yourThread.start()
    atexit.register(interrupt)
    print("web server launching!")
    socketio.run(app, debug=True)


"""
import threading
import atexit
import time
import os
import random
from flask import Flask, render_template, copy_current_request_context, jsonify, send_from_directory, session
from flask_socketio import SocketIO, send, emit, join_room, leave_room, close_room, disconnect, rooms
import requests
import gevent
import geventwebsocket


SOUND_DIRECTORY = "./static/numbers"
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode="gevent")
# variables that are accessible from anywhere
commonDataStruct = {"file": "", "numbers": False}
# lock to control access to variable
dataLock = threading.Lock()
# thread handler
yourThread = threading.Thread()


def interrupt():
    global yourThread
    yourThread.cancel()


@socketio.on_error()        # Handles the default namespace
def error_handler(e):
    print("SOCKET ERROR")
    print(e)
    pass


@socketio.on('json', namespace="/mq")
def handle_json(json):
    print("SOCKET IN")
    print('received json: ' + str(json))


@socketio.on('my_event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})


@socketio.on('my_broadcast_event', namespace='/test')
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)


@socketio.on('join', namespace='/test')
def join(message):
    join_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.on('leave', namespace='/test')
def leave(message):
    leave_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.on('close_room', namespace='/test')
def close(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                         'count': session['receive_count']},
         room=message['room'])
    close_room(message['room'])


@socketio.on('my_room_event', namespace='/test')
def send_room_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         room=message['room'])


@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    session['receive_count'] = session.get('receive_count', 0) + 1
    # for this emit we use a callback function
    # when the callback function is invoked we know that the message has been
    # received and it is safe to disconnect
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']},
         callback=can_disconnect)


@socketio.on('my_ping', namespace='/test')
def ping_pong():
    emit('my_pong')


@socketio.on('message', namespace="/mq")
def handle_text(json):
    print("SOCKET IN")
    print('received text: ' + str(json))


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/otr/<the_file>')
def otr(the_file):
    return send_from_directory('static', the_file)


@app.route('/emit/<name>')
def ws_emit(name):
    print(name)
    try:
        send({"file": name, "numbers": True}, namespace="/mq")
        print("Message sent!")
    except AttributeError:
        pass
    return jsonify({"result": "ok"})


def player():
    # wait until web starts
    print("START PLAYER")
    time.sleep(5)
    while True:
        print("boink")
        play_next = random.choice(os.listdir(SOUND_DIRECTORY))
        requests.get("http://127.0.0.1:5000/emit/{}".format(play_next))
        print("Playing -> {}", play_next)
        time.sleep(500)


print("Launching background threads")
print("player...")
yourThread = threading.Thread(target=player)
yourThread.start()
atexit.register(interrupt)
print("web server launching!")
socketio.run(app)
"""
