from celery import Celery

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO, send

from logic import OrderTrackManager

manager = OrderTrackManager()

flask_app = Flask(__name__)
flask_app.host = 'localhost'
flask_app.config['SECRET_KEY'] = 'SUPERsecret'
flask_app.config['CELERY_BROKER_URL'] = 'redis://redis:6379'
flask_app.config['result_backend'] = 'redis://redis:6379'
CORS(flask_app, support_credentials=True)

socket = SocketIO(flask_app, cors_allowed_origins='*')

celery = Celery(flask_app.name, broker=flask_app.config['CELERY_BROKER_URL'])
celery.conf.update(flask_app.config)


@celery.task(name='check_sheet_updates')
def check_sheet_updates():
    manager.check_delivery_expected()

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Check delivery expected every hour
    sender.add_periodic_task(60 * 60, check_sheet_updates.s())


@socket.on('connect')
def on_connect():
    jsonable_df = manager.get_jsonable_df_from_db()
    send(jsonable_df)

@socket.on('message')
def on_message(message):
    if message == 'get_data':
        need_update = manager.check_updates()
        if need_update:
            data = manager.get_jsonable_df_from_db()
            send(data)


if __name__ == '__main__':
   socket.run(flask_app, host='0.0.0.0')
