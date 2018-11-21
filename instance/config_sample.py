import os
# Create dummy secrey key so we can use sessions
SECRET_KEY = ''

# Create in-memory database
DATABASE_FILE = ''
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.join(os.getcwd(), 'instance'), DATABASE_FILE)
SQLALCHEMY_ECHO = True

# Flask-Security config
SECURITY_URL_PREFIX = "/"
SECURITY_PASSWORD_HASH = "bcrypt"
SECURITY_PASSWORD_SALT = ""

# Flask-Security URLs, overridden because they don't put a / at the end
SECURITY_LOGIN_URL = "/login/"
SECURITY_LOGOUT_URL = "/logout/"
SECURITY_REGISTER_URL = "/register/"

SECURITY_POST_LOGIN_VIEW = "/"
SECURITY_POST_LOGOUT_VIEW = "/"
SECURITY_POST_REGISTER_VIEW = "/"

# Flask-Security features
SECURITY_REGISTERABLE = True
SECURITY_SEND_REGISTER_EMAIL = False
SECURITY_TRACKABLE = True
SECURITY_CONFIRMABLE = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECURITY_RESET_PASSWORD_WITHIN = 1

UPLOAD_FOLDER = "./faces"
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
