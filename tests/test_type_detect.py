from proxycheck.checks.type_detect import classify


def test_classifies_datacenter_by_org_keyword():
    assert classify(isp="DigitalOcean LLC", org="DigitalOcean") == "datacenter"


def test_classifies_mobile_by_hint():
    assert classify(isp="China Mobile", org="", is_mobile_hint=True) == "mobile"


def test_defaults_to_residential():
    assert classify(isp="Comcast Cable", org="Comcast") == "residential_or_isp"


def test_hosting_hint_overrides_keyword_absence():
    assert classify(isp="Some Random ISP", org="Unclear Org", is_hosting_hint=True) == "datacenter"


def test_empty_input_defaults_to_residential():
    assert classify() == "residential_or_isp"


def test_telecom_named_isp_is_not_auto_classified_as_mobile():
    # 回归测试: 早期版本把关键词库里的 "telecom" 匹配得太宽,导致像
    # Tojiktelecom 这类实际是固网/住宅宽带运营商的ISP被误判成 mobile。
    assert classify(
        isp='Opened Joint Stock Company "Tojiktelecom"',
        org="OJSC Tojiktelecom",
    ) == "residential_or_isp"
