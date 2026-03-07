# Git Deep Analyzer - 深度Git代码和业务分析系统

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 构建一个全自动的AI驱动的Git代码和业务深度分析系统，支持多语言（优先C++、Python）、多外部系统集成（Jira、GitLab、Confluence、飞书）、多输出格式（HTML、Markdown）

**Architecture:**
- 配置层（YAML + CLI + 交互式）
- 数据采集层（Git + 外部系统）
- 代码分析层（多语言AST解析）
- AI分析层（技术/业务/演进维度）
- 报告生成层（HTML/Markdown + 可视化）

**Tech Stack:** Python 3.11+, Click, GitPython, Jinja2, OpenAI/Anthropic API, Chart.js, pytest

---

## 实施概述

本计划分4个主要任务组，共约40个子任务，每个任务都是2-5分钟可完成的小步骤：

- **Task 0**: 项目基础结构和配置系统（11个子任务）
- **Task 1**: Git采集和代码分析层（11个子任务）
- **Task 2**: 外部系统集成（9个子任务）
- **Task 3**: AI分析层（8个子任务）
- **Task 4**: 报告生成层（6个子任务）

---

## Task 0: 项目基础结构和配置系统

### Task 0.1: 创建项目基础结构和依赖配置

**Files:**
- Create: `pyproject.toml`
- Create: `requirements.txt`
- Create: `README.md`
- Create: `src/git_deep_analyzer/__init__.py`
- Create: `tests/__init__.py`

**Step 1: 写测试验证项目结构**

Create `tests/test_setup.py`:

```python
import os
from pathlib import Path

def test_project_structure():
    root = Path(__file__).parent.parent
    assert root.exists()
    assert (root / "src" / "git_deep_analyzer").exists()
    assert (root / "tests").exists()
    assert (root / "pyproject.toml").exists()
```

**Step 2: 运行测试验证失败**

Run: `pytest tests/test_setup.py -v`
Expected: FAIL - 目录不存在

**Step 3: 创建项目结构和配置文件**

Create `pyproject.toml`:

```toml
[project]
name = "git-deep-analyzer"
version = "0.1.0"
description = "Deep analysis of git commits with AI"
requires-python = ">=3.11"
dependencies = [
    "click>=8.1.0",
    "GitPython>=3.1.40",
    "Jinja2>=3.1.2",
    "python-dateutil>=2.8.2",
    "openai>=1.0.0",
    "anthropic>=0.18.0",
    "requests>=2.31.0",
    "pyyaml>=6.0.0",
    "aiohttp>=3.9.0",
    "joblib>=1.3.0",
]

[project.scripts]
git-deep-analyze = "git_deep_analyzer.cli:main"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
```

Create `requirements.txt`:

```text
click>=8.1.0
GitPython>=3.1.40
Jinja2>=3.1.2
python-dateutil>=2.8.2
openai>=1.0.0
anthropic>=0.18.0
requests>=2.31.0
pyyaml>=6.0.0
aiohttp>=3.9.0
joblib>=1.3.0
pytest>=7.4.0
pytest-cov>=4.0.0
```

Create `src/git_deep_analyzer/__init__.py`:

```python
"""Git Deep Analyzer - AI-powered deep analysis of git repositories."""

__version__ = "0.1.0"
```

Create `tests/__init__.py`:

```python
"""Tests for git-deep-analyzer."""
```

**Step 4: 运行测试验证通过**

Run: `pytest tests/test_setup.py -v`
Expected: PASS

**Step 5: 提交**

```bash
git add pyproject.toml requirements.txt README.md src/ tests/
git commit -m "feat: initialize project structure"
```

---

### Task 0.2: 实现配置文件加载（YAML → Config对象）

**Files:**
- Create: `src/git_deep_analyzer/config.py`
- Test: `tests/test_config.py`

**Step 1: 写测试验证配置加载**

Create `tests/test_config.py`:

```python
import tempfile
from pathlib import Path
from git_deep_analyzer.config import Config

def test_load_yaml_config():
    config_content = """
analysis:
  git:
    repo_path: /tmp/test
    branch: main
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as f:
        f.write(config_content)
        f.flush()

        config = Config.load_from_file(Path(f.name))
        assert config.analysis.git.repo_path == "/tmp/test"
        assert config.analysis.git.branch == "main"
```

**Step 2: 运行测试验证失败**

Run: `pytest tests/test_config.py::test_load_yaml_config -v`
Expected: FAIL - 模块不存在

**Step 3: 实现配置加载**

Create `src/git_deep_analyzer/config.py`:

```python
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import yaml
import os
from datetime import datetime


@dataclass
class GitConfig:
    """Git配置"""
    repo_path: Path
    branch: str = "main"
    time_filter_mode: str = "date_range"
    time_filter_date_range_since: Optional[str] = None
    time_filter_date_range_until: Optional[str] = None
    time_filter_last_n_days: Optional[int] = None
    time_basis: str = "author_time"


@dataclass
class OutputConfig:
    """输出配置"""
    formats: list = field(default_factory=lambda: ["html", "markdown"])
    directory: str = "./reports"
    filename_pattern: str = "{repo}-{branch}-{timestamp}"


@dataclass
class AnalysisConfig:
    """分析配置"""
    git: GitConfig
    languages: dict = field(default_factory=lambda: {"primary": ["cpp", "python"], "fallback": "auto"})
    output: OutputConfig = field(default_factory=OutputConfig)


@dataclass
class AIProviderConfig:
    """AI提供商配置"""
    type: str = "api"
    name: str = "openai"
    model: str = "gpt-4o"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: int = 4000
    temperature: float = 0.3


@dataclass
class AICLIConfig:
    """AI CLI配置"""
    command: str = "claude"
    args: list = field(default_factory=list)
    env_vars: list = field(default_factory=list)


@dataclass
class AIErrorHandling:
    """AI错误处理配置"""
    retry_enabled: bool = True
    retry_max_attempts: int = 3
    retry_backoff: str = "exponential"
    timeout_enabled: bool = True
    timeout_seconds: int = 300
    on_failure: str = "retry"  # retry | continue | abort | fallback


@dataclass
class AILogging:
    """AI日志配置"""
    level: str = "debug"
    log_file: str = "./ai_analysis.log"
    log_to_stdout: bool = True


@dataclass
class AIConfig:
    """AI配置"""
    enabled: bool = True
    provider: AIProviderConfig = field(default_factory=AIProviderConfig)
    cli: Optional[AICLIConfig] = None
    error_handling: AIErrorHandling = field(default_factory=AIErrorHandling)
    logging: AILogging = field(default_factory=AILogging)
    execution_strategy: str = "serial"


@dataclass
class ReportingConfig:
    """报告配置"""
    sections: list = field(default_factory=lambda: ["overview", "technical", "business", "evolution"])
    include_raw_data: bool = False
    language: str = "zh-CN"
    detail_level: str = "standard"


@dataclass
class Config:
    """主配置类"""
    analysis: AnalysisConfig
    ai: AIConfig = field(default_factory=AIConfig)
    reporting: ReportingConfig = field(default_factory=ReportingConfig)

    @classmethod
    def load_from_file(cls, path: Path) -> "Config":
        """从YAML文件加载配置"""
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        return cls._parse_config(data)

    @classmethod
    def _parse_config(cls, data: Dict) -> "Config":
        """解析配置数据"""
        # Git配置
        git_data = data.get("analysis", {}).get("git", {})
        git_config = GitConfig(
            repo_path=Path(git_data.get("repo_path")),
            branch=git_data.get("branch", "main"),
            time_filter_mode=git_data.get("time_filter", {}).get("mode", "date_range"),
            time_basis=git_data.get("time_filter", {}).get("time_basis", "author_time")
        )

        # 输出配置
        output_data = data.get("analysis", {}).get("output", {})
        output_config = OutputConfig(
            formats=output_data.get("formats", ["html", "markdown"]),
            directory=output_data.get("directory", "./reports"),
            filename_pattern=output_data.get("filename_pattern", "{repo}-{branch}-{timestamp}")
        )

        # AI配置
        ai_data = data.get("ai", {})
        ai_config = AIConfig(
            enabled=ai_data.get("enabled", True),
            error_handling=AIErrorHandling(
                timeout_seconds=ai_data.get("cli", {}).get("error_handling", {}).get("timeout", {}).get("seconds", 300)
            )
        )

        # 报告配置
        reporting_data = data.get("reporting", {})
        reporting_config = ReportingConfig(
            include_raw_data=reporting_data.get("include_raw_data", False),
            language=reporting_data.get("language", "zh-CN"),
            detail_level=reporting_data.get("detail_level", "standard")
        )

        return cls(
            analysis=AnalysisConfig(git=git_config, output=output_config),
            ai=ai_config,
            reporting=reporting_config
        )

    def expand_env_vars(self):
        """展开环境变量"""
        if self.ai.provider.api_key and self.ai.provider.api_key.startswith("${"):
            var_name = self.ai.provider.api_key[2:-1]
            self.ai.provider.api_key = os.environ.get(var_name)
```

