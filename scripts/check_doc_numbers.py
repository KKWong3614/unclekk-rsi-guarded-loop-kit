#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_doc_numbers.py — 全包文档数字一致性校验（防「说明数字与实际对不上」）。

背景：SkillHub 测评多轮扣分「自检数量与实际不一致」「少数步骤数字没同步」。
根因是文档里的 N/N 靠人手写，脚本升级后漏改；早期版本只守护 SKILL.md，
README / getting-started / runnable-guide / walkthrough 仍靠人工同步。
本脚本默认守护【全包所有活动 md 文档】，把文档数字与脚本真实输出机器绑定：

  ① 实跑每个脚本的 --self-test，抓真实用例数（如 gate_min 8/8）；
  ② 逐文档扫描「声明式数字」（gate_min self-test X/Y / AGGREGATE: X/Y 等），
     任何与真实值不符 → 报差异；
  ③ 权威文档（SKILL.md）与数字密集文档必须含全部真实数字，防裸写数字漏改；
  ④ 全包禁止回避式表述（「以实跑为准」「以 --print 输出为准」「N/N 占位」）；
  ⑤ 校验 SKILL.md 文档地图与 references/ 目录双向一致，防避坑清单等新文档变孤岛。

合法数字不误报：退出码 0/1/2/3、免责措辞 N/N、用户自建任务集的 3/3，
都不匹配「声明式数字」模式；CHANGELOG.md 是历史存档，整体排除。

用法：
  python3 check_doc_numbers.py                 # 默认：全包校验（exit 1 = 有不一致）
  python3 check_doc_numbers.py --all           # 显式全包（等价默认）
  python3 check_doc_numbers.py --doc <文件>     # 只校验指定文档
  python3 check_doc_numbers.py --print         # 只打印真实数字，不校验
  python3 check_doc_numbers.py --list          # 列出参与校验的活动文档
  python3 check_doc_numbers.py --self-test     # 内置自检（9/9）
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

# 参与校验的「活动文档」。CHANGELOG.md 是历史存档（旧数字合法），整体排除。
ACTIVE_DOCS = (
    "SKILL.md",
    "README.md",
    "references/getting-started.md",
    "references/runnable-guide.md",
    "references/walkthrough.md",
    "references/faq.md",
    "references/claim-boundary.md",
    "references/four-stage-status.md",
)
# 权威文档 + 数字密集文档：必须出现全部真实数字（覆盖 README 里的裸写 6/6 等）
REQUIRE_ALL_DOCS = frozenset({
    "SKILL.md", "README.md", "references/runnable-guide.md", "references/walkthrough.md",
})
# 只有这些文档里的「[PASS] X/Y 冻结任务通过」是包内 demo（应为 5/5）；
# walkthrough 里用户自建 3 任务集的 3/3 是示例数据，豁免。
DEMO_DOCS = frozenset({"SKILL.md", "README.md", "references/getting-started.md"})

# 每个脚本 self-test 输出的正则 → 真实用例数
SELFTESTS = {
    "gate_min.py": re.compile(r"gate_min self-test (\d+)/(\d+)"),
    "claim_lint.py": re.compile(r"claim_lint self-test (\d+)/(\d+)"),
    "run_loop_min.py": re.compile(r"run_loop_min self-test (\d+)/(\d+)"),
}
AGG_RE = re.compile(r"AGGREGATE: (\d+)/(\d+) scripts passed")
DEMO_RE = re.compile(r"\[PASS\] (\d+)/(\d+) 冻结任务通过")

# 文档中的「声明式数字」：只认脚本名/简写 + self-test 语境，避开退出码与 N/N 免责。
# 每个脚本支持全名与简写两套模式（README 用 gate 8/8，SKILL 用 gate_min self-test 8/8）。
SELFTEST_DECL = {
    "gate_min.py": [
        re.compile(r"\bgate_min(?:\.py)?(?:\s+self-test)?[:\s]+(\d+)/(\d+)"),
        re.compile(r"\bgate(?:\s+self-test)?[:\s]+(\d+)/(\d+)"),
    ],
    "claim_lint.py": [
        re.compile(r"\bclaim_lint(?:\.py)?(?:\s+self-test)?[:\s]+(\d+)/(\d+)"),
        re.compile(r"\bclaim(?:\s+self-test)?[:\s]+(\d+)/(\d+)"),
    ],
    "run_loop_min.py": [
        re.compile(r"\brun_loop_min(?:\.py)?(?:\s+self-test)?[:\s]+(\d+)/(\d+)"),
        re.compile(r"\bloop(?:\s+self-test)?[:\s]+(\d+)/(\d+)"),
    ],
}
AGG_DECL = re.compile(r"AGGREGATE:\s*(\d+)/(\d+)\s*scripts\s+passed")
DEMO_DECL = re.compile(r"\[PASS\]\s*(\d+)/(\d+)\s*冻结任务通过")

