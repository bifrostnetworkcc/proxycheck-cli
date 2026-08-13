"""基于 ISP / 组织名称关键词的代理类型启发式分类。

重要说明: 这是一个基于关键词匹配的启发式方法,不是绝对准确的判断。
生产环境如果需要更高准确度,建议接入专业的 IP 情报服务
(例如 IPinfo 的 Privacy Detection、IP2Location、IPQualityScore 等),
它们通常基于持续更新的 IP 数据库而不是简单的名称匹配。
"""

DATACENTER_KEYWORDS = [
    "amazon", "aws", "google cloud", "microsoft", "azure", "digitalocean",
    "linode", "ovh", "hetzner", "vultr", "contabo", "oracle cloud",
    "alibaba", "tencent cloud", "hosting", "datacenter", "data center",
    "cloud", "colocation", "server",
]

MOBILE_KEYWORDS = [
    "mobile", "wireless", "cellular", " lte", " 4g", " 5g",
    "vodafone", "verizon wireless", "at&t mobility",
    "china mobile", "china unicom",
]
# 注意: 故意不把泛泛的 "telecom" 放进关键词——很多国家的电信运营商
# (如 Deutsche Telekom、PT Telkom、Tojiktelecom 等)名字里带 "telecom"
# 但主营固网宽带,不代表就是移动网络,加这个词误判率太高。


def classify(isp: str = "", org: str = "", is_mobile_hint: bool = False,
             is_hosting_hint: bool = False) -> str:
    """返回 'datacenter' / 'mobile' / 'residential_or_isp' 三者之一。

    is_mobile_hint / is_hosting_hint 通常来自查询接口自带的标记位
    (例如 ip-api.com 返回的 mobile / hosting 字段),优先级高于关键词匹配。
    """
    text = f"{isp or ''} {org or ''}".lower()

    if is_hosting_hint or any(keyword in text for keyword in DATACENTER_KEYWORDS):
        return "datacenter"
    if is_mobile_hint or any(keyword in text for keyword in MOBILE_KEYWORDS):
        return "mobile"
    return "residential_or_isp"