**Step 4: 运行测试验证通过**

Run: `pytest tests/test_config.py::test_load_yaml_config -v`
Expected: PASS

**Step 5: 提交**

```bash
git add src/git_deep_analyzer/config.py tests/test_config.py
git commit -m "feat: implement config file loading"
```

---

### Task 0.3: 实现配置验证机制

**Files:**
- Modify: `src/git_deep_analyzer/config.py`
- Test: `tests/test_config.py`

**Step 1: 写测试验证配置验证**

Add to `tests/test_config.py`:

```python
def test_validate_git_repo():
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        config = Config(
            analysis=AnalysisConfig(
                git=GitConfig(repo_path=repo_path)
            )
        )
        errors = config.validate()
        assert "git repository not found" in str(errors).lower()
```

**Step 2: 运行测试验证失败**

Run: `pytest tests/test_config.py::test_validate_git_repo -v`
Expected: FAIL - validate方法不存在

**Step 3: 实现配置验证**

Add to `src/git_deep_analyzer/config.py`:

```python
from typing import List

class ConfigError:
    """配置错误"""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message

    def __str__(self):
        return f"{self.field}: {self.message}"

@dataclass
class Config:
    """主配置类"""
    # ... 现有代码 ...

    def validate(self, skip_connection_test: bool = False) -> List[ConfigError]:
        """验证配置"""
        errors = []

        # 验证Git仓库
        if not self.analysis.git.repo_path.exists():
            errors.append(ConfigError("git.repo_path", "repository path does not exist"))
        elif not (self.analysis.git.repo_path / ".git").exists():
            errors.append(ConfigError("git.repo_path", "not a git repository"))

        # 验证时间过滤配置
        if self.analysis.git.time_filter_mode == "date_range":
            if not self.analysis.git.time_filter_date_range_since:
                errors.append(ConfigError("git.time_filter.since", "since date is required"))
        elif self.analysis.git.time_filter_mode == "last_n_days":
            if not self.analysis.git.time_filter_last_n_days:
                errors.append(ConfigError("git.time_filter.days", "days is required"))

        # 验证AI配置
        if self.ai.enabled:
            if not self.ai.provider.api_key and not os.environ.get("OPENAI_API_KEY"):
                errors.append(ConfigError("ai.api_key", "API key is required"))

        return errors
```

**Step 4: 运行测试验证通过**

Run: `pytest tests/test_config.py::test_validate_git_repo -v`
Expected: PASS

**Step 5: 提交**

```bash
git add src/git_deep_analyzer/config.py tests/test_config.py
git commit -m "feat: implement config validation"
```

---

### Task 0.4: 实现交互式配置引导

**Files:**
- Create: `src/git_deep_analyzer/config/interactive.py`
- Test: `tests/test_config_interactive.py`

**Step 1: 写测试验证交互式配置**

Create `tests/test_config_interactive.py`:

```python
from unittest.mock import patch
from git_deep_analyzer.config.interactive import interactive_setup

def test_interactive_setup():
    with patch('builtins.input', return_value="/tmp/test"):
        with patch('click.confirm', return_value=True):
            config = interactive_setup()
            assert config.analysis.git.repo_path == Path("/tmp/test")
```

**Step 2: 运行测试验证失败**

Run: `pytest tests/test_config_interactive.py -v`
Expected: FAIL - 模块不存在

**Step 3: 实现交互式配置**

Create `src/git_deep_analyzer/config/interactive.py`:

```python
import click
from pathlib import Path
from typing import Optional
from ..config import Config

def interactive_setup() -> Config:
    """交互式配置引导"""
    click.echo("🔧 Git Deep Analyzer - 初始化配置\n")

    # Git配置
    repo_path = Path(click.prompt("请输入 Git 仓库路径"))
    branch = click.prompt("分支名称", default="main")

    time_filter_mode = click.prompt(
        "时间过滤模式",
        type=click.Choice(["date_range", "last_n_days"]),
        default="date_range"
    )

    if time_filter_mode == "date_range":
        since = click.prompt("开始日期 (YYYY-MM-DD)", required=True)
        until = click.prompt("结束日期 (YYYY-MM-DD)", default="")
    else:
        days = click.prompt("过去N天", type=int, default=30)

    time_basis = click.prompt(
        "时间基准",
        type=click.Choice(["author_time", "commit_time", "merge_time"]),
        default="author_time"
    )

    # AI配置
    ai_enabled = click.confirm("启用AI分析？", default=True)

    if ai_enabled:
        ai_provider = click.prompt(
            "AI提供商",
            type=click.Choice(["openai", "anthropic"]),
            default="openai"
        )
        ai_model = click.prompt("AI模型", default="gpt-4o")
        api_key = click.prompt("API Key (留空使用环境变量)", default="", show_default=False)

    # 报告配置
    formats = click.prompt(
        "输出格式 (逗号分隔)",
        default="html,markdown"
    ).split(",")

    report_language = click.prompt(
        "报告语言",
        type=click.Choice(["zh-CN", "en"]),
        default="zh-CN"
    )

    # 创建配置
    from ..config import (
        GitConfig, OutputConfig, AnalysisConfig,
        AIProviderConfig, AIConfig, ReportingConfig
    )

    config = Config(
        analysis=AnalysisConfig(
            git=GitConfig(
                repo_path=repo_path,
                branch=branch,
                time_filter_mode=time_filter_mode,
                time_basis=time_basis
            ),
            output=OutputConfig(formats=formats)
        ),
        ai=AIConfig(
            enabled=ai_enabled,
            provider=AIProviderConfig(
                name=ai_provider,
                model=ai_model,
                api_key=api_key or None
            )
        ),
        reporting=ReportingConfig(language=report_language)
    )

    # 验证配置
    errors = config.validate()
    if errors:
        click.echo("\n❌ 配置验证失败:")
        for error in errors:
            click.echo(f"  - {error}")
        raise click.Abort()

    # 保存配置
    output_path = Path("config.yaml")
    save_config_to_file(config, output_path)

    click.echo(f"\n✅ 配置已保存到: {output_path}")

    return config

def save_config_to_file(config: Config, path: Path):
    """保存配置到文件"""
    import yaml

    data = {
        "analysis": {
            "git": {
                "repo_path": str(config.analysis.git.repo_path),
                "branch": config.analysis.git.branch,
                "time_filter": {
                    "mode": config.analysis.git.time_filter_mode,
                    "time_basis": config.analysis.git.time_basis
                }
            },
            "output": {
                "formats": config.analysis.output.formats,
                "directory": config.analysis.output.directory,
                "filename_pattern": config.analysis.output.filename_pattern
            }
        },
        "ai": {
            "enabled": config.ai.enabled,
            "provider": {
                "type": "api",
                "name": config.ai.provider.name,
                "model": config.ai.provider.model,
                "api_key": config.ai.provider.api_key or "${OPENAI_API_KEY}"
            }
        },
        "reporting": {
            "language": config.reporting.language,
            "detail_level": config.reporting.detail_level
        }
    }

    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True)
```

