import pytest
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, LoginManager, login_required
from flask_migrate import Migrate
from flask_mail import Mail
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
import logging
from .config import Config

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    login_manager.init_app(app)

    from my_flask_app.main.routes import main_bp
    from my_flask_app.auth.auth_bp import auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')

    @app.errorhandler(404)
    def not_found_error(error):
        logging.error(f"404 error: {error}, URL: {request.url}, Referrer: {request.referrer}")

        request_details = {
            "url": request.url,
            "method": request.method,
            "headers": dict(request.headers),
            "args": request.args,
            "form": request.form,
            "user": current_user.get_id() if current_user.is_authenticated else None,
            "session": dict(session)
        }
        logging.info(f"Request details: {request_details}")

        if is_user_logged_in():
            return handle_authenticated_user()
        elif session_contains_key():
            return handle_session_key()
        elif request_has_expected_value():
            return handle_expected_value()
        else:
            return render_default_error_page(error, request_details)

    def is_user_logged_in():
        return current_user.is_authenticated

    def session_contains_key():
        return 'some_key' in session

    def request_has_expected_value():
        return request.args.get('some_parameter') == 'expected_value'

    def handle_authenticated_user():
        return redirect(url_for('main.index'))

    def handle_session_key():
        return redirect(url_for('main.index'))

    def handle_expected_value():
        return redirect(url_for('main.index'))

    def render_default_error_page(error, request_details):
        return render_template(
            '404_custom.html',
            error=error,
            request_details=request_details,
            suggestions=[
                "Check the URL for typos.",
                "Return to the homepage.",
                "Search for the content using the search bar."
            ]
        ), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html', error=error), 500

    # Setup logging
    setup_logging(app)

    return app


@login_manager.user_loader
def load_user(user_id):
    from my_flask_app.models import User
    return User.query.get(int(user_id))


def setup_logging(app):
    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr=f"no-reply@{app.config['MAIL_SERVER']}",
                toaddrs=app.config['ADMINS'],
                subject='YourApplication Failure',
                credentials=auth,
                secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        log_dir = os.path.join(app.instance_path, 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_file = os.path.join(log_dir, 'meta.li.log')
        file_handler = RotatingFileHandler(log_file, maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('YourApplication startup')


@pytest.fixture
def app():
    app = create_app(Config)
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Hello, World!" in response.data


def test_about_route(client):
    response = client.get('/about')
    assert response.status_code == 200
    assert b"About Us" in response.data


def test_404_error(client):
    response = client.get('/nonexistent-route')
    assert response.status_code == 404
    assert b"404 Not Found" in response.data
