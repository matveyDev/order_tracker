from flask import Flask
from flask_socketio import SocketIO


app = Flask(__name__)
app.config['SECRET_KEY'] = 'SUPERsecret'
socketio = SocketIO(app)


@app.route("/")
@socketio.on('connect')
def test_connect():
    return "<p>Hello, World!</p>"


if __name__ == '__main__':
    socketio.run(app)
