from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from dreams import app
from sqlalchemy import Unicode
from flask_login import LoginManager, UserMixin


db = SQLAlchemy(app)


class Users(UserMixin, db.Model):

    __tablename__ = 'users'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    id = db.Column('idUsers', db.Integer, primary_key=True, autoincrement=True)
    login = db.Column('login', db.String(Unicode(collation='utf8_bin')), unique=True, nullable=False)
    username = db.Column('username', db.String(), unique=True, nullable=False)
    password = db.Column('password', db.String(),  nullable=False)
    email = db.Column('email', db.String(50), unique=True, nullable=False)
    if_admin = db.Column('if_admin', db.Boolean, default=0)


    """
    Klasa Users jest tabelą z bazy danych (users). __tablename__ przyjmuje nazwę tabeli z bazy danych
    """

    def __init__(self, login, username, password,  email, if_admin):

        self.login = login
        self.username = username
        self.password = password
        self.email = email
        self.if_admin = if_admin
"""
__init jest konstruktorem klasy Users. Przyjmuje wartości: login, username, czyli imię, password (hasło) zahashowane w 
bcrypt, email, oraz if_admin, które sprawdza czy użytkownik jest adminem"
"""


class Categories(db.Model):
    __tablename__ = 'categories'
    idcategory = db.Column('idcategory', db.Integer, primary_key=True, autoincrement=True)
    category = db.Column('category', db.VARCHAR, nullable=False)

    def __init__(self, category):
        self.category = category



class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    title = db.Column('title', db.String(), nullable=False)
    content = db.Column('content', db.Text, nullable=False)
    # img_url = db.Column('img_url', db.String(), nullable=False)
    comments = db.relationship('Comment', backref='comments')
    idcategory = db.Column('idcategory', db.Integer, db.ForeignKey('categories.idcategory'), nullable=False)
    idphoto = db.Column('idphoto', db.Integer, db.ForeignKey('photos.idphoto'))

    def __init__(self, title, content,  idcategory, idphoto):
        self.title = title
        self.content = content
        # self.img_url =img_url
        self.idcategory = idcategory
        self.idphoto = idphoto


class Comment(db.Model):
    __tablename__ = 'comments'
    id_comment = db.Column('id_comment', db.Integer, primary_key=True, autoincrement=True)
    comment_content = db.Column('comment_content', db.Text(), nullable=False)
    idUsers = db.Column('idUsers', db.Integer, db.ForeignKey('users.idUsers'), nullable=False)
    id_article = db.Column('id_article', db.Integer, db.ForeignKey('articles.id'), nullable=False)


class Subscribers(db.Model):
    __tablename__ = 'subscribers'
    idsubscribers = db.Column('idsubscribers', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(),  nullable=False)
    email = db.Column('email', db.String, nullable=False)

    def __init__(self, name, email):
        self.name = name
        self.email = email

class Photos(db.Model):
    __tablename__ = 'photos'
    idphoto = db.Column('idphoto', db.Integer, primary_key=True, autoincrement=True)
    photo = db.Column('photo', db.VARCHAR(100), nullable=False)

    def __init__(self, photo):
        self.photo = photo

