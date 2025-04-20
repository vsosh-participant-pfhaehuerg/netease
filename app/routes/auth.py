from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
from app.modules.auth_manager import AuthManager

auth_bp = Blueprint('auth', __name__)
auth_manager = AuthManager()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not auth_manager.is_setup_complete():
            return redirect(url_for('auth.setup'))
        if 'authenticated' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/setup', methods=['GET', 'POST'])
def setup():
    if auth_manager.is_setup_complete():
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        if 'accept_license' not in request.form:
            flash('Необходимо принять лицензионное соглашение', 'error')
            return redirect(url_for('auth.setup'))

        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')

        if not password or len(password) < 6:
            flash('Пароль должен содержать минимум 6 символов', 'error')
            return redirect(url_for('auth.setup'))

        if password != password_confirm:
            flash('Пароли не совпадают', 'error')
            return redirect(url_for('auth.setup'))

        auth_manager.set_password(password)
        auth_manager.complete_setup()
        session['authenticated'] = True
        return redirect(url_for('main.index'))

    return render_template('auth/setup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if not auth_manager.is_setup_complete():
        return redirect(url_for('auth.setup'))

    if request.method == 'POST':
        password = request.form.get('password')
        if auth_manager.verify_password(password):
            session['authenticated'] = True
            return redirect(url_for('main.index'))
        flash('Неверный пароль', 'error')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('auth.login')) 