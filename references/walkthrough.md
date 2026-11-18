# 实战案例：从「回归退化」走到「未退化」| Walkthrough

目标：用一个**可复现**的小场景，把四段最小链完整走一遍，看清每段真实做了什么、人工要在哪里把关、哪些话不能说。全程零依赖、不联网、不调用模型、不改任何生产技能。

> 术语：`未退化` = 冻结基线回归判定通过，不等于能力变强。`fail-closed` = 判据或输入异常时拒绝放行，不误判为通过。

## 场景 | Scenario

你维护一个技能，冻结了 3 个基线任务（`t1/t2/t3`）。同事提交一版候选结果，其中 `t2` 失败了。你要判断：能不能放行？该走哪条工作流？候选说明该怎么写才不算洗绿？

所有命令都从本包根目录执行，`python3` 换成你的解释器。

---

## 步骤 0：确认工具能跑（聚合自检）

```bash
python3 scripts/test_all.py
```

真实输出应为：

```
[PASS] gate_min.py: [PASS] gate_min self-test 8/8
[PASS] claim_lint.py: [PASS] claim_lint self-test 6/6
[PASS] run_loop_min.py: [PASS] run_loop_min self-test 10/10
AGGREGATE: 3/3 scripts passed

> 上述用例数可用 `python3 scripts/check_doc_numbers.py --print` 复核；`check_doc_numbers.py` 会校验全包 8 个活动文档的数字是否与实跑一致。
```

这一步只验证脚本本身，与你的技能无关。

---

## 步骤 1：用随包 demo 看一遍四段链

```bash
python3 scripts/run_loop_min.py
```

真实输出：

```
[① 诊断] 无显著瓶颈 / 需人工判定
[② 选流] freeze_then_gate（禁止项已声明）
[③ 蒸馏] 候选骨架已生成（is_final_skill=false，不自动写回）
[④ 门禁] PASS — 回归未退化（非能力提升）
[边界] PASS=回归未退化；非能力变强；非严格 RSI；非四段自动落地（严格）
```

注意四段各自的真实含义：

| 段 | 这一步做了什么 | 没做什么 |
|---|---|---|
| ① 诊断 | 按确定性规则把信号归桶 | 不下「能力变强/变弱」价值判断 |
| ② 选流 | 选一条确定性工作流，列出禁止项 | 不替你做最终选流 |
| ③ 蒸馏 | 产出候选 SOP 骨架和待填槽位 | 不出最终技能、不写回、不批准 |
| ④ 门禁 | 逐项比对冻结任务 | 不修 bug、不改判据 |

---

## 步骤 2：构造「退化」场景，看门禁怎么拒绝

把下面两份 JSON 存到任意目录（例如 `tmp/`）。

`tmp/tasks.json`：

```json
{"tasks": [{"id": "t1"}, {"id": "t2"}, {"id": "t3"}]}
```

`tmp/results-bad.json`：

```json
{"results": [
  {"id": "t1", "passed": true},
  {"id": "t2", "passed": false, "reason": "候选实现漏了边界分支"},
  {"id": "t3", "passed": true}
]}
```

跑门禁：

```bash
python3 scripts/gate_min.py --tasks tmp/tasks.json --results tmp/results-bad.json
```

真实输出：

```
[FAIL] 未通过: t2 — 候选实现漏了边界分支
[VERDICT] 回归退化 → 不通过（不自动批准、不自动修复）
```

退出码 `1`。**门禁只拒绝，不代你修复**——这是防洗绿的第一道。

---

## 步骤 3：带诊断信号走完整链，看选流如何随证据改变

失败项会被自动转成诊断信号，所以直接把坏结果喂给最小链：

```bash
python3 scripts/run_loop_min.py \
  --tasks tmp/tasks.json --results tmp/results-bad.json \
  --out tmp/report-bad.json
```

真实输出（节选）：

```
[① 诊断] 冻结任务未通过 → 行为退化
[② 选流] diagnose_then_patch（禁止项已声明）
[③ 蒸馏] 候选骨架已生成（is_final_skill=false，不自动写回）
[④ 门禁] REGRESSION — 回归退化 → 不自动批准/不自动修复
```

退出码 `1`。报告写到 `tmp/report-bad.json`，里面有四段的完整结构化结果：

- `stages.1_diagnose.counts`：`{"failed_result": 1}`——诊断只数证据，不评价能力。
- `stages.2_select.forbidden`：含 `auto_writeback` / `edit_judge` / `skip_gate`——这些是硬禁止项，选流不会绕过。
- `stages.3_distill_skeleton.slots`：待填槽位 `candidate_sop` / `human_reviewer` / `evidence_refs`——**骨架不是成品**。
- `stages.4_gate.verdict`：`REGRESSION`。

---

## 步骤 4：人工环节——这里才轮到你判断

最小链到此停住。接下来是**人的工作**，脚本刻意不代劳：