# 回避式表述：测评多次把这类写法判成「无法核对」，一律禁止（CHANGELOG 已排除）。
VAGUE_PATTERNS = (
    ("以实跑为准", re.compile(r"以实跑(?:输出)?为准")),
    ("以 --print 输出为准", re.compile(r"以\s*`?[^`\n]{0,60}--print`?[^`\n]{0,20}输出为准")),
    ("N/N 占位", re.compile(r"(?:AGGREGATE|self-test)[^\n]{0,20}N/N")),
)

DOC_REF_RE = re.compile(r"references/[A-Za-z0-9_-]+\.md")


def _run(script: str) -> str:
    r = subprocess.run([sys.executable, str(HERE / script), "--self-test"],
                       capture_output=True, text=True, timeout=60)
    return (r.stdout or "") + (r.stderr or "")


def collect() -> dict:
    """实跑拿真实数字。"""
    out = {}
    for script, pat in SELFTESTS.items():
        m = pat.search(_run(script))
        out[script] = f"{m.group(1)}/{m.group(2)}" if m else None
    agg = subprocess.run([sys.executable, str(HERE / "test_all.py")],
                         capture_output=True, text=True, timeout=60)
    m = AGG_RE.search(agg.stdout or "")
    out["AGGREGATE"] = f"{m.group(1)}/{m.group(2)}" if m else None
    demo = subprocess.run([sys.executable, str(HERE / "gate_min.py")],
                          capture_output=True, text=True, timeout=60)
    m = DEMO_RE.search(demo.stdout or "")
    out["DEMO"] = f"{m.group(1)}/{m.group(2)}" if m else None
    return out


def check_text(text: str, real: dict, *, require_all: bool = False,
               check_demo: bool = False) -> list[str]:
    """与 check 同逻辑，输入是文本（供 self-test 与单文档校验复用）。"""
    problems: list[str] = []
    # 1) 权威/数字密集文档必须含全部【脚本/聚合】真实数字（覆盖裸写数字漏改）。
    #    DEMO 是包内示意数据，只在 DEMO_DOCS 用 check_demo 校验，不强加给所有文档。
    if require_all:
        for script, val in real.items():
            if script == "DEMO":
                continue
            if val is None:
                problems.append(f"无法从脚本输出提取数字: {script}")
            elif val not in text:
                problems.append(f"文档缺少真实数字 {val}（来自 {script}）")
    # 2) 声明式数字：任何与真实值不符都报（精确模式，退出码/N N 不会命中）
    for script, patterns in SELFTEST_DECL.items():
        val = real.get(script)
        if not val:
            continue
        for pat in patterns:
            for m in pat.finditer(text):
                seen = f"{m.group(1)}/{m.group(2)}"
                if seen != val:
                    problems.append(f"{script} 文档数字 {seen} ≠ 真实 {val}")
    if real.get("AGGREGATE"):
        for m in AGG_DECL.finditer(text):
            seen = f"{m.group(1)}/{m.group(2)}"
            if seen != real["AGGREGATE"]:
                problems.append(f"AGGREGATE 文档数字 {seen} ≠ 真实 {real['AGGREGATE']}")
    if check_demo and real.get("DEMO"):
        for m in DEMO_DECL.finditer(text):
            seen = f"{m.group(1)}/{m.group(2)}"
            if seen != real["DEMO"]:
                problems.append(f"demo 数字 {seen} ≠ 真实 {real['DEMO']}")
    # 3) 回避式表述
    for label, pat in VAGUE_PATTERNS:
        if pat.search(text):
            problems.append(f"文档仍有回避式表述「{label}」，应写确切数字")
    return problems


def check(doc: Path, real: dict, rel: str | None = None) -> list[str]:
    """校验单个文档；rel 为相对 ROOT 的路径（决定 require_all/check_demo）。"""
    rel = rel or doc.name
    try:
        text = doc.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"读不到文档 {doc}: {exc}"]
    # 变更记录是历史叙述，旧数字/回避式措辞合法，不参与校验
    cut = re.search(r"^## 变更记录", text, re.MULTILINE)
    if cut:
        text = text[:cut.start()]
    return check_text(text, real,
                      require_all=(rel in REQUIRE_ALL_DOCS),
                      check_demo=(rel in DEMO_DOCS))


def doc_map_problems(skill_text: str, refs_present: set[str]) -> list[str]:
    """SKILL.md 文档地图与 references/ 目录双向一致性。"""
    listed = set(DOC_REF_RE.findall(skill_text))
    problems = []
    for ref in sorted(listed - refs_present):
        problems.append(f"文档地图引用不存在的 references 文件: {ref}")
    for ref in sorted(refs_present - listed):
        problems.append(f"references 文件未被 SKILL.md 文档地图列出: {ref}")
    return problems


