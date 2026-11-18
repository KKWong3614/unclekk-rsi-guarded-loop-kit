#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gate_min.py — 零依赖最小回归门禁（本包的最小可运行实例）。

只读冻结任务集，判定「候选结果是否让基线退化」，不做任何写回、不改判据、
不自动批准。判据异常一律 fail-closed（拒绝放行）。

退出码：0=通过 1=回归退化 2=输入错误 3=完整性告警
用法：
  python3 gate_min.py                       # 跑随包 fixtures 示意数据
  python3 gate_min.py --tasks <tasks.json> --results <results.json>
  python3 gate_min.py --self-test
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIX = HERE / "fixtures"


def _load(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"无法读取 {p.name}: {exc}")


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _as_items(obj, key: str):
    """安全取列表字段；结构不对返回 None 而不是抛异常（fail-closed）。"""
    if not isinstance(obj, dict):
        return None
    items = obj.get(key, [])
    if not isinstance(items, list):
        return None
    return items


def check(tasks: dict, results: dict) -> tuple[bool, list[str]]:
    """判定：每个冻结任务都必须有通过结果；缺项/失败即退化。结构异常一律 fail-closed。"""
    t_items = _as_items(tasks, "tasks")
    r_items = _as_items(results, "results")
    if t_items is None:
        return False, ["输入结构错误: tasks 应为含 tasks 数组的对象"]
    if r_items is None:
        return False, ["输入结构错误: results 应为含 results 数组的对象"]
    # 逐项校验：任务/结果项必须是对象且带字符串 id，否则 fail-closed 而非崩溃
    for i, t in enumerate(t_items):
        if not isinstance(t, dict) or not isinstance(t.get("id"), str):
            return False, [f"输入结构错误: tasks[{i}] 缺少字符串 id"]
    for i, r in enumerate(r_items):
        if not isinstance(r, dict) or not isinstance(r.get("id"), str):
            return False, [f"输入结构错误: results[{i}] 缺少字符串 id"]
    expected = {t["id"] for t in t_items}
    got = {r["id"]: r for r in r_items}
    if not expected:
        return False, ["冻结任务集为空"]
    problems = []
    for tid in sorted(expected):
        if tid not in got:
            problems.append(f"缺结果: {tid}")
        elif not got[tid].get("passed"):
            problems.append(f"未通过: {tid} — {got[tid].get('reason', '')}")
    return (not problems), problems


def run(tasks_p: Path, results_p: Path, lock_p: Path | None) -> int:
    tasks = _load(tasks_p)
    results = _load(results_p)
    # 完整性：若提供哈希锁，任务集字节哈希必须匹配，否则 fail-closed
    if lock_p and lock_p.is_file():
        lock = _load(lock_p)
        want = lock.get("task_sha256") if isinstance(lock, dict) else None
        if want is not None and not isinstance(want, str):
            print(f"[INPUT ERROR] 哈希锁 task_sha256 应为字符串 ({lock_p.name})", file=sys.stderr)
            return 2
        if want and _sha(tasks_p) != want:
            print(f"[INTEGRITY] 任务集哈希不符 → fail-closed ({lock_p.name})")
            return 3
    ok, problems = check(tasks, results)
    if ok:
        print(f"[PASS] {len(tasks['tasks'])}/{len(tasks['tasks'])} 冻结任务通过 = 回归未退化（非能力提升）")
        return 0
    for p in problems:
        print(f"[FAIL] {p}")
    print("[VERDICT] 回归退化 → 不通过（不自动批准、不自动修复）")
    return 1


def self_test() -> int:
    t = {"tasks": [{"id": "a"}, {"id": "b"}]}
    cases = [
        ({"results": [{"id": "a", "passed": True}, {"id": "b", "passed": True}]}, True),
        ({"results": [{"id": "a", "passed": True}]}, False),
        ({"results": [{"id": "a", "passed": True}, {"id": "b", "passed": False}]}, False),
    ]
    ok = 0
    for res, want in cases:
        got, _ = check(t, res)
        if got == want:
            ok += 1
        else:
            print(f"[FAIL] self-test case want={want} got={got}")
    # 负例：空任务集 + 结构异常都应 fail-closed（不崩溃）
    empty_ok, _ = check({"tasks": []}, {"results": []})
    if not empty_ok:
        ok += 1
    bad_structs = [
        ([1, 2, 3], {"results": []}),                    # tasks 非 dict
        ({"tasks": [1]}, {"results": []}),               # task 项非 dict
        ({"tasks": [{"id": "a"}]}, {"results": ["x"]}),  # result 项非 dict
        ({"tasks": "bad"}, {"results": []}),             # tasks 字段非 list
    ]
    for tasks_bad, results_bad in bad_structs:
        try:
            bad_ok, _ = check(tasks_bad, results_bad)
            if not bad_ok:
                ok += 1
        except Exception:
            print("[FAIL] self-test: 结构异常不应抛异常")
    total = 8
    print(f"[{'PASS' if ok == total else 'FAIL'}] gate_min self-test {ok}/{total}")
    return 0 if ok == total else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="零依赖最小回归门禁")
    ap.add_argument("--tasks", type=Path, default=FIX / "tasks.json")
    ap.add_argument("--results", type=Path, default=FIX / "results.json")
    ap.add_argument("--lock", type=Path, default=None)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    try:
        return run(args.tasks, args.results, args.lock)
    except (ValueError, FileNotFoundError) as exc:
        print(f"[INPUT ERROR] {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
