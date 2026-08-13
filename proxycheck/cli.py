"""命令行入口: proxycheck --host <ip> --port <port> [选项]"""
import argparse
import sys

from .report import run_full_check, to_json, to_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="proxycheck",
        description="测试代理的连通性、匿名等级、类型判断与速度的命令行工具",
    )
    parser.add_argument("--host", required=True, help="代理服务器地址")
    parser.add_argument("--port", required=True, type=int, help="代理服务器端口")
    parser.add_argument("--username", default=None, help="代理认证用户名(可选)")
    parser.add_argument("--password", default=None, help="代理认证密码(可选)")
    parser.add_argument("--real-ip", default=None,
                         help="你的真实公网IP,用于精确判断是否为透明代理(可选)")
    parser.add_argument("--skip-speed", action="store_true", help="跳过下载测速,加快检测速度")
    parser.add_argument("--speed-url", default=None,
                         help="自定义测速下载地址(可选)。默认用httpbingo.org的80KB小样本,"
                              "样本较小仅供参考;如需更真实的带宽测试,可传入自己的大文件URL")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出结果")
    parser.add_argument("--quiet", "-q", action="store_true", help="不显示检测进度提示")
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    report = run_full_check(
        host=args.host,
        port=args.port,
        username=args.username,
        password=args.password,
        real_ip=args.real_ip,
        skip_speed=args.skip_speed,
        speed_url=args.speed_url,
        quiet=args.quiet,
    )

    print(to_json(report) if args.json else to_text(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
