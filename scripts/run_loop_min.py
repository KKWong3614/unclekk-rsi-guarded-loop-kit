#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""run_loop_min.py — 零依赖「四段最小链」一键入口。

把方法论四段串成一条可运行链：
  ① 诊断 → ② 选流 → ③ 蒸馏骨架 → ④ 门禁 → 报告

诚实边界（必须随使用保留）：
- ③ 只产出「候选 SOP 骨架 + 待填槽位」，不生成最终技能、不自动写回、不自动批准。
- ④ 门禁只判「冻结基线是否退化」，PASS 不等于能力变强。
- 全程零第三方依赖、不联网、不调用任何模型；这是一条**确定性编排骨架**，
  不宣称严格 RSI 完成态、不宣称四段自动落地（严格）。

退出码：0=门禁通过 1=门禁退化 2=输入错误 3=完整性/边界告警
用法：
  python3 run_loop_min.py                          # 用随包 demo 走一遍
  python3 run_loop_min.py --signals s.json --tasks t.json --results r.json --out report.json
  python3 run_loop_min.py --self-test
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIX = HERE / "fixtures"

# ① 诊断归桶：只做确定性规则分类，不给「能力变强」结论。
BUCKETS = {
    "missing_result": "冻结任务缺结果 → 交付不完整",
    "failed_result": "冻结任务未通过 → 行为退化",
    "empty_tasks": "冻结任务集为空 → 判据不可信",
    "integrity": "哈希锁不符 → 输入完整性告警",
}

# ② 选流：候选工作流 + 禁止项（硬约束，不可用「捷径解」绕过门禁）。
ALLOWED_FLOWS = ["freeze_then_gate", "diagnose_then_patch", "abstain"]
FORBIDDEN = ["auto_approve", "auto_writeback", "edit_judge", "skip_gate"]


def diagnose(signals: list[dict]) -> dict:
    """把信号列表归桶，输出主瓶颈与计数；不输出价值判断。"""
    counts: dict[str, int] = {}
    for s in signals:
        kind = s.get("kind", "unknown")
        if kind in BUCKETS:
            counts[kind] = counts.get(kind, 0) + 1
    primary = max(counts, key=counts.get) if counts else "none"
    return {
        "primary": primary,
        "label": BUCKETS.get(primary, "无显著瓶颈 / 需人工判定"),
        "counts": counts,
        "signals_seen": len(signals),
    }


def select_flow(diag: dict) -> dict:
    """按诊断主瓶颈选一条确定性工作流，附禁止项。"""
    p = diag.get("primary")
    if p in ("failed_result", "missing_result"):
        flow = "diagnose_then_patch"
    elif p == "empty_tasks" or p == "integrity":
        flow = "abstain"
    else:
        flow = "freeze_then_gate"
    if flow not in ALLOWED_FLOWS:  # 防御：永不返回白名单外工作流
        flow = "abstain"
    return {"flow": flow, "forbidden": list(FORBIDDEN),
            "note": "选流为确定性建议，最终选流仍需人工确认"}


def distill_skeleton(flow: str) -> dict:
    """③ 只产出候选骨架 + 待填槽位；明确「非最终技能、需人工/外部模型」。"""
    return {
        "skeleton": [
            "STEP 冻结基线：读取任务集与哈希锁",
            "STEP 诊断：按证据归桶，标注主瓶颈",
            "STEP 选流：选定工作流 {flow} 并声明禁止项",
            "STEP 蒸馏：产出候选 SOP 骨架（槽位 {{candidate_sop}} 待填）",
            "STEP 门禁：候选结果逐项对冻结任务判定，缺项/失败即退化",
        ],
        "slots": ["flow", "candidate_sop", "human_reviewer", "evidence_refs"],
        "filled": {"flow": flow},
        "is_final_skill": False,
        "auto_writeback": False,
        "caveat": "仅骨架，非最终技能；不自动写回、不自动批准；严格 RSI 不可声称",
    }


def gate(tasks: dict, results: dict, lock: dict | None = None,
         task_hash: str | None = None) -> dict:
    """④ 复用 gate_min.check 的同一判据：逐项通过才未退化；异常 fail-closed 不崩溃。"""
    def _items(obj, key):
        if not isinstance(obj, dict) or not isinstance(obj.get(key, []), list):
            return None
        return obj[key]
    t_items, r_items = _items(tasks, "tasks"), _items(results, "results")
    def _bad(verdict, msg, meaning):
        return {"passed": False, "verdict": verdict, "problems": [msg], "meaning": meaning}
    if t_items is None or r_items is None:
        return _bad("INPUT_ERROR", "输入结构错误: tasks/results 应为含对应数组的对象", "输入错误 → 不判定、需修正后重试")
    for i, t in enumerate(t_items):
        if not isinstance(t, dict) or not isinstance(t.get("id"), str):
            return _bad("INPUT_ERROR", f"输入结构错误: tasks[{i}] 缺少字符串 id", "输入错误 → 不判定、需修正后重试")
    for i, r in enumerate(r_items):
        if not isinstance(r, dict) or not isinstance(r.get("id"), str):
            return _bad("INPUT_ERROR", f"输入结构错误: results[{i}] 缺少字符串 id", "输入错误 → 不判定、需修正后重试")
    expected = {t["id"] for t in t_items}
    got = {r["id"]: r for r in r_items}
    if isinstance(lock, dict) and lock.get("task_sha256") and task_hash and lock["task_sha256"] != task_hash:
        return _bad("INTEGRITY", "任务集哈希不符 → fail-closed", "完整性告警 → 拒绝放行")
    if not expected:
        return _bad("REGRESSION", "冻结任务集为空 → 判据不可信", "回归退化 → 不自动批准/不自动修复")
    problems = []
    for tid in sorted(expected):
        if tid not in got:
            problems.append(f"缺结果: {tid}")
        elif not got[tid].get("passed"):
            problems.append(f"未通过: {tid} — {got[tid].get('reason', '')}")
    return {
        "passed": not problems,
        "verdict": "PASS" if not problems else "REGRESSION",
        "problems": problems,
        "total": len(expected),
        "meaning": "回归未退化（非能力提升）" if not problems else "回归退化 → 不自动批准/不自动修复",
    }


