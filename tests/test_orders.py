"""订单主流程、校验、权限与事务回归测试。"""
import unittest
from shop.database import connect, initialize
from shop.service import BusinessError, OrderService


class OrderTests(unittest.TestCase):
    def setUp(self):
        self.db = connect(":memory:")
        initialize(self.db)
        self.service = OrderService(self.db)

    def tearDown(self):
        self.db.close()

    def create(self, **kwargs):
        return self.service.create_order(10, [{"product_id": 1, "quantity": 2}], **kwargs)

    def test_create_and_discount(self):
        order = self.create(coupon="SAVE10")
        self.assertEqual(order["total_cents"], 53820)
        self.assertEqual(self.service.list_products()[0]["stock"], 18)

    def test_access_is_scoped_to_owner(self):
        order = self.create()
        with self.assertRaises(BusinessError):
            self.service.get_order(order["id"], 20)

    def test_cancel_is_idempotent(self):
        order = self.create()
        for _ in range(2):
            self.service.cancel_order(order["id"], 10)
        self.assertEqual(self.service.list_products()[0]["stock"], 20)

    def test_insufficient_stock_rolls_back(self):
        with self.assertRaises(BusinessError):
            self.service.create_order(10, [{"product_id": 1, "quantity": 1},
                                           {"product_id": 2, "quantity": 100}])
        self.assertEqual(self.service.list_products()[0]["stock"], 20)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM orders").fetchone()[0], 0)

    def test_duplicate_items_are_merged(self):
        order = self.service.create_order(10, [{"product_id": 1, "quantity": 1}] * 2)
        self.assertEqual(order["items"][0]["quantity"], 2)

    def test_invalid_quantity(self):
        for quantity in (0, -1, True, "2"):
            with self.subTest(quantity=quantity), self.assertRaises(BusinessError):
                self.service.create_order(10, [{"product_id": 1, "quantity": quantity}])

    def test_missing_order(self):
        with self.assertRaises(BusinessError) as error:
            self.service.get_order(999, 10)
        self.assertEqual(error.exception.status, 404)

    def test_invalid_coupon(self):
        with self.assertRaises(BusinessError):
            self.create(coupon="UNKNOWN")


if __name__ == "__main__":
    unittest.main()