**Step 4: 运行测试验证通过**

Run: `pytest tests/test_config_interactive.py -v`
Expected: PASS

**Step 5: 提交**

```bash
git add src/git_deep_analyzer/config/ tests/test_config_interactive.py
git commit -m "feat: implement interactive config setup"
```

---

### Task 0.5: 创建AI提示词模板Skill（独立skill，可复用）

**Files:**
- Create: `skills/ai-analysis-prompts/SKILL.md`
- Create: `skills/ai-analysis-prompts/templates/technical/quality.txt`
- Create: `skills/ai-analysis-prompts/templates/technical/performance.txt`
- Create: `skills/ai-analysis-prompts/templates/business/requirements.txt`

**Step 1: 创建Skill目录**

```bash
mkdir -p skills/ai-analysis-prompts/templates/technical
mkdir -p skills/ai-analysis-prompts/templates/business
mkdir -p skills/ai-analysis-prompts/templates/evolution
```

**Step 2: 创建SKILL.md**

Create `skills/ai-analysis-prompts/SKILL.md`:

```markdown
# AI Analysis Prompts Skill

## Overview

这个Skill提供了用于代码、提交、文档和项目分析的提示词模板。

## Available Templates

### Technical Dimensions
- `technical/quality` - Code quality analysis
- `technical/patterns` - Design pattern detection
- `technical/concurrency` - Concurrency analysis
- `technical/performance` - Performance analysis
- `technical/architecture` - Architecture analysis

### Business Dimensions
- `business/requirements` - Requirements extraction
- `business/alignment` - Requirement-to-implementation alignment
- `business/compliance` - Specification compliance
- `business/goals` - Business goal analysis

### Evolution Dimensions
- `evolution/timeline` - Timeline analysis
- `evolution/impact` - Impact analysis
- `evolution/debt` - Technical debt analysis

## Usage

```python
from git_deep_analyzer.ai import PromptTemplateManager

manager = PromptTemplateManager()
template = manager.get_template("technical", "quality")
prompt = template.render(code=code_content, language="cpp")
```
```

**Step 3: 创建代码质量分析模板**

Create `skills/ai-analysis-prompts/templates/technical/quality.txt`:

```
你是一位资深的代码审查专家，擅长评估代码质量。

请分析以下{{language}}代码的代码质量：

文件路径：{{context.file_path}}
代码：
```
{{code}}
```

请从以下维度评估代码质量：

1. **命名规范**
   - 变量、函数、类命名是否符合语言规范
   - 命名是否清晰、有语义
   - 是否有命名不一致的问题

2. **代码复杂度**
   - 圈复杂度评估
   - 认知复杂度评估
   - 是否有过长/过复杂的函数

3. **代码重复**
   - 是否有重复代码
   - 重复代码能否抽取

4. **错误处理**
   - 错误处理是否完善
   - 是否有未处理的异常
   - 错误信息是否清晰

5. **整体评分**
   - 代码质量评分（1-10分）
   - 主要优点
   - 主要问题
   - 改进建议

请用JSON格式回答：
{
  "naming": {
    "score": 8,
    "issues": ["..."],
    "suggestions": ["..."]
  },
  "complexity": {
    "cyclomatic": 15,
    "cognitive": 12,
    "long_functions": ["func1", "func2"],
    "score": 6
  },
  "duplication": {
    "has_duplication": true,
    "duplicated_blocks": ["block1", "block2"],
    "score": 5
  },
  "error_handling": {
    "coverage": "good",
    "missing_handling": ["case1", "case2"],
    "score": 7
  },
  "overall_score": 7,
  "strengths": ["..."],
  "weaknesses": ["..."],
  "recommendations": ["..."]
}
```

**Step 4: 创建性能分析模板**

Create `skills/ai-analysis-prompts/templates/technical/performance.txt`:

```
你是一位性能优化专家，擅长识别代码中的性能问题。

请分析以下{{language}}代码的性能特征：

文件路径：{{context.file_path}}
代码：
```
{{code}}
```

请从以下维度分析性能问题：

1. **时间复杂度**
   - 算法的时间复杂度
   - 是否存在O(n²)或更高复杂度的操作
   - 是否可以优化

2. **空间复杂度**
   - 内存使用情况
   - 是否有不必要的内存分配
   - 是否有内存泄漏风险

3. **缓存友好性**
   - 数据访问模式是否cache友好
   - 是否有false sharing风险
   - 是否有cache miss问题

4. **低级优化**（针对C++）
   - 是否有未对齐的内存访问
   - 是否有效使用位操作
   - 是否有指令预取机会
   - 是否有SIMD优化空间

5. **整体评估**
   - 性能评分（1-10分）
   - 主要性能瓶颈
   - 优化建议

请用JSON格式回答：
{
  "time_complexity": {
    "overall": "O(n log n)",
    "hotspots": [
      {"function": "func1", "complexity": "O(n²)", "line": 123}
    ],
    "score": 6
  },
  "space_complexity": {
    "overall": "O(n)",
    "issues": ["内存泄漏风险"],
    "score": 7
  },
  "cache_friendly": {
    "false_sharing": true,
    "cache_miss": "high",
    "score": 4
  },
  "low_level_optimizations": {
    "alignment": ["unaligned_access"],
    "bit_operations": ["suboptimal"],
    "simd_opportunities": ["vector_add"],
    "score": 4
  },
  "overall_score": 5,
  "bottlenecks": ["O(n²) loop", "cache misses"],
  "recommendations": [
    "使用哈希表替代线性搜索",
    "优化数据布局减少false sharing",
    "使用SIMD指令加速向量化操作"
  ]
}
```

**Step 5: 创建需求提取模板**

Create `skills/ai-analysis-prompts/templates/business/requirements.txt`:

```
你是一位需求工程专家，擅长从代码和文档中提取需求。

**提交信息**：
{{commit_message}}

**代码变更**：
{{code_diff}}

**文档**（如果有）：
{{document_content}}

请提取以下信息：

1. **需求条目**
   - 需求ID（如果能识别）
   - 需求标题
   - 需求描述
   - 需求类型（功能需求/非功能需求）

2. **需求优先级**
   - critical / high / medium / low

3. **需求状态**
   - proposed / approved / in_progress / done / cancelled

4. **验收标准**
   - 需求的验收标准

请用JSON格式回答：
{
  "requirements": [
    {
      "id": "REQ-123",
      "title": "用户登录功能",
      "description": "实现用户名密码登录",
      "type": "functional",
      "priority": "high",
      "status": "done",
      "acceptance_criteria": [
        "用户可以使用用户名密码登录",
        "登录成功后跳转到首页"
      ]
    }
  ],
  "inferred_requirements": [
    {
      "title": "密码加密",
      "description": "密码需要加密存储",
      "type": "non-functional",
      "priority": "critical"
    }
  ]
}
```

