# proxycheck-cli

A command-line tool to check a proxy's protocol support, anonymity level, type (residential / datacenter / mobile), exit IP info, and rough download speed — all in one command.

[![CI](https://github.com/your-username/proxycheck-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/proxycheck-cli/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

[中文说明](#中文说明)

## Features

- **Protocol connectivity check** — tests HTTP / HTTPS / SOCKS5 / SOCKS5h and records latency for each
- **Auto-picks a working protocol** — the anonymity/type/speed checks automatically reuse whichever protocol actually worked in the connectivity test, instead of hardcoding one that might be down
- **Automatic retry on failure** — residential/mobile proxies have a natural intermittent failure rate; a single failed request is retried once to reduce false negatives
- **Anonymity level detection** — transparent / anonymous / elite, based on comparing request headers
- **Proxy type detection** — heuristic classification (residential / datacenter / mobile) based on ISP/ASN keywords, see Limitations below
- **Exit IP info** — country, region, city, ISP, org
- **Edge node trace** — a sanity check for whether the network exit matches the proxy's claimed region
- **Download speed test** — a rough small-sample estimate (uses httpbingo.org's `/bytes` endpoint, capped at ~100KB by that endpoint; pass `--speed-url` to point at your own larger file for a more realistic number)
- **Live progress output** — prints a line per stage so you're not left wondering if it's hung (disable with `--quiet`)
- **JSON or plain text output** — easy to pipe into your own scripts or CI

## Install

```bash
git clone https://github.com/your-username/proxycheck-cli.git
cd proxycheck-cli
pip install -r requirements.txt
```

Or install as a package (registers the `proxycheck` command):

```bash
pip install .
```

## Usage

> If you only ran `pip install -r requirements.txt` (not `pip install .`), the `proxycheck` command isn't registered as an executable — run everything below as `python -m proxycheck.cli ...` instead. If you ran `pip install .`, the `proxycheck` command works directly as shown.

```bash
proxycheck --host 1.2.3.4 --port 8080
```

With username/password auth:

```bash
proxycheck --host 1.2.3.4 --port 8080 --username user --password pass
```

Skip the speed test (faster):

```bash
proxycheck --host 1.2.3.4 --port 8080 --skip-speed
```

JSON output, for piping into other scripts:

```bash
proxycheck --host 1.2.3.4 --port 8080 --json
```

Suppress progress output (for scripted/automated calls):

```bash
proxycheck --host 1.2.3.4 --port 8080 --quiet
```

Progress output goes to stderr, so it never pollutes the JSON on stdout — `proxycheck ... --json > result.json` is always safe, with or without `--quiet`.

Example text output:

```
目标代理: 1.2.3.4:8080

协议连通性:
  [OK]   http     412.3ms
  [OK]   https    438.1ms
  [FAIL] socks5   -
  [FAIL] socks5h  -

出口IP信息:
  IP: 1.2.3.4
  地理位置: United States / California / Los Angeles
  ISP/组织: Some Residential ISP (Some Residential ISP)
  代理类型判断: residential_or_isp

匿名等级: elite

边缘节点回源: ip=1.2.3.4 colo=LAX

下载速度: 24.7 Mbps (5.0MB / 1.62s)
```

(Text output labels are currently in Chinese; `--json` gives you English field names like `ok`, `latency_ms`, `country`, `level`, `proxy_type` if you're integrating this into another tool. An `--lang en` flag for English text output is a reasonable future addition — PRs welcome.)

## Limitations (please read before trusting the results)

- **Proxy type detection is heuristic**, based on ISP/org name keyword matching — not authoritative. For production-grade accuracy, plug in a dedicated IP intelligence service (e.g. IPinfo Privacy Detection, IP2Location, IPQualityScore) in place of the logic in `geoip.py`.
- **The DNS check is simplified**, not a full authoritative DNS leak test (a proper one requires running your own authoritative DNS server to observe resolution requests). It's a rough sanity check on exit-region consistency, nothing more.
- **No WebRTC leak detection** — that inherently requires a browser environment, which a CLI tool can't simulate. If you need this, it belongs in a browser extension or a web-based version.
- **The speed test is a small-sample estimate**, downloading only ~80KB by default (limited by httpbingo.org's `/bytes` endpoint cap). Latency dominates at that sample size, so it's not a rigorous bandwidth benchmark. Use `--speed-url` with your own larger file for something closer to real throughput.
- Protocol connectivity currently covers HTTP/HTTPS/SOCKS5; UDP/QUIC (HTTP/3) connectivity testing isn't implemented yet (see Roadmap) — some newer-generation residential proxies (e.g. BifrostNetwork) natively support UDP/QUIC, and this check will be added later.

## Roadmap

- [ ] UDP/QUIC (HTTP/3) connectivity check
- [ ] Batch proxy pool testing (input a list, output a CSV/table report)
- [ ] Web-based version (for non-developers to test directly in a browser)
- [ ] Optional integration with a proper IP intelligence data source

Issues and PRs welcome.

## Contributing

1. Fork this repo
2. Create a branch: `git checkout -b feature/xxx`
3. Run the tests before submitting: `pytest tests/ -v`
4. Open a PR with a short description of the change

## License

MIT License, see [LICENSE](LICENSE).

---

Initiated and maintained by the [BifrostNetwork](https://bifrostnetwork.cc/) team.

<a id="中文说明"></a>
## 中文说明

一个命令行代理质量检测工具:一条命令测出代理的连通性、匿名等级、类型判断(住宅/机房/移动)、出口IP信息和大致下载速度。

### 功能特性

- **协议连通性检测**:同时测试 HTTP / HTTPS / SOCKS5 / SOCKS5h 是否可用,并记录延迟
- **自动选用可用协议**:后续的匿名/类型/测速等检测会自动使用连通性测试中真正测通的协议,不会在某个协议抽风时连带把其他检测也拖垮
- **失败自动重试一次**:住宅/移动代理天然有一定的偶发失败率,单次网络请求失败会自动重试,减少"误报"
- **匿名等级判断**:透明 / 匿名 / 高匿三级分类(基于请求头对比)
- **代理类型判断**:基于 ISP/ASN 关键词的启发式分类(住宅、机房、移动),见下方"局限性"
- **出口IP信息**:国家、地区、城市、ISP、组织
- **边缘节点回源检测**:辅助判断网络出口是否和代理声称的地区一致
- **下载测速**:小样本粗略估算吞吐量(默认走 httpbingo.org 的 `/bytes` 接口,受限于该接口约100KB的大小上限,仅供参考;可用 `--speed-url` 传入自己的大文件地址做更真实的测试)
- **实时进度提示**:每个检测阶段都有进度提示,长时间无响应时不会让人以为程序卡死了(可用 `--quiet` 关闭)
- **JSON / 文本双格式输出**,方便接入自己的脚本或CI流水线

### 安装

```bash
git clone https://github.com/your-username/proxycheck-cli.git
cd proxycheck-cli
pip install -r requirements.txt
```

或者直接以包的形式安装(会注册 `proxycheck` 命令):

```bash
pip install .
```

### 使用

> 如果你只跑了 `pip install -r requirements.txt`(没有 `pip install .`),`proxycheck` 这个命令不会被注册成可执行命令,下面所有命令都要换成 `python -m proxycheck.cli ...` 来跑。如果你跑了 `pip install .`,才能直接用 `proxycheck` 这个简写命令。

```bash
proxycheck --host 1.2.3.4 --port 8080
```

带用户名密码认证:

```bash
proxycheck --host 1.2.3.4 --port 8080 --username user --password pass
```

跳过测速(检测更快):

```bash
proxycheck --host 1.2.3.4 --port 8080 --skip-speed
```

输出 JSON,方便接入其他脚本:

```bash
proxycheck --host 1.2.3.4 --port 8080 --json
```

不显示检测进度(适合脚本化调用,只关心最终结果):

```bash
proxycheck --host 1.2.3.4 --port 8080 --quiet
```

进度提示会输出到 stderr,不会污染 stdout 的 JSON 结果,所以即使不加 `--quiet`,也可以放心 `proxycheck ... --json > result.json` 重定向。

### 局限性说明(请诚实对待检测结果)

- **代理类型判断是启发式的**,基于 ISP/组织名称关键词匹配,不是绝对准确。生产环境如果需要更高准确度,建议接入专业 IP 情报服务(如 IPinfo Privacy Detection、IP2Location、IPQualityScore 等)替换 `geoip.py` 里的实现。
- **DNS 检测是简化版**,不是完整的权威 DNS 泄漏测试,只作为网络出口地区一致性的辅助参考。
- **WebRTC 泄漏检测未包含**,这类检测本质上依赖浏览器环境,命令行工具无法模拟。
- **测速是小样本估算**,默认只下载约80KB数据,不是严谨的带宽跑分。需要更真实的数据可以用 `--speed-url` 指定自己的大文件。
- 目前的协议连通性测试覆盖 HTTP/HTTPS/SOCKS5;对 UDP/QUIC(HTTP/3)的连通性测试暂未实现,属于 Roadmap 里的下一步(部分新一代住宅代理,例如 BifrostNetwork,已经原生支持 UDP/QUIC)。

### 贡献

欢迎提 Issue 或 PR。Fork 本仓库 → 新建分支 → 提交前跑一下 `pytest tests/ -v` → 提交 PR。

### 协议

MIT License,详见 [LICENSE](LICENSE)。

---

由 [BifrostNetwork](https://bifrostnetwork.cc/) 团队发起并维护。
