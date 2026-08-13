"""通过对比目标服务器收到的请求头,判断代理的匿名等级。

判断逻辑(业内通用的三级分类):
- transparent(透明代理): 请求头中直接泄漏了你的真实IP
- anonymous(匿名代理): 泄漏了 Via / X-Forwarded-For 等表明"这是代理"的头,
  但没有直接暴露真实IP
- elite(高匿代理): 没有任何能表明请求经过代理的痕迹
"""
import requests

ECHO_URL = "https://httpbingo.org/get"

LEAK_HEADERS = ["via", "x-forwarded-for", "forwarded", "proxy-connection", "x-real-ip"]


def check_anonymity(proxy_url: str, real_ip: str = None, timeout: float = 15.0) -> dict:
    proxies = {"http": proxy_url, "https": proxy_url}
    try:
        resp = requests.get(ECHO_URL, proxies=proxies, timeout=timeout)
        headers = {k.lower(): v for k, v in resp.json().get("headers", {}).items()}
    except (requests.exceptions.RequestException, ValueError) as exc:
        return {"ok": False, "error": str(exc)}

    leaked = [h for h in LEAK_HEADERS if h in headers]
    leaks_real_ip = bool(real_ip and any(real_ip in v for v in headers.values()))

    if leaks_real_ip:
        level = "transparent"
    elif leaked:
        level = "anonymous"
    else:
        level = "elite"

    return {
        "ok": True,
        "level": level,
        "leaked_headers": leaked,
        "leaks_real_ip": leaks_real_ip,
    }
