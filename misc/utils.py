import json
import os

import redis
from bson import json_util
from dotenv import load_dotenv
from flask import make_response, request

from app.database import mongodb_client

load_dotenv()


class ParamsParser:
    @staticmethod
    def get(names):
        params = {}
        for name in names:
            params[name] = request.args.get(name)

        return params


class QueryParser:
    # User may query complex search with configurable, this function helps automate it
    @staticmethod
    def parse_config(params):
        query = {}
        if len(params) != 0:
            query = {"$and": []}

        processed_key = []

        for key in params:
            if key in processed_key:
                continue
            try:
                multichoice = []
                for value in params[key]:
                    # Query color
                    if key == "color":
                        option_name = "Màu"
                        multichoice.append(
                            {
                                "attributes.configurable_options": {
                                    "$elemMatch": {
                                        "$elemMatch": {
                                            "name": option_name,
                                            "values": {
                                                "$elemMatch": {
                                                    "label": value
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        )
                    # Query screen size
                    elif key == "screen_size":
                        multichoice.append(
                            {
                                "attributes.specifications.attributes": {
                                    "$elemMatch": {
                                        "code": "screen_size",
                                        "value": value
                                    }
                                }
                            }

                        )
                    elif key == "price1":
                        if params['price2'] is not None:
                            multichoice.append(
                                {
                                    "price": {
                                        "$gt": value,
                                        "$lt": params['price2'][0]
                                    }
                                }
                            )
                        processed_key.append('price2')
                    # Any other query
                    else:
                        multichoice.append({key: value})

                    query["$and"].append({"$or": multichoice})
            except KeyError as e:
                raise KeyError("Query return KeyError.") from e
        return query


class Handler:
    def get(self, cache_key):
        raise NotImplementedError


def update_params(params):
    defaults = {'limit': int(os.getenv('QUERY_LIMIT')),
                'page': 1,
                'sort_order': int(os.getenv('QUERY_DEFAULT_ORDER')),
                'sort_by': os.getenv('QUERY_DEFAULT_SORT')}

    if params is None:
        return defaults
    else:
        for key in params:
            if params[key] is None:
                params[key] = defaults[key]

        return params


class Request:
    def __init__(self, attributes=None, params=None):
        self.attributes = attributes
        self.params = update_params(params)

    def mongoDbQuery(self):
        raise NotImplementedError

    def get(self, cache_key):
        cache_data = RedisHandler().get(cache_key)
        if cache_data:
            return self.make_response(cache_data, 200)
        data = self.mongoDbQuery()
        RedisHandler().set(cache_key, data)
        return self.make_response(data, 200)

    @staticmethod
    def make_response(data, code):
        res = make_response(data)
        res.status_code = code
        res.headers['Content-Type'] = 'application/json'
        return res


class RedisHandler(Handler):
    def __init__(self):
        self.rds = redis.StrictRedis(port=6379, db=0)

    def set(self, cache_key, api):
        cache_time = os.getenv('CACHE_SECOND')
        api = json.dumps(api, ensure_ascii=False).encode('utf8')
        self.rds.set(cache_key, api)
        self.rds.expire(cache_key, int(cache_time))

    def get(self, cache_key):
        cacheData = self.rds.get(cache_key)
        if cacheData:
            cacheData = cacheData.decode('utf-8')
            cacheData = json.loads(cacheData)
            return cacheData
        else:
            return None


class ProductRequest(Request):

    def mongoDbQuery(self):
        skip = (int(self.params['page']) - 1) * int(os.getenv('QUERY_LIMIT'))
        products = mongodb_client.db.products.find(self.attributes).skip(skip) \
            .sort(self.params['sort_by'], int(self.params['sort_order'])).limit(int(self.params['limit']))
        data = json_util.dumps(products)
        return data


class ProductRequestByAttribute(Request):

    def mongoDbQuery(self):
        products = mongodb_client.db.products.find_one(self.attributes)
        data = json_util.dumps(products)
        return data


class UsersRequest(Request):
    def mongoDbQuery(self):
        users = mongodb_client.db.users.find()
        return json_util.dumps(users)


class CartRequestByAttribute(Request):
    def mongoDbQuery(self):
        carts = mongodb_client.db.carts.find_one(self.attributes)
        return json_util.dumps(carts)

    def get(self, cache_key):
        data = self.mongoDbQuery()
        return self.make_response(data, 200)


class VoucherRequest(Request):
    def mongoDbQuery(self):
        carts = mongodb_client.db.vouchers.find_one(self.attributes)
        return json_util.dumps(carts)


class CartsRequestByAttribute(Request):
    def mongoDbQuery(self):
        carts = mongodb_client.db.carts.find(self.attributes)
        return json_util.dumps(carts)

    def get(self, cache_key):
        data = self.mongoDbQuery()
        return self.make_response(data, 200)
