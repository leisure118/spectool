# spectool

`spectool` 是一个用于 C 程序 ACSL 规约生成与 Frama-C/WP 验证的确定性命令行工具箱。它面向 LLM/人工辅助形式化规约生成场景，将容易出错但可机械化的工作固定为可重复执行的命令：函数抽取、项目切片、ACSL 注入、Frama-C/WP 调用、失败 goal 定位，以及 `//@ admit` 使用策略检查。

工具本身不调用 LLM，所有命令均可脚本化运行。它的设计目标是作为“确定性后端”：外层用户或 agent 生成、修改或修复 ACSL 注解，`spectool` 负责抽取上下文、注入注解、调用 Frama-C/WP、解析结果并返回结构化 JSON。

## 1. 安装

推荐使用虚拟环境安装，避免受系统 Python 的 PEP 668 限制影响：

```bash
git clone https://github.com/leisure118/spectool.git
cd spectool/spectool
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
spectool --help
```

如果暂时不安装 package，也可以从仓库根目录直接运行：

```bash
PYTHONPATH=spectool python3 -m CLI --help
PYTHONPATH=spectool python3 -m CLI doctor --proj .
```

## 2. 快速演示

检查外部工具和项目目录：

```bash
spectool doctor --proj ..
```

列出或抽取 C 文件中的函数：

```bash
spectool extract --src ../dataset/autobench/1.c
```

对带 ACSL 注解的 C 文件运行 Frama-C/WP：

```bash
spectool verify -f input.acsl.c --timeout 8 --save-stdout wp.log
```

定位 WP 输出中的失败 goal：

```bash
spectool locate-fail --wp wp.log --src input.acsl.c
```

检查 `.acsl.c` 文件中是否存在违规 `//@ admit`：

```bash
spectool check-admit -f input.acsl.c
```

## 3. 版本验证

确认 Python 包版本：

```bash
cd spectool
python - <<'PY'
import CLI
print(CLI.__version__)
PY
```

当前应输出：

```text
0.1.0
```

版本号位于：

- `spectool/pyproject.toml` 中的 `[project].version`
- `spectool/CLI/__init__.py` 中的 `__version__`

## 4. 命令行接口约定

所有子命令遵循统一接口：

- stdout：只输出 JSON，便于脚本、agent、CI 解析；
- stderr：输出人类可读日志；
- exit code：
  - `0`：成功；
  - `2`：外部工具缺失或不可用；
  - `3`：输入错误；
  - `1`：未预期内部错误。

主要命令如下：

| 命令 | 作用 |
|---|---|
| `doctor` | 检查 Frama-C、veri-clang、prover 和项目目录可用性。 |
| `extract` | 列出 C 文件中的函数或抽取单个函数。 |
| `slice` | 为目标函数生成最小切片。 |
| `inject` | 将 ACSL 函数契约和循环注解注入 C 文件。 |
| `verify` | 调用 Frama-C/WP 并返回 `{result, proved, total}`。 |
| `locate-fail` | 解析 WP 输出并定位失败 goal。 |
| `check-admit` | 检查 `.acsl.c` 中是否存在违规 `//@ admit`。 |
| `init-contracts` / `fill-contracts` / `save-contract` | 维护自底向上的函数契约状态。 |

查看完整帮助：

```bash
spectool --help
spectool <command> --help
```

## 5. 外部依赖

Python package 本身只使用标准库。以下工具为外部依赖：

- Frama-C：`verify` 的核心后端；
- Alt-Ergo 或 Z3：Frama-C/WP 使用的 prover；
- veri-clang：用于部分 repo-scale 分析场景，非所有命令必需。

`doctor` 会报告外部工具是否存在。缺失 Frama-C/prover 时，仍可使用抽取、注入、admit 检查等不依赖验证器的命令。

## 6. 仓库结构

```text
.
├── LICENSE                  # MIT License
├── README.md                # 安装、演示和使用说明
├── .claude/skills/          # 规约生成/编排 skill 描述
├── dataset/                 # AutoBench、live24、live25 C benchmark
├── scripts/                 # 辅助脚本
└── spectool/
    ├── CLI/                 # Python CLI 包
    │   ├── commands/        # 一命令一文件
    │   └── vendored/        # 抽取、注入、Frama-C 输出解析等核心实现
    ├── SKILL.md             # 工具能力清单
    └── pyproject.toml       # Python 包元数据与 console script
```
