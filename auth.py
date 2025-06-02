from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa estar logado para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from models import Usuario
            if 'user_id' not in session:
                flash('Você precisa estar logado para acessar esta página.', 'warning')
                return redirect(url_for('login'))
            
            user = Usuario.query.get(session['user_id'])
            if not user:
                flash('Usuário não encontrado.', 'error')
                return redirect(url_for('login'))
            
            # Admin tem acesso a tudo
            if user.admin:
                return f(*args, **kwargs)
            
            # Verificar permissão específica
            if not getattr(user, f'perm_{permission}', False):
                flash('Você não tem permissão para acessar esta página.', 'error')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_current_user():
    from models import Usuario
    if 'user_id' in session:
        return Usuario.query.get(session['user_id'])
    return None

def get_current_empresa():
    from models import Empresa
    if 'empresa_id' in session:
        return Empresa.query.get(session['empresa_id'])
    return None
