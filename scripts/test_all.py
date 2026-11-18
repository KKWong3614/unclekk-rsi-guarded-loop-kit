#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_all.py — 聚合自检：一次跑遍本包全部脚本的内置用例。零依赖。"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# 只聚合「被测脚本」。check_doc_numbers.py 是校验这些数字的元工具，
# 若把自己计入会导致 AGGREGATE 数字自我引用、每次改它都触发文档漂移。
SCRIPTS = ["gate_min.py", "claim_lint.py", "run_loop_min.py"]


def main() -> int:
    total = 0
    for name in SCRIPTS:
        p = HERE / name
        r = subprocess.run([sys.executable, str(p), "--self-test"],
                           capture_output=True, text=True)
        line = (r.stdout or r.stderr).strip().splitlines()
        print(f"[{'PASS' if r.returncode == 0 else 'FAIL'}] {name}: "
              f"{line[-1] if line else 'no output'}")
        total += 0 if r.returncode == 0 else 1
    print(f"AGGREGATE: {len(SCRIPTS) - total}/{len(SCRIPTS)} scripts passed")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
