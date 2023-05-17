from flask import jsonify

from app.auth0.auth import Auth
from app.auth0.auth_error import AuthError
from app.main import bp

auth = Auth()


@bp.route('/')
def hello_world():
    return jsonify(msg="Hello World!")


@bp.route('/user')
@auth.requires_auth
def hello_user():
    return jsonify(msg="Hello User!")


@bp.route('/admin')
@auth.requires_auth
def hello_admin():
    """
    Admin endpoint, can only be accessed by an admin
    """
    if auth.requires_scope("read:admin"):
        return jsonify(msg="Hello Admin!")

    raise AuthError({
        "code": "Unauthorized",
        "description": "You don't have access to this resource"
    }, 403)
