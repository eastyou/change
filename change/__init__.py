"""购物找零：价格、付款、找零与可打印练习纸。"""

from .model import (
    DENOMINATIONS,
    KINDS,
    PAYMENTS,
    PRODUCTS,
    MoneyError,
    Product,
    WorksheetItem,
    breakdown,
    breakdown_text,
    build_worksheet,
    check_answer,
    format_money,
    format_yuan,
    parse_money,
    product_table,
)

__version__ = "0.1.0"

__all__ = [
    "DENOMINATIONS",
    "KINDS",
    "PAYMENTS",
    "PRODUCTS",
    "MoneyError",
    "Product",
    "WorksheetItem",
    "breakdown",
    "breakdown_text",
    "build_worksheet",
    "check_answer",
    "format_money",
    "format_yuan",
    "parse_money",
    "product_table",
]
