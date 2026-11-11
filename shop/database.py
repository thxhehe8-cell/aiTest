"""数据库连接、表结构与演示数据。"""
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY, name TEXT NOT NULL,
    price_cents INTEGER NOT NULL CHECK(price_cents >= 0),
    stock INTEGER NOT NULL CHECK(stock >= 0)
);
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('pending', 'cancelled')),
    subtotal_cents INTEGER NOT NULL, total_cents INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS order_items (
    order_id INTEGER NOT NULL REFERENCES orders(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    price_cents INTEGER NOT NULL,
    PRIMARY KEY(order_id, product_id)
);
"""


def connect(path):
    """为每次请求建立独立连接，并开启外键校验。"""
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def initialize(db):
    db.executescript(SCHEMA)
    with db:
        db.executemany(
            "INSERT OR IGNORE INTO products VALUES (?, ?, ?, ?)",
            [(1, "机械键盘", 29900, 20), (2, "无线鼠标", 9900, 50),
             (3, "桌面支架", 15900, 15)],
        )
