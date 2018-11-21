import os
import uuid
import signal
import sys
from time import sleep

from flask import Flask, render_template, request
from flask_mail import Mail
from flask_security import utils, login_required
from flask_admin import Admin

from observer.processing.main import system_init, SystemMng


# create and configure the app
app = Flask(__name__, static_folder="./obmng/static", static_url_path="/static", template_folder="./obmng/templates", instance_relative_config=True)
app.config.from_pyfile('config.py')

from observer.obmng.view import HomeView
admin = Admin(app, name='Observer', template_mode='bootstrap3', base_template='index.html', index_view=HomeView(url='/'))

upload_folder = app.config['UPLOAD_FOLDER']
try:
    os.makedirs(upload_folder)
except OSError:
    pass

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

import observer.obmng.video as video
app.register_blueprint(video.bp)

from observer.obmng.view import AdminModelView, FaceModelView, DashboardModelView, OptionsView
from observer.obmng.database import db_session, init_db
from observer.obmng.security import user_datastore
from observer.obmng.model import User, Role, Face, Log, Option

with app.app_context():
    admin.add_view(AdminModelView(User, db_session))
    admin.add_view(FaceModelView(Face, db_session))
    admin.add_view(DashboardModelView(Log, db_session))
    admin.add_view(OptionsView(Option, db_session))

if not os.path.isfile(app.config["SQLALCHEMY_DATABASE_URI"]):
    init_db()

system_init()

# Create a user to test with
@app.before_first_request
def create_user():
    user_datastore.find_or_create_role(name='superuser', description='Administrator')
    
    encrypted_password = utils.encrypt_password('admin')
    if not user_datastore.get_user('admin@local'):
        user_datastore.create_user(email='admin@local', password=encrypted_password)
    db_session.commit()

    user_datastore.add_role_to_user('admin@local', 'superuser')
    db_session.commit()

def signal_handler(sig, frame):
        print('Closing everything up, wait a second.')
        SystemMng().video_cameras_stop()
        sleep(10)
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
