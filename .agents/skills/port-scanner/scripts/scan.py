#!/usr/bin/env python3
"""
端口扫描脚本 - Port Scanner Skill 的脚本组件

功能：
    使用 TCP 连接扫描目标主机的端口状态

用法：
    python scan.py <host> <port1,port2,...>

示例：
    python scan.py localhost 80,443,22
    python scan.py 192.168.1.1 3306,5432
"""
import sys
import socket


def scan_port(host: str, port: int) -> str:
    """
    扫描单个端口

    Args:
        host: 目标主机 IP 或域名
        port: 端口号

    Returns:
        "open", "closed", 或 "error: ..."
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)  # 1 秒超时
            result = s.connect_ex((host, port))
            return "open" if result == 0 else "closed"
    except Exception as e:
        return f"error: {e}"


def main():
    if len(sys.argv) < 3:
        print("用法: python scan.py <host> <port1,port2,...>")
        print("示例: python scan.py localhost 80,443,22")
        sys.exit(1)

    host = sys.argv[1]
    ports_str = sys.argv[2]

    # 解析端口列表
    ports = [int(p.strip()) for p in ports_str.split(",")]

    print(f"扫描目标: {host}")
    print("-" * 30)

    for port in ports:
        status = scan_port(host, port)
        print(f"端口 {port}: {status}")


if __name__ == "__main__":
    main()
