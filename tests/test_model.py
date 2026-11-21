"""购物找零模型测试。"""

import unittest
from dataclasses import FrozenInstanceError

from change.model import (
    KINDS,
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


class FormatTest(unittest.TestCase):
    def test_money(self):
        self.assertEqual(format_money(0), "0.00 元")
        self.assertEqual(format_money(5), "0.05 元")
        self.assertEqual(format_money(350), "3.50 元")
        self.assertEqual(format_money(1000), "10.00 元")

    def test_money_invalid(self):
        for bad in (-1, True, "3"):
            with self.assertRaises(MoneyError):
                format_money(bad)

    def test_yuan_whole(self):
        self.assertEqual(format_yuan(1000), "10 元")
        self.assertEqual(format_yuan(500), "5 元")

    def test_yuan_fraction(self):
        self.assertEqual(format_yuan(1250), "12.50 元")
        self.assertEqual(format_yuan(50), "0.50 元")


class ParseMoneyTest(unittest.TestCase):
    def test_plain(self):
        self.assertEqual(parse_money("3.5"), 350)
        self.assertEqual(parse_money("3.50"), 350)
        self.assertEqual(parse_money("12"), 1200)
        self.assertEqual(parse_money("0.05"), 5)

    def test_units(self):
        self.assertEqual(parse_money("3.50 元"), 350)
        self.assertEqual(parse_money("3元5角"), 350)
        self.assertEqual(parse_money("3块5"), 350)
        self.assertEqual(parse_money("人民币 8.8"), 880)

    def test_whitespace(self):
        self.assertEqual(parse_money("  4.2  "), 420)

    def test_empty(self):
        for bad in ("", "   ", None):
            with self.assertRaises(MoneyError):
                parse_money(bad)

    def test_unrecognized(self):
        for bad in ("abc", "-1", "3.555", "3.5.6", "一元"):
            with self.assertRaises(MoneyError):
                parse_money(bad)


class BreakdownTest(unittest.TestCase):
    def test_mixed(self):
        rows = breakdown(750)
        self.assertEqual(
            rows,
            [(500, "5 元", 1), (100, "1 元", 2), (50, "5 角", 1)],
        )

    def test_ten_yuan(self):
        self.assertEqual(breakdown(1000), [(1000, "10 元", 1)])

    def test_small(self):
        self.assertEqual(breakdown(10), [(10, "1 角", 1)])
        self.assertEqual(breakdown(50), [(50, "5 角", 1)])

    def test_zero(self):
        self.assertEqual(breakdown(0), [])

    def test_not_multiple_of_ten(self):
        with self.assertRaises(MoneyError):
            breakdown(5)

    def test_negative(self):
        with self.assertRaises(MoneyError):
            breakdown(-10)

    def test_text(self):
        self.assertEqual(
            breakdown_text(750), "5 元 × 1 + 1 元 × 2 + 5 角 × 1"
        )

    def test_text_zero(self):
        self.assertEqual(breakdown_text(0), "0 元")


class ProductTest(unittest.TestCase):
    def test_catalog_size(self):
        self.assertEqual(len(PRODUCTS), 20)

    def test_prices_valid(self):
        for product in PRODUCTS:
            self.assertGreater(product.price_cents, 0)
            self.assertEqual(product.price_cents % 10, 0)

    def test_names_unique(self):
        self.assertEqual(len({product.name for product in PRODUCTS}), len(PRODUCTS))

    def test_price_text(self):
        self.assertEqual(Product("测试", 1250).price_text, "12.50 元")

    def test_invalid_name(self):
        with self.assertRaises(MoneyError):
            Product("", 100)

    def test_invalid_price(self):
        with self.assertRaises(MoneyError):
            Product("测试", 0)

    def test_frozen(self):
        product = Product("测试", 100)
        with self.assertRaises(FrozenInstanceError):
            product.price_cents = 200

    def test_product_table(self):
        rows = product_table()
        self.assertEqual(len(rows), 20)
        self.assertEqual(rows[0]["name"], "铅笔")
        self.assertEqual(rows[0]["text"], "1.50 元")


class WorksheetItemTest(unittest.TestCase):
    def test_single_totals(self):
        item = WorksheetItem("single", (0,), 500)
        self.assertEqual(item.total_cents, 150)
        self.assertEqual(item.change_cents, 350)
        self.assertEqual(item.answer_text, "3.50 元")

    def test_double_totals(self):
        item = WorksheetItem("double", (0, 1), 500)
        self.assertEqual(item.total_cents, 350)
        self.assertEqual(item.change_cents, 150)

    def test_prompt(self):
        item = WorksheetItem("single", (0,), 500)
        self.assertIn("铅笔", item.prompt)
        self.assertIn("1.50 元", item.prompt)
        self.assertIn("付 5 元", item.prompt)

    def test_breakdown(self):
        item = WorksheetItem("single", (0,), 500)
        self.assertEqual(item.breakdown, [(100, "1 元", 3), (50, "5 角", 1)])
        self.assertIn("1 元 × 3", item.breakdown_text)

    def test_items_property(self):
        item = WorksheetItem("double", (0, 1), 500)
        self.assertEqual([product.name for product in item.items], ["铅笔", "橡皮"])

    def test_invalid_kind(self):
        with self.assertRaises(MoneyError):
            WorksheetItem("triple", (0, 1, 2), 500)

    def test_single_needs_one(self):
        with self.assertRaises(MoneyError):
            WorksheetItem("single", (0, 1), 500)

    def test_double_needs_two(self):
        with self.assertRaises(MoneyError):
            WorksheetItem("double", (0,), 500)

    def test_empty_items(self):
        with self.assertRaises(MoneyError):
            WorksheetItem("single", (), 500)

    def test_duplicate_items(self):
        with self.assertRaises(MoneyError):
            WorksheetItem("double", (0, 0), 500)

    def test_index_out_of_range(self):
        with self.assertRaises(MoneyError):
            WorksheetItem("single", (99,), 500)

    def test_paid_not_enough(self):
        with self.assertRaises(MoneyError):
            WorksheetItem("single", (0,), 100)

    def test_paid_equal_total(self):
        with self.assertRaises(MoneyError):
            WorksheetItem("single", (0,), 150)

    def test_paid_bool(self):
        with self.assertRaises(MoneyError):
            WorksheetItem("single", (0,), True)


class CheckAnswerTest(unittest.TestCase):
    def test_plain(self):
        item = WorksheetItem("single", (0,), 500)
        self.assertTrue(check_answer(item, "3.5"))

    def test_units(self):
        item = WorksheetItem("single", (0,), 500)
        self.assertTrue(check_answer(item, "3.50 元"))

    def test_jiao(self):
        item = WorksheetItem("single", (0,), 500)
        self.assertTrue(check_answer(item, "3元5角"))

    def test_wrong(self):
        item = WorksheetItem("single", (0,), 500)
        self.assertFalse(check_answer(item, "4"))

    def test_unparseable(self):
        item = WorksheetItem("single", (0,), 500)
        self.assertFalse(check_answer(item, "很多"))

    def test_empty(self):
        item = WorksheetItem("single", (0,), 500)
        self.assertFalse(check_answer(item, ""))

    def test_non_item(self):
        self.assertFalse(check_answer(None, "3.5"))


class BuildWorksheetTest(unittest.TestCase):
    def test_count(self):
        self.assertEqual(len(build_worksheet(10, seed=1)), 10)

    def test_unique(self):
        items = build_worksheet(12, seed=2)
        keys = {(item.kind, item.product_indexes, item.paid_cents) for item in items}
        self.assertEqual(len(keys), 12)

    def test_kinds(self):
        for item in build_worksheet(12, seed=3):
            self.assertIn(item.kind, KINDS)

    def test_single_shape(self):
        items = build_worksheet(5, seed=4, kinds=("single",))
        for item in items:
            self.assertEqual(len(item.items), 1)

    def test_double_shape(self):
        items = build_worksheet(5, seed=5, kinds=("double",))
        for item in items:
            self.assertEqual(len(item.items), 2)

    def test_deterministic(self):
        first = build_worksheet(6, seed=6)
        second = build_worksheet(6, seed=6)
        self.assertEqual(
            [(item.kind, item.product_indexes, item.paid_cents) for item in first],
            [(item.kind, item.product_indexes, item.paid_cents) for item in second],
        )

    def test_invalid_count(self):
        for bad in (0, -2, True, "6"):
            with self.assertRaises(MoneyError):
                build_worksheet(bad)

    def test_invalid_kind(self):
        with self.assertRaises(MoneyError):
            build_worksheet(3, kinds=("triple",))

    def test_empty_kinds(self):
        with self.assertRaises(MoneyError):
            build_worksheet(3, kinds=())

    def test_too_many(self):
        with self.assertRaises(MoneyError):
            build_worksheet(5000, kinds=("single",))


if __name__ == "__main__":
    unittest.main()
