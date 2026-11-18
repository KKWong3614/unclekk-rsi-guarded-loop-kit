#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""claim_lint.py — 宣称边界 linter（只报告，不改文件、不提升级）。

对齐本包 references/claim-boundary.md。strict 模式要求「方法论内核」「精简版」
两个限定词与 PASS 免责声明同时在场。除显性禁语外，还检测隐性夸大（绝对化 /
品质形容词暗示已达标，如 100%可靠、显著提升、彻底解决），并用章节感知 +
否定豁免避免误伤「不可声称」反例表。退出码 0=干净 1=违规 2=输入错误。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# 显性禁语：直接触碰严格完成态 / 能力宣称的措辞。
PROHIBITED = [
    ("T1_loop_auto", [r"四段闭环自动落地", r"four[- ]?stage loop implemented automatically", r"闭环自动落地"]),
    ("T2_rsi_achieved", [r"已实现递归自我改进", r"recursive self[- ]?improvement achieved", r"已实现\s*rsi\b", r"rsi achieved"]),
    ("capability_gain", [r"能力变强", r"capability (gain|improved)", r"语义质量达标"]),
    ("live_loop", [r"实时闭环已验证", r"live loop (validated|verified)"]),
]
# 隐性夸大：不点名 RSI，但用绝对化 / 品质形容词暗示「已达标 / 已变强」。
# 测评反馈「面对复杂表述判断较浅」主要针对这一类——它不是关键词命中，需单列。
SUBTLE = [
    ("absolute", [r"100\s*%", r"百分百", r"完全(正确|可靠|准确|自主|自动|无)", r"零(错误|失误|缺陷|风险)",
                  r"永不(失败|出错|退化)", r"万无一失", r"绝对(可靠|正确|安全)"]),
    ("superlative", [r"显著(提升|改善|增强|变强|进步)", r"质的(飞跃|提升|改变)",
                     r"大幅(提升|改善|增强|进步)", r"能力(显著|大幅)提高",
                     r"全(面)?(领先|超越|最优|最强)", r"彻底(解决|完成|实现)"]),
    ("maturity", [r"已(成为|是)?成熟(的)?(系统|方案|产品)", r"生产级(就绪|可用)",
                  r"可直接(上线|商用|部署到生产)", r"已(达到|具备)严格"]),
]
# 否定 / 限定词：出现在命中窗口内即视为「在解释边界」而非宣称。
SAFE = ["不可", "不能", "未", "不是", "禁止", "避免", "杜绝", "别把", "不等于", "不代表", "非严格", "非完成态",
        "无法", "难以", "尚", "仍", "no ", "not", "prohibited", "cannot", "never", "non-", "avoid", "do not",
        "无显著", "非实测", "demo",
        # 否定性动词短语：诚实表述常用「不声称/不宣称 X」，X 本身是禁语但整句在划边界
        "不声称", "不宣称", "不承诺", "不保证", "不说", "未声称", "未宣称", "绝不", "非能力", "不代表能力"]
WINDOW = 80
REQUIRED = ["方法论内核", "精简版"]
# 上下文语境：代码块（反例演示）与引用内的词不是本文件自身的宣称。
CODE_FENCE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE = re.compile(r"`[^`\n]+`")
QUOTED = re.compile(r"[「『\"'][^」』\"'\n]{1,60}[」』\"']")


def _context_free(text: str, s: int, e: int) -> bool:
    """命中是否落在代码块 / 行内代码 / 引号内——这些是引用或反例，不是宣称。"""
    for pat in (CODE_FENCE, INLINE_CODE, QUOTED):
        for m in pat.finditer(text):
            if m.start() <= s and e <= m.end():
                return True
    return False


# 阴性章节标题：这些章节本就收录禁语作反例，命中不算宣称。
NEG_HEADINGS = ["不可声称", "不允许说", "禁止", "反例", "误判", "负面", "边界", "negative",
                "prohibited", "not claimable", "常见错误", "踩坑"]


def _in_negative_section(text: str, pos: int) -> bool:
    """命中是否位于「不可声称/反例/边界」等阴性章节下（章节以 markdown 标题划分）。"""
    last_heading = ""
    for line in text[:pos].split("\n"):
        if line.strip().startswith("#"):
            last_heading = line
    low = last_heading.lower()
    return any(k.lower() in low for k in NEG_HEADINGS)


