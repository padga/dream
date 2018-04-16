from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import InputRequired, Email, EqualTo, Length, ValidationError
from flask_sqlalchemy import SQLAlchemy
from dreams import app, database
from flask_bcrypt import Bcrypt


bcrypt = Bcrypt(app)
db = SQLAlchemy(app)


def validate_login(form,field):

    db.engine.connect()
    query = 'SELECT users.login FROM users WHERE login = %s COLLATE utf8_bin'
    results = db.engine.execute(query, field.data).scalar()
    if results is not None:
        raise ValidationError('Podany login jest zajęty!')


def validate_email(form,field1):

    exists_email = db.session.query(database.Users.email).filter_by(email=field1.data).scalar()
    if exists_email is not None:
        raise ValidationError('Podany adres e-mail jest zajęty!')


class RegisterForm(FlaskForm):
    login = StringField('Login', validators=[InputRequired(message="Musisz podać login!"), Length(min=2, max=15,
                                                                     message="Login musi zawierać od 3 do 15 znaków!"),
                                             validate_login])
    username = StringField('Imię', validators=[InputRequired(message="Podaj swoje imię!"), Length(min=2, max=40,
                                                                       message="Imię musi zawierać od 3 do 40 znaków!")])
    email = StringField('Adres email', validators=[InputRequired(message="Podaj swój adres e-mail"),
                                                   Email(message='Podaj poprawny e-mail!'),
                                                   Length(max=50), validate_email])
    password = PasswordField('Hasło', validators=[InputRequired(message="Musisz podać hasło!"), Length(min=8,
                                                                        message="Hasło musi zawierać minimum 8 znaków!")])
    password2 = PasswordField('Powtórz hasło', validators=[InputRequired(message='To pole nie może być puste!'),
                                                       EqualTo('password', message='Podane hasła nie są takie same'),
                                                       Length(min=8, message="Hasło musi zawierać minimum 8 "
                                                                                    "znaków!")])
    subscriber = BooleanField("Chcę zapisać się na newsletter")


def correct_login(form, field):
        cand = form.login.data
        db.engine.connect()
        query = 'SELECT users.login FROM users WHERE login = %s COLLATE utf8_bin'
        results = db.engine.execute(query, cand).scalar()
        print(results)
        if results is None:
            raise ValidationError('Nie ma takiego loginu w bazie!')


def correct_password(form, field1):
    db.engine.connect()
    password = 'SELECT users.password FROM users WHERE login = %s COLLATE utf8_bin'
    log = form.login.data
    query = db.engine.execute(password, log).scalar()
    if query is None:
        raise ValidationError("Błąd!")
    candidate = form.passwd.data
    candidate.encode('utf-8')
    result = bcrypt.check_password_hash(query, candidate)
    print(result)
    if not result:
        raise ValidationError('Błędne hasło!')



class LoginForm(FlaskForm):
    login = StringField('login', validators=[InputRequired(message="Musisz podać login"), Length(min=2, max=15),
                                             correct_login])
    passwd = PasswordField('passwd', validators=[InputRequired(message="Nie możesz się zalogować bez hasła"),
                                                 Length(min=8), correct_password])
    remember = BooleanField('remember me')


def unique_title(form, field):
    db.engine.connect()
    query = 'SELECT articles.title FROM articles WHERE title = %s COLLATE utf8_bin'
    results = db.engine.execute(query, field.data).scalar()
    if results is not None:
        raise ValidationError('Tytuł zajęty!')


class ArticleForm(FlaskForm):
    title = StringField('title', validators=[InputRequired(message="Nie możesz dodać wpisu bez tytułu"), unique_title])
    content = TextAreaField('content', validators=[InputRequired(message="Nie możesz dodać wpisu bez treści!")])
    img_url = StringField('img_url', validators=[InputRequired(message="To pole nie może zostać puste!")])
    category = SelectField("Dział wpisu",
                           choices=[('joga i medytacja', 'Joga i medytacja'), ('filozofie szczęścia', 'filozofie szczęścia'), ('sen', 'sen'), ('psychologia', 'psychologia')])
    image = FileField(validators=[FileRequired(message="Nie możesz dodać wpisu bez zdjęcia!")])

class CommentForm(FlaskForm):
    comment_content = TextAreaField('comment_content', validators=[InputRequired(message="Komentarz musi mieć treść!")])


class ContactForm(FlaskForm):
    name = StringField('Imię', validators=[InputRequired(message="Wpisz imię!")])
    email = StringField("Adres e-mail", validators=[InputRequired(message="Podaj swój adres e-mail"),
                                                    Email(message="Podaj poprawnego maila!")])
    content = TextAreaField('Treść', validators=[InputRequired(message="Nie możesz wysłać pustej wiadomości!")])


class ChangePasswordForm(FlaskForm):
    password = PasswordField('Hasło', validators=[InputRequired(message="Musisz podać hasło!"), Length(min=8,
                                                            message="Hasło musi zawierać minimum 8 znaków!"), EqualTo('password2',
                                                                                                                      message="Hasła są różne!")])
    password2 = PasswordField('Powtórz hasło', validators=[InputRequired(message='To pole nie może być puste!'),
                                                           EqualTo('password',
                                                                   message='Podane hasła nie są takie same'),
                                                           Length(min=8, message="Hasło musi zawierać minimum 8 "
                                                                                 "znaków!")])


class ChangeEmailForm(FlaskForm):
    new_email = StringField("Adres e-mail", validators=[InputRequired(message="Podaj swój adres e-mail"),
                                                    Email(message="Podaj poprawnego maila!"), validate_email])


def unique_email(form,field1):

    exists_email = db.session.query(database.Subscribers.email).filter_by(email=field1.data).scalar()
    if exists_email is not None:
        raise ValidationError('Podany adres e-mail jest już zapisany!')


class SubscribeForm(FlaskForm):
    name = StringField("", validators=[InputRequired(message="Podaj swoje imię!")])
    email = StringField("", validators=[InputRequired(), Email(message="Podaj poprawny mail!"), unique_email])


def unsub_email(form,field1):

    exists_email = db.session.query(database.Subscribers.email).filter_by(email=field1.data).scalar()
    if exists_email is None:
        raise ValidationError('Ten adres nie był zapisany na liście subskrybentów!')


class Unsubscribe(FlaskForm):
    email = StringField("", validators=[InputRequired(), Email(message="Podaj poprawny mail!"), unsub_email])




