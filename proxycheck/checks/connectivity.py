"""代理连通性检测:分别用 http / https / socks5 / socks5h 协议前缀
尝试通过代理请求一个公开的回显接口,记录是否成功以及延迟。
"""
import time
import requests

from ..progress import log

TEST_URL = "https://httpbingo.org/get"


def _build_proxies(proxy_url: str) -> dict:
    return {"http": proxy_url, "https": proxy_url}


def check_protocol(proxy_url: str, timeout: float = 15.0) -> dict:
    """对单个 proxy_url(已包含协议前缀)发起一次探测请求。"""
    proxies = _build_proxies(proxy_url)
    result = {"proxy": proxy_url, "ok": False, "latency_ms": None, "error": None}
    start = time.perf_counter()
    try:
        resp = requests.get(TEST_URL, proxies=proxies, timeout=timeout)
        resp.raise_for_status()
        result["ok"] = True
        result["latency_ms"] = round((time.perf_counter() - start) * 1000, 1)
        result["status_code"] = resp.status_code
    except requests.exceptions.RequestException as exc:
        result["error"] = str(exc)
    return result


def check_all_protocols(host: str, port: int, username: str = None, password: str = None,
                         quiet: bool = False) -> list:
    """依次拼出 http / https / socks5 / socks5h 的代理URL并逐个测试。

    每个协议测试开始/结束都会打印一行提示(除非 quiet=True)。

    注意: socks5 用户认证需要安装 PySocks(requirements.txt 已包含)。
    """
    auth = f"{username}:{password}@" if username and password else ""
    schemes = ["http", "https", "socks5", "socks5h"]
    results = []
    for scheme in schemes:
        proxy_url = f"{scheme}://{auth}{host}:{port}"
        log(f"    测试 {scheme} 中...", quiet=quiet)
        result = {"scheme": scheme, **check_protocol(proxy_url)}
        results.append(result)
        status = "成功" if result["ok"] else "失败"
        log(f"    {scheme}: {status}", quiet=quiet)
    return results
