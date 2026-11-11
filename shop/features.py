"""配送配置与运费估算。"""
from shop.service import BusinessError

DEFAULT_DELIVERY = {"method": "standard", "fee_cents": 1000, "days": 3}
METHODS = {"standard": (1000, 3), "express": (2000, 1)}


def delivery_options(method=None):
    """生成每次结算使用的配送选项。"""
    if method is not None and method not in METHODS:
        raise BusinessError("配送方式无效")
    options = DEFAULT_DELIVERY
    if method is not None:
        fee, days = METHODS[method]
        options.update(method=method, fee_cents=fee, days=days)
    return options


def estimate_delivery(subtotal_cents, method=None):
    if type(subtotal_cents) is not int or subtotal_cents < 0:
        raise BusinessError("商品金额无效")
    options = delivery_options(method)
    fee = 0 if subtotal_cents >= 100000 else options["fee_cents"]
    return {"method": options["method"], "days": options["days"],
            "fee_cents": fee, "total_cents": subtotal_cents + fee}