def _ok(text, s, e):
    """命中是否被同句否定 / 限定词覆盖。窗口回退到分句边界，跨句不豁免。"""
    if _in_negative_section(text, s) or _context_free(text, s, e):
        return True
    lo = max(0, s - WINDOW)
    hi = min(len(text), e + WINDOW)
    # 回退到最近的分句/句子起点，避免「上一句的『不可』」错误豁免这一句的宣称
    for sep in "。；;\n":
        idx = text.rfind(sep, lo, s)
        if idx != -1:
            lo = max(lo, idx + 1)
    w = text[lo:hi].lower()
    return any(m.lower() in w for m in SAFE)


def lint(text: str):
    """返回 (显性/隐性违规列表, 缺项警告)。"""
    errs = []
    groups = [(key, pats, "prohibited") for key, pats in PROHIBITED] + \
             [(key, pats, "subtle") for key, pats in SUBTLE]
    for key, pats, kind in groups:
        for pat in pats:
            for m in re.finditer(pat, text, re.IGNORECASE):
                if not _ok(text, m.start(), m.end()):
                    errs.append((key, m.group(0), kind))
    warns = [q for q in REQUIRED if q not in text]
    has_pass = bool(re.search(r"PASS", text)) and bool(
        re.search(r"回归未退化|did not regress", text, re.IGNORECASE))
    if not has_pass:
        warns.append("PASS+回归未退化 免责声明")
    return errs, warns


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", help="待检查文本文件（默认 SKILL.md）")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)
    if args.self_test:
        clean = ("精简版 RSI，基于方法论内核。不可声称：四段闭环自动落地；已实现 RSI。"
                 "PASS=回归未退化。无显著瓶颈 ≠ 变强。")
        bad = "本包四段闭环自动落地，已实现 RSI，能力变强。方法论内核 精简版。"
        subtle = ("精简版 RSI，方法论内核。PASS=回归未退化。本工具 100% 可靠，"
                  "能力显著提升，可彻底解决技能退化问题。")
        negated = ("精简版 RSI，方法论内核。PASS=回归未退化。不可宣称 100% 可靠；"
                   "能力未显著提升。")
        quoted = ('精简版 RSI，方法论内核。PASS=回归未退化。'
                  '反例："100% 可靠""显著提升"不该说。')  # 引号/反例语境
        coded = ("精简版 RSI，方法论内核。PASS=回归未退化。\n"
                 "```\n它能 100% 可靠，能力显著提升。\n```")  # 代码块反例
        e1, w1 = lint(clean)
        e2, _ = lint(bad)
        e3, _ = lint(subtle)
        e4, _ = lint(negated)
        e5, _ = lint(quoted)
        e6, _ = lint(coded)
        cases = {
            "clean_no_fp": not e1 and not w1,
            "explicit_caught": len(e2) >= 2,
            "subtle_caught": any(k == "absolute" for k, _, _ in e3) and any(k == "superlative" for k, _, _ in e3),
            "negated_exempt": not e4,
            "quoted_exempt": not e5,
            "codeblock_exempt": not e6,
        }
        passed = sum(cases.values())
        for name, good in cases.items():
            if not good:
                print(f"[FAIL] self-test case: {name}")
        print(f"[{'PASS' if passed == 6 else 'FAIL'}] claim_lint self-test {passed}/6")
        return 0 if passed == 6 else 1
    p = Path(args.path or "SKILL.md")
    try:
        text = p.read_text(encoding="utf-8")
    except Exception as exc:
        print(f"[INPUT ERROR] {exc}", file=sys.stderr)
        return 2
    errs, warns = lint(text)
    for k, hit, kind in errs:
        tag = "隐性夸大" if kind == "subtle" else "显性禁语"
        print(f"[VIOLATION] {tag}/{k}: '{hit}'")
    for w in warns:
        print(f"[WARN] 缺少 {w}")
    if not errs and not warns:
        print(f"[OK] {p.name}: claim boundary satisfied.")
    if errs:
        return 1
    if args.strict and warns:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
