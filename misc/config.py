import os

from dotenv import load_dotenv

from app.carts import bp as carts_bp
from app.main import bp as main_bp
from app.products import bp as products_bp
from app.users import bp as users_bp
from app.vouchers import bp as vouchers_bp

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    MONGO_URI = os.getenv('MONGO_URI')
    apis = [{
        "prefix": "/api/v1/",
        "bp": main_bp
    }, {
        "prefix": "/api/v1/products",
        "bp": products_bp
    }, {
        "prefix": "/api/v1/users",
        "bp": users_bp
    }, {
        "prefix": "/api/v1/carts",
        "bp": carts_bp
    }, {
        "prefix": "/api/v1/vouchers",
        "bp": vouchers_bp
    }]
