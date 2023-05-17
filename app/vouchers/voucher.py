class Voucher:
    def __init__(self, voucher):
        self.voucher_id = voucher['voucher_id']
        self.voucher_code = voucher['voucher_code']
        self.voucher_type = voucher['voucher_type']
        self.voucher_discount = voucher['voucher_discount']

    def validate(self):
        return self.voucher_type

    def to_dict(self):
        return vars(self)
