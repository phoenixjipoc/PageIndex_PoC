"""Render a concise experiment report from frozen results and separate grading."""
import argparse
import json
from pathlib import Path
from summarize_benchmark import summarize

ROOT = Path(__file__).resolve().parents[1]


def report(out):
    s = summarize(out)
    cfg = json.loads((out/'config.json').read_text(encoding='utf-8'))
    rows = json.loads((out/'question_results.json').read_text(encoding='utf-8'))
    sem = s['semantic_evaluation']
    cost = s.get('estimated_standard_price_usd', {})
    source = s['required_source_retrieval']
    def link(label, filename):
        return f'[{label}](<{(out/filename).as_posix()}>)'
    lines = [
        '# PageIndex 全量实验结果', '',
        f'实验 `{cfg["run_id"]}` · 2026-10-27 · 78 份 PDF / 2,546 页 / 110 道问题。', '',
        f'索引成功 **{s["index_status_counts"].get("completed",0)}/78**；获得完成回答 **{s["question_status_counts"].get("completed",0)}/110**。',
        f'本会话 AI 逐题对照参考答案的初评：完全正确 **{sem["fully_correct"]}/110（{sem["correct_rate_all_110"]:.1%}）**，部分正确 **{sem["partially_correct"]}**，错误或运行失败 **{sem["zero_score"]}**。',
        f'正确=1、部分正确=0.5、错误/失败=0 时，平均得分为 **{sem["mean_score_all_110"]:.3f}**。已完成评分 {sem["scored_questions"]}/110。', '',
        '**语义标签来自当前 Codex 会话逐题审阅，不是人工确认准确率，也不是独立评审模型实验。** 答案先冻结，再按原有 acceptance 标准计 1/0.5/0 分；没有额外评分 API 调用。本会话 AI 同时参与实验执行与评估，存在确认偏差，建议人工复核扣分项和有歧义的题目。', '',
        '本次观察到的主要问题是遗漏：INV-19 漏掉组合层面的承诺金额汇总；XD-17 漏掉南卡 RSIC；XD-18 漏掉 Arizona PSPRS。后两题均没有成功读取被遗漏文件的原文。三项扣分已额外对照原 PDF 核实。CONS-16 的众数回答正确，但列举 COAERS 时没有提到例外路径，保留一项人工复核标记。', '',
        '## 实验设置', '',
        '- PageIndex 0.2.10；固定官方源码 commit e38b40ebaeea26d2c7206b80ce7bc9bf2935cdec。',
        '- Windows 本机运行，gpt-6-luna 建索引、gpt-6-sol 检索回答，全部 medium。',
        '- 官方 Flash/full、官方提示词；不添加自定义 instructions，不开启可选 citation prompt。',
        '- 官方摘要并发上限 64、问答上限 10 轮；不覆盖 SDK 超时、重试、输出上限。',
        '- 文档按文件名升序逐份索引；问题以种子 42 打乱，4 个独立会话并发。',
        '- 每题面对整个已索引库，不给正确来源、不传 doc_id、不共享历史；参考答案仅在答案冻结后用于评分，不进入 PageIndex 的生成请求。',
        '- 初始本地索引为空。服务端自然缓存不清空，缓存命中单独记录。', '',
        '## 分组表现', '',
        '| 问题范围 | 题数 | 完成回答 | 完全正确 | 部分正确 |',
        '|---|---:|---:|---:|---:|',
    ]
    names={'single_document':'单文档','required_combination':'多文档组合','negative':'不可回答'}
    for name, v in s['by_scope'].items():
        lines.append(f'| {names.get(name,name)} | {v["total"]} | {v["completed"]} | {v["fully_correct"]} | {v["partially_correct"]} |')
    lines += ['', '| 原始题型 | 题数 | 完成回答 | 完全正确 | 部分正确 |', '|---|---:|---:|---:|---:|']
    for name,v in s['by_type'].items():
        lines.append(f'| {name} | {v["total"]} | {v["completed"]} | {v["fully_correct"]} | {v["partially_correct"]} |')
    lines += ['', f'14 组配对题中，两题均获完全正确评分的有 **{s["paired_both_correct"]["both_correct"]} 组**。这是配对全对率，不等同于完整的语义一致性评审。', '',
        '## 检索到原文的情况', '',
        f'在 {source["denominator"]} 道可回答题中，至少成功读到一个必需来源：**{source["questions_with_any_required_source"]}**；读齐全部必需来源：**{source["questions_with_all_required_sources"]}**。',
        f'逐题必需来源召回率的宏平均为 **{source["macro_recall_all_answerable"]:.1%}**。',
        '统计依据是实际成功的 get_page_content 返回；仅浏览到文档名或读取章节摘要不算读到原文。它衡量文档覆盖，不能证明具体答案句子的证据充分性。', '',
        '## 耗时与用量', '',
        '| 阶段 | 墙钟秒数 | 模型响应数 | 输入 tokens | 输出 tokens | 估算美元 |',
        '|---|---:|---:|---:|---:|---:|',
    ]
    for key,label,usage,calls,price in [
        ('index','建索引',s['index_observed_usage'],s['index_model_calls'],cost.get('index')),
        ('questions','检索与回答',s['chat_observed_usage'],s['chat_model_calls'],cost.get('chat')),
        ('grading','额外评分 API（未执行）',s['semantic_grading_usage'],s['semantic_grading_usage']['model_calls'],cost.get('semantic_grading'))]:
        duration=s['stage_wall_clock_seconds'].get(key)
        lines.append(f'| {label} | {duration if duration is not None else "—"} | {calls} | {usage["input_tokens"]:,} | {usage["output_tokens"]:,} | {price if price is not None else "未估算"} |')
    lines += ['', f'逐题延迟中位数 **{s["question_latency_seconds"]["median"]} 秒**，P95 **{s["question_latency_seconds"]["p95"]} 秒**，包括失败题的实际耗时。问答有 4 路并发，不能用每题延迟之和代替墙钟时间。',
        f'从首次索引启动至全部答案结束，包含恢复间隔的墙钟时间为 **{s.get("generation_wall_seconds_including_resume_gap")} 秒**；运行时首次依赖导入不在该计时内。',
        f'索引和问答估算合计 **${cost.get("generation_total")}**。额外评分 API 未执行，费用为 $0；当前 Codex 会话的审阅用量和费用不在该 API 成本统计内。',
        '估算使用 2026-10-27 的公开 Standard token 单价及逐次缓存读写、长上下文规则：'
        '[GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna)、[GPT-6 Sol](https://developers.openai.com/api/docs/models/gpt-6-sol)。未计账户折扣、其他服务档位、地区附加费、税费及无 usage 返回的失败请求，不是实际账单。', '',
        '## 运行异常和边界', '',
        '- 初始进程在完成第 5 份索引后遇到 Windows 进度文件替换权限错误。已为记录文件增加短暂重试，从第 6 份续跑；前 5 份没有重新生成，原始脚本与修订快照均保留。模型、提示词、数据和评分规则没有因该修复改变。',
        '- 进度汇总主线程存在重复获取非重入锁的问题。独立答题任务继续执行，进度通过逐题检查点另行监控；全部答案检查点完成后，用重入锁修复版恢复汇总，不重新调用模型。修复与恢复记录保存在 runner_revisions.json。',
        f'- 文档处理失败 {len(s["index_failures"])} 份；问答运行失败 {len(s["question_failures"])} 题。下列失败保留在总分母中。',
        f'- 所有已观测模型与请求配置核对结果：**{s["generation_settings_match"]}**。',
        f'- 索引结构共 {s["index_structure_checks"]["nodes"]} 个节点，缺摘要 {s["index_structure_checks"]["nodes_without_summary"]} 个，页码范围异常 {s["index_structure_checks"]["invalid_page_ranges"]} 个。这是结构完整性检查，不代表摘要语义均已人工验证。',
        '- 82 个核心输入文件、110 份冻结答案和 96 个已安装官方 Python 源文件均通过哈希核验；恢复前后 486 份请求、响应及工具日志未改变，确认汇总恢复没有重复调用模型。',
        '- 没有同步重跑 Sirchmunk 或向量 RAG，本报告不能用于断言跨系统优劣。',
        '- 这是一次固定数据集运行，没有重复采样；延迟与缓存表现取决于本次 4 路并发及服务端缓存状态，不代表稳定生产 SLA。',
        '- 本次评分按参考答案的事实与完整性要求进行，未另做全量逐条引用页码及额外陈述的独立核验。',
        '- 官方默认没有强制结构化引用，答案可能使用普通文字引用；不能用空 citation 标签列表代表未引用。', '',
    ]
    for failure in s['index_failures']:
        lines.append(f'- 索引失败 `{failure["file"]}`：{failure.get("error_type")} — {failure.get("error")}')
    if s['question_failures']:
        lines += ['', '问答失败题号：' + '、'.join(f'`{f["id"]}`' for f in s['question_failures']) + '。具体错误见逐题结果。']
    lines += ['', '## 优先复核项', '', '| 题号 | 初评 | 简要原因 |', '|---|---|---|']
    review=[r for r in rows if r.get('score') in (0,0.5) or r.get('needs_review')]
    for r in review[:20]:
        reason=(r.get('grading_reason') or r.get('error') or '').replace('|','/').replace('\n',' ')[:260]
        label=str(r.get('verdict')) + ('；边界待人工复核' if r.get('needs_review') else '')
        lines.append(f'| {r["id"]} | {label} | {reason} |')
    lines += ['', '这里只列前 20 个优先复核项，全部逐题结果和理由均在明细文件中。', '', '## 文件入口', '',
        '- '+link('逐题答案、来源覆盖和评分 CSV','question_results.csv'),
        '- '+link('逐文档索引结果 CSV','index_results.csv'),
        '- '+link('机器可读汇总','summary.json'),
        '- '+link('实验规程','EXPERIMENT_PROTOCOL.md'),
        '- '+link('冻结配置','config.json'),
        '- '+link('官方生成提示词','official_chat_instructions.txt'),
        '- '+link('实际评估方式及变更原因','evaluation/review_method.json'),
        '- '+link('最终完整性核验','final_verification.json'),
        '- '+link('原文重点复核记录','evaluation/source_spot_checks.json'),
        '- '+link('脚本修订记录','runner_revisions.json'), '',
        '每题完整证据和工具轨迹位于 `questions/<题号>/`；评分输入及判定位于 `evaluation/<题号>/`。原评分 API 计划和提示词保留作审计记录，未执行；它们没有进入 PageIndex 的索引或问答请求。', '',
        '自动审批拒绝了额外 API 评分，理由是将本地答案和评分标准发送至 api.openai.com 的授权不足。已改为当前会话中的 AI 逐题审阅，没有向该评分 API 发送这批材料。', '']
    (out/'REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
    print('REPORT',str(out/'REPORT.md'))


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--run-dir',required=True)
    args=parser.parse_args(); report((ROOT/args.run_dir).resolve())
