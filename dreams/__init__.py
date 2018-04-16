from flask import Flask
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_login import LoginManager
from werkzeug.utils import secure_filename
from flask_uploads import UploadSet, configure_uploads, IMAGES

UPLOAD_FOLDER = '/static/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


app = Flask(__name__)
mail = Mail(app)
bcrypt = Bcrypt(app)
mail.init_app(app)

photos = UploadSet('photos', IMAGES)

app.config['UPLOADED_PHOTOS_DEST'] = 'static/img'
configure_uploads(app, photos)

login_manager = LoginManager()

login_manager.init_app(app)
login_manager.session_protection = "strong"
login_manager.login_view = 'zaloguj'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:nowak123@localhost:3306/licencjat'
app.config['SECRET_KEY'] = 'secretshit'
app.config['UPLOAD_FOLDER'] = 'uploads'

db = SQLAlchemy(app)


engine = create_engine("mysql+mysqldb://root:nowak123@localhost:3306/licencjat", echo=True, encoding='utf8')
Session = sessionmaker()
session = Session(bind=engine)
SESSION_COOKIE_NAME = 'ciastko'
SESSION_COOKIE_SECURE = True

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_USERNAME']='newsletterpatrycja@gmail.com'
app.config['MAIL_PASSWORD']='Pierre123$'
app.config['MAIL_PORT']=587
app.config['MAIL_USE_TLS' ]= True
app.config['MAIL_DEFAULT_SENDER'] = 'Patrycja'


from dreams import views
