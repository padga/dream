from flask import render_template, request, flash, redirect, url_for, session, abort, send_from_directory, Blueprint
from dreams import app, bcrypt, database, ALLOWED_EXTENSIONS
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from dreams import forms
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Message, Mail
from werkzeug.utils import secure_filename
import os

mail = Mail(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = os.urandom(24)


@login_manager.user_loader
def load_user(user_id):
    return database.Users.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():

    if current_user.is_authenticated and current_user.if_admin == 1:

        return render_template('admin/index.html', username=current_user.username)

    elif current_user.is_authenticated:

        return render_template('user/index.html', username=current_user.username)
    else:
        return render_template('guest/index.html')


@app.context_processor
def inject_variables():
    subscribe = forms.SubscribeForm()
    return dict(subscribe=subscribe)


@app.route('/post/')
def post():
    if current_user.is_authenticated and current_user.if_admin == 1:

        return render_template('/admin/post.html', username=current_user.username)

    elif current_user.is_authenticated:

        return render_template('/user/post.html', username=current_user.username)
    else:
        return render_template('/guest/post.html')


@app.route('/contact')
def contact():
    form = forms.ContactForm()
    return render_template('contact.html', form=form)


@app.route('/send', methods=['POST'])
def send():
    form = forms.ContactForm()
    name = form.name.data
    text = form.content.data
    sender = form.email.data
    subject = name + " przesyła wiadomość!"
    if form.validate():
        msg = Message(subject=subject,  body=text + " "+"Adres e-mail "+sender, recipients=["newsletterpatrycja@gmail.com "])
        mail.send(msg)
        flash("Twój formularz został wysłany!")
        return redirect(url_for('contact'))
    else:
        return render_template('contact.html', form=form)


@app.route('/zarejestruj', methods=['GET', 'POST'])
def register():
    form = forms.RegisterForm()
    if current_user.is_authenticated:
        abort(401)
    return render_template('/guest/register.html', form=form)


@app.route('/submit', methods=['POST'])
def submit():
    form = forms.RegisterForm()
    if current_user.is_authenticated:
        abort(401)
    else:
        cand = form.password.data
        hash_password = str(bcrypt.generate_password_hash(cand).decode('utf-8'))
        login = form.login.data
        username = form.username.data
        email = form.email.data
        password = hash_password
        subscribe = form.subscriber.data

        if form.validate():
            new_user = database.Users(login=login, username=username, password=password, email=email, if_admin=0)
            db.session.add(new_user)
            db.session.commit()
            if subscribe:
                new_Subscriber = database.Subscribers(name=username, email=email)
                db.session.add(new_Subscriber)
                db.session.commit()

            return render_template('/guest/index.html', form=form)
        else:
            return render_template('/guest/register.html', form=form)


@app.route('/zaloguj', methods=['POST', 'GET'])
def login():
    form = forms.LoginForm()
    remember = form.remember.data
    if current_user.is_authenticated:
        abort(404)
    else:

        db.engine.connect()
        if form.validate_on_submit():
            user = database.Users.query.filter_by(login=form.login.data).first()
            if remember:
                login_user(user, remember=True)
            else:
                login_user(user)
                flash("No witaj!")
                return redirect(url_for('index'))

    return render_template('/guest/login.html', form=form)


@app.route('/dodaj_artykul')
def add_article():
    form = forms.ArticleForm()
    if current_user.is_anonymous or current_user.is_authenticated and current_user.if_admin ==0:
        abort(401)
    else:
        return render_template('/admin/add_article.html', form=form)


@app.route('/posts', methods=['POST', 'GET'])
def posts():
    form = forms.ArticleForm()
    title = form.title.data
    content = form.content.data
    file = form.image.data
    category =form.category.data
    print(form.data)
    filename = secure_filename(file.filename)
    print(filename)
    if form.validate:
        filename = secure_filename(file.filename)
        path = file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        newPhoto = database.Photos(photo=filename)
        db.session.add(newPhoto)
        db.session.commit()
        phot = 'select idphoto from photos order by idphoto desc limit 1'
        idphoto = db.engine.execute(phot).scalar()
        id = 'SELECT idcategory from categories where category_name =%s'
        idcategory = db.engine.execute(id, category).scalar()
        new_article = database.Article(title=title, content=content, idphoto=idphoto, idcategory=idcategory)
        db.session.add(new_article)
        db.session.commit()

        return redirect(url_for('posty'), flash("Wpis dostał poprawnie dodany!"))

    else:
        print('cos jest nie halo')
        return render_template('admin/add_article.html', form=form)

@app.route('/posty', methods=['POST', 'GET'])
def posty():
    db.engine.connect()
    query = 'select * from articles join photos where photos.idphoto = articles.idphoto order by id desc '
    result = db.engine.execute(query)

    res = result.fetchall()
    print("to jest res ", res)
    query1 = 'SELECT * from categories'
    results = db.engine.execute(query1)


    data = results.fetchall()


    print(data)

    if current_user.is_authenticated and current_user.if_admin == 1:
        return render_template('/admin/posty.html', dat=res, data=data)
    elif current_user.is_authenticated:
        return render_template('/user/posty.html', dat=res, data=data)
    else:
        return render_template('/guest/posty.html', dat=res, data=data)


@app.route('/<category_slug>')
def category(category_slug):
    db.engine.connect()

    query = 'SELECT * FROM articles where idcategory=%s ORDER BY id DESC'
    query2 = 'SELECT idcategory from categories where (category_name)=%s '
    exc = db.engine.execute(query2, category)
    exc = exc.fetchone()
    res = db.engine.execute(query, exc)
    final = res.fetchall()

    query1 = 'SELECT * FROM categories'
    results = db.engine.execute(query1)
    data = results.fetchall()

    if current_user.is_authenticated and current_user.if_admin == 1:
        return render_template('/admin/posty.html', dat=final, data=data)
    elif current_user.is_authenticated:
        return render_template('/user/posty.html', dat=final, data=data)
    else:
        return render_template('/guest/posty.html', dat=final, data=data)



@app.route('/post/<id_postu>')
def post_id(id_postu):
    form = forms.CommentForm()
    db.engine.connect()
    title = 'SELECT title FROM articles WHERE id=%s'
    result_title = db.engine.execute(title, id_postu).scalar()

    content = 'SELECT content FROM articles WHERE id=%s'
    result_content = db.engine.execute(content, id_postu).scalar()

    # img_url = 'SELECT img_url FROM articles WHERE id=%s'
    # result_img = db.engine.execute(img_url, id_postu).scalar()

    query = 'SELECT * FROM comments WHERE id_article=%s'

    result = db.engine.execute(query, id_postu)
    query = 'select login from users join comments where users.idUsers=comments.idUsers and id_article=%s'
    login = db.engine.execute(query, id_postu).scalar()

    data = result.fetchall()
    if current_user.is_anonymous:
        return render_template('/guest/post.html', title=result_title, content=result_content,
                                                             id_postu=id_postu, data=data, login=login,  form=form)
    elif current_user.is_authenticated:
        return render_template('/user/post.html', title=result_title, content=result_content,
                           id_postu=id_postu, data=data, login=login,  form=form)
    else:
        return render_template('/admin/post.html', title=result_title, content=result_content,
                               id_postu=id_postu, data=data, login=login, form=form)


@app.route('/post/<id_postu>/add', methods=['POST'])
def post_submit(id_postu):
    form = forms.CommentForm()
    db.engine.connect()
    comment_content = form.comment_content.data
    idusers = current_user.id

    if form.validate():
        new_comment = database.Comment(comment_content=comment_content, idUsers=idusers, id_article=id_postu)
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('posty'))
    else:
        return render_template('/user/post.html', form=form)


