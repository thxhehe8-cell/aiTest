# AI Review Agent 测试项目

## 背景与目标

使用无第三方依赖的 Python 订单服务测试 GitHub PR 自动审查。建议 Python 3.10 及以上版本。

## 总体设计

`order.py` 提供金额计算、订单权限校验和独立请求配置；数据保存在内存中。`test_order.py` 提供最小回归测试，无需数据库或网络服务。

## 核心接口与流程

- `calculate_total(unit_price, quantity, discount_percent=0)`：校验单价、数量、折扣，返回折后金额，非法值抛出 ValueError。
- `get_order(order_id, current_user_id)`：查询订单并校验所有者，返回副本；不存在返回 None，越权抛出 PermissionError。
- `build_options(currency=None)`：返回独立配置，默认币种为 CNY。

## 审查样例

每个分支均直接基于 main，创建 PR 时以 main 为目标分支：

| 分支 | 预期识别的问题 |
| --- | --- |
| codex/review-discount | 折扣计算方向错误，折扣反而增加金额 |
| codex/review-authorization | 缺少所有者校验，可读取其他用户订单 |
| codex/review-shared-state | 直接修改默认字典，导致后续请求受到污染 |

这些问题是故意注入的测试样例，不应合并到 main。要进行盲测，可不向 Agent 提供本说明。

## 最小验证

在任意分支执行 `python -m unittest -v`。main 预期全部通过，各样例分支预期各有一个相关测试失败。

## 后续迭代

先验证 Agent 能否定位三个独立问题，再按需增加跨文件调用和复杂业务场景。
