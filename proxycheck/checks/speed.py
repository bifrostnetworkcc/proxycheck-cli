"""通过代理下载测试数据来估算吞吐速度。

用 httpbingo.org 自带的 /bytes/{n} 接口生成指定大小的随机数据作为测试
负载,而不是依赖第三方测速站点(如 hetzner)——实测发现不少大型云服务商
会对"看起来像代理/机器人"的下载请求做限流或直接拦截(502)。

注意: go-httpbin(httpbingo.org 用的实现)的 /bytes 和 /stream-bytes 接口
本身有请求体大小上限(项目里叫 MAX_BODY_SIZE,默认约 100KB),超过这个
大小会直接返回 400 Bad Request——这里默认用 80KB,留了一点余量。因为
样本小,这不是严谨的带宽跑分,只能作为"这个代理大致通不通、快不快"的
粗略参考;如果需要更真实的大文件吞吐测试,可以通过 url 参数传入自己的
测试文件地址。
"""
import time
import requests

DEFAULT_DOWNLOAD_BYTES = 80_000  # 留在 httpbingo.org 100KB 上限以内
DEFAULT_DOWNLOAD_URL = f"https://httpbingo.org/bytes/{DEFAULT_DOWNLOAD_BYTES}"


def measure_speed(proxy_url: str, url: str = None, timeout: float = 25.0) -> dict:
    proxies = {"http": proxy_url, "https": proxy_url}
    target_url = url or DEFAULT_DOWNLOAD_URL
    try:
        start = time.perf_counter()
        downloaded = 0
        with requests.get(target_url, proxies=proxies, stream=True, timeout=timeout) as resp:
            resp.raise_for_status()
            for chunk in resp.iter_content(chunk_size=32 * 1024):
                downloaded += len(chunk)
        elapsed = time.perf_counter() - start
        mbps = (downloaded * 8 / elapsed) / 1_000_000 if elapsed > 0 else 0
        return {
            "ok": True,
            "downloaded_mb": round(downloaded / 1_000_000, 3),
            "seconds": round(elapsed, 2),
            "mbps": round(mbps, 2),
            "small_sample": url is None,
        }
    except requests.exceptions.RequestException as exc:
        return {"ok": False, "error": str(exc)}