def _signals_from_results(results: dict) -> list[dict]:
    """把结果集的失败项转成 ① 诊断信号（demo/默认路径用）。结构异常返回空，交 gate fail-closed。"""
    out = []
    items = results.get("results", []) if isinstance(results, dict) else []
    if not isinstance(items, list):
        return out
    for r in items:
        if isinstance(r, dict) and not r.get("passed"):
            out.append({"kind": "failed_result", "id": r.get("id", "?"),
                        "reason": r.get("reason", "")})
    return out


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def loop(signals: list[dict], tasks: dict, results: dict,
         lock: dict | None = None, task_hash: str | None = None) -> dict:
    d = diagnose(signals)
    f = select_flow(d)
    s = distill_skeleton(f["flow"])
    g = gate(tasks, results, lock, task_hash)
    return {
        "ts": datetime.now(timezone.utc).isoformat(),
        "stages": {"1_diagnose": d, "2_select": f, "3_distill_skeleton": s, "4_gate": g},
        "verdict": g["verdict"],
        "claim_boundary": "PASS=回归未退化；非能力变强；非严格 RSI；非四段自动落地（严格）",
    }


def self_test() -> int:
    t = {"tasks": [{"id": "a"}, {"id": "b"}]}
    ok = {}
    ok["pass_path"] = loop([], t, {"results": [
        {"id": "a", "passed": True}, {"id": "b", "passed": True}]})["verdict"] == "PASS"
    ok["regression"] = loop([{"kind": "failed_result"}], t, {"results": [
        {"id": "a", "passed": True}, {"id": "b", "passed": False}]})["verdict"] == "REGRESSION"
    ok["empty_tasks"] = loop([{"kind": "empty_tasks"}], {"tasks": []}, {"results": []})["verdict"] == "REGRESSION"
    ok["integrity"] = loop([], t, {"results": []},
                           {"task_sha256": "deadbeef"}, "different")["verdict"] == "INTEGRITY"
    ok["abstain_on_bad_input"] = select_flow({"primary": "integrity"})["flow"] == "abstain"
    ok["skeleton_not_final"] = distill_skeleton("abstain")["is_final_skill"] is False
    ok["no_auto_writeback"] = distill_skeleton("abstain")["auto_writeback"] is False
    ok["forbidden_kept"] = "auto_writeback" in select_flow({"primary": "none"})["forbidden"]
    # 结构异常：不崩溃，判 INPUT_ERROR
    ok["tasks_not_dict"] = gate([1, 2], {"results": []})["verdict"] == "INPUT_ERROR"
    ok["result_item_bad"] = gate(t, {"results": ["x"]})["verdict"] == "INPUT_ERROR"
    passed = sum(ok.values())
    for name, good in ok.items():
        if not good:
            print(f"[FAIL] self-test case: {name}")
    total = 10
    print(f"[{'PASS' if passed == total else 'FAIL'}] run_loop_min self-test {passed}/{total}")
    return 0 if passed == total else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="零依赖四段最小链一键入口")
    ap.add_argument("--signals", type=Path, help="① 诊断信号 JSON（默认由结果集失败项派生）")
    ap.add_argument("--tasks", type=Path, default=FIX / "tasks.json")
    ap.add_argument("--results", type=Path, default=FIX / "results.json")
    ap.add_argument("--lock", type=Path, help="可选哈希锁 JSON（含 task_sha256）")
    ap.add_argument("--out", type=Path, help="报告输出路径；省略则只打印摘要")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    try:
        tasks = json.loads(args.tasks.read_text(encoding="utf-8"))
        results = json.loads(args.results.read_text(encoding="utf-8"))
        lock = json.loads(args.lock.read_text(encoding="utf-8")) if args.lock else None
        task_hash = _sha(args.tasks) if isinstance(lock, dict) else None
        if args.signals:
            sig_obj = json.loads(args.signals.read_text(encoding="utf-8"))
            signals = sig_obj.get("signals", []) if isinstance(sig_obj, dict) else []
            if not isinstance(signals, list):
                print("[INPUT ERROR] signals 应为数组", file=sys.stderr)
                return 2
        else:
            signals = _signals_from_results(results)
    except (OSError, ValueError) as exc:
        print(f"[INPUT ERROR] {exc}", file=sys.stderr)
        return 2
    report = loop(signals, tasks, results, lock, task_hash)
    if args.out:
        try:
            args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        except OSError as exc:
            print(f"[OUTPUT ERROR] 报告写入失败: {exc}（判定仍已完成）", file=sys.stderr)
            return 2
    print(f"[① 诊断] {report['stages']['1_diagnose']['label']}")
    print(f"[② 选流] {report['stages']['2_select']['flow']}（禁止项已声明）")
    print(f"[③ 蒸馏] 候选骨架已生成（is_final_skill=false，不自动写回）")
    g = report["stages"]["4_gate"]
    print(f"[④ 门禁] {g['verdict']} — {g['meaning']}")
    print(f"[边界] {report['claim_boundary']}")
    if args.out:
        print(f"[报告] {args.out}")
    return {"PASS": 0, "REGRESSION": 1, "INPUT_ERROR": 2, "INTEGRITY": 3}.get(report["verdict"], 1)


if __name__ == "__main__":
    raise SystemExit(main())
