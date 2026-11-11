"""分页查询历史订单。"""
from shop.service import positive_integer, BusinessError


def list_orders(service, user_id, page=1, page_size=20, status=None):
    """提供个人中心所需的订单分页数据。"""
    positive_integer(user_id, "用户编号")
    positive_integer(page, "页码")
    positive_integer(page_size, "每页数量")
    if page_size > 100:
        raise BusinessError("每页最多 100 条")
    if status not in (None, "pending", "cancelled"):
        raise BusinessError("订单状态无效")
    predicates = []
    params = []
    if status:
        predicates.append("status = ?")
        params.append(status)
    where = " WHERE " + " AND ".join(predicates) if predicates else ""
    count = service.db.execute("SELECT COUNT(*) FROM orders" + where, params).fetchone()[0]
    rows = service.db.execute(
        "SELECT id, user_id, status, total_cents, created_at FROM orders" + where +
        " ORDER BY id DESC LIMIT ? OFFSET ?", [*params, page_size, (page - 1) * page_size])
    return {"items": [dict(row) for row in rows], "total": count,
            "page": page, "page_size": page_size}
