"""支持 python -m change 调用。"""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
