from flask import url_for
from flask_security import Security, login_required, \
     SQLAlchemySessionUserDatastore
from flask_admin import helpers as admin_helpers
from flask_admin.contrib import sqla
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer

from observer import app, admin
from observer.obmng.database import db_session
from observer.obmng.model import User, Role

user_datastore = SQLAlchemySessionUserDatastore(db_session,
                                                User, Role)
security = Security(app, user_datastore)
mail = Mail(app)

@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )

def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email