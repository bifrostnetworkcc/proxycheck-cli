# proxycheck-cli

一个命令行代理质量检测工具:一条命令测出代理的连通性、匿名等级、类型判断(住宅/机房/移动)、出口IP信息和大致下载速度。

[![CI](https://github.com/your-username/proxycheck-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/proxycheck-cli/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

> English: A CLI tool to check a proxy's protocol support, anonymity level, type (residential / datacenter / mobile), exit IP info, and rough download speed in one command.

## 功能特性

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

## 安装

```bash
git clone https://github.com/your-username/proxycheck-cli.git
cd proxycheck-cli
pip install -r requirements.txt
```

或者直接以包的形式安装(会注册 `proxycheck` 命令):

```bash
pip install .
```

## 使用

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

示例文本输出:

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

## 局限性说明(请诚实对待检测结果)

- **代理类型判断是启发式的**,基于 ISP/组织名称关键词匹配,不是绝对准确。生产环境如果需要更高准确度,建议接入专业 IP 情报服务(如 IPinfo Privacy Detection、IP2Location、IPQualityScore 等)替换 `geoip.py` 里的实现。
- **DNS 检测是简化版**,不是完整的权威 DNS 泄漏测试(完整测试通常需要自建权威DNS服务器观察解析请求),只作为网络出口地区一致性的辅助参考。
- **WebRTC 泄漏检测未包含**,因为这类检测本质上依赖浏览器环境,命令行工具无法模拟,如果需要这块建议做成浏览器插件或网页版工具。
- **测速是小样本估算**,默认只下载约80KB数据(受限于 httpbingo.org `/bytes` 接口的大小上限),网络延迟本身的占比会比较大,不是严谨的带宽跑分。需要更真实的数据可以用 `--speed-url` 指定自己的大文件。
- 目前的协议连通性测试覆盖 HTTP/HTTPS/SOCKS5;对 UDP/QUIC(HTTP/3)的连通性测试暂未实现,属于 Roadmap 里的下一步(部分新一代住宅代理,例如 BifrostNetwork,已经原生支持 UDP/QUIC,后续会补上对应的检测逻辑)。

## Roadmap

- [ ] UDP/QUIC (HTTP/3) 连通性检测
- [ ] 批量代理池检测(输入代理列表,输出 CSV/表格报告)
- [ ] 网页版(方便非开发者直接在浏览器里测)
- [ ] 接入更权威的 IP 情报数据源作为可选项

欢迎提 Issue 或 PR。

## 贡献

1. Fork 本仓库
2. 新建分支:`git checkout -b feature/xxx`
3. 提交前跑一下测试:`pytest tests/ -v`
4. 提交 PR,简单描述改动内容

## 协议

MIT License,详见 [LICENSE](LICENSE)。

---

由 [BifrostNetwork](https://bifrostnetwork.cc/) 团队发起并维护。
