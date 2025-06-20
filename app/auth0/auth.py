import json
import os
from functools import wraps

from dotenv import load_dotenv
from flask import request, _request_ctx_stack
from jose import jwt
from six.moves.urllib.request import urlopen

from app.auth0.auth_error import AuthError

load_dotenv()


class Auth:
    @staticmethod
    def get_token_auth_header():
        """Obtains the Access Token from the Authorization Header
        """
        auth = request.headers.get("Authorization", None)
        if not auth:
            raise AuthError({"code": "authorization_header_missing",
                             "description":
                                 "Authorization header is expected"}, 401)

        parts = auth.split()

        if parts[0].lower() != "bearer":
            raise AuthError({"code": "invalid_header",
                             "description":
                                 "Authorization header must start with"
                                 " Bearer"}, 401)
        elif len(parts) == 1:
            raise AuthError({"code": "invalid_header",
                             "description": "Token not found"}, 401)
        elif len(parts) > 2:
            raise AuthError({"code": "invalid_header",
                             "description":
                                 "Authorization header must be"
                                 " Bearer token"}, 401)

        token = parts[1]
        return token

    def requires_auth(self, f):
        """Determines if the Access Token is valid
        """

        @wraps(f)
        def decorated(*args, **kwargs):
            domain = os.getenv('AUTH0_DOMAIN')
            algorithms = [os.getenv('ALGORITHMS')]
            audience = os.getenv('API_AUDIENCE')
            token = self.get_token_auth_header()
            jsonurl = urlopen("https://" + domain + "/.well-known/jwks.json")
            jwks = json.loads(jsonurl.read())
            unverified_header = jwt.get_unverified_header(token)
            rsa_key = {}
            for key in jwks["keys"]:
                if key["kid"] == unverified_header["kid"]:
                    rsa_key = {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "use": key["use"],
                        "n": key["n"],
                        "e": key["e"]
                    }
            if rsa_key:
                try:
                    payload = jwt.decode(
                        token,
                        rsa_key,
                        algorithms=algorithms,
                        audience=audience,
                        issuer="https://{}/".format(domain)
                    )
                except jwt.ExpiredSignatureError as e:
                    raise AuthError({"code": "token_expired",
                                     "description": "token is expired"}, 401) from e
                except jwt.JWTClaimsError as e:
                    raise AuthError({"code": "invalid_claims",
                                     "description":
                                         "incorrect claims,"
                                         "please check the audience and issuer"}, 401) from e
                except Exception as e:
                    raise AuthError({"code": "invalid_header",
                                     "description":
                                         "Unable to parse authentication"
                                         " token."}, 401) from e

                _request_ctx_stack.top.current_user = payload
                return f(*args, **kwargs)
            raise AuthError({"code": "invalid_header",
                             "description": "Unable to find appropriate key"}, 401)

        return decorated

    def requires_scope(self, required_scope):
        """Determines if the required scope is present in the Access Token
        Args:
            required_scope (str): The scope required to access the resource
        """
        token = self.get_token_auth_header()
        unverified_claims = jwt.get_unverified_claims(token)
        if unverified_claims.get("scope"):
            token_scopes = unverified_claims["scope"].split()
            for token_scope in token_scopes:
                if token_scope == required_scope:
                    return True
        return False