def check_all(real: dict) -> tuple[list[str], dict[str, list[str]]]:
    """全包校验；返回 (所有问题, 每文档问题映射)。"""
    all_problems: list[str] = []
    per_doc: dict[str, list[str]] = {}
    for rel in ACTIVE_DOCS:
        ps = check(ROOT / rel, real, rel)
        per_doc[rel] = ps
        all_problems.extend(f"{rel}: {p}" for p in ps)
    # 文档地图双向一致（防避坑清单等新文档变孤岛）
    refs_dir = ROOT / "references"
    refs_present = ({p.relative_to(ROOT).as_posix() for p in refs_dir.glob("*.md")}
                    if refs_dir.exists() else set())
    try:
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    except OSError as exc:
        skill_text = ""
        all_problems.append(f"读不到 SKILL.md 用于文档地图校验: {exc}")
    for p in doc_map_problems(skill_text, refs_present):
        all_problems.append(f"文档地图: {p}")
    return all_problems, per_doc


def self_test() -> int:
    real = {"gate_min.py": "8/8", "claim_lint.py": "6/6", "run_loop_min.py": "10/10",
            "AGGREGATE": "3/3", "DEMO": "5/5"}
    base = ("| gate | gate_min self-test 8/8 |\n"
            "| claim | claim_lint self-test 6/6 |\n"
            "| loop | run_loop_min self-test 10/10 |\n"
            "| agg | AGGREGATE: 3/3 scripts passed |\n"
            "| demo | [PASS] 5/5 冻结任务通过 |")
    stale = base.replace("claim_lint self-test 6/6", "claim_lint self-test 4/4")
    vague = base.replace("AGGREGATE: 3/3 scripts passed", "AGGREGATE: N/N（以实跑为准）")
    vague_print = "看到 `AGGREGATE: 3/3 scripts passed` 就对了（升级后以 `python3 scripts/check_doc_numbers.py --print` 输出为准）。"
    ok = {
        # 正向：真实数字齐全即通过
        "all_present": check_text(base, real, require_all=True, check_demo=True) == [],
        # 旧数字被抓（声明式 + 缺失真实值双通道）
        "stale_caught": any("claim_lint" in p or "4/4" in p
                            for p in check_text(stale, real, require_all=True)),
        # 回避式表述被抓（以实跑为准）
        "vague_caught": any("回避式" in p
                            for p in check_text(vague, real, require_all=True)),
        # 回避式表述被抓（以 --print 输出为准，closure backtick 变体）
        "vague_print_caught": any("回避式" in p
                                  for p in check_text(vague_print, real)),
        # 退出码 0/1/2/3 不误报
        "exit_code_safe": check_text(base + "\n退出码 0/1/2/3, 0/1/2/3", real) == [],
        # 免责措辞 N/N 不误报
        "nn_disclaimer_safe": check_text(base + "\nPASS / 全绿 / N/N 只表示回归未退化", real) == [],
        # 用户自建 3 任务集的 3/3 不误报（非 demo 文档不校验 demo 数字）
        "user_demo_safe": check_text(base + "\n# [PASS] 3/3 冻结任务通过", real) == [],
        # 文档地图：引用不存在的文件被抓
        "docmap_missing_caught": any("不存在" in p for p in
                                     doc_map_problems("见 references/nope.md", {"references/faq.md"})),
        # 文档地图：存在但未列出的孤岛文档被抓
        "docmap_orphan_caught": any("未被" in p for p in
                                    doc_map_problems("见 references/faq.md",
                                                     {"references/faq.md", "references/orphan.md"})),
    }
    passed = sum(ok.values())
    total = len(ok)
    for name, good in ok.items():
        if not good:
            print(f"[FAIL] self-test case: {name}")
    print(f"[{'PASS' if passed == total else 'FAIL'}] check_doc_numbers self-test {passed}/{total}")
    return 0 if passed == total else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="全包文档数字一致性校验")
    ap.add_argument("--all", action="store_true", help="校验全包活动文档（默认行为）")
    ap.add_argument("--doc", type=Path, help="只校验指定文档")
    ap.add_argument("--print", action="store_true", help="只打印真实数字，不校验")
    ap.add_argument("--list", action="store_true", help="列出参与校验的活动文档")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    if args.list:
        for rel in ACTIVE_DOCS:
            print(rel)
        return 0
    real = collect()
    if args.print:
        for k, v in real.items():
            print(f"{k}: {v}")
        return 0
    for k, v in real.items():
        print(f"[REAL] {k}: {v}")
    if args.doc is not None:
        problems = check(args.doc, real)
        for p in problems:
            print(f"[MISMATCH] {p}")
        if problems:
            print(f"[VERDICT] {args.doc.name} 数字不一致 → {len(problems)} 处（exit 1）")
            return 1
        print(f"[PASS] {args.doc.name} 文档数字与脚本真实输出一致")
        return 0
    problems, per_doc = check_all(real)
    for rel, ps in per_doc.items():
        for p in ps:
            print(f"[MISMATCH] {rel}: {p}")
    if problems:
        print(f"[VERDICT] 全包数字不一致 → {len(problems)} 处 / {len(ACTIVE_DOCS)} 文档（exit 1）")
        return 1
    print(f"[PASS] 全包 {len(ACTIVE_DOCS)} 个活动文档数字一致，文档地图完整")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