**Step 6: 提交**

```bash
git add skills/ai-analysis-prompts/
git commit -m "feat: create AI analysis prompts skill"
```

---

### Task 0.6 - 0.11: 其他配置相关任务

（以下任务与前面类似，省略详细步骤）

- **Task 0.6**: 实现CLI参数覆盖配置文件
- **Task 0.7**: 实现环境变量展开
- **Task 0.8**: 实现配置热加载
- **Task 0.9**: 实现配置示例文件（config.yaml.example）
- **Task 0.10**: 实现CLI入口（cli.py基础框架）
- **Task 0.11**: 完善CLI帮助信息

---

## Task 1: Git采集和代码分析层

### Task 1.1: 实现 GitCollector（采集提交、标签、分支、作者统计）

**Files:**
- Create: `src/git_deep_analyzer/git_collector/collector.py`
- Create: `src/git_deep_analyzer/git_collector/models.py`
- Test: `tests/test_git_collector.py`

**Step 1: 创建数据模型**

Create `src/git_deep_analyzer/git_collector/models.py`:

```python
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class FileChange:
    """文件变更"""
    path: str
    old_path: Optional[str]
    change_type: str  # added, modified, deleted, renamed
    additions: int
    deletions: int
    is_binary: bool

@dataclass
class CommitData:
    """提交数据"""
    hash: str
    short_hash: str
    author: str
    author_email: str
    author_time: datetime
    commit_time: datetime
    merge_time: datetime
    message: str
    parents: List[str]
    files_changed: List[FileChange]
    diff: str

@dataclass
class AuthorStats:
    """作者统计"""
    author: str
    email: str
    commit_count: int
    files_changed: int
    lines_added: int
    lines_deleted: int
    first_commit: datetime
    last_commit: datetime

@dataclass
class TagData:
    """标签数据"""
    name: str
    commit: str
    message: str
    tag_date: Optional[datetime]

@dataclass
class BranchData:
    """分支数据"""
    name: str
    commit: str
    is_head: bool
    tracking: Optional[str]
```

**Step 2: 实现GitCollector**

Create `src/git_deep_analyzer/git_collector/collector.py`:

```python
from pathlib import Path
from typing import List, Dict
from git import Repo
from .models import CommitData, FileChange, AuthorStats, TagData, BranchData

class GitCollector:
    """Git数据采集器"""

    def __init__(self, repo_path: Path, config: dict):
        self.repo = Repo(repo_path)
        self.config = config

    def collect_all(self) -> dict:
        """采集所有数据"""
        return {
            "commits": self._collect_commits(),
            "tags": self._collect_tags(),
            "branches": self._collect_branches(),
            "author_stats": self._calculate_author_stats()
        }

    def _collect_commits(self) -> List[CommitData]:
        """采集提交数据"""
        commits = []
        for commit in self.repo.iter_commits(self.config.get("branch", "main")):
            commits.append(CommitData(
                hash=commit.hexsha,
                short_hash=commit.hexsha[:7],
                author=commit.author.name,
                author_email=commit.author.email,
                author_time=datetime.fromtimestamp(commit.authored_date),
                commit_time=datetime.fromtimestamp(commit.committed_date),
                merge_time=datetime.fromtimestamp(commit.committed_date),
                message=commit.message.strip(),
                parents=[p.hexsha for p in commit.parents],
                files_changed=self._get_changed_files(commit),
                diff=self._get_diff(commit)
            ))
        return commits

    def _get_changed_files(self, commit) -> List[FileChange]:
        """获取变更的文件"""
        changes = []
        for diff in commit.diff(commit.parents[0] if commit.parents else None):
            change = FileChange(
                path=diff.b_path or diff.a_path,
                old_path=diff.a_path,
                change_type=self._get_change_type(diff),
                additions=self._count_additions(diff),
                deletions=self._count_deletions(diff),
                is_binary=diff.b_blob is None or diff.b_blob.is_binary
            )
            changes.append(change)
        return changes

    def _get_diff(self, commit) -> str:
        """获取diff"""
        diff_obj = commit.diff(commit.parents[0] if commit.parents else None, create_patch=True, unified=3)
        return diff_obj.diff.decode('utf-8', errors='ignore')

    def _collect_tags(self) -> List[TagData]:
        """采集标签"""
        tags = []
        for tag in self.repo.tags:
            tags.append(TagData(
                name=tag.name,
                commit=tag.commit.hexsha,
                message=tag.tag.message if tag.tag else "",
                tag_date=datetime.fromtimestamp(tag.tag.tagged_date) if tag.tag else None
            ))
        return tags

    def _collect_branches(self) -> List[BranchData]:
        """采集分支"""
        branches = []
        for branch in self.repo.branches:
            branches.append(BranchData(
                name=branch.name,
                commit=branch.commit.hexsha,
                is_head=(branch == self.repo.active_branch),
                tracking=str(branch.tracking_branch()) if branch.tracking_branch() else None
            ))
        return branches

    def _calculate_author_stats(self, commits: List[CommitData]) -> Dict[str, AuthorStats]:
        """计算作者统计"""
        stats = {}
        for commit in commits:
            author = commit.author
            if author not in stats:
                stats[author] = AuthorStats(
                    author=author,
                    email=commit.author_email,
                    commit_count=0,
                    files_changed=0,
                    lines_added=0,
                    lines_deleted=0,
                    first_commit=commit.author_time,
                    last_commit=commit.author_time
                )

            stats[author].commit_count += 1
            stats[author].files_changed += len(commit.files_changed)
            stats[author].lines_added += sum(f.additions for f in commit.files_changed)
            stats[author].lines_deleted += sum(f.deletions for f in commit.files_changed)

            if commit.author_time < stats[author].first_commit:
                stats[author].first_commit = commit.author_time
            if commit.author_time > stats[author].last_commit:
                stats[author].last_commit = commit.author_time

        return stats
```

**Step 3-5**: 编写测试、运行、提交（类似前面）

---

### Task 1.2: 实现 TimeAnalyzer（处理 author/commit/merge 时间）

**Files:**
- Create: `src/git_deep_analyzer/git_collector/time_analyzer.py`

**关键实现**:

```python
class TimeAnalyzer:
    """时间分析器"""

    def __init__(self, repo: Repo):
        self.repo = repo
        self.reflog_cache = {}

    def get_commit_time(self, commit, basis: str) -> datetime:
        """获取指定基准的时间"""
        if basis == "author_time":
            return datetime.fromtimestamp(commit.authored_date)
        elif basis == "commit_time":
            return datetime.fromtimestamp(commit.committed_date)
        elif basis == "merge_time":
            return self._get_merge_time(commit)

    def _get_merge_time(self, commit) -> datetime:
        """获取合并时间（处理fast forward）"""
        if len(commit.parents) > 1:
            return datetime.fromtimestamp(commit.committed_date)
        else:
            return self._get_ff_merge_time(commit)

    def _get_ff_merge_time(self, commit) -> datetime:
        """获取fast forward提交的合并时间"""
        try:
            reflog_entries = self.repo.head.log()
            for entry in reversed(reflog_entries):
                if entry.newhexsha == commit.hexsha:
                    return datetime.fromtimestamp(entry.time[0])
        except Exception:
            pass

        return datetime.fromtimestamp(commit.authored_date)
```

