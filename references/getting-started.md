# 新手分步上手 | Getting started（写给第一次用的人）

> 目标：完全没接触过「回归门禁」的新手，10 分钟内跑通一次判定、看懂输出、知道下一步。
> 全程零第三方依赖，不需要联网、账号或 API Key。

## 第 0 步：先搞清楚三个词

| 词 | 大白话 |
|---|---|
| 冻结任务集 | 一组「题目 + 期望结果」，先固定住，之后不许随便改——它是你的基线尺子 |
| 回归门禁 | 拿尺子量「改完之后有没有变差」，只判断退化，不判断「变聪明」 |
| fail-closed | 判据自己出错时，一律当「不通过」处理，绝不 guessed 成通过 |

## 第 1 步：设路径变量（别写死机器路径）

把 `SKILL_ROOT` 指向你存放本包的目录。路径用环境变量，换机器不用改命令：

```bash
export SKILL_ROOT="$HOME/path/to/unclekk-rsi-guarded-loop-kit"   # macOS / Linux / Git Bash
```
```powershell
$env:SKILL_ROOT = "$env:USERPROFILE\path\to\unclekk-rsi-guarded-loop-kit"  # PowerShell
```

## 第 2 步：先自检，确认工具本身没坏

```bash
python3 "$SKILL_ROOT/scripts/test_all.py"
```
看到 `AGGREGATE: 3/3 scripts passed` 就对了（3 = 本包当前 3 个被测脚本：gate_min、claim_lint、run_loop_min）。数字若随版本变化，重跑 `python3 scripts/test_all.py` 看本次真实输出，再用 `python3 scripts/check_doc_numbers.py` 核对全包文档数字是否同步（不一致会 exit 1 并列出差异）。这一步只验证脚本能跑，不涉及你的技能。

## 第 3 步：跑一次示意判定，看懂输出

```bash
python3 "$SKILL_ROOT/scripts/gate_min.py"
```
包内带的是**示意数据（demo only）**，你会看到：
`[PASS] 5/5 冻结任务通过 = 回归未退化（非能力提升）`

记住这句免责：**5/5 只是格式演示，不是实测，也不代表能力变强。**

## 第 4 步：换成你自己的任务集

复制 `scripts/fixtures/tasks.json` 和 `results.json`，改成你的题目与结果：
- `tasks.json`：每项给一个唯一 `id`；
- `results.json`：每个 `id` 给 `passed: true/false`，失败可加 `reason`。

然后：
```bash
python3 "$SKILL_ROOT/scripts/gate_min.py" --tasks 你的tasks.json --results 你的results.json
```

## 第 5 步：写对外文案前，先过宣称边界

```bash
python3 "$SKILL_ROOT/scripts/claim_lint.py" SKILL.md --strict
```
它通过，才说明你的文案没有把「回归未退化」吹成「能力变强」。详细可说/不可说见 `claim-boundary.md`。

## 常见卡点

- **退出码 3（完整性告警）**：任务集和哈希锁对不上——要么恢复原任务集，要么按 `runnable-guide.md` 重算哈希。
- **退出码 1（回归退化）**：有任务没通过或缺结果——去看 `[FAIL]` 行的具体 id，改完再跑。
- **提示找不到文件**：检查 `SKILL_ROOT` 是否指对，路径别带多余引号或写死盘符。
