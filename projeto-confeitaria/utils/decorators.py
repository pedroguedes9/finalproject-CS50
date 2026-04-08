from functools import wraps
from flask_login import current_user
from flask import flash, url_for, redirect

def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Acesso restrito a administradores.", "error")
            return redirect(url_for('index'))
        return view(*args, **kwargs)
    return wrapped
