from dreams import app
from flask import render_template
from flask_login import current_user


@app.route('/')
def index():
    if current_user.is_authenticated and current_user.if_admin == 1:
        navigation =[
            {
               "href" : 'posty',
                'caption' : 'Wszystkie wpisy'
            },
            {
                'href' : 'adminpanel',
                'caption' : 'Panel administratora'
            },
            {
                'href' : 'addarticle',
                'caption': 'Dodaj wpis'
            },
            {
                'href' : 'logout',
                'caption': 'Wyloguj się'
            }
        ]
        return render_template('index.html', username=current_user.username, navigation=navigation)

    elif current_user.is_authenticated:
        navigation =[
            {
               "href" : 'posty',
                'caption' : 'Wszystkie wpisy'
            },
            {
                'href' : 'userpanel',
                'caption' : 'Moje konto'
            },

            {
                'href' : 'logout',
                'caption': 'Wyloguj się'
            },
            {
                'href' : 'contact',
                'caption' : 'Kontakt'
            }
        ]

        return render_template('index.html',username=current_user.username, navigation=navigation)
    else:
        print("anonek")
        navigation =[
            {
               "href" : 'posty',
                'caption' : 'Wszystkie wpisy'
            },
            {
                'href' : 'zaloguj',
                'caption' : 'Zaloguj się'
            },
            {
                'href' : 'zarejestruj',
                'caption': 'Zarejestruj się'
            },
            {
                'href' : 'contact',
                'caption': 'Kontakt'
            }
        ]
        return render_template('index.html', navigation=navigation)


@app.context_processor
def inject_variables():
    if current_user.is_authenticated and current_user.if_admin == 1:
        return dict(navigation=[
            {
               "href" : 'posty',
                'caption' : 'Wszystkie wpisy'
            },
            {
                'href' : 'adminpanel',
                'caption' : 'Panel administratora'
            },
            {
                'href' : 'addarticle',
                'caption': 'Dodaj wpis'
            },
            {
                'href' : 'logout',
                'caption': 'Wyloguj się'
            }
        ])
    elif current_user.is_authenticated:
        return dict(navigation=[
            {
               "href" : 'posty',
               'caption' : 'Wszystkie wpisy'
            },
            {
                'href' : 'userpanel',
                'caption' : 'Moje konto'
            },

            {
                'href' : 'logout',
                'caption': 'Wyloguj się'
            },
            {
                'href' : 'contact',
                'caption' : 'Kontakt'
            }
        ])
    else:
        return dict(navigation =[
            {
               "href" : 'posty',
               'caption' : 'Wszystkie wpisy'
            },
            {
                'href' : 'zaloguj',
                'caption' : 'Zaloguj się'
            },
            {
                'href' : 'zarejestruj',
                'caption': 'Zarejestruj się'
            },
            {
                'href' : 'contact',
                'caption': 'Kontakt'
            }
        ])

