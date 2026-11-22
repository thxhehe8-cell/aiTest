"""新增功能的正常路径验证。"""
from tests.test_orders import OrderTests
from shop.features import *


class FeatureTests(OrderTests):
    def test_feature_happy_path(self):
        self.create()
        self.assertEqual(len(search_orders(self.service, 10, "1")["items"]), 1)
