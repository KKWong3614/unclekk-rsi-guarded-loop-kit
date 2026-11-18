# UncleKK Guarded RSI Loop Kit / 受护栏 RSI 闭环工具包

> 版本 **0.2.4**（当前版本以 SKILL.md frontmatter 与 CHANGELOG.md 首条为准）｜ 中文在前、英文在后 ｜ 零第三方依赖

## 这是什么

一份**方法论 + 零依赖回归门禁 + 宣称边界**的技能包。把 RSIFlow 四段思路（诊断→选流→蒸馏→门禁）落成可复用 SOP，用冻结任务集做回归护栏，强调防洗绿与诚实宣称。

**它不是**：完整 RSI 系统、严格完成态的四段闭环自动落地成品。名中 `rsi` = bounded 项目侧原型，`guarded` = 受护栏、方向裁决系统外。

## 30 秒上手

```bash
python3 scripts/test_all.py          # 聚合自检（当前 gate 8/8 + claim 6/6 + loop 10/10，AGGREGATE 3/3）
python3 scripts/run_loop_min.py      # 四段最小链一键走通（demo，5/5 示意）
python3 scripts/gate_min.py          # 单独跑回归判定（5/5 demo only）
python3 scripts/claim_lint.py SKILL.md --strict
```

零依赖、无需联网/账号。新手先看 `references/walkthrough.md` 实战案例，再按 `references/getting-started.md` 分步走。

**不想记命令？** 直接说「跑一遍四段闭环」「查冻结基线退化没有」「这句话能不能对外说」，我会跑对应脚本并回报真实结果（只读判定，不改你的文件）。前端 30 秒可信范围速查见 `SKILL.md` 的 TL;DR。

## 文件结构

| 文件 | 用途 |
|---|---|
| `SKILL.md` | 主文档：防误读声明、四段现状、SOP、宣称速查、最小示例 |
| `scripts/run_loop_min.py` | **一键四段最小链**：诊断→选流→蒸馏骨架→门禁→报告（零依赖、不写回） |
| `scripts/gate_min.py` | 零依赖回归门禁（退出码 0/1/2/3） |
| `scripts/claim_lint.py` | 宣称边界 linter（`--strict` 硬闸） |
| `scripts/test_all.py` | 聚合自检（当前 8/8 · 6/6 · 10/10 = 3/3） |
| `scripts/check_doc_numbers.py` | 全包 8 个活动文档数字一致性校验（实跑比对，不一致 exit 1） |
| `scripts/fixtures/*.json` | 示意任务集/结果（demo only，非实测） |
| `references/getting-started.md` | 新手分步说明 |
| `references/walkthrough.md` | 完整实战案例（退化→诊断→选流→门禁→通过） |
| `references/runnable-guide.md` | 输入输出、退出码、哈希重算 |
| `references/claim-boundary.md` | 可声称/不可声称权威对照 |
| `references/four-stage-status.md` | 四段 × 自动/人工明细 |
| `references/faq.md` | 高频问答 |
| `references/pitfalls.md` | 集中避坑清单（数字/写回/宣称/异常/触发五类） |
| `CHANGELOG.md` | 版本记录（许可声明见本节「参考与许可」） |

## 边界（务必随引用保留）

- `PASS / 全绿 / N/N` 只表示**冻结基线未退化**，非能力提升、非语义达标、非实时闭环已验证。
- 严格 RSI 完成态、四段闭环自动落地（严格）、能力递归自证——均**不可声称**。
- 包内 `5/5` 等数字均为**示意值，非实测**。
- 改进对象是技能文本，方向裁决保留系统外。

## 参考与许可

RSIFlow: *Adaptive Self-Improvement Workflows with an Evolving Meta-Agent*, arXiv:2610.21791v2, https://arxiv.org/abs/2610.21791 。独立方法论整理，非官方实现、未复现其实验、未使用其代码。许可：个人非商用。

---

## English summary

Version 0.2.4. A methodology guide plus a one-command four-stage skeleton chain, a zero-dependency regression gate, and a claim-boundary linter. Run `python3 scripts/test_all.py` then `python3 scripts/run_loop_min.py`; no install, network or account needed. Full walkthrough in `references/walkthrough.md`. `rsi` means a bounded project-side prototype, `guarded` means human-external direction judgement. `PASS` means frozen baselines did not regress — not capability gain. Strict RSI completion and automatic four-stage closure are NOT claimable. All bundled numbers are demo values. Reference: arXiv:2610.21791v2 (independent write-up). License: personal non-commercial.
