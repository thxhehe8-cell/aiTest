"""订单业务与事务边界，金额统一使用整数分。"""


class BusinessError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def positive_integer(value, name):
    if type(value) is not int or value <= 0:
        raise BusinessError(f"{name}必须是正整数")
    return value


class OrderService:
    def __init__(self, db):
        self.db = db

    def list_products(self):
        return [dict(row) for row in self.db.execute(
            "SELECT id, name, price_cents, stock FROM products ORDER BY id"
        )]

    def create_order(self, user_id, items, coupon=None):
        positive_integer(user_id, "用户编号")
        if not isinstance(items, list) or not 1 <= len(items) <= 50:
            raise BusinessError("商品明细需要包含 1 到 50 项")
        quantities = {}
        for item in items:
            if not isinstance(item, dict):
                raise BusinessError("商品明细格式错误")
            product_id = positive_integer(item.get("product_id"), "商品编号")
            quantity = positive_integer(item.get("quantity"), "数量")
            quantities[product_id] = quantities.get(product_id, 0) + quantity
        if coupon not in (None, "SAVE10"):
            raise BusinessError("优惠券无效")
        # 在读取库存前获取写锁，保证检查与扣减处于同一事务。
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            lines = []
            for product_id, quantity in quantities.items():
                product = self.db.execute(
                    "SELECT * FROM products WHERE id = ?", (product_id,)
                ).fetchone()
                if product is None:
                    raise BusinessError("商品不存在", 404)
                if product["stock"] < quantity:
                    raise BusinessError("库存不足", 409)
                lines.append((product_id, quantity, product["price_cents"]))
            subtotal = sum(quantity * price for _, quantity, price in lines)
            total = subtotal * 90 // 100 if coupon == "SAVE10" else subtotal
            cursor = self.db.execute(
                "INSERT INTO orders(user_id, status, subtotal_cents, total_cents) "
                "VALUES (?, 'pending', ?, ?)", (user_id, subtotal, total)
            )
            order_id = cursor.lastrowid
            for product_id, quantity, price in lines:
                self.db.execute("INSERT INTO order_items VALUES (?, ?, ?, ?)",
                                (order_id, product_id, quantity, price))
                self.db.execute("UPDATE products SET stock = stock - ? WHERE id = ?",
                                (quantity, product_id))
        return self.get_order(order_id, user_id)

    def get_order(self, order_id, user_id):
        positive_integer(order_id, "订单编号")
        positive_integer(user_id, "用户编号")
        row = self.db.execute(
            "SELECT * FROM orders WHERE id = ? AND user_id = ?", (order_id, user_id)
        ).fetchone()
        if row is None:
            raise BusinessError("订单不存在", 404)
        result = dict(row)
        result["items"] = [dict(item) for item in self.db.execute(
            "SELECT product_id, quantity, price_cents FROM order_items "
            "WHERE order_id = ? ORDER BY product_id", (order_id,)
        )]
        return result

    def cancel_order(self, order_id, user_id):
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            order = self.get_order(order_id, user_id)
            if order["status"] == "cancelled":
                return order
            for item in order["items"]:
                self.db.execute("UPDATE products SET stock = stock + ? WHERE id = ?",
                                (item["quantity"], item["product_id"]))
            self.db.execute("UPDATE orders SET status = 'cancelled' WHERE id = ?",
                            (order_id,))
        return self.get_order(order_id, user_id)
