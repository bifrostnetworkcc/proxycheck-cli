"""轻量重试工具。

住宅/移动代理天然有一定的单次请求失败率(网络波动、出口节点切换等),
一次失败不代表代理真的不可用。这里提供一个简单的重试包装,用在
geoip / anonymity / dns_leak / speed 这几个"只测一次容易误判"的检测项上。

协议连通性测试(connectivity.check_all_protocols)故意不做重试——那里
测的就是"这次请求到底通不通",重试会让这个信号失真。
"""
import time


def call_with_retry(func, *args, attempts: int = 2, delay: float = 1.5, **kwargs) -> dict:
    """调用 func(*args, **kwargs),如果返回结果的 "ok" 字段是 False 就重试。

    要求 func 返回一个带 "ok" 字段的 dict(checks/* 各模块的统一返回格式)。
    返回最后一次尝试的结果,无论成功与否。
    """
    result = None
    for attempt in range(1, attempts + 1):
        result = func(*args, **kwargs)
        if result.get("ok"):
            return result
        if attempt < attempts:
            time.sleep(delay)
    return result
