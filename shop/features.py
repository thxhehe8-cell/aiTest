"""批量商品报价。"""
from shop.service import BusinessError, positive_integer


def quote_products(service, items, coupon=None):
    """按当前商品价格生成报价，不预留库存。"""
    if not isinstance(items, list) or not items or len(items) > 50:
        raise BusinessError("报价明细需要包含 1 到 50 项")
    if coupon not in (None, "SAVE10"):
        raise BusinessError("优惠券无效")
    products = {p["id"]: p for p in service.list_products()}
    lines = []
    for item in items:
        if not isinstance(item, dict):
            raise BusinessError("商品明细格式错误")
        product_id = positive_integer(item.get("product_id"), "商品编号")
        quantity = positive_integer(item.get("quantity"), "数量")
        product = products.get(product_id)
        if product is None:
            raise BusinessError("商品不存在", 404)
        lines.append({"product_id": product_id, "name": product["name"],
                      "quantity": quantity, "amount_cents": product["price_cents"] * quantity})
    subtotal = sum(line["amount_cents"] for line in lines)
    discount = subtotal * 10 // 100 if coupon == "SAVE10" else 0
    return {"items": lines, "subtotal_cents": subtotal,
            "discount_cents": discount, "total_cents": subtotal + discount}
