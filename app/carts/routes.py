import json

from bson import ObjectId
from flask import request, jsonify

from app.auth0.auth import Auth
from app.carts import bp
from app.carts.cart import Cart
from app.database import mongodb_client
from app.products import Product
from app.vouchers.voucher import Voucher
from misc.utils import CartRequestByAttribute, CartsRequestByAttribute

auth = Auth()


@bp.route('/by_id/<cart_id>', methods=['GET'])
@auth.requires_auth
def get_cart_by_id(cart_id):
    cache_key = 'cart id:{}'.format(cart_id)
    res = CartRequestByAttribute({"_id": ObjectId(cart_id + "")}).get(cache_key)
    return res


@bp.route('/by_user_id/<user_id>', methods=['GET'])
@auth.requires_auth
def get_carts_from_user(user_id):
    cache_key = 'cart id:{}'.format(user_id)
    res = CartsRequestByAttribute({"user_id": user_id, "state": "Incomplete"}).get(cache_key)
    if len(res.json) == 0:
        print("Creating new cart")
        res = post_new_cart(user_id)
    return res


def post_new_cart(user_id):
    carts_collection = mongodb_client.db.carts
    cart = Cart(
        {
            'user_id': user_id,
            'products': [],
            'vouchers': [],
            'discount_products': [],
            'total_payment': 0,
            'state': "Incomplete"
        }
    )
    carts_collection.insert_one(cart.to_dict())
    return jsonify(message="success")


@bp.route('/post', methods=['POST'])
@auth.requires_auth
def create_new_cart():
    if request.method == 'POST':
        user_id = request.json['user_id']
        post_new_cart(user_id)


@bp.route('/post_to_cart/<cart_id>', methods=['POST'])
@auth.requires_auth
def insert_new_product_to_cart(cart_id):
    if request.method == 'POST':
        cart_obj = get_cart_object(cart_id)
        cart_obj.add_product(Product(request.json['product']))
        update_cart(cart_id, cart_obj)

        return jsonify(message="success")


@bp.route('/delete/<cart_id>/<product_id>', methods=['DELETE'])
@auth.requires_auth
def delete_product_from_cart(cart_id, product_id):
    if request.method == 'DELETE':
        cart_obj = get_cart_object(cart_id)
        cart_obj.remove_product_by_id(product_id)
        update_cart(cart_id, cart_obj)

        return jsonify(message="success")


@bp.route('/complete/<cart_id>', methods=['POST'])
@auth.requires_auth
def set_complete(cart_id):
    if request.method == 'POST':
        cart_obj = get_cart_object(cart_id)
        cart_obj.set_completed()
        update_cart(cart_id, cart_obj)

        return jsonify(message="success")


@bp.route('/use_voucher/<cart_id>', methods=['POST'])
@auth.requires_auth
def use_voucher(cart_id):
    if request.method == 'POST':
        cart_obj = get_cart_object(cart_id)
        cart_obj.add_voucher(request.json['product_id'], Voucher(request.json['voucher']))
        update_cart(cart_id, cart_obj)

        return jsonify(message="success")


def get_cart_object(cart_id):
    cart = get_cart_by_id(cart_id).data
    cart_json = json.loads(cart.decode('utf-8'))

    return Cart(cart_json)


def update_cart(cart_id, cart_obj):
    carts_collection = mongodb_client.db.carts
    cart = cart_obj.to_dict()
    carts_collection.update_one(
        {"_id": ObjectId(cart_id)},
        {"$set": {"products": cart['products'],
                  "total_payment": cart['total_payment'],
                  "discount_products": cart['discount_products'],
                  "vouchers": cart['vouchers'],
                  "state": cart['state']
                  }
         }
    )
