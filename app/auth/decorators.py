# app/auth/decorators.py
from functools import wraps
from flask import abort
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. Cek apakah user sudah login
        if not current_user.is_authenticated:
            abort(403) # Forbidden (Dilarang)
        
        # 2. Cek apakah role user adalah 'admin'
        # Pastikan di database, user admin kolom role-nya berisi 'admin'
        if current_user.role != 'admin':
            abort(403) # Jika bukan admin, tampilkan Error 403
            
        return f(*args, **kwargs)
    return decorated_function