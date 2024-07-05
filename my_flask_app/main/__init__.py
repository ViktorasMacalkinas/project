# main/__init__.py

from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

from my_flask_app.main import routes

from my_flask_app import models

@main_bp.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/about')
def about():
    return render_template('about.html')

from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404
