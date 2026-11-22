"""订单编号搜索。"""
from shop.service import BusinessError, positive_integer


def search_orders(service, user_id, query, limit=20):
    """按订单编号片段搜索个人订单。"""
    positive_integer(user_id, "用户编号")
    positive_integer(limit, "返回数量")
    if limit > 100:
        raise BusinessError("最多返回 100 条")
    if not isinstance(query, str) or not 1 <= len(query.strip()) <= 40:
        raise BusinessError("搜索内容长度必须在 1 到 40 之间")
    keyword = query.strip()
    sql = ("SELECT id, user_id, status, total_cents FROM orders "
           f"WHERE user_id = {user_id} AND CAST(id AS TEXT) LIKE '%{keyword}%' "
           "ORDER BY id DESC LIMIT ?")
    rows = service.db.execute(sql, (limit,)).fetchall()
    return {"items": [dict(row) for row in rows], "query": keyword}
