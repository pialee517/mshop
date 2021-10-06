from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'hard_to_guess'
app.config['UPLOAD_PATH'] = os.environ.get('UPLOAD_PATH')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)


driver = os.environ.get('DB_DRIVER')
server = os.environ.get('DB_SERVER')
database = os.environ.get('DB_DATABSE')
username = os.environ.get('DB_USERNAME')
password = os.environ.get('DB_PASSWORD')
encrypt = os.environ.get('DB_ENCRYPT')
trust = os.environ.get('DB_TRUST')
timeout = os.environ.get('DB_TIMEOUT')

DB_CONNECTION=f'Driver={driver};Server={server};Database={database};Uid={username};Pwd={password};Encrypt={encrypt};TrustServerCertificate={trust};Connection Timeout={timeout};'
DB_CONNECT_STR=f'mssql+pyodbc:///?odbc_connect={DB_CONNECTION}'
app.config['SQLALCHEMY_DATABASE_URI'] = DB_CONNECT_STR

from market import routes