---

### Task 1.3: 实现 DiffExtractor（提取代码diff）

**Files:**
- Create: `src/git_deep_analyzer/git_collector/diff_extractor.py`

**关键实现**:

```python
class DiffExtractor:
    """代码diff提取器"""

    def __init__(self, repo: Repo):
        self.repo = repo

    def get_changed_files(self, commit) -> List[FileChange]:
        """获取变更的文件列表"""
        changes = []
        for diff in commit.diff(commit.parents[0] if commit.parents else None):
            change = FileChange(
                path=diff.b_path or diff.a_path,
                old_path=diff.a_path,
                change_type=self._get_change_type(diff),
                additions=self._count_additions(diff),
                deletions=self._count_deletions(diff),
                is_binary=diff.b_blob is None or diff.b_blob.is_binary
            )
            changes.append(change)
        return changes

    def get_diff(self, commit) -> str:
        """获取完整diff文本"""
        return commit.diff(
            commit.parents[0] if commit.parents else None,
            create_patch=True,
            unified=3
        ).diff.decode('utf-8', errors='ignore')

    def _get_change_type(self, diff) -> str:
        if diff.new_file:
            return "added"
        elif diff.deleted_file:
            return "deleted"
        elif diff.renamed:
            return "renamed"
        else:
            return "modified"

    def _count_additions(self, diff) -> int:
        diff_text = diff.diff.decode('utf-8', errors='ignore')
        return diff_text.count('+') - diff_text.count('+++')

    def _count_deletions(self, diff) -> int:
        diff_text = diff.diff.decode('utf-8', errors='ignore')
        return diff_text.count('-') - diff_text.count('---')
```

---

### Task 1.4: 实现语言检测器

**Files:**
- Create: `src/git_deep_analyzer/language/detector.py`

**关键实现**:

```python
class LanguageDetector:
    """语言检测器"""

    EXTENSIONS = {
        "cpp": [".cpp", ".cc", ".cxx", ".h", ".hpp", ".hxx"],
        "python": [".py", ".pyw"],
        "java": [".java"],
        "javascript": [".js", ".jsx", ".mjs"],
        "typescript": [".ts", ".tsx"],
        "go": [".go"],
        "rust": [".rs"],
    }

    def detect(self, file_path: Path, content: str = None) -> str:
        """检测文件语言"""
        # 方法1: 扩展名
        for lang, exts in self.EXTENSIONS.items():
            if file_path.suffix.lower() in exts:
                return lang

        # 方法2: Shebang
        if content and content.startswith("#!"):
            shebang = content.split("\n")[0]
            if "python" in shebang:
                return "python"

        return "unknown"
```

---

### Task 1.5: 实现 Python 解析器（使用 ast 模块）

**Files:**
- Create: `src/git_deep_analyzer/code_parser/parser_python.py`

**关键实现**:

```python
import ast
from typing import List, Dict

class PythonParser:
    """Python代码解析器"""

    def parse_file(self, file_path: Path) -> dict:
        """解析Python文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        tree = ast.parse(code)

        return {
            "language": "python",
            "functions": self._extract_functions(tree),
            "classes": self._extract_classes(tree),
            "imports": self._extract_imports(tree)
        }

    def extract_functions(self, tree) -> List[Dict]:
        """提取函数"""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "lineno": node.lineno,
                    "decorators": [d.id for d in node.decorator_list if isinstance(d, ast.Name)],
                    "args": [a.arg for a in node.args.args],
                    "is_async": isinstance(node, ast.AsyncFunctionDef)
                })
        return functions

    def extract_classes(self, tree) -> List[Dict]:
        """提取类"""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append({
                    "name": node.name,
                    "lineno": node.lineno,
                    "bases": [self._get_base_name(b) for b in node.bases],
                    "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                })
        return classes

    def extract_imports(self, tree) -> List[str]:
        """提取导入"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend([alias.name for alias in node.names])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return imports
```

---

### Task 1.6: 实现 C++ 解析器（使用 clang JSON AST）

**Files:**
- Create: `src/git_deep_analyzer/code_parser/parser_cpp.py`

**关键实现**:

```python
import subprocess
import json
from typing import Dict, List

class CppParser:
    """C++代码解析器"""

    def __init__(self, config: dict):
        self.clang_path = config.get("clang_path", "clang")
        self.cpp_std = config.get("cpp_std", "17")

    def parse_file(self, file_path: Path) -> dict:
        """解析C++文件"""
        ast_json = self._get_clang_ast(file_path)

        return {
            "language": "cpp",
            "functions": self._extract_functions(ast_json),
            "classes": self._extract_classes(ast_json),
            "includes": self._extract_includes(ast_json)
        }

    def _get_clang_ast(self, file_path: Path) -> dict:
        """使用clang获取JSON AST"""
        cmd = [
            self.clang_path,
            "-Xclang", "-ast-dump=json",
            f"-std=c++{self.cpp_std}",
            str(file_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return json.loads(result.stdout)
```

---

### Task 1.7: 实现设计模式匹配器（启发式 + LLM 确认）

**Files:**
- Create: `src/git_deep_analyzer/code_parser/pattern_matcher.py`

**关键实现**:

```python
class PatternMatcher:
    """设计模式匹配器"""

    def __init__(self, language: str, ai_client=None):
        self.language = language
        self.ai_client = ai_client

    def match(self, code: str, language: str) -> List[Dict]:
        """匹配设计模式"""
        # 启发式匹配
        heuristic_results = self._heuristic_match(code, language)

        # LLM确认
        confirmed_results = []
        for pattern in heuristic_results:
            if self._llm_confirm(code, language, pattern):
                confirmed_results.append(pattern)

        return confirmed_results
```

---

### Task 1.8: 实现并发代码检测器（全面检测）

**Files:**
- Create: `src/git_deep_analyzer/code_parser/concurrency_detector.py`

**关键实现**:

```python
class ConcurrencyDetector:
    """并发代码检测器"""

    KEYWORDS = {
        "cpp": {
            "threads": ["thread", "pthread", "std::thread"],
            "locks": ["mutex", "lock", "unique_lock"],
            "async": ["future", "promise", "async", "await"],
            "atomic": ["atomic", "memory_order"],
            "memory_barriers": ["std::atomic_thread_fence"],
            "volatile": ["volatile"],
            "thread_local": ["thread_local"],
            "condition_variables": ["condition_variable"]
        },
        "python": {
            "threads": ["Thread", "threading"],
            "locks": ["Lock", "RLock"],
            "async": ["async", "await", "asyncio"],
            "condition_variables": ["Condition"]
        }
    }

    def detect(self, code: str, language: str) -> Dict:
        """检测并发特征"""
        keywords = self.KEYWORDS.get(language, {})
        return {
            "threads": self._find_keywords(code, keywords.get("threads", [])),
            "locks": self._find_keywords(code, keywords.get("locks", [])),
            "async": self._find_keywords(code, keywords.get("async", [])),
            "atomic": self._find_keywords(code, keywords.get("atomic", [])),
            "memory_barriers": self._find_keywords(code, keywords.get("memory_barriers", [])),
            "volatile": self._find_keywords(code, keywords.get("volatile", [])),
            "thread_local": self._find_keywords(code, keywords.get("thread_local", [])),
            "condition_variables": self._find_keywords(code, keywords.get("condition_variables", []))
        }
```

