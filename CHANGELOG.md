# Changelog

> 版本权威：当前版本以 `SKILL.md` frontmatter `version` 与本文件首条为准。下方历史条目仅存档，描述的是当时状态，不代表当前行为。

## v0.2.4 (2026-11-18)

按第五轮 SkillHub 测评（4.7，「主要还是文档部分要改进」）补齐两处结构性缺口，同 slug 升级：

- **数字校验扩到全包**（对应「少数步骤数字没同步」根因）：`scripts/check_doc_numbers.py` 由只守护 `SKILL.md` 改为默认校验全部 8 个活动 md 文档。用「声明式数字」精确模式（脚本名/简写 + self-test 语境）避开三类合法数字——退出码 `0/1/2/3`、免责措辞 `N/N`、用户自建任务集 `3/3`——避免扩展后误报；CHANGELOG 历史段整体排除。新增 SKILL.md 文档地图与 `references/` 目录双向一致性校验，防止新增文档变孤岛。默认行为即全包（`--all` 为显式等价项），保留 `--doc` 单文档模式；自检扩到 9/9。端到端负向测试 4/4：篡改数字、塞回回避式措辞、造幻影文档引用均被抓。
- **集中避坑清单**：新增 `references/pitfalls.md`，把散落在 changelog 与各文档里的教训收敛成五类速查表（数字/写回/宣称/异常/触发），每条「错误做法 → 后果 → 正确替代」。清单作为反面教材集故意保留禁用措辞作对照，不参与数字/回避式校验，但已登记文档地图。
- **修回避式残留**：`getting-started.md` 第 2 步的「以 `--print` 输出为准」改为确切 `3/3` + 重跑脚本核对的全包指引。
- **修一处样例-实跑不符**：复验时发现 `walkthrough.md` 案例二把 linter 实际输出 `'生产级可用'` 误写成 `'生产级'`（「示例与运行不符」类），已按实跑逐字修正，并把该教训补进避坑清单。
- 宣称边界、slug、所有真实数字（8/8、6/6、10/10、3/3、5/5）、IMMUTABLE 判官链均不变。版本统一为 0.2.4。

## v0.2.3 (2026-11-18)

按第四轮 SkillHub 测评（4.6，「文档说明不进反退、数字与实际不一致、异常输入裸崩」）彻底修复，同 slug 升级：

- **数字一致性（核心）**：新增 `scripts/check_doc_numbers.py`——实跑各脚本 `--self-test` 抓真实用例数，校验 `SKILL.md` 审计表数字是否与之一致，不一致 exit 1 并列出差异；`--print` 输出当前真实值供改文档。把上一版散落各处的「以实跑为准/N/N 占位」（测评认为无法核对）全部改回**确切数字**并机器绑定：gate_min 8/8、claim_lint 6/6、run_loop_min 10/10、AGGREGATE 3/3、demo 5/5。README / runnable-guide / getting-started / walkthrough / FAQ 同步。新增 FAQ Q10 说明数字漂移怎么查。
- **异常输入加固**（对应运行稳定性 4.0 / 异常处理 4.5）：`gate_min.check` / `run_loop_min.gate` 对 tasks 非 dict、字段非 list、结果项非 dict、哈希锁类型错一律 fail-closed 返回友好错误，不再裸 `AttributeError/TypeError` traceback；`run_loop_min` 补报告写入失败的 `[OUTPUT ERROR]` 捕获；退出码补齐 INPUT_ERROR=2 / INTEGRITY=3；两脚本自检各补结构异常负例（gate 4→8、loop 8→10）。
- **平台触发**（对应触发 4.8）：SKILL.md 补「不同平台怎么触发」表（WorkBuddy / SkillHub / 其他宿主）与「triggers 只是建议信号、白话指令最可靠」说明；FAQ 补 Q9。
- 宣称边界、slug、IMMUTABLE 判官链均不变。版本统一为 0.2.3。

## v0.2.2 (2026-11-18)

按第三轮 SkillHub 测评反馈（「内容偏多、旧说明残留、信息冲突、缺触发优先级」）精简统一，同 slug 升级：

- **精简正文**：SKILL.md 由 150 行压到 106 行（-29%）。移除内嵌的三版 CHANGELOG（与 CHANGELOG.md 重复）、合并重复的宣称边界表与 FAQ、术语解释并入受众段；各章节只留浅入口，细节指向 references。
- **统一旧状态**：`getting-started.md` 的 `2/2` → `以实跑输出为准`；`runnable-guide.md` 脚本表补 `run_loop_min.py`（原写「上面两个」已过时）；CHANGELOG 历史条目统一改「历史存档，现行见首条/frontmatter」；SKILL.md 与 README 的易漂移数字改「以实跑为准」。
- **触发优先级**：SKILL.md「直接调用」段新增优先级规则（宣称边界 > 回归门禁 > 四段链 > 泛化咨询），回应「相近说法缺优先顺序」。
- **版本权威标注**：SKILL.md 顶部与 README、CHANGELOG 均声明「当前版本以 frontmatter + CHANGELOG 首条为准」，历史条目仅存档，消除「多个版本信息迷路」。
- 宣称边界、slug、IMMUTABLE 判官链均不变。版本统一为 0.2.2。

