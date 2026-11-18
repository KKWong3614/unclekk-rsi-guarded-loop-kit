---
slug: unclekk-rsi-guarded-loop-kit
name: unclekk-rsi-guarded-loop-kit
displayName: "UncleKK Guarded RSI Loop Kit / 受护栏 RSI 闭环工具包"
version: 0.2.4
summary: "基于 RSIFlow 方法论内核的精简版 RSI 受护栏四段闭环工具包：诊断→选流→蒸馏→门禁 SOP，附零依赖回归门禁与宣称边界。/ A guarded four-stage loop kit inspired by the RSIFlow methodology: diagnose-select-distill-gate SOP, zero-dependency regression gate, and claim boundaries."
description: "当用户要做技能进化、四段闭环、回归门禁、防洗绿、宣称边界判断时加载；也可直接说「跑一遍四段闭环」「查退化没有」「这句话能不能说」触发对应脚本。把 RSIFlow 四段思路落成可复用 SOP：诊断瓶颈→选流硬闸→蒸馏重写→严格门禁，附零依赖一键四段链、回归门禁、宣称边界 linter、实战案例与新手说明。本包是方法论内核 + 项目侧原型工具包，名中 rsi 指 bounded 参考实现、guarded 指受护栏且方向裁决系统外；严格 RSI 完成态不可声称。/ Load for skill evolution, four-stage loops, regression gates, anti-whitewash, claim-boundary checks. Say 'run the four-stage loop' / 'check regression' / 'lint my claim' to invoke scripts directly. A guarded loop SOP with zero-dependency scripts; strict RSI completion is NOT claimed."
license: "个人非商用 / personal non-commercial"
tags: [rsi, guarded-loop, four-stage, skill-evolution, regression-gate, claim-boundary, anti-whitewash, bounded-rsi, beginner-friendly, unclekk]
triggers:
  - 技能进化 / skill evolution
  - 四段闭环 / four-stage loop
  - 受护栏闭环 / guarded loop
  - 回归门禁 / regression gate
  - 诊断选流蒸馏门禁 / diagnose select distill gate
  - 防洗绿 / anti-whitewash
  - 宣称边界 / claim boundary
  - 新手怎么建技能 / beginner skill guide
---

# UncleKK Guarded RSI Loop Kit / 受护栏 RSI 闭环工具包

> **版本权威**：当前版本以本文件 frontmatter `version` 与 `CHANGELOG.md` 首条为准；CHANGELOG 历史条目仅存档，不代表当前行为。

## 受众 | Audience

新手照下方「最小示例」复制命令即可跑通；老手改任务集、接 CI、按边界写对外文案。零第三方依赖、离线可跑。术语：*四段闭环* = 诊断→选流→蒸馏→门禁；*回归门禁* = 用冻结任务集判「有没有退化」；*fail-closed* = 判据出错即拒绝放行。

> **防误读声明（对外引用须一起保留）**：`rsi` = 基于 RSIFlow 方法论内核的 **bounded 项目侧原型**，非严格完成态；`guarded` = 受护栏、方向裁决系统外。`PASS / 全绿 / N/N` 只表示**冻结基线回归未退化**，不代表能力变强或实时闭环已验证。严格「已实现 RSI」「四段闭环自动落地（严格）」**不可声称**。

---

## 30 秒可信范围 | TL;DR

| 问题 | 回答 |
|---|---|
| 完整 RSI？ | **不是**，方法论内核 + 项目侧原型，方向裁决在系统外。 |
| 全绿=变强？ | **不是**，只说明基线未退化；方向靠独立指标 + 人工。 |
| 自动改技能？ | **不会**，刻意不写回、不批准（防洗绿护栏）。 |
| 要联网/账号？ | **不要**，离线零依赖。 |
| 一句话 | 一把**回归护栏尺 + 宣称边界尺**，不是自动变强的机器。 |

## 直接调用（不必等关键词自动匹配）

