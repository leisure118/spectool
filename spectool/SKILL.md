# spectool — 确定性规约工具箱（Layer B）

> 支撑 Part 1（自底向上）skill 的薄 CLI。**只做确定性/工具活，不调用 LLM**。stdout 输出 JSON、stderr 输出日志、退出码语义化。

## 调用约定
- **stdout 仅 JSON**：解析它即可，不会被日志污染。
- **stderr 为人类日志**：调试用。
- **退出码**：`0` 成功 / `2` 外部工具缺失（frama-c/prover）/ `3` 输入错误。
- ACSL/JSON 类参数支持 `@path` 从文件读入。

## 子命令清单

| 子命令 | 作用 | 关键 I/O |
|---|---|---|
| `doctor` | 环境体检（frama-c/prover 是否就绪） | → `{ready, tools, missing}` |
| `extract` | 抽取单个函数 / 列出全部函数（含行号） | `--src --func` → source + 行号 |
| `inject` | 把 ACSL 注入到函数契约位 / 循环前 | `--src --out --func --acsl --loops` → 注解后 .c |
| `verify` | **核心**：跑 frama-c -wp，解析 proved/total | `-f file.acsl.c --timeout --save-stdout` → `{result,proved,total}` |
| `locate-fail` | 解析 WP 输出定位失败 goal+行号 | `--wp --src` → failures[] |
| `check-admit` | 扫描 .acsl.c 中的违规 admit（仅允许 `\valid`/`\separated`） | `-f file.acsl.c` → `{ok, violations[]}` |
