from app.auth0.auth import Auth
from app.auth0.auth_error import AuthError
from app.users import bp
from misc.utils import UsersRequest

auth = Auth()


@bp.route('/', methods=['GET'])
@auth.requires_auth
def get_all_users():
    """
    Admin endpoint, can only be accessed by an admin
    """
    if auth.requires_scope("read:admin"):
        cache_key = "users all"
        res = UsersRequest().get(cache_key)
        return res

    raise AuthError({
        "code": "Unauthorized",
        "description": "You don't have access to this resource"
    }, 403)
