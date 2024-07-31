import pytest
from my_flask_app import create_app, db
from my_flask_app.models import User
from bs4 import BeautifulSoup


@pytest.fixture(scope='module')
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory database for testing

    with app.app_context():
        db.create_all()  # Create the tables manually
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def user(app):
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        yield user
        db.session.remove()


def test_index(client):
    response = client.get('/')
    assert response.status_code == 200


def test_login(client):
    response = client.get('/login')
    assert response.status_code == 200


def test_signin(client):
    response = client.get('/signin')
    assert response.status_code == 200


def test_login_post(client):
    data = {'email': 'test@example.com', 'password': 'password'}
    response = client.post('/login', data=data, follow_redirects=True)
    assert response.status_code == 200


def test_signin_post(client):
    data = {'username': 'testuser', 'email': 'test@example.com', 'password': 'password', 'confirm_password': 'password'}
    response = client.post('/signin', data=data, follow_redirects=True)
    assert response.status_code == 200