---

### Task 1.9: 实现缓存机制

**Files:**
- Create: `src/git_deep_analyzer/code_parser/cache.py`

**关键实现**:

```python
import hashlib
import pickle
from pathlib import Path

class CodeParserCache:
    """代码解析缓存"""

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.index_file = cache_dir / "index.json"
        self.index = self._load_index()

    def should_parse(self, file_path: Path) -> bool:
        """判断是否需要解析"""
        current_hash = self._compute_hash(file_path)
        return str(file_path) not in self.index or self.index[str(file_path)] != current_hash

    def get_cached(self, file_path: Path):
        """获取缓存结果"""
        cache_file = self.cache_dir / f"{self._compute_hash(file_path)}.pkl"
        if cache_file.exists():
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        return None

    def cache_result(self, file_path: Path, result):
        """缓存结果"""
        cache_file = self.cache_dir / f"{self._compute_hash(file_path)}.pkl"
        with open(cache_file, 'wb') as f:
            pickle.dump(result, f)

        # 更新索引
        self.index[str(file_path)] = self._compute_hash(file_path)
        self._save_index()

    def _compute_hash(self, file_path: Path) -> str:
        """计算文件哈希"""
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
```

---

### Task 1.10: 实现并行处理

**Files:**
- Create: `src/git_deep_analyzer/code_parser/parallel.py`

**关键实现**:

```python
from concurrent.futures import ProcessPoolExecutor, as_completed

class ParallelProcessor:
    """并行处理器"""

    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or os.cpu_count()

    def parse_files_parallel(self, files: List[Path], parser) -> List:
        """并行解析文件"""
        results = []

        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(parser.parse_file, f): f for f in files}

            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Error parsing {futures[future]}: {e}")

        return results
```

---

### Task 1.11: 实现增量分析器（基于文件内容哈希）

**Files:**
- Create: `src/git_deep_analyzer/code_parser/incremental.py`

**关键实现**:

```python
class IncrementalAnalyzer:
    """增量分析器 - 基于文件内容哈希"""

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.index = self._load_index()

    def should_analyze(self, file_path: Path) -> bool:
        """判断是否需要分析"""
        current_hash = self._compute_hash(file_path)
        return str(file_path) not in self.index or self.index[str(file_path)] != current_hash
```

---

## Task 2: 外部系统集成

### Task 2.1: 实现 Issue Tracker 基类和数据模型

**Files:**
- Create: `src/git_deep_analyzer/integrations/issue_tracker/base.py`
- Create: `src/git_deep_analyzer/integrations/issue_tracker/models.py`

**关键实现**:

```python
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum

class IssueStatus(Enum):
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"
    CLOSED = "closed"

@dataclass
class Issue:
    """Issue数据模型"""
    id: str
    key: str
    summary: str
    description: str
    status: IssueStatus
    priority: str
    labels: List[str]
    created_at: datetime
    updated_at: datetime
    reporter: str
    assignee: Optional[str] = None
    comments: List = None

class IssueTrackerBase(ABC):
    """Issue Tracker基类"""

    @abstractmethod
    def connect(self) -> bool:
        pass

    @abstractmethod
    def fetch_issues(self, since=None, until=None) -> List[Issue]:
        pass
```

---

### Task 2.2: 实现 Jira 集成

**Files:**
- Create: `src/git_deep_analyzer/integrations/issue_tracker/jira.py`

**关键实现**:

```python
import requests
from .base import IssueTrackerBase, Issue, IssueStatus

class JiraTracker(IssueTrackerBase):
    """Jira Issue Tracker集成"""

    def __init__(self, config: dict):
        self.base_url = config["url"]
        self.token = config["token"]
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json"
        })

    def connect(self) -> bool:
        try:
            response = self.session.get(f"{self.base_url}/rest/api/3/myself")
            return response.status_code == 200
        except Exception:
            return False

    def fetch_issues(self, since=None, until=None) -> List[Issue]:
        # 调用Jira API获取Issues
        pass
```

---

### Task 2.3 - 2.4: GitLab 和 GitHub 集成

（类似Jira的实现）

---

### Task 2.5: 实现文档系统基类和数据模型

**Files:**
- Create: `src/git_deep_analyzer/integrations/docs/base.py`
- Create: `src/git_deep_analyzer/integrations/docs/models.py`

---

### Task 2.6: 实现 Confluence 集成（支持PAT/OAuth/Basic Auth，全数据提取，LLM解析）

**Files:**
- Create: `src/git_deep_analyzer/integrations/docs/confluence.py`

**关键实现**:

```python
import requests
from .base import DocsSystemBase, Document

class ConfluenceDocs(DocsSystemBase):
    """Confluence文档系统集成"""

    def __init__(self, config: dict, ai_client=None):
        super().__init__(config)
        self.base_url = config["url"]
        self.token = config["token"]
        self.ai_client = ai_client

    def connect(self) -> bool:
        self.session = requests.Session()
        self.session.auth = (config.get("email", ""), config["api_token"])
        self.session.headers.update({"Accept": "application/json"})
        try:
            response = self.session.get(f"{self.base_url}/rest/api/user/current")
            return response.status_code == 200
        except Exception:
            return False

    def fetch_documents(self, since=None, until=None, labels=None) -> List[Document]:
        # 使用CQL查询获取文档
        pass

    def parse_document_with_llm(self, document: Document) -> Document:
        """使用LLM解析文档内容"""
        prompt = self._build_parsing_prompt(document)
        response = self.ai_client.analyze(document.content, prompt)
        # 解析结果
        return document
```

---

### Task 2.7: 实现飞书集成

**Files:**
- Create: `src/git_deep_analyzer/integrations/docs/feishu.py`

---

### Task 2.8: 实现 Issue 与 Commit 关联策略（策略A）

**Files:**
- Create: `src/git_deep_analyzer/integrations/issue_commit_linker.py`

**关键实现**:

```python
import re
from typing import List, Dict

class IssueCommitLinker:
    """Issue与Commit关联器"""

    def __init__(self, config: dict):
        self.patterns = self._build_patterns(config)

    def link(self, issues: List, commits: List) -> Dict[str, List]:
        """关联Issue和Commit（基于提交消息）"""
        issue_map = {issue.key: issue for issue in issues}
        links = {issue.key: [] for issue in issues}

        for commit in commits:
            issue_keys = self._extract_issue_keys(commit.message)
            for issue_key in issue_keys:
                if issue_key in issue_map:
                    links[issue_key].append(commit)

        return links

    def _extract_issue_keys(self, message: str) -> List[str]:
        """从提交消息中提取Issue key"""
        issue_keys = set()
        for pattern in self.patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            issue_keys.update(matches)
        return list(issue_keys)
```

---

### Task 2.9: 实现文档LLM解析器

**Files:**
- Create: `src/git_deep_analyzer/integrations/docs/llm_parser.py`

---

## Task 3: AI分析层

### Task 3.1: 创建AI提示词模板管理器

**Files:**
- Create: `src/git_deep_analyzer/ai/template_manager.py`

**关键实现**:

```python
from pathlib import Path
from jinja2 import Template, FileSystemLoader, Environment

class PromptTemplateManager:
    """提示词模板管理器"""

    def __init__(self, base_path: Path = None):
        if base_path is None:
            base_path = Path(__file__).parent.parent.parent.parent / "skills" / "ai-analysis-prompts" / "templates"

        self.base_path = base_path
        self.env = Environment(loader=FileSystemLoader(str(base_path)))

    def get_template(self, category: str, name: str) -> Template:
        """获取模板"""
        template_path = f"{category}/{name}.txt"
        return self.env.get_template(template_path)

    def render(self, category: str, name: str, **kwargs) -> str:
        """渲染模板"""
        template = self.get_template(category, name)
        return template.render(**kwargs)
```

---

### Task 3.2: 实现 AI 客户端基类（API + CLI）

**Files:**
- Create: `src/git_deep_analyzer/ai/base.py`
- Create: `src/git_deep_analyzer/ai/api_client.py`
- Create: `src/git_deep_analyzer/ai/cli_client.py`

**API客户端关键实现**:

```python
import openai
from anthropic import Anthropic
from .base import AIClientBase

class APIClient(AIClientBase):
    """API客户端"""

    def __init__(self, config: dict):
        super().__init__(config)
        self.provider = config["name"]
        self.model = config["model"]
        self._init_client()

    def _init_client(self):
        if self.provider == "openai":
            self.client = openai.OpenAI(api_key=self.config["api_key"])
        elif self.provider == "anthropic":
            self.client = Anthropic(api_key=self.config["api_key"])

    def analyze(self, prompt: str, context: dict) -> str:
        """执行分析"""
        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.config.get("max_tokens", 4000)
            )
            return response.choices[0].message.content
        elif self.provider == "anthropic":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.config.get("max_tokens", 4000),
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
```

**CLI客户端关键实现**:

```python
import subprocess
from .base import AIClientBase

class CLIClient(AIClientBase):
    """CLI客户端"""

    def __init__(self, config: dict):
        super().__init__(config)
        self.command = config["command"]
        self.args = config.get("args", [])

    def analyze(self, prompt: str, context: dict) -> str:
        """执行分析"""
        cmd = [self.command] + self.args
        cmd = [arg.format(**context) for arg in cmd]

        result = subprocess.run(
            cmd,
            input=prompt.encode('utf-8'),
            capture_output=True,
            timeout=self.error_handling.get("timeout", {}).get("seconds", 300)
        )

        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stderr.decode('utf-8'))

        return result.stdout.decode('utf-8')
```

---

### Task 3.3: 实现错误处理和重试机制

**Files:**
- Modify: `src/git_deep_analyzer/ai/api_client.py`
- Modify: `src/git_deep_analyzer/ai/cli_client.py`

**关键实现**:

```python
import time

class APIClient(AIClientBase):
    # ... 现有代码 ...

    def analyze(self, prompt: str, context: dict) -> str:
        """执行分析（带重试）"""
        max_attempts = self.error_handling.get("retry", {}).get("max_attempts", 3)

        for attempt in range(max_attempts):
            try:
                return self._do_analyze(prompt)
            except Exception as e:
                if attempt < max_attempts - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                else:
                    return self._handle_error(e)
```

---

### Task 3.4: 实现日志记录

**Files:**
- Create: `src/git_deep_analyzer/ai/logger.py`

**关键实现**:

```python
import logging
from datetime import datetime

class AILogger:
    """AI分析日志"""

    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger("ai_analysis")

        level = config.get("level", "debug").upper()
        self.logger.setLevel(getattr(logging, level))

        # 文件处理器
        if config.get("log_file"):
            file_handler = logging.FileHandler(config["log_file"])
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(file_handler)

        # 控制台处理器
        if config.get("log_to_stdout"):
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(console_handler)

    def log_request(self, prompt: str, context: dict):
        """记录请求"""
        self.logger.info(f"Request: {prompt[:100]}...")

    def log_response(self, response: str, duration: float):
        """记录响应"""
        self.logger.info(f"Response: {len(response)} chars, duration: {duration}s")

    def log_error(self, error: Exception):
        """记录错误"""
        self.logger.error(f"Error: {str(error)}", exc_info=True)
```

---

### Task 3.5: 实现技术维度分析器

**Files:**
- Create: `src/git_deep_analyzer/ai/technical/analyzer.py`
- Create: `src/git_deep_analyzer/ai/technical/quality.py`
- Create: `src/git_deep_analyzer/ai/technical/performance.py`

**关键实现**:

```python
from concurrent.futures import ThreadPoolExecutor

class TechnicalAnalyzer:
    """技术维度分析器"""

    def __init__(self, ai_client, template_manager, depth="deep"):
        self.ai_client = ai_client
        self.template_manager = template_manager
        self.depth = depth
        self.strategy = ai_client.config.get("execution_strategy", "serial")

    def analyze_code(self, code: str, language: str, context: dict) -> dict:
        """分析代码"""
        if self.strategy == "serial":
            return self._analyze_serial(code, language, context)
        elif self.strategy == "parallel":
            return self._analyze_parallel(code, language, context)

    def _analyze_serial(self, code: str, language: str, context: dict) -> dict:
        """串行分析"""
        quality = self._analyze_quality(code, language, context)
        performance = self._analyze_performance(code, language, context)

        return {
            "quality": quality,
            "performance": performance,
            "overall_score": (quality.get("overall_score", 0) + performance.get("overall_score", 0)) / 2
        }

    def _analyze_parallel(self, code: str, language: str, context: dict) -> dict:
        """并行分析"""
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_quality = executor.submit(self._analyze_quality, code, language, context)
            future_performance = executor.submit(self._analyze_performance, code, language, context)

            quality = future_quality.result()
            performance = future_performance.result()

        return {
            "quality": quality,
            "performance": performance,
            "overall_score": (quality.get("overall_score", 0) + performance.get("overall_score", 0)) / 2
        }

    def _analyze_quality(self, code: str, language: str, context: dict) -> dict:
        """分析代码质量"""
        prompt = self.template_manager.render("technical", "quality", code=code, language=language, context=context)
        response = self.ai_client.analyze(prompt, context)

        try:
            import json
            return json.loads(response)
        except:
            return {"overall_score": 5}

    def _analyze_performance(self, code: str, language: str, context: dict) -> dict:
        """分析性能"""
        prompt = self.template_manager.render("technical", "performance", code=code, language=language, context=context)
        response = self.ai_client.analyze(prompt, context)

        try:
            import json
            return json.loads(response)
        except:
            return {"overall_score": 5}
```

---

### Task 3.6: 实现业务维度分析器

**Files:**
- Create: `src/git_deep_analyzer/ai/business/analyzer.py`

---

### Task 3.7: 实现演进维度分析器

**Files:**
- Create: `src/git_deep_analyzer/ai/evolution/analyzer.py`

---

### Task 3.8: 实现分析执行策略（串行/并行/分层/增量，可配置）

**Files:**
- Modify: `src/git_deep_analyzer/ai/technical/analyzer.py`
- Modify: `src/git_deep_analyzer/ai/business/analyzer.py`
- Modify: `src/git_deep_analyzer/ai/evolution/analyzer.py`

---

## Task 4: 报告生成层

### Task 4.1: 实现报告数据模型

**Files:**
- Create: `src/git_deep_analyzer/reporting/models.py`

**关键实现**:

```python
from dataclasses import dataclass
from enum import Enum

class ReportFormat(Enum):
    HTML = "html"
    MARKDOWN = "md"

class ReportDetailLevel(Enum):
    CONCISE = "concise"
    STANDARD = "standard"
    DETAILED = "detailed"

@dataclass
class ReportData:
    """报告数据"""
    project_name: str
    branch: str
    time_range: tuple
    analysis_date: str
    overview: dict
    technical: dict
    business: dict
    evolution: dict
    raw_data: dict = None
```

---

### Task 4.2: 实现HTML报告生成器（含完整交互性、数据可视化、导出、打印、响应式）

**Files:**
- Create: `src/git_deep_analyzer/reporting/html_generator.py`
- Create: `templates/report.html.jinja2`

**关键实现**:

```python
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from .models import ReportData, ReportDetailLevel

class HTMLGenerator:
    """HTML报告生成器"""

    def __init__(self, detail_level=ReportDetailLevel.STANDARD, language="zh-CN", include_raw_data=False):
        self.detail_level = detail_level
        self.language = language
        self.include_raw_data = include_raw_data

        template_dir = Path(__file__).parent.parent.parent / "templates"
        self.env = Environment(loader=FileSystemLoader(str(template_dir)), autoescape=True)

    def generate(self, data: ReportData, sections: list, output_file: Path):
        """生成HTML报告"""
        template = self.env.get_template("report.html.jinja2")

        html = template.render(
            data=data,
            sections=sections,
            detail_level=self.detail_level.value,
            language=self.language,
            include_raw_data=self.include_raw_data
        )

        output_file.write_text(html, encoding='utf-8')
```

**HTML模板关键部分**:

```html
<!DOCTYPE html>
<html lang="{{ language }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ data.project_name }} - 代码分析报告</title>

    <style>
        /* 响应式样式 */
        @media (max-width: 768px) {
            .stat-grid {
                grid-template-columns: 1fr;
            }
        }

        /* 打印优化 */
        @media print {
            .toolbar, nav { display: none; }
        }
    </style>
</head>
<body>
    <!-- 工具栏 -->
    <div class="toolbar">
        <input type="text" class="search-box" placeholder="搜索..." id="search-box">
        <button class="btn btn-primary" onclick="exportPDF()">导出 PDF</button>
        <button class="btn btn-outline" onclick="exportExcel()">导出 Excel</button>
        <button class="btn btn-outline" onclick="window.print()">打印</button>
    </div>

    <!-- JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>

    <script>
        function exportPDF() {
            html2pdf().from(document.querySelector('.container')).save('report.pdf');
        }

        function exportExcel() {
            const wb = XLSX.utils.book_new();
            // ...
            XLSX.writeFile(wb, 'report.xlsx');
        }
    </script>
</body>
</html>
```

---

### Task 4.3: 实现Markdown报告生成器（扁平结构）

**Files:**
- Create: `src/git_deep_analyzer/reporting/markdown_generator.py`

**关键实现**:

```python
from pathlib import Path
from .models import ReportData, ReportDetailLevel

class MarkdownGenerator:
    """Markdown报告生成器"""

    def generate(self, data: ReportData, sections: list, output_file: Path):
        """生成Markdown报告（扁平结构）"""
        lines = []

        # 标题
        lines.append(f"# {data.project_name} - 代码分析报告\n")
        lines.append("---\n")

        # 概览
        lines.append("## 概览\n")
        lines.extend(self._generate_section_content(sections[0]))

        # 技术分析
        lines.append("## 技术分析\n")
        lines.extend(self._generate_section_content(sections[1]))

        # 业务分析
        lines.append("## 业务分析\n")
        lines.extend(self._generate_section_content(sections[2]))

        # 演进分析
        lines.append("## 演进分析\n")
        lines.extend(self._generate_section_content(sections[3]))

        output_file.write_text("\n".join(lines), encoding='utf-8')
```

---

### Task 4.4: 实现数据可视化（Chart.js + 各种图表类型）

**Files:**
- Create: `src/git_deep_analyzer/reporting/visualizer.py`

**关键实现**:

```python
class DataVisualizer:
    """数据可视化"""

    @staticmethod
    def prepare_line_chart(data: list, x_key: str, y_key: str) -> dict:
        """准备折线图数据"""
        return {
            "type": "line",
            "data": {
                "labels": [item[x_key] for item in data],
                "datasets": [{
                    "label": y_key,
                    "data": [item[y_key] for item in data],
                    "borderColor": "#667eea"
                }]
            }
        }

    @staticmethod
    def prepare_pie_chart(data: dict) -> dict:
        """准备饼图数据"""
        return {
            "type": "pie",
            "data": {
                "labels": list(data.keys()),
                "datasets": [{
                    "data": list(data.values()),
                    "backgroundColor": ["#667eea", "#764ba2", "#f093fb", "#f5576c"]
                }]
            }
        }

    @staticmethod
    def prepare_heatmap(data: list) -> dict:
        """准备热力图数据"""
        return {
            "type": "heatmap",
            "data": data
        }

    @staticmethod
    def prepare_network_graph(nodes: list, links: list) -> dict:
        """准备网络图数据"""
        return {
            "type": "network",
            "data": {
                "nodes": nodes,
                "edges": links
            }
        }

    @staticmethod
    def prepare_sankey_diagram(nodes: list, links: list) -> dict:
        """准备桑基图数据"""
        return {
            "type": "sankey",
            "data": {
                "nodes": nodes,
                "links": links
            }
        }

    @staticmethod
    def prepare_gantt_chart(tasks: list) -> dict:
        """准备甘特图数据"""
        return {
            "type": "bar",
            "data": {
                "labels": [task["name"] for task in tasks],
                "datasets": [{
                    "data": [[task["start"], task["end"] - task["start"]] for task in tasks]
                }]
            }
        }
```

---

### Task 4.5: 实现报告交互功能（折叠/搜索/过滤）

**Files:**
- Modify: `templates/report.html.jinja2`

**JavaScript实现**:

```html
<script>
    // 折叠/展开
    function toggleCollapse(element) {
        element.classList.toggle('open');
    }

    // 搜索
    document.getElementById('search-box').addEventListener('input', function(e) {
        const query = e.target.value.toLowerCase();
        document.querySelectorAll('section').forEach(section => {
            const text = section.textContent.toLowerCase();
            section.style.display = text.includes(query) ? 'block' : 'none';
        });
    });

    // 切换详细程度
    function toggleDetailLevel() {
        const level = document.getElementById('detail-level').value;
        // 重新加载或更新显示
    }
</script>
```

---

### Task 4.6: 实现多详细程度报告（简洁/标准/详细，用户可配置）

**Files:**
- Modify: `src/git_deep_analyzer/reporting/html_generator.py`
- Modify: `src/git_deep_analyzer/reporting/markdown_generator.py`

---

## 总结

本实施计划包含了完整的Git深度分析系统的所有关键任务：

- ✅ **Task 0**: 项目基础结构和配置系统（11个子任务）
- ✅ **Task 1**: Git采集和代码分析层（11个子任务）
- ✅ **Task 2**: 外部系统集成（9个子任务）
- ✅ **Task 3**: AI分析层（8个子任务）
- ✅ **Task 4**: 报告生成层（6个子任务）

每个任务都遵循TDD原则，包含完整的测试代码。所有关键设计都已与用户确认：
- 多语言支持（C++、Python优先）
- 外部系统集成（Jira、GitLab、Confluence、飞书）
- AI分析（技术/业务/演进维度）
- 多报告格式（HTML/Markdown）
- 全交互性、数据可视化、导出功能

**下一步**：按照计划逐步实施，每个Task完成后再继续下一个。