@app.route('/delete_post/<id_postu>')
def delete_post(id_postu):
    db.engine.connect()
    query = 'delete from articles where id=%s'
    query1 = 'delete from comments where id_article=%s'
    db.engine.execute(query1, id_postu)
    db.engine.execute(query, id_postu)
    db.session.commit()
    return redirect(url_for('index'))



@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user', None)
    return redirect(url_for('index'))



@app.errorhandler(404)
def not_found(exc):
    return("Nie ma takiej strony!", 404)


@app.route('/usersi')
def usersi():
    if current_user.is_authenticated and current_user.if_admin == 1:
        query = 'SELECT * FROM users'
        result = db.engine.execute(query)
        data = result.fetchall()
        return render_template('usersi.html', data=data)
    else:
        abort(401)


@app.route('/mojekonto')
@login_required
def my_account():
    query = 'SELECT * FROM users WHERE idUsers=%s'
    id = current_user.id
    result =db.engine.execute(query, id)
    data = result.fetchall()
    print(data)
    form = forms.ChangePasswordForm()
    mail_form = forms.ChangeEmailForm()
    return render_template('/user/my_account.html', data=data, form=form, mail_form=mail_form)


@app.route('/changepassword', methods=['POST'])
@login_required
def changepassword():
    form = forms.ChangePasswordForm()
    cand = form.password.data
    id = current_user.id
    if form.validate():
        new_password = str(bcrypt.generate_password_hash(cand).decode('utf-8'))
        query = 'Update users SET password=%s where idUsers=%s'
        db.engine.execute(query, new_password, id)
        db.session.commit()

        return redirect(url_for('index'))
    else:
        return render_template('/user/my_account.html',form=form)

