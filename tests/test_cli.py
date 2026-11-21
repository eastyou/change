"""命令行测试。"""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from change.cli import main


def run_cli(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


class ChangeCommandTest(unittest.TestCase):
    def test_basic(self):
        code, out, _ = run_cli(["change", "12.5", "20"])
        self.assertEqual(code, 0)
        self.assertIn("找零：7.50 元", out)
        self.assertIn("5 元 × 1", out)
        self.assertIn("1 元 × 2", out)
        self.assertIn("5 角 × 1", out)

    def test_whole(self):
        code, out, _ = run_cli(["change", "3", "5"])
        self.assertEqual(code, 0)
        self.assertIn("找零：2.00 元", out)

    def test_units(self):
        code, out, _ = run_cli(["change", "12.5元", "20元"])
        self.assertEqual(code, 0)
        self.assertIn("7.50 元", out)

    def test_totals(self):
        code, out, _ = run_cli(["change", "1.5", "10"])
        self.assertEqual(code, 0)
        self.assertIn("商品总价：1.50 元", out)
        self.assertIn("付款：10.00 元", out)

    def test_paid_too_little(self):
        code, _, err = run_cli(["change", "20", "10"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_zero_price(self):
        code, _, err = run_cli(["change", "0", "10"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_unparseable(self):
        code, _, err = run_cli(["change", "abc", "10"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)


class CatalogCommandTest(unittest.TestCase):
    def test_lists_products(self):
        code, out, _ = run_cli(["catalog"])
        self.assertEqual(code, 0)
        self.assertIn("铅笔", out)
        self.assertIn("1.50 元", out)

    def test_all_products(self):
        code, out, _ = run_cli(["catalog"])
        self.assertEqual(code, 0)
        self.assertIn("书包", out)
        self.assertIn("89.00 元", out)


class SheetCommandTest(unittest.TestCase):
    def test_stdout(self):
        code, out, _ = run_cli(["sheet", "--count", "2", "--seed", "1"])
        self.assertEqual(code, 0)
        self.assertIn("<!DOCTYPE html>", out)

    def test_item_count(self):
        code, out, _ = run_cli(["sheet", "--count", "6", "--seed", "2"])
        self.assertEqual(code, 0)
        self.assertEqual(out.count('class="item"'), 6)

    def test_answers(self):
        code, out, _ = run_cli(["sheet", "--count", "3", "--seed", "3", "--answers"])
        self.assertEqual(code, 0)
        self.assertIn("参考答案", out)
        self.assertIn("应找回", out)

    def test_writes_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = os.path.join(folder, "sheet.html")
            code, out, _ = run_cli(["sheet", "--count", "2", "--seed", "4", "-o", target])
            self.assertEqual(code, 0)
            self.assertIn("已写入", out)
            self.assertTrue(os.path.exists(target))

    def test_single_only(self):
        code, out, _ = run_cli(["sheet", "--count", "4", "--seed", "5", "--kinds", "single"])
        self.assertEqual(code, 0)
        self.assertEqual(out.count('class="item"'), 4)

    def test_custom_title(self):
        code, out, _ = run_cli(["sheet", "--count", "1", "--title", "超市小测"])
        self.assertEqual(code, 0)
        self.assertIn("超市小测", out)

    def test_invalid_count(self):
        code, _, err = run_cli(["sheet", "--count", "0"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_invalid_kind(self):
        code, _, err = run_cli(["sheet", "--kinds", "triple"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_seed_reproducible(self):
        _, first, _ = run_cli(["sheet", "--count", "4", "--seed", "9"])
        _, second, _ = run_cli(["sheet", "--count", "4", "--seed", "9"])
        self.assertEqual(first, second)


class HelpTest(unittest.TestCase):
    def test_help_exits_zero(self):
        with redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                main(["--help"])
        self.assertEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
