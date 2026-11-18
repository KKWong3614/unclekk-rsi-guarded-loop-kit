# 可运行指南 | Runnable guide

## 脚本一览（零依赖，Python 3.8+）

| 脚本 | 作用 | 自检 |
|---|---|---|
| `scripts/run_loop_min.py` | 四段最小链一键入口（诊断→选流→蒸馏骨架→门禁→报告） | `--self-test` |
| `scripts/gate_min.py` | 冻结任务集回归判定（门禁入口） | `--self-test` |
| `scripts/claim_lint.py` | 宣称边界检查，`--strict` 可当硬闸 | `--self-test` |
| `scripts/test_all.py` | 聚合：一次跑遍上面三个被测脚本 | 命令本身即自检 |
| `scripts/check_doc_numbers.py` | 元工具：实跑上面脚本、校验文档数字与真实输出是否一致 | `--self-test` / `--print` |

> 当前各脚本 `--self-test` 用例数：`gate_min 8/8`、`claim_lint 6/6`、`run_loop_min 10/10`，聚合 `AGGREGATE: 3/3`。
> 用例数随版本变化时，跑 `python3 scripts/check_doc_numbers.py` 校验文档是否被漏改；它会实跑比对并报出不一致。

## 输入格式

`tasks.json`：`{"tasks":[{"id":"唯一ID","expect":"期望描述"}]}`
`results.json`：`{"results":[{"id":"唯一ID","passed":true,"reason":"可选"}]}`

判据逻辑：冻结任务集里每个 `id` 都必须在结果集里有 `passed:true`；缺结果或未通过即判回归退化。判据异常（文件坏、任务集空）fail-closed。

## 退出码

| 码 | 含义 |
|---|---|
| 0 | 通过 = 冻结基线回归未退化（**非**能力提升） |
| 1 | 回归退化：有任务未通过 |
| 2 | 输入错误：文件缺失或 JSON 解析失败 |
| 3 | 完整性告警：任务集哈希与锁不符（需按下方重算或恢复） |

## 哈希锁重算（换成你自己的任务集时）

`gate_min.py --lock <lock.json>` 会比对任务集字节的 sha256。换成自己的任务集后，重算：

```bash
python3 -c "import hashlib,pathlib,json; p=pathlib.Path('你的tasks.json'); \
print(json.dumps({'task_sha256':hashlib.sha256(p.read_bytes()).hexdigest()},ensure_ascii=False))" > lock.json
python3 "$SKILL_ROOT/scripts/gate_min.py" --tasks 你的tasks.json --results 你的results.json --lock lock.json
```

**刻意不自动重算锁去匹配被改的任务集**——那正是门禁要拦的洗绿动作。改任务集必须人工确认后显式重算。

## 重复运行一致性

同一组输入重复跑，判定与退出码应完全一致（纯函数判定，无随机、无网络）。若不一致，属异常，停下排查。

## 完整性/边界

- 本包只做判定与报告，**不写回任何生产技能、不改判据、不自动批准**。
- 宣称边界见 `claim-boundary.md`；严格 RSI 完成态、能力变强等均不可声称。
