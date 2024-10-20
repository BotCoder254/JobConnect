from flask import abort
from flask_login import current_user

def check_role(required_role):
    if not current_user.is_authenticated or current_user.role != required_role:
        abort(403)
