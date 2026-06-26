# spectool

`spectool` 是一个用于 C 程序 ACSL 规约生成与 Frama-C/WP 验证的确定性命令行工具箱。它面向 LLM/人工辅助形式化规约生成场景，将容易出错但可机械化的工作固定为可重复执行的命令：函数抽取、项目切片、ACSL 注入、Frama-C/WP 调用、失败 goal 定位，以及 `//@ admit` 使用策略检查。

本仓库用于准备 ISSTA/SPLASH 2026 Tool Demonstrations 中与 **tool availability / repository / archived version** 相关的材料：工具可公开访问、可安装、可打版本 tag、可归档复现。

- Repository: <https://github.com/leisure118/spectool>
- Submitted version: `v0.1.0`
- License: MIT
- Archived artifact: TODO：Zenodo DOI 或等价归档 URL

## 1. 工具定位

ACSL 规约，尤其是函数契约、循环不变式和循环变体，能够为 C 程序提供强验证保证，但人工编写成本高。LLM 可以辅助提出候选规约，但候选规约必须经过确定性工具链检查，才能用于研究评估或工程实践。

`spectool` 的目标是作为“确定性后端”：

1. 外层用户或 agent 生成、修改或修复 ACSL 注解；
2. `spectool` 负责抽取上下文、注入注解、调用 Frama-C/WP、解析结果并返回结构化 JSON；
3. 外层流程根据 JSON 结果继续修复或记录实验结果。

工具本身不调用 LLM，所有命令均可脚本化运行。

## 2. Tool Availability 信息

面向投稿/归档时，可使用以下信息：

- **Latest version / repository:** <https://github.com/leisure118/spectool>
- **Version submitted:** `v0.1.0`
- **Archived artifact:** TODO：发布 release 后在 Zenodo 归档并填写 DOI。
- **Documentation:** 本 README、`spectool/SKILL.md`、`spectool --help` 与各子命令 `--help`。
- **Access:** MIT 开源协议。Python 包本身无第三方 Python 依赖；验证功能需要外部安装 Frama-C 和至少一个 prover，例如 Alt-Ergo 或 Z3。

可直接放入 Tool Availability 段落的文本：

> The latest version of spectool is available at https://github.com/leisure118/spectool. The submitted version is v0.1.0 and is archived at TODO-ARCHIVE-DOI. The repository includes installation instructions, command-line documentation, benchmark inputs, and deterministic JSON interfaces for extraction, ACSL injection, Frama-C/WP verification, failure localization, and admit-policy checking. spectool is released under the MIT License.

## 3. 安装

推荐使用虚拟环境安装，避免受系统 Python 的 PEP 668 限制影响：

```bash
git clone https://github.com/leisure118/spectool.git
cd spectool/spectool
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
spectool --help
```

检查外部验证工具是否可用：

```bash
spectool doctor --proj ..
```

如果暂时不安装 package，也可以从仓库根目录直接运行：

```bash
PYTHONPATH=spectool python3 -m CLI --help
PYTHONPATH=spectool python3 -m CLI doctor --proj .
```

## 4. 版本验证

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

版本号需要保持一致：

- `spectool/pyproject.toml` 中的 `[project].version`
- `spectool/CLI/__init__.py` 中的 `__version__`
- Git release tag，例如 `v0.1.0`

## 5. 命令行接口约定

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

示例：

```bash
spectool extract --src ../dataset/autobench/1.c
spectool verify -f input.acsl.c --timeout 8 --save-stdout wp.log
spectool locate-fail --wp wp.log --src input.acsl.c
spectool check-admit -f input.acsl.c
```

## 6. 外部依赖

Python package 本身只使用标准库。以下工具为外部依赖：

- Frama-C：`verify` 的核心后端；
- Alt-Ergo 或 Z3：Frama-C/WP 使用的 prover；
- veri-clang：用于部分 repo-scale 分析场景，非所有命令必需。

`doctor` 会报告外部工具是否存在。缺失 Frama-C/prover 时，仍可使用抽取、注入、admit 检查等不依赖验证器的命令。

## 7. 仓库结构

```text
.
├── LICENSE                  # MIT License
├── README.md                # 仓库、安装、版本和归档说明
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

## 8. 发布与归档流程

本仓库准备作为 `v0.1.0` artifact release。发布流程如下：

1. 确认安装测试通过：
   ```bash
   cd spectool
   python3 -m venv /tmp/spectool-test-venv
   . /tmp/spectool-test-venv/bin/activate
   python -m pip install -e .
   spectool --help
   spectool doctor --proj ..
   ```
2. 提交仓库：
   ```bash
   git add .
   git commit -m "Prepare spectool v0.1.0 artifact release"
   ```
3. 创建并推送 tag：
   ```bash
   git tag -a v0.1.0 -m "spectool v0.1.0 submitted artifact"
   git push origin main
   git push origin v0.1.0
   ```
4. 在 GitHub 上基于 `v0.1.0` 创建 release。
5. 将 release 归档到 Zenodo，获得 DOI。
6. 将 DOI 写回：
   - 本 README 的 `Archived artifact` 和 `TODO-ARCHIVE-DOI`；
   - `spectool/pyproject.toml` 的 `Archive` URL。
7. 重新提交 DOI 更新，可选择打 `v0.1.0-artifact` 或保留 DOI 更新在主分支说明中。

## 9. 注意事项

- 当前仓库重点维护可公开仓库、可安装版本和归档信息；论文正文和视频录制材料不在本仓库中处理。
- 如果复现实验需要完整 Frama-C/WP 验证，应在 release notes 中记录 Frama-C、prover 和操作系统版本。
- `.gitignore` 已排除 `.spec/`、`output/` 等运行生成目录，归档时应确认不误删必要 benchmark 输入。
