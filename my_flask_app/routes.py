from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Email, Length, EqualTo
from flask_wtf.recaptcha import RecaptchaField
from .config import Config
from .models import User
from .database import db
from flask_login import login_user
import requests

main = Blueprint('main', __name__)


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])
    recaptcha = RecaptchaField()
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])
    recaptcha = RecaptchaField()
    submit = SubmitField('Sign Up')


def verify_recaptcha(token):
    secret_key = Config.RECAPTCHA_PRIVATE_KEY
    response = requests.post(
        'https://www.google.com/recaptcha/api/siteverify',
        data={
            'secret': secret_key,
            'response': token,
            'remoteip': request.remote_addr
        }
    )
    result = response.json()
    print(f"reCAPTCHA result: {result}")  # Debug statement
    return result.get('success', False)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        print("Login form validated")  # Debug statement
        if verify_recaptcha(form.recaptcha.data):
            print("reCAPTCHA verified for login")  # Debug statement
            email = form.email.data
            password = form.password.data
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                print("User authenticated")  # Debug statement
                login_user(user)
                return redirect(url_for('main.index'))
            else:
                flash('Invalid credentials. Please try again.')
        else:
            flash('reCAPTCHA verification failed. Please try again.')
    return render_template('login.html', form=form, site_key=Config.RECAPTCHA_SITE_KEY)


@main.route('/signin', methods=['GET', 'POST'])
def signin():
    form = RegistrationForm()
    if form.validate_on_submit():
        print("Registration form validated")
        if verify_recaptcha(form.recaptcha.data):
            print("reCAPTCHA verified for registration")
            username = form.username.data
            email = form.email.data
            password = form.password.data
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful. Please log in.')
            return redirect(url_for('main.login'))  # Corrected URL
        else:
            flash('reCAPTCHA verification failed. Please try again.')
    return render_template('signin.html', form=form, site_key=Config.RECAPTCHA_SITE_KEY)


@main.route('/how_it_works')
def how_it_works():
    return render_template('how-it-works.html')


@main.route('/aluminum')
def aluminum():
    return render_template('aluminum.html')


@main.route('/mild-steel')
def mild_steel():
    return render_template('mild-steel.html')


@main.route('/stainless-steel')
def stainless_steel():
    return render_template('stainless-steel.html')


@main.route('/abs')
def abs():
    return render_template('abs.html')


@main.route('/nylon')
def nylon():
    return render_template('nylon.html')


@main.route('/pom')
def pom():
    return render_template('pom.html')


@main.route('/about')
def about():
    return render_template('about.html')


@main.route('/partner')
def partner():
    return render_template('partner.html')


@main.route('/contacts')
def contacts():
    return render_template('contacts.html')


@main.route('/team')
def team():
    return render_template('team.html')