| 你说 | 我执行（均只读判定，不改你的文件） |
|---|---|
| 「跑一遍四段闭环」 | `python3 scripts/run_loop_min.py` |
| 「查冻结基线退化没有」 | `python3 scripts/gate_min.py --tasks … --results …` |
| 「这句话能不能对外说」 | `python3 scripts/claim_lint.py <文件> --strict` |
| 「自检这个包」 | `python3 scripts/test_all.py` |

**触发优先级**（相近需求同时出现时）：先判是不是「宣称能不能这么说」→ 用 `claim_lint`；再判是不是「某次改动退化没有」→ 用 `gate_min`；要完整走一遍才用 `run_loop_min`；泛化咨询才答 SOP 与文档。理由：边界风险最高、判定最确定的先处理，避免用泛泛的 SOP 掩盖具体判定需求。

**不同平台怎么触发**：本包的 `triggers` 是语义匹配，由宿主平台决定加载与否，各平台行为不同：

| 平台 | 触发方式 |
|---|---|
| WorkBuddy（本环境） | 命中 `triggers` 关键词自动加载；或直接在对话里说上方「直接调用」的白话指令精确触发 |
| SkillHub 页面 | 从技能详情页复制测试提示（`test-prompts.json`）试探；平台是否自动注入以其规则为准，本包无法控制 |
| 其他 Agent 宿主 | 以该宿主的 skill 加载规则为准；不保证自动触发，建议用白话指令显式指定 |

> 关键：`triggers` 只是「建议加载信号」，不是本包能强制的开关。**最可靠的方式是直接说白话指令**；若某平台没自动加载，不代表本包失效，只是该平台未采用语义触发。

## 60 秒最小示例 | Minimal example

`SKILL_ROOT` 指向本包目录（走环境变量，别写死机器路径）：

```bash
export SKILL_ROOT="$HOME/path/to/unclekk-rsi-guarded-loop-kit"
python3 "$SKILL_ROOT/scripts/test_all.py"          # 聚合自检
python3 "$SKILL_ROOT/scripts/run_loop_min.py"      # 四段最小链一键走通（demo）
python3 "$SKILL_ROOT/scripts/gate_min.py"          # 单独回归判定
python3 "$SKILL_ROOT/scripts/claim_lint.py" "$SKILL_ROOT/SKILL.md" --strict  # 宣称硬闸
```

PowerShell 把首行换为 `$env:SKILL_ROOT = "$env:USERPROFILE\path\to\unclekk-rsi-guarded-loop-kit"`，其余 `python3 "$env:SKILL_ROOT\scripts\..."` 同理。

退出码 `0=通过 / 1=回归退化 / 2=输入错误 / 3=完整性告警`。包内 `5/5` 是 **demo 示意，非实测**。分步图解见 `references/getting-started.md`。

## 审计报告样例 | Sample audit report

| 命令 | 真实输出（2026-11-18 实测，由 `check_doc_numbers.py` 自动守护一致性） |
|---|---|
| `python3 scripts/test_all.py` | `gate_min.py: gate_min self-test 8/8` · `claim_lint.py: claim_lint self-test 6/6` · `run_loop_min.py: run_loop_min self-test 10/10` · `AGGREGATE: 3/3 scripts passed` |
| `python3 scripts/gate_min.py` | `[PASS] 5/5 冻结任务通过 = 回归未退化（非能力提升）` — **demo 数据** |
| `python3 scripts/run_loop_min.py` | 四段走通，`[④ 门禁] PASS — 回归未退化` — demo |
| `python3 scripts/claim_lint.py SKILL.md --strict` | `[OK] SKILL.md: claim boundary satisfied.` |

> **任何 `N/N` 都是脚本用例数或 demo 数据，不是能力评分**；`PASS` = 回归未退化。
> **数字一致性**：跑 `python3 scripts/check_doc_numbers.py`，它会实跑上面每个脚本、核对全包 8 个活动文档的数字与真实输出是否一致（含本表）；不一致 exit 1 并列出差异。它还校验 SKILL.md 文档地图与 `references/` 目录双向一致，防新文档变孤岛。脚本升级改了用例数后，跑 `check_doc_numbers.py --print` 看新值再改文档。

