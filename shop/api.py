"""基于标准库的演示 HTTP 接口。"""
import json
import logging
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from shop.database import connect, initialize
from shop.service import BusinessError, OrderService, positive_integer

LOGGER = logging.getLogger(__name__)
DATABASE = os.environ.get("SHOP_DATABASE", "shop.db")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.dispatch()

    def do_POST(self):
        self.dispatch()

    def read_body(self):
        try:
            size = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            raise BusinessError("请求长度无效")
        if not 0 < size <= 65536:
            raise BusinessError("请求体需要在 1 到 65536 字节之间")
        try:
            body = json.loads(self.rfile.read(size))
        except (ValueError, UnicodeError):
            raise BusinessError("JSON 格式错误")
        if not isinstance(body, dict):
            raise BusinessError("请求体必须是对象")
        return body

    def dispatch(self):
        db = connect(DATABASE)
        try:
            service = OrderService(db)
            if self.command == "GET" and self.path == "/products":
                data = service.list_products()
            else:
                # 仅用于本地演示；生产环境应替换为经过认证的用户身份。
                try:
                    user_id = int(self.headers.get("X-User-Id", "0"))
                except ValueError:
                    raise BusinessError("用户身份无效", 401)
                positive_integer(user_id, "用户编号")
                match = re.fullmatch(r"/orders/([1-9][0-9]*)(/cancel)?", self.path)
                if self.command == "POST" and self.path == "/orders":
                    body = self.read_body()
                    data = service.create_order(user_id, body.get("items"), body.get("coupon"))
                elif match and self.command == "GET" and not match[2]:
                    data = service.get_order(int(match[1]), user_id)
                elif match and self.command == "POST" and match[2]:
                    data = service.cancel_order(int(match[1]), user_id)
                else:
                    raise BusinessError("接口不存在", 404)
            self.respond(200, {"data": data})
        except BusinessError as error:
            self.respond(error.status, {"error": str(error)})
        except Exception:
            LOGGER.exception("处理请求失败")
            self.respond(500, {"error": "服务内部错误"})
        finally:
            db.close()

    def respond(self, status, body):
        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def main():
    db = connect(DATABASE)
    try:
        initialize(db)
    finally:
        db.close()
    logging.basicConfig(level=logging.INFO)
    server = ThreadingHTTPServer(("127.0.0.1", 8000), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
