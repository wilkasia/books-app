import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor(dictionary=True)
        error = None

        if not name:
            error = 'Name is required.'
        elif not surname:
            error = 'Surname is required.'
        elif not email:
            error = 'E-mail is required.'
        elif not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        else:
            cursor.execute(
                'SELECT id FROM user WHERE username = %s', (username,)
            )
            user = cursor.fetchone()
            if user:
                error = 'User {} is already registered.'.format(username)
            else:
                cursor.execute(
                    'SELECT id FROM user WHERE email = %s', (email,)
                )
                user = cursor.fetchone()
                if user:
                    error = 'E-mail {} exists in database.'.format(email)

        if error is None:
            cursor.execute(
                'INSERT INTO user (username, password, name, surname, email) VALUES (%s, %s, %s, %s, %s)',
                (username, generate_password_hash(password), name, surname, email)
            )
            db.commit()
            return redirect(url_for('auth.login'))

        cursor.close()
        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            'SELECT * FROM user WHERE username = %s', (username,)
        )
        user = cursor.fetchone()
        cursor.close()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        cursor = get_db().cursor(dictionary=True)
        cursor.execute(
            'SELECT * FROM user WHERE id = %s', (user_id,)
        )
        g.user = cursor.fetchone()
        cursor.close()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
