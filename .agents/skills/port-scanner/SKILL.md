---
name: port-scanner
description: 扫描目标主机的端口开放情况。当用户需要检查端口、扫描主机、检查服务是否运行时激活。
---

# 端口扫描 Skill

使用 TCP 连接扫描目标主机的端口状态。这是一个带参数传递的 Skill 示例。

## 工作流程

1. 解析用户提供的目标主机和端口
2. 执行端口扫描脚本
3. 返回扫描结果

## 可用脚本

### scan.py - 端口扫描器

```bash
python scripts/scan.py <host> <port1,port2,...>
```

参数：
- `host`: 目标主机 IP 或域名（必需）
- `ports`: 要扫描的端口列表，逗号分隔（必需）

示例：
```bash
# 扫描本地常用端口
python scripts/scan.py localhost 80,443,22,3306

# 扫描 Web 端口
python scripts/scan.py example.com 80,443,8080

# 扫描数据库端口
python scripts/scan.py db.server.local 3306,5432,27017,6379
```

输出格式：
```
扫描目标: localhost
端口 80: open
端口 443: closed
端口 22: open
端口 3306: closed
```

## 常用端口参考

| 端口 | 服务 |
|------|------|
| 22 | SSH |
| 80 | HTTP |
| 443 | HTTPS |
| 3306 | MySQL |
| 5432 | PostgreSQL |
| 6379 | Redis |
| 27017 | MongoDB |
| 8080 | HTTP 代理/替代 |

## 技术说明

- 使用 Python `socket` 模块进行 TCP 连接测试
- 每个端口超时时间为 1 秒
- 扫描顺序按端口列表顺序执行
