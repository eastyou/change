# change

[![CI](https://github.com/eastyou/change/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/change/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)

购物找零：商品总价、付款、找零计算与硬币拆分，生成可打印练习纸。

## 特性

- 20 件文具商品，价格以分存储，避免浮点误差
- 一件或两件商品的购物题，付款从 5/10/20/50/100 元中选取
- 找零自动拆成 50/20/10/5/1 元与 5 角、1 角
- 答案支持 `3.5`、`3.50 元`、`3元5角` 等写法
- 答案页附找零纸币与硬币示意图
- 纯标准库，零依赖，跨平台

## 安装

```bash
python -m pip install -e .
```

## 用法

```bash
change change 12.5 20
change catalog
change sheet --count 12 --seed 3 --answers -o sheet.html
change sheet --count 8 --kinds double -o double.html
```

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| `--count` | 题目数量 | 12 |
| `--kinds` | 题型，`single` 或 `double`，逗号分隔 | 两种都出 |
| `--seed` | 随机种子 | 无 |
| `--answers` | 追加参考答案 | 关闭 |

## 题型

- `single`：买一件商品，算找零
- `double`：买两件商品，先算总价再算找零

## 示例

- [examples/change.html](examples/change.html)：12 道购物找零题，带答案与硬币图

## 测试

```bash
python -m unittest discover -s tests -v
```

## 说明

金额统一使用整数分，找零拆分按现有面值贪心计算。价格与商品为教学示例，不构成真实售价。

## 协议

MIT © 2026 eastyou
