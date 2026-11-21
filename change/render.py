"""购物找零页面与硬币示意图渲染。"""

from __future__ import annotations

import html
from typing import List, Sequence

from .model import WorksheetItem, breakdown, format_money

STYLE = """
@page { size: A4 portrait; margin: 14mm 13mm; }
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
  color: #1f2937;
  font-size: 11pt;
  line-height: 1.65;
}
h1 { font-size: 21pt; margin: 0 0 1.5mm; }
.sub { color: #6b7280; font-size: 9.5pt; margin: 0 0 5mm; }
ol.items { margin: 0; padding-left: 7mm; }
li.item { margin-bottom: 7mm; page-break-inside: avoid; }
.prompt { margin: 0 0 2mm; }
.prompt .num { color: #b45309; font-weight: 600; margin-right: 1.5mm; }
.work { border: 0.4pt dashed #cbd5e1; border-radius: 2mm; padding: 3mm; }
.work .row { color: #475569; font-size: 10pt; margin-bottom: 1.5mm; }
.blank { display: inline-block; min-width: 32mm; border-bottom: 0.7pt solid #94a3b8; height: 1.1em; }
.space { height: 8mm; border-bottom: 0.4pt dashed #e2e8f0; margin-top: 2mm; }
.answers { page-break-before: always; }
.answers h2 { font-size: 15pt; margin: 0 0 4mm; }
.answers ol { margin: 0; padding-left: 7mm; }
.answers li { margin-bottom: 4mm; page-break-inside: avoid; }
.answers .ans { color: #0f4c81; font-weight: 600; }
.answers .break { color: #6b7280; font-size: 9.5pt; margin-left: 2mm; }
.money { height: 16mm; }
"""


def _escape(text: str) -> str:
    return html.escape(str(text), quote=True)


def render_money_svg(cents: int) -> str:
    """把金额画成纸币与硬币，每组标注张数。"""
    groups = breakdown(cents)
    if not groups:
        return '<svg class="money" viewBox="0 0 60 44" role="img" aria-label="0 元"></svg>'
    width = 8 + 34 * len(groups)
    parts: List[str] = [
        '<svg class="money" viewBox="0 0 %d 44" role="img" aria-label="找零示意图">' % width
    ]
    for index, (value, label, count) in enumerate(groups):
        x = 4 + index * 34
        if value >= 500:
            parts.append(
                '<rect x="%.1f" y="7" width="26" height="14" rx="1.5" '
                'fill="#bbf7d0" stroke="#15803d" stroke-width="0.5"></rect>'
                % x
            )
            parts.append(
                '<text x="%.1f" y="16.5" font-size="6" text-anchor="middle" '
                'fill="#14532d">%s</text>' % (x + 13, _escape(label))
            )
        else:
            parts.append(
                '<circle cx="%.1f" cy="14" r="7" fill="#fde68a" '
                'stroke="#b45309" stroke-width="0.5"></circle>' % (x + 13)
            )
            parts.append(
                '<text x="%.1f" y="16" font-size="3.6" text-anchor="middle" '
                'fill="#78350f">%s</text>' % (x + 13, _escape(label))
            )
        parts.append(
            '<text x="%.1f" y="38" font-size="5" text-anchor="middle" '
            'fill="#475569">×%d</text>' % (x + 13, count)
        )
    parts.append("</svg>")
    return "".join(parts)


def render_worksheet(
    items: Sequence[WorksheetItem],
    title: str = "购物找零练习",
    include_answers: bool = False,
) -> str:
    """生成 A4 找零练习纸。"""
    if not items:
        raise ValueError("至少需要一道题目")
    rows: List[str] = []
    for index, item in enumerate(items, start=1):
        rows.append(
            '<li class="item"><p class="prompt"><span class="num">%d.</span>%s</p>'
            '<div class="work">'
            '<div class="row">合计：<span class="blank"></span>元　'
            "付款：%s</div>"
            '<div class="row">应找回：<span class="blank"></span>元</div>'
            '<div class="space"></div>'
            "</div></li>"
            % (
                index,
                _escape(item.prompt),
                _escape(format_money(item.paid_cents)),
            )
        )
    body = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>%s</title>" % _escape(title),
        "<style>%s</style>" % STYLE,
        "</head>",
        "<body>",
        "<h1>%s</h1>" % _escape(title),
        '<p class="sub">姓名：__________　班级：__________　日期：__________</p>',
        '<ol class="items">',
        "\n".join(rows),
        "</ol>",
    ]
    if include_answers:
        body.extend(_answer_section(items))
    body.extend(["</body>", "</html>"])
    return "\n".join(body)


def _answer_section(items: Sequence[WorksheetItem]) -> List[str]:
    rows: List[str] = []
    for index, item in enumerate(items, start=1):
        rows.append(
            '<li><span class="num">%d.</span> 合计 %s，'
            '<span class="ans">应找回 %s</span>'
            '<span class="break">%s</span><br>%s</li>'
            % (
                index,
                _escape(format_money(item.total_cents)),
                _escape(item.answer_text),
                _escape(item.breakdown_text),
                render_money_svg(item.change_cents),
            )
        )
    return [
        '<section class="answers">',
        "<h2>参考答案</h2>",
        "<ol>",
        "\n".join(rows),
        "</ol>",
        "</section>",
    ]
