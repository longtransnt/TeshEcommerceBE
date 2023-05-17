from flask import Blueprint

bp = Blueprint('products', __name__)
from app.products import routes


class Product:
    def __init__(self, product,
                 **kwargs):
        self.id = product['id']
        self.sku = product['sku']
        self.name = product['name']
        self.href = product['href']
        self.seller_name = product['seller_name']
        self.brand_name = product['brand_name']
        self.price = product['price']
        self.primary_category_name = product['primary_category_name']
        self.review_count = product['review_count']
        self.thumbnail_url = product['thumbnail_url']

        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        return vars(self)
