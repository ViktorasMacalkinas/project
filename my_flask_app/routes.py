from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from .forms import RegistrationForm, LoginForm
from flask import current_app as app, render_template, request, redirect, url_for
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Email, Length
from .config import Config
from .models import db, User
import requests

auth_bp = Blueprint('auth', __name__)


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])
    submit = SubmitField('Sign In')


def verify_recaptcha(token):
    secret_key = Config.RECAPTCHA_SECRET_KEY
    response = requests.post(
        'https://www.google.com/recaptcha/api/siteverify',
        data={
            'secret': secret_key,
            'response': token
        }
    )
    result = response.json()
    return result.get('success', False)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        recaptcha_token = request.form.get('g-recaptcha-response')
        if verify_recaptcha(recaptcha_token):
            username = form.email.data
            password = form.password.data
            return redirect(url_for('index'))
        else:
            return "reCAPTCHA verification failed", 400

    site_key = Config.RECAPTCHA_SITE_KEY
    return render_template('login.html', form=form, site_key=site_key)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return "Hello, World!"


@main_bp.route('/about')
def about():
    return "About Us"


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)

    return app
