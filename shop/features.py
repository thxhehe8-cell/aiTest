"""购物车库存预览。"""
from shop.service import BusinessError, positive_integer


def preview_cart(service, items):
    """返回商品展示信息与库存是否满足，不写入数据库。"""
    if not isinstance(items, list) or not 1 <= len(items) <= 50:
        raise BusinessError("购物车需要包含 1 到 50 项")
    products = {p["id"]: p for p in service.list_products()}
    quantities = {}
    for item in items:
        if not isinstance(item, dict):
            raise BusinessError("商品明细格式错误")
        product_id = positive_integer(item.get("product_id"), "商品编号")
        quantity = item.get("quantity")
        if type(quantity) is not int or quantity < 0:
            raise BusinessError("数量必须是正整数")
        quantities[product_id] = quantities.get(product_id, 0) + quantity
    result = []
    for product_id, quantity in quantities.items():
        product = products.get(product_id)
        if product is None:
            raise BusinessError("商品不存在", 404)
        result.append({"product_id": product_id, "name": product["name"],
                       "quantity": quantity, "available": product["stock"] >= quantity,
                       "amount_cents": product["price_cents"] * quantity})
    return {"items": result, "subtotal_cents": sum(i["amount_cents"] for i in result)}
