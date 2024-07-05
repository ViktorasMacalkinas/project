from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

from my_flask_app.auth import routes

from my_flask_app.forms import RegistrationForm

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Create new user instance
        new_user = User(username=form.username.data, email=form.email.data)
        new_user.set_password(form.password.data)

        # Add user to the database
        db.session.add(new_user)
        db.session.commit()

        flash('Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('auth.login'))  # Redirect to login page after successful registration

    return render_template('register.html', title='Register', form=form)