@app.route('/changemail', methods=['POST'])
@login_required
def changemail():
    mail_form = forms.ChangeEmailForm()
    form=forms.ChangePasswordForm()
    cand = mail_form.new_email.data

    id = current_user.id
    if mail_form.validate():

        query = 'Update users SET email=%s where idUsers=%s'
        db.engine.execute(query, cand, id)
        db.session.commit()
        print("Udało się?")
        return redirect(url_for('index'))
    else:
        return render_template('/user/my_account.html', mail_form=mail_form, form=form)

@app.route('/panel')
def panel():
    if current_user.is_anonymous or current_user.is_authenticated and current_user.if_admin ==0:
        abort(401)
    else:
        db.engine.connect()
        query = 'select * from users where idUsers > 1'
        data = db.engine.execute(query).fetchall()

        return render_template('admin/usersi.html', data=data)


@app.route('/delete_user/<idUsers>')
def delete_user(idUsers):
    if database.Users.if_admin == 0:
        abort("Nie możesz usunąć admina!")
    query = 'delete from comments where idUsers=%s'
    query1 = 'delete from users WHERE idUsers=%s'
    results = db.engine.execute(query, idUsers)
    results1 = db.engine.execute(query1, idUsers)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/subscribe', methods=['POST'])
def subscribe():
    form = forms.SubscribeForm()
    name = form.name.data
    mail = form.email.data

    if form.validate():
        db.engine.connect()
        new_Subscriber = database.Subscribers(name=name, email=mail)
        db.session.add(new_Subscriber)
        db.session.commit()

        return redirect(url_for('index'))
    else:
        return "Coś sie zjebało"


@app.route('/wypisz')
def wypisz():
    form = forms.Unsubscribe()
    return render_template("/guest/unsubscribe.html", form=form)

@app.route('/unsub', methods=['POST'])
def unsub():
    form = forms.Unsubscribe()
    email = form.email.data
    if form.validate():
        query = 'delete from subscribers WHERE email=%s'
        db.engine.execute(query, email)
        db.session.commit()
        flash("Wypisano adres z listy subskrybentów!")
        return redirect(url_for('index'))
    else:
        if current_user.is_authenticated and current_user.if_admin ==1:
            return render_template('', form=form)
        elif current_user.is_authenticated:
            return render_template('/user/unsubscribe.html', form=form)
        else:
            return render_template('/guest/unsubscribe.html', form=form)


@app.route('/zmien_dane/<idUsers>')
@login_required
def zmien_dane(idUsers):
    query = 'SELECT * FROM users WHERE idUsers=%s'

    result =db.engine.execute(query, idUsers)
    data = result.fetchall()
    print(data)
    form = forms.ChangePasswordForm()
    mail_form = forms.ChangeEmailForm()
    if current_user.is_authenticated and current_user.if_admin ==1:
        return render_template('/admin/change-data.html', data=data, form=form, mail_form=mail_form)
    else:
        abort(401)

@app.route('/o-serwisie')
def oserwisie():
    return render_template('/guest/oserwisie.html')

@app.route('/newsletter')
def newsletter():
    form = forms.NewsletterForm()
    return render_template('admin/newsletter.html', form=form)



@app.route('/sendnewsletter', methods=['POST'])
def sendnewsletter():
    form = forms.NewsletterForm()
    db.engine.connect()
    content = form.newsletter.data
    title = form.title.data
    query = 'SELECT * FROM subscribers'
    mails = db.engine.execute(query).fetchall()

    if form.validate:
        for row in mails:
            name = row[1]
            recipent = row[2]
            news = Message(subject=name, body=content, recipients=[recipent])
            mail.send(news)
    flash("Newsletter został wysłany do wszystkich subskrybentów")
    return render_template('admin/newsletter.html', form=form)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