## 文档地图 | 按需往下读

| 你想做什么 | 读这个 |
|---|---|
| 新手第一次上手 | `references/getting-started.md` |
| 看一个完整改造过程（推荐） | `references/walkthrough.md` |
| 输入输出 / 退出码 / 哈希重算 / 全部脚本 | `references/runnable-guide.md` |
| 某句话能不能说（权威对照） | `references/claim-boundary.md` |
| 四段 × 自动/人工明细 | `references/four-stage-status.md` |
| 高频问题 | `references/faq.md` |
| 集中避坑清单（错误做法→后果→正确替代） | `references/pitfalls.md` |

## 边界与兜底

- **不自动**：不写回生产技能、不改判据、不自动批准；写回需人工授权与回滚。
- **fail-closed**：判据异常（哈希不符 / 任务集空 / JSON 坏）一律拒绝放行，不误判为通过。
- **宣称**：可说「参考方法论内核的精简版项目侧原型 + 回归未退化」；不可说「严格 RSI 完成态 / 四段闭环自动落地（严格）/ 能力变强 / 实时闭环已验证」。完整对照见 `references/claim-boundary.md`。

## 变更记录 | Changelog

**v0.2.4**（2026-11-18）：针对第五轮测评「主要还是文档部分要改进」收口两项结构缺口。①`check_doc_numbers.py` 从只守护 SKILL.md 扩到**全包 8 个活动 md 文档**（README / getting-started / runnable-guide / walkthrough / faq / claim-boundary / four-stage-status + SKILL）；用精确声明模式避开退出码 0/1/2/3、免责 `N/N`、案例自建 3/3 三类合法数字，CHANGELOG 历史段排除；新增文档地图双向一致性校验防孤岛文档；自检扩至 9/9。②新增 `references/pitfalls.md` 集中避坑清单（数字/写回/宣称/异常/触发五类，错误做法→后果→正确替代）。③修 getting-started「以 --print 输出为准」回避式表述为确切数字 + 重跑指引。宣称边界、slug、数字与 IMMUTABLE 判官链均不变。

**v0.2.3**（2026-11-18）：针对第四轮测评「文档数字与实际不一致、异常输入裸崩、平台触发未展开」彻底修复。①新增 `scripts/check_doc_numbers.py`：实跑各脚本、机器校验文档 N/N 与真实输出一致（不一致 exit 1），并把散落各处的「以实跑为准」全部改回确切数字（gate 8/8、claim 6/6、loop 10/10、聚合 3/3、demo 5/5），README/runnable-guide/walkthrough/faq 同步。②加固异常输入：`gate_min`/`run_loop_min` 对结构错误、文件写入失败改为友好提示 + 明确退出码（2=输入/输出错误），不再裸 traceback；自检补结构异常负例。③补「不同平台怎么触发」表与 FAQ Q9/Q10。宣称边界、slug 不变。

**v0.2.2**（2026-11-18）：精简正文（去内嵌历史版本、合并重复表）、修过时数字与失效引用、补触发优先级。完整历史见 `CHANGELOG.md`；本文件不内嵌旧版本，避免新旧信息冲突。

---

## English summary

A guarded four-stage loop kit (diagnose → select → distill → gate) inspired by the RSIFlow methodology: zero-dependency scripts for regression gating, a claim-boundary linter, a one-command four-stage skeleton, and a full walkthrough. **Beginners** copy one command; advanced users swap in their own frozen task sets. `rsi` = bounded project-side prototype, NOT strict RSI; `guarded` = human-external direction judgement. `PASS` means frozen baselines did not regress — not capability gain. Strict "RSI achieved" / "four-stage loop auto-implemented (strict)" are NOT claimable. Current version: see frontmatter and CHANGELOG.md. Reference: RSIFlow, arXiv:2610.21791v2 (independent write-up, not official, experiments not reproduced). License: personal non-commercial.
