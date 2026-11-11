"""订单 CSV 导出。"""
import csv
import io
from shop.service import positive_integer


def export_orders(service, user_id):
    """将当前用户的订单导出为可下载的 CSV 文本。"""
    positive_integer(user_id, "用户编号")
    rows = service.db.execute(
        "SELECT id, status, subtotal_cents, total_cents, created_at FROM orders "
        "WHERE user_id = ? ORDER BY id", (user_id,)).fetchall()
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["订单编号", "状态", "原价（元）", "实付（元）", "创建时间"])
    for row in rows:
        writer.writerow([row["id"], row["status"],
                         row["subtotal_cents"] // 100,
                         row["total_cents"] // 100, row["created_at"]])
    return output.getvalue()
