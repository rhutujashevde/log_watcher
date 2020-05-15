from flask import Flask, render_template
from flask_socketio import SocketIO, send
import pyinotify


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
thread = None
all_logs = open("logs.txt",'r').read().split('\n')
try:
    all_logs.remove("")
except ValueError:
    pass
log_length = len(all_logs)

class ModHandler(pyinotify.ProcessEvent):
    def process_IN_CLOSE_WRITE(self, evt):
        new_all_logs = open("logs.txt",'r').read().split('\n')
        global log_length
        new_logs = new_all_logs[log_length:]
        log_length = len(new_all_logs)
        socketio.emit('file updated', {'data':new_logs})


def background_thread():
    handler = ModHandler()
    wm = pyinotify.WatchManager()
    notifier = pyinotify.Notifier(wm, handler)
    wm.add_watch('logs.txt', pyinotify.IN_CLOSE_WRITE)
    notifier.loop()


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on('connect')
def test_connect():
    global thread
    global all_logs
    if thread is None:
        thread = socketio.start_background_task(target=background_thread)
    old_logs = all_logs[-10:]
    socketio.emit('display log', {'data':old_logs})


if __name__ == '__main__':
    socketio.run(app, debug=True)