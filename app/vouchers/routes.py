from flask import request, jsonify

from app.database import mongodb_client
from app.vouchers import bp
from app.vouchers.voucher import Voucher
from misc.utils import VoucherRequest


@bp.route('/post', methods=['POST'])
def post_new_voucher():
    if request.method == 'POST':
        vouchers_collection = mongodb_client.db.vouchers
        payload = request.json
        voucher = Voucher(
            {
                'voucher_id': payload['voucher_id'],
                'voucher_code': payload['voucher_code'],
                'voucher_discount': payload['voucher_discount'],
                'voucher_type': payload['voucher_type']
            }
        )
        vouchers_collection.insert_one(voucher.to_dict())
        return jsonify(message="success")


@bp.route('/<voucher_code>', methods=['GET'])
def get_voucher(voucher_code):
    print(voucher_code)
    cache_key = 'voucher code:{}'.format(voucher_code)
    res = VoucherRequest({"voucher_code": voucher_code}).get(cache_key)
    return res
