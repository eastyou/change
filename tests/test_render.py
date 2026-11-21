"""购物找零页面渲染测试。"""

import unittest

from change.model import WorksheetItem
from change.render import render_money_svg, render_worksheet


class MoneySvgTest(unittest.TestCase):
    def test_zero(self):
        svg = render_money_svg(0)
        self.assertIn("<svg", svg)
        self.assertNotIn("<circle", svg)

    def test_coins_only(self):
        svg = render_money_svg(350)
        self.assertEqual(svg.count("<circle"), 2)
        self.assertEqual(svg.count("<rect"), 0)

    def test_bill_and_coins(self):
        svg = render_money_svg(750)
        self.assertEqual(svg.count("<rect"), 1)
        self.assertEqual(svg.count("<circle"), 2)

    def test_labels(self):
        svg = render_money_svg(750)
        self.assertIn("5 元", svg)
        self.assertIn("1 元", svg)
        self.assertIn("5 角", svg)

    def test_counts(self):
        svg = render_money_svg(750)
        self.assertIn("×2", svg)
        self.assertIn("×1", svg)

    def test_aria_label(self):
        self.assertIn('role="img"', render_money_svg(500))


class WorksheetTest(unittest.TestCase):
    def setUp(self):
        self.items = [
            WorksheetItem("single", (0,), 500),
            WorksheetItem("double", (0, 1), 1000),
        ]

    def test_doctype(self):
        self.assertTrue(render_worksheet(self.items).startswith("<!DOCTYPE html>"))

    def test_item_count(self):
        self.assertEqual(render_worksheet(self.items).count('class="item"'), 2)

    def test_prompts(self):
        page = render_worksheet(self.items)
        self.assertIn("铅笔", page)
        self.assertIn("应找回多少元", page)

    def test_paid_amount(self):
        page = render_worksheet(self.items)
        self.assertIn("5.00 元", page)
        self.assertIn("10.00 元", page)

    def test_no_answers_default(self):
        self.assertNotIn("参考答案", render_worksheet(self.items))

    def test_answers(self):
        page = render_worksheet(self.items, include_answers=True)
        self.assertIn("参考答案", page)
        self.assertIn("应找回 3.50 元", page)
        self.assertIn("6.50 元", page)

    def test_answer_breakdown(self):
        page = render_worksheet(self.items, include_answers=True)
        self.assertIn("1 元 × 3", page)

    def test_answer_money_svg(self):
        page = render_worksheet(self.items, include_answers=True)
        self.assertEqual(page.count('class="money"'), 2)

    def test_empty(self):
        with self.assertRaises(ValueError):
            render_worksheet([])

    def test_custom_title(self):
        self.assertIn("找零小测", render_worksheet(self.items, title="找零小测"))

    def test_title_escaped(self):
        page = render_worksheet(self.items, title="<找零>")
        self.assertIn("&lt;找零&gt;", page)

    def test_blank_count(self):
        self.assertEqual(render_worksheet(self.items).count('class="blank"'), 4)


if __name__ == "__main__":
    unittest.main()
