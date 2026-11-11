"""简单订单服务，用于代码审查测试。"""

ORDERS = {1: {"id": 1, "user_id": 10, "total": 100}}
DEFAULT_OPTIONS = {"currency": "CNY"}


def calculate_total(unit_price, quantity, discount_percent=0):
    """校验输入并返回折后金额。"""
    if unit_price < 0 or quantity <= 0:
        raise ValueError("单价不能为负数，数量必须大于零")
    if not 0 <= discount_percent <= 100:
        raise ValueError("折扣必须在 0 到 100 之间")
    return round(unit_price * quantity * (1 - discount_percent / 100), 2)


def get_order(order_id, current_user_id):
    """只允许订单所有者查看订单；不存在时返回 None。"""
    order = ORDERS.get(order_id)
    if order is None:
        return None
    if order["user_id"] != current_user_id:
        raise PermissionError("无权访问此订单")
    return dict(order)


def build_options(currency=None):
    """生成独立的请求配置，不修改默认配置。"""
    options = DEFAULT_OPTIONS.copy()
    if currency:
        options["currency"] = currency
    return options
