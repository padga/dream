from flask import render_template, request, flash, redirect, url_for, session, abort, send_from_directory, Blueprint
from dreams import app, bcrypt, database, ALLOWED_EXTENSIONS
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from dreams import forms
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Message, Mail
from werkzeug.utils import secure_filename
import os

db = SQLAlchemy(app)

query = 'select * from subscribers'
mails = db.engine.execute(query).fetchall()
print(mails)

correct = []
for row in mails:
    a = "xd" + row[1]
    print(a)


print(mails)







