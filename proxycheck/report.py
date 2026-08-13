"""把各个独立的检测项汇总成一份完整报告,并提供 JSON / 文本两种输出。"""
import json

from .checks import connectivity, geoip, anonymity, speed, dns_leak, type_detect
from .progress import log
from .retry import call_with_retry

# 挑选后续单目标检测(geoip/anonymity/dns_trace/speed)要用哪个协议时的
# 优先级顺序。之前的版本写死用 "http://",导致如果这次恰好是 http 协议
# 抽风、而 https/socks5h 其实是通的,后面所有检测也会跟着一起失败——
# 这是真实测试中发现的 bug,这里改成从协议连通性测试的结果里动态挑一个
# 真正测通的协议。
SCHEME_PREFERENCE = ["https", "socks5h", "http", "socks5"]


def _pick_working_proxy_url(protocol_results: list):
    ok_by_scheme = {r["scheme"]: r["proxy"] for r in protocol_results if r["ok"]}
    for scheme in SCHEME_PREFERENCE:
        if scheme in ok_by_scheme:
            return ok_by_scheme[scheme]
    return None


def run_full_check(host: str, port: int, username: str = None, password: str = None,
                    real_ip: str = None, skip_speed: bool = False, speed_url: str = None,
                    quiet: bool = False) -> dict:
    total_stages = 4 if skip_speed else 5
    stage = 0
    report = {"target": f"{host}:{port}"}

    stage += 1
    log(f"[{stage}/{total_stages}] 测试协议连通性...", quiet=quiet)
    report["protocols"] = connectivity.check_all_protocols(
        host, port, username, password, quiet=quiet,
    )
    log(f"[{stage}/{total_stages}] 协议连通性检测完成", quiet=quiet)

    working_proxy_url = _pick_working_proxy_url(report["protocols"])

    if working_proxy_url is None:
        log("所有协议均连接失败,跳过后续检测。", quiet=quiet)
        skip_reason = {"ok": False, "error": "所有协议均连接失败,已跳过此项检测"}
        report["geoip"] = skip_reason
        report["anonymity"] = skip_reason
        report["dns_trace"] = skip_reason
        if not skip_speed:
            report["speed"] = skip_reason
        report["proxy_type"] = "unknown"
        return report

    stage += 1
    log(f"[{stage}/{total_stages}] 查询出口IP信息...", quiet=quiet)
    report["geoip"] = call_with_retry(geoip.lookup_exit_ip, working_proxy_url)
    log(f"[{stage}/{total_stages}] 出口IP信息查询完成", quiet=quiet)

    stage += 1
    log(f"[{stage}/{total_stages}] 检测匿名等级...", quiet=quiet)
    report["anonymity"] = call_with_retry(anonymity.check_anonymity, working_proxy_url, real_ip=real_ip)
    log(f"[{stage}/{total_stages}] 匿名等级检测完成", quiet=quiet)

    stage += 1
    log(f"[{stage}/{total_stages}] 检测边缘节点回源...", quiet=quiet)
    report["dns_trace"] = call_with_retry(dns_leak.trace_edge, working_proxy_url)
    log(f"[{stage}/{total_stages}] 边缘节点回源检测完成", quiet=quiet)

    if not skip_speed:
        stage += 1
        log(f"[{stage}/{total_stages}] 测速中(下载80KB测试数据)...", quiet=quiet)
        report["speed"] = call_with_retry(speed.measure_speed, working_proxy_url, url=speed_url)
        log(f"[{stage}/{total_stages}] 测速完成", quiet=quiet)

    geo = report["geoip"]
    if geo.get("ok"):
        report["proxy_type"] = type_detect.classify(
            isp=geo.get("isp"),
            org=geo.get("org"),
            is_mobile_hint=geo.get("mobile", False),
            is_hosting_hint=geo.get("hosting", False),
        )
    else:
        report["proxy_type"] = "unknown"

    log("全部检测完成,正在生成报告...", quiet=quiet)

    return report


def to_json(report: dict) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2)


def to_text(report: dict) -> str:
    lines = [f"目标代理: {report['target']}", ""]

    lines.append("协议连通性:")
    for p in report["protocols"]:
        status = "OK" if p["ok"] else "FAIL"
        latency = f"{p['latency_ms']}ms" if p.get("latency_ms") else "-"
        line = f"  [{status}] {p['scheme']:<8} {latency}"
        if not p["ok"] and p.get("error"):
            short_error = p["error"][:80]
            line += f"  ({short_error})"
        lines.append(line)

    geo = report["geoip"]
    lines.append("")
    if geo.get("ok"):
        lines.append("出口IP信息:")
        lines.append(f"  IP: {geo.get('query')}")
        lines.append(f"  地理位置: {geo.get('country')} / {geo.get('regionName')} / {geo.get('city')}")
        lines.append(f"  ISP/组织: {geo.get('isp')} ({geo.get('org')})")
        lines.append(f"  代理类型判断: {report['proxy_type']}")
    else:
        lines.append(f"出口IP查询失败: {geo.get('error')}")

    anon = report["anonymity"]
    lines.append("")
    if anon.get("ok"):
        lines.append(f"匿名等级: {anon['level']}")
        if anon["leaked_headers"]:
            lines.append(f"  检测到泄漏头: {', '.join(anon['leaked_headers'])}")
    else:
        lines.append(f"匿名检测失败: {anon.get('error')}")

    trace = report["dns_trace"]
    lines.append("")
    if trace.get("ok"):
        lines.append(f"边缘节点回源: ip={trace.get('edge_ip')} colo={trace.get('edge_colo')}")

    if "speed" in report:
        sp = report["speed"]
        lines.append("")
        if sp.get("ok"):
            note = "(小样本估算,仅供参考)" if sp.get("small_sample") else ""
            lines.append(f"下载速度: {sp['mbps']} Mbps ({sp['downloaded_mb']}MB / {sp['seconds']}s) {note}")
        else:
            lines.append(f"速度测试失败: {sp.get('error')}")

    return "\n".join(lines)
