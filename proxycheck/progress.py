"""极简终端进度反馈工具,不依赖任何第三方库。

v0.1.0 曾经用 \r(回车不换行)做过一版转圈动画,但在 Windows cmd 下
遇到过中文字符显示宽度计算不准导致内容重叠乱码的问题。这一版改成
最朴素的逐行输出——不做任何原地覆盖,牺牲一点动画效果,换取在任何
终端(Windows cmd / PowerShell / Windows Terminal / 各种 Linux/macOS
终端)下都不会出错的稳定性。

所有进度信息打印到 stderr,不会污染 `--json` 模式下 stdout 的输出。
"""
import sys


def log(message: str, quiet: bool = False) -> None:
    """打印一行进度提示,带真实换行,不做任何原地覆盖。"""
    if not quiet:
        print(message, file=sys.stderr, flush=True)
