"""新增功能的正常路径验证。"""
from tests.test_orders import OrderTests
from shop.features import *


class FeatureTests(OrderTests):
    def test_feature_happy_path(self):
        self.create()
        self.assertEqual(quote_products(self.service, [{"product_id": 1, "quantity": 1}])["total_cents"], 29900)