## v0.2.1 (2026-11-18)

按第二轮 SkillHub 测评反馈（「表述不足」「复杂表述判断较浅」）强化，同 slug 升级：

- **可信范围表述**：SKILL.md 新增 30 秒 TL;DR 表（是不是完整 RSI / 全绿是否变强 / 会不会自动改技能 / 要不要联网 / 一句话定位），让普通用户一眼看懂可信边界。
- **直接调用入口**：新增「直接调用」表，「跑一遍四段闭环」「查退化没有」「这句话能不能说」「自检这个包」等白话指令可直接触发对应脚本，无需依赖关键词自动匹配；同步 frontmatter description 与 `test-prompts.json`（新增 direct_invocation / subtle_overclaim 两类）。
- **判断力（核心）**：`claim_lint.py` 新增隐性夸大检测 `SUBTLE` 三组（absolute/superlative/maturity，覆盖 100%、百分百、完全可靠、显著提升、彻底解决、生产级等）；新增章节感知豁免（「不可声称/反例/边界」章节内的禁语不误报）、否定短语豁免（不声称/不宣称/不保证）与代码块/引号语境豁免（反例演示与引用不算宣称）；自检由 1 项扩为 6 项（clean 无 FP / 显性抓 / 隐性抓 / 否定豁免 / 引号豁免 / 代码块豁免）。实测修复了「也不声称能力变强」被误报的真实弱点。
- **数字可核对**：审计报告样例由代码块改为带命令的表格，每条数字附可复跑命令，并修正上一版遗留的 `2/2` → 真实 `3/3`、`claim_lint 6/6`。
- **实战案例**：`walkthrough.md` 新增案例二「宣称越界文本改造」（100%/显著/彻底/生产级 → lint 抓 → 人工改写 → 复核通过）。
- 宣称边界、slug、IMMUTABLE 判官链均不变。版本统一为 0.2.1。

## v0.2.0 (2026-11-18)

按 SkillHub 测评反馈提分，同 slug 升级（slug 仍为 `unclekk-rsi-guarded-loop-kit`）：

- **功能完善性**：新增 `scripts/run_loop_min.py` —— 零依赖「四段最小链」一键入口（①诊断→②选流→③蒸馏骨架→④门禁→报告）。③ 只产候选骨架不写回、不自动批准，保持宣称边界。
- **内容完整度**：新增 `references/walkthrough.md` 完整实战案例（退化→诊断→门禁拒绝→人工环节→通过→fail-closed→宣称 lint），所有输出样例实跑核对。
- **输出准确性**：修正 `SKILL.md` 审计报告样例中与实际不符的数字（原 6/6、18/18 → 真实 4/4、2/2）；聚合自检因新增脚本由 2/2 变为 3/3。
- **开箱即用 / 触发方式**：SKILL.md 与 README 的 60 秒示例加入一键链入口，文档地图加入实战案例。
- **显示名**：调整为 `UncleKK Guarded RSI Loop Kit / 受护栏 RSI 闭环工具包`（英文在前）。
- 宣称边界、IMMUTABLE 判官链、严格 RSI 不可声称口径均不变。

包内所有文件版本当时统一为 0.2.0（历史存档；现行版本见本文件首条与 SKILL.md frontmatter）。

## v0.1.0 (2026-11-18)

首发版本。内容：

- 四段闭环（诊断→选流→蒸馏→门禁）可复用 SOP + 项目侧原型现状披露
- 零依赖回归门禁 `scripts/gate_min.py`（退出码 0/1/2/3、哈希锁完整性、fail-closed）
- 宣称边界 linter `scripts/claim_lint.py`（`--strict` 硬闸）与聚合自检 `scripts/test_all.py`
- 最小运行实例（`scripts/fixtures/`，示意数据非实测）
- 新手分步说明（`references/getting-started.md`）与完整 FAQ、可运行指南、宣称边界对照
- 防误读声明：`rsi` = bounded 项目侧原型，`guarded` = 受护栏且方向裁决系统外；严格 RSI 完成态不可声称

包内所有文件版本当时统一为 0.1.0（历史存档；现行版本见本文件首条与 SKILL.md frontmatter）。参考 RSIFlow（arXiv:2610.21791v2）为独立方法论整理，非官方实现。
