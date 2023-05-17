import json

from flask import request, jsonify

from app.database import mongodb_client
from app.products import bp
from misc.utils import QueryParser, ProductRequest, ProductRequestByAttribute, ParamsParser


@bp.route('/<product_id>', methods=['GET'])
def get_product_by_id(product_id):
    cache_key = 'product id:{}'.format(product_id)
    res = ProductRequestByAttribute({"id": int(product_id)}).get(cache_key)
    return res


@bp.route('/', methods=['GET'])
def get_all_products():
    cache_key = "products all"
    res = ProductRequest({}).get(cache_key)
    return res


@bp.route('/query', methods=['POST'])
def get_products_by_query():
    if request.method == 'POST':
        names = ['page', 'sort_by', 'sort_order', 'limit']
        params = ParamsParser.get(names)

        format_query = QueryParser.parse_config(request.json)

        cache_key = "products query: {} params: {}".format(str(request.json), str(params))
        res = ProductRequest(format_query, params).get(cache_key)
        return res


@bp.route("/preload", methods=['POST'])
def preload_data():
    if request.method == 'POST':
        products_collection = mongodb_client.db.products
        # products_collection.drop()
        try:
            f = open("./prepared_data/laptop.json", "r")
            products = json.load(f)
            products_collection.insert_many(products)
        except FileNotFoundError as e:
            raise FileNotFoundError("Preload file not found.") from e
        else:
            f.close()
        return jsonify(message="success")
