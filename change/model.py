"""人民币购物找零：价格、付款、找零与硬币拆分。"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

KINDS = ("single", "double")

PAYMENTS: Tuple[int, ...] = (500, 1000, 2000, 5000, 10000)

DENOMINATIONS: Tuple[Tuple[int, str], ...] = (
    (5000, "50 元"),
    (2000, "20 元"),
    (1000, "10 元"),
    (500, "5 元"),
    (100, "1 元"),
    (50, "5 角"),
    (10, "1 角"),
)


class MoneyError(ValueError):
    """金额与找零相关的输入错误。"""


def _check_cents(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise MoneyError("%s必须是整数分" % name)
    if value < 0:
        raise MoneyError("%s不能为负数" % name)
    return value


@dataclass(frozen=True)
class Product:
    """一件商品。"""

    name: str
    price_cents: int

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise MoneyError("商品名称不能为空")
        _check_cents(self.price_cents, "价格")
        if self.price_cents <= 0:
            raise MoneyError("价格必须大于 0")

    @property
    def price_text(self) -> str:
        return format_money(self.price_cents)


PRODUCTS: Tuple[Product, ...] = (
    Product("铅笔", 150),
    Product("橡皮", 200),
    Product("直尺", 300),
    Product("三角尺", 450),
    Product("练习本", 350),
    Product("笔记本", 650),
    Product("卷笔刀", 550),
    Product("书签", 200),
    Product("文件夹", 780),
    Product("便签本", 420),
    Product("圆珠笔", 250),
    Product("蜡笔", 980),
    Product("水彩笔", 1280),
    Product("墨水", 1200),
    Product("文具盒", 2600),
    Product("水杯", 3200),
    Product("雨伞", 2800),
    Product("钢笔", 3500),
    Product("计算器", 4500),
    Product("书包", 8900),
)


def format_money(cents: int) -> str:
    """把分格式化为两位小数的元。"""
    _check_cents(cents, "金额")
    return "%d.%02d 元" % (cents // 100, cents % 100)


def format_yuan(cents: int) -> str:
    """整元时不带小数，否则保留两位。"""
    _check_cents(cents, "金额")
    if cents % 100 == 0:
        return "%d 元" % (cents // 100)
    return format_money(cents)


_MONEY_RE = re.compile(r"^(\d+)(?:\.(\d{1,2}))?$")


def parse_money(text: str) -> int:
    """解析金额，返回整数分；支持 ``3.5``、``3.50 元``、``3元5角``。"""
    if not isinstance(text, str) or not text.strip():
        raise MoneyError("金额不能为空")
    cleaned = text.strip()
    cleaned = cleaned.replace("人民币", "").replace("块钱", "").replace("块", "元")
    cleaned = cleaned.replace("元", ".").replace("角", "").replace("分", "")
    cleaned = re.sub(r"\s+", "", cleaned)
    if cleaned.endswith("."):
        cleaned = cleaned[:-1]
    match = _MONEY_RE.match(cleaned)
    if not match:
        raise MoneyError("无法识别金额：%s" % text)
    fraction = (match.group(2) or "").ljust(2, "0")
    return int(match.group(1)) * 100 + int(fraction)


def breakdown(cents: int) -> List[Tuple[int, str, int]]:
    """把金额拆成面值与张数，按面值从大到小排列。"""
    _check_cents(cents, "金额")
    if cents % 10 != 0:
        raise MoneyError("金额需是 1 角的整数倍")
    rows: List[Tuple[int, str, int]] = []
    remaining = cents
    for value, label in DENOMINATIONS:
        count, remaining = divmod(remaining, value)
        if count:
            rows.append((value, label, count))
    if remaining:
        raise MoneyError("无法用现有面值凑出该金额")
    return rows


def breakdown_text(cents: int) -> str:
    rows = breakdown(cents)
    if not rows:
        return "0 元"
    return " + ".join("%s × %d" % (label, count) for _, label, count in rows)


def _candidates(kind: str) -> List[Tuple[str, Tuple[int, ...], int]]:
    rows: List[Tuple[str, Tuple[int, ...], int]] = []
    if kind == "single":
        for index, product in enumerate(PRODUCTS):
            for paid in PAYMENTS:
                if paid > product.price_cents:
                    rows.append((kind, (index,), paid))
        return rows
    for first in range(len(PRODUCTS)):
        for second in range(first + 1, len(PRODUCTS)):
            total = PRODUCTS[first].price_cents + PRODUCTS[second].price_cents
            for paid in PAYMENTS:
                if paid > total:
                    rows.append((kind, (first, second), paid))
    return rows


def build_worksheet(
    count: int = 12,
    seed: Optional[int] = None,
    kinds: Sequence[str] = KINDS,
) -> List["WorksheetItem"]:
    """随机抽取购物找零题，同一题目不会重复。"""
    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
        raise MoneyError("题目数量必须是正整数")
    if not kinds:
        raise MoneyError("至少需要一种题型")
    for kind in kinds:
        if kind not in KINDS:
            raise MoneyError("未知题型：%s" % kind)
    pool: List[Tuple[str, Tuple[int, ...], int]] = []
    for kind in kinds:
        pool.extend(_candidates(kind))
    if count > len(pool):
        raise MoneyError("可用题目不足 %d 道" % count)
    rng = random.Random(seed)
    chosen = rng.sample(pool, count)
    return [
        WorksheetItem(kind=kind, product_indexes=indexes, paid_cents=paid)
        for kind, indexes, paid in chosen
    ]


@dataclass(frozen=True)
class WorksheetItem:
    """一道购物找零题。"""

    kind: str
    product_indexes: Tuple[int, ...]
    paid_cents: int

    def __post_init__(self) -> None:
        if self.kind not in KINDS:
            raise MoneyError("未知题型：%s" % self.kind)
        if not isinstance(self.product_indexes, tuple) or not self.product_indexes:
            raise MoneyError("至少需要一件商品")
        if self.kind == "single" and len(self.product_indexes) != 1:
            raise MoneyError("single 题型只能有一件商品")
        if self.kind == "double" and len(self.product_indexes) != 2:
            raise MoneyError("double 题型需要两件商品")
        if len(set(self.product_indexes)) != len(self.product_indexes):
            raise MoneyError("商品不能重复")
        for index in self.product_indexes:
            if isinstance(index, bool) or not isinstance(index, int):
                raise MoneyError("商品序号必须是整数")
            if index < 0 or index >= len(PRODUCTS):
                raise MoneyError("商品序号越界：%d" % index)
        _check_cents(self.paid_cents, "付款")
        if self.paid_cents <= self.total_cents:
            raise MoneyError("付款必须大于商品总价")

    @property
    def items(self) -> Tuple[Product, ...]:
        return tuple(PRODUCTS[index] for index in self.product_indexes)

    @property
    def total_cents(self) -> int:
        return sum(product.price_cents for product in self.items)

    @property
    def change_cents(self) -> int:
        return self.paid_cents - self.total_cents

    @property
    def answer_text(self) -> str:
        return format_money(self.change_cents)

    @property
    def breakdown(self) -> List[Tuple[int, str, int]]:
        return breakdown(self.change_cents)

    @property
    def breakdown_text(self) -> str:
        return breakdown_text(self.change_cents)

    @property
    def prompt(self) -> str:
        names = "、".join(
            "%s（%s）" % (product.name, product.price_text) for product in self.items
        )
        return "买%s，付 %s，应找回多少元？" % (names, format_yuan(self.paid_cents))


def check_answer(item: WorksheetItem, text: str) -> bool:
    """校验找零答案，统一按分比较。"""
    if not isinstance(item, WorksheetItem):
        return False
    try:
        given = parse_money(text)
    except MoneyError:
        return False
    return given == item.change_cents


def product_table() -> List[Dict[str, object]]:
    """返回商品清单，供命令行展示。"""
    return [
        {"name": product.name, "price": product.price_cents, "text": product.price_text}
        for product in PRODUCTS
    ]
