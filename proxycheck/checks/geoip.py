"""查询代理出口IP的地理位置、ISP/组织信息。

默认使用 ip-api.com 的免费接口(无需 API Key,限速 45 次/分钟)。
如需更高准确度或更高频率,可以在此模块替换为付费的 IP 情报服务
(如 IPinfo、MaxMind、IPQualityScore 等),接口保持返回同样的字段即可。
"""
import requests

IP_API_URL = (
    "http://ip-api.com/json/?fields="
    "status,message,country,countryCode,region,regionName,city,"
    "isp,org,as,query,mobile,proxy,hosting"
)


def lookup_exit_ip(proxy_url: str, timeout: float = 10.0) -> dict:
    proxies = {"http": proxy_url, "https": proxy_url}
    try:
        resp = requests.get(IP_API_URL, proxies=proxies, timeout=timeout)
        data = resp.json()
        if data.get("status") != "success":
            return {"ok": False, "error": data.get("message", "查询失败")}
        data["ok"] = True
        return data
    except requests.exceptions.RequestException as exc:
        return {"ok": False, "error": str(exc)}
