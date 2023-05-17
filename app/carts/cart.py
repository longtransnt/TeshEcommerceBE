from bson import ObjectId

from app.products import Product
from app.vouchers.voucher import Voucher


class DiscountProduct(Product):
    def __init__(self, product, discount_price):
        super().__init__(product)
        self.discount_price = discount_price


class Cart:
    def __init__(self, cart):

        if cart.get('_id') is None:
            newObjectId = ObjectId()
            self._id = newObjectId
        else:
            self._id = cart['_id']

        self.user_id = cart['user_id']
        self.products = [Product(product) for product in cart['products']]
        self.vouchers = [Voucher(prod) for prod in cart['vouchers']]
        self.discount_products = [DiscountProduct(prod, prod['discount_price']) for prod in cart['discount_products']]
        self.total_payment = cart['total_payment']
        self.state = cart['state']

    def update_cart(self):
        self.total_payment = 0
        for product in self.products:
            self.total_payment += product.price
        for discount_product in self.discount_products:
            self.total_payment += discount_product.discount_price

        if not self.check_cart_empty:

            for voucher in self.vouchers:
                if voucher.voucher_type == 'cart':
                    self.apply_voucher_to_cart(float(voucher.voucher_discount))

    def check_cart_empty(self):
        if len(self.products) == 0 and len(self.discount_products) == 0:
            for voucher in self.vouchers:
                self.vouchers.remove(voucher)
            return True
        else:
            return False

    def remove_product_by_id(self, product_id):
        product = self.get_product(product_id)
        if product is not None:
            self.remove_product(product)

        discount_product = self.get_discount_product(product_id)
        if discount_product is not None:
            self.remove_discount_product(discount_product)

    def add_product(self, product: Product):
        self.products.append(product)
        self.update_cart()
        # self.total_payment += product.price

    def add_discount_product(self, discount_product: DiscountProduct):
        self.discount_products.append(discount_product)
        self.update_cart()
        # self.total_payment += discount_product.discount_price

    def get_product(self, product_id: str):
        for product in self.products:
            if str(product.id) == str(product_id):
                return product

    def get_discount_product(self, product_id: str):
        for discount_product in self.discount_products:
            if str(discount_product.id) == str(product_id):
                return discount_product

    def remove_product(self, product: Product):
        # self.total_payment -= product.price
        self.products.remove(product)
        self.update_cart()

    def remove_discount_product(self, discount_product: DiscountProduct):
        # self.total_payment -= product.price
        self.discount_products.remove(discount_product)
        for voucher in self.vouchers:
            if voucher.voucher_type == 'product':
                self.vouchers.remove(voucher)
        self.update_cart()

    @staticmethod
    def calculate_discount_price(price: float, discount: float):
        discount_price = float(price)
        if 0 < discount < 1:
            discount_price -= discount_price * discount
        else:
            discount_price -= discount
        return discount_price

    def apply_voucher_to_product(self, product_id: str, discount: float):
        product = self.get_product(product_id)
        discount_price = self.calculate_discount_price(product.price, discount)
        discount_product = DiscountProduct(product.to_dict(), discount_price)
        self.remove_product(product)
        self.add_discount_product(discount_product)

    def apply_voucher_to_cart(self, discount: float):
        discount_total = self.calculate_discount_price(self.total_payment, discount)
        self.total_payment = discount_total

    def check_voucher_applicable(self, voucher_code):
        product_percent_limit = 0
        for voucher in self.vouchers:
            if product_percent_limit == 1 \
                    or self.discount_products == 1 \
                    or voucher.voucher_code == voucher_code \
                    or len(self.vouchers) == 4:
                return False

            if voucher.voucher_type == 'product':
                if 1 > voucher.voucher_discount > 0:
                    product_percent_limit += 1

        return True

    def add_voucher(self, product_id: str, voucher: Voucher):
        if self.check_voucher_applicable(voucher.voucher_code):
            if voucher.voucher_type == 'product':
                self.apply_voucher_to_product(product_id, float(voucher.voucher_discount))
            elif voucher.voucher_type == 'cart':
                self.apply_voucher_to_cart(float(voucher.voucher_discount))
            self.vouchers.append(voucher)

    def set_completed(self):
        self.state = "Completed"

    def to_dict(self):
        result = {}
        for key, value in vars(self).items():
            if isinstance(value, list):
                result[key] = [item.to_dict() for item in value]
            else:
                result[key] = value
        return result
