"""基于 Cloudflare 公开的 trace 接口做一个轻量级的"边缘节点回源"检测。

重要说明: 这不是完整意义上的 DNS 泄漏测试(完整测试通常需要自建权威
DNS 服务器来观察解析请求实际从哪里发出)。这里只是让请求打到 Cloudflare
的边缘节点,读取它看到的来源IP和机房代号(colo),作为"网络出口是否和
代理声称的出口地区一致"的辅助参考,建议结合 geoip 模块的结果一起看。
"""
import requests

TRACE_URL = "https://www.cloudflare.com/cdn-cgi/trace"


def trace_edge(proxy_url: str, timeout: float = 10.0) -> dict:
    proxies = {"http": proxy_url, "https": proxy_url}
    try:
        resp = requests.get(TRACE_URL, proxies=proxies, timeout=timeout)
        data = {}
        for line in resp.text.strip().splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                data[key] = value
        return {"ok": True, "edge_ip": data.get("ip"), "edge_colo": data.get("colo")}
    except requests.exceptions.RequestException as exc:
        return {"ok": False, "error": str(exc)}