1. 确认 `t2` 失败是真退化还是冻结任务集本身写错（确认瓶颈类型）。
2. 决定最终选流：接受 `diagnose_then_patch` 建议，或改为 `abstain`（暂缓）。
3. 填 `candidate_sop` 槽位、指定 `human_reviewer`、附 `evidence_refs`。
4. 修好后产出新结果集 `tmp/results-good.json`（把 `t2` 改成 `passed:true`），再跑一次门禁。

```bash
python3 scripts/gate_min.py --tasks tmp/tasks.json --results tmp/results-good.json
# [PASS] 3/3 冻结任务通过 = 回归未退化（非能力提升）
```

---

## 步骤 5：完整性告警（fail-closed 实测）

给门禁一个哈希锁，再篡改任务集，看它拒绝放行：

```bash
python3 scripts/gate_min.py --tasks tmp/tasks.json --results tmp/results-good.json --lock tmp/lock.json
```

`tmp/lock.json` 里的 `task_sha256` 若与任务集当前字节哈希不符，输出：

```
[INTEGRITY] 任务集哈希不符 → fail-closed
```

退出码 `3`。这证明"通过"不是恒真：输入被改动时门禁会拒绝，而不是照常放行。哈希用 `sha256sum tmp/tasks.json`（Windows 用 `certutil -hashfile tmp\tasks.json SHA256`）计算。

---

## 步骤 6：对外措辞——宣称边界硬闸

写完说明后，用 linter 检查有没有越界措辞：

```bash
python3 scripts/claim_lint.py tmp/my-report.md --strict
```

允许说："基于方法论内核的精简版四段闭环骨架；本轮冻结基线回归未退化。"
不允许说："四段闭环自动落地""已实现 RSI""能力变强""实时闭环已验证"。
命中禁止措辞会输出 `[VIOLATION] ...` 并返回 `1`；缺限定词（方法论内核/精简版/PASS 免责）在 `--strict` 下也返回 `1`。

---

## 退出码速查 | Exit codes

| 码 | 门禁 `gate_min.py` | 最小链 `run_loop_min.py` |
|---|---|---|
| 0 | 回归未退化 | 四段走完且门禁 PASS |
| 1 | 回归退化 | 门禁 REGRESSION |
| 2 | 输入错误（文件坏/格式错） | 输入错误 |
| 3 | 完整性告警（哈希不符） | 完整性告警（INTEGRITY） |

---

## 这个案例证明了什么、没证明什么

- **证明**：四段最小链可确定性运行；门禁有判别力（坏结果退化、哈希篡改 fail-closed）；禁止项不会自动绕过；宣称越界会被 linter 拦下。
- **没证明**：能力变强、严格 RSI 完成态、四段闭环自动落地（严格）、全本地模型自主闭环。这些都是**不可声称**项。
- 更多边界见 `references/claim-boundary.md`；逐脚本参数见 `references/runnable-guide.md`。

---

# 案例二：改写一份「宣称越界」的技能说明 | Real rewrite

场景：同事写了一段技能介绍要对外发，你怀疑措辞夸大。这次不用门禁，只用**宣称边界 linter**做一次真实文本改造（只读检查，不改原文）。

## 步骤 1：把待查文本存成文件

`tmp/pitch.md`：

```markdown
# 我的技能

本工具基于方法论内核的精简版实现，PASS=回归未退化。
它能 100% 可靠地完成任务，能力显著提升，可彻底解决技能退化问题，
是生产级可用的成熟方案。
```

## 步骤 2：lint 抓隐性夸大

```bash
python3 scripts/claim_lint.py tmp/pitch.md --strict
```

真实输出：

```
[VIOLATION] 隐性夸大/absolute: '100%'
[VIOLATION] 隐性夸大/superlative: '显著提升'
[VIOLATION] 隐性夸大/superlative: '彻底解决'
[VIOLATION] 隐性夸大/maturity: '生产级可用'
```

退出码 `1`。注意这几句**没有**直白的「已实现 RSI」，但绝对化与品质形容词同样暗示「已达标」——这就是隐性夸大。

## 步骤 3：按边界改写

改成（保留限定词与 PASS 免责，去掉绝对化表述）：

```markdown
# 我的技能

本工具基于方法论内核的精简版项目侧原型，PASS=回归未退化（非能力提升）。
在冻结任务集上可重复通过；这是回归护栏，不保证方向正确，
也不声称能力变强。是否达标需独立指标与人工判定。
```

再 lint：

```bash
python3 scripts/claim_lint.py tmp/pitch-fixed.md --strict
# [OK] pitch-fixed.md: claim boundary satisfied.
```

退出码 `0`。

## 这个案例说明了什么

- linter 不只认关键词，还识别「100% / 显著 / 彻底 / 生产级」这类**复杂夸大表述**——回应「判断能力较浅」的批评。
- 「不可声称」章节里的禁语不会被误报（章节感知豁免），所以对照文档本身能安全存在。
- 改写稿里的「**也不声称**能力变强」不会被误报——否定性动词短语（不声称/不宣称/不保证）会豁免，这正是诚实表述的常见写法；早期版本会误报此处，已实测修正。
- 改造是**人工改写 + linter 复核**，脚本不替你写文案、不替你决定对外发布。
