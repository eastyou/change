"""命令行入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .model import (
    KINDS,
    PRODUCTS,
    MoneyError,
    breakdown_text,
    build_worksheet,
    format_money,
    parse_money,
)
from .render import render_worksheet


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="change",
        description="购物找零：商品总价、付款、找零与硬币拆分",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    change_parser = subparsers.add_parser("change", help="计算找零")
    change_parser.add_argument("price", help="商品总价，例如 12.5")
    change_parser.add_argument("paid", help="付款金额，例如 20")

    subparsers.add_parser("catalog", help="列出商品与价格")

    sheet_parser = subparsers.add_parser("sheet", help="生成练习纸 HTML")
    sheet_parser.add_argument("--count", type=int, default=12, help="题目数量，默认 12")
    sheet_parser.add_argument("--seed", type=int, default=None, help="随机种子")
    sheet_parser.add_argument(
        "--kinds",
        default=",".join(KINDS),
        help="题型，用逗号分隔：single（一件）、double（两件）",
    )
    sheet_parser.add_argument("--title", default="购物找零练习", help="练习纸标题")
    sheet_parser.add_argument("--answers", action="store_true", help="追加参考答案")
    sheet_parser.add_argument("-o", "--output", default=None, help="输出文件")
    return parser


def _write_output(text: str, output: Optional[str]) -> None:
    if not output:
        print(text)
        return
    path = Path(output)
    if path.parent and str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print("已写入 %s" % path)


def _parse_kinds(text: str) -> List[str]:
    parts = [part.strip() for part in text.split(",") if part.strip()]
    if not parts:
        raise MoneyError("至少需要一种题型")
    return parts


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "change":
            price = parse_money(args.price)
            paid = parse_money(args.paid)
            if price <= 0:
                raise MoneyError("商品总价必须大于 0")
            if paid < price:
                raise MoneyError("付款不能少于商品总价")
            change = paid - price
            print("商品总价：%s" % format_money(price))
            print("付款：%s" % format_money(paid))
            print("找零：%s" % format_money(change))
            print("拆分：%s" % breakdown_text(change))
            return 0
        if args.command == "catalog":
            print("%-8s %s" % ("商品", "价格"))
            for product in PRODUCTS:
                print("%-8s %s" % (product.name, product.price_text))
            return 0
        kinds = _parse_kinds(args.kinds)
        items = build_worksheet(args.count, args.seed, kinds)
        _write_output(render_worksheet(items, args.title, args.answers), args.output)
        return 0
    except MoneyError as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2
    except OSError as exc:
        print("写入失败：%s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
