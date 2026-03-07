# Git Deep Analyzer API 文档

## 概述

Git Deep Analyzer是一个基于AI驱动的Git提交深度分析工具，提供技术、业务和演进三个维度的深度洞察。

## 安装

```bash
pip install -e .
```

### 可选依赖

```bash
# 包含C++支持
pip install -e ".[cpp]"

# 开发依赖
pip install -e ".[dev, cpp]"
```

## 配置

### 环境变量

```bash
# OpenAI API
export OPENAI_API_KEY="your-api-key"

# Anthropic (Claude) API
export ANTHROPIC_API_KEY="your-api-key"

# Jira认证
export JIRA_TOKEN="your-token"
# 或
export JIRA_USERNAME="your-email"
export JIRA_PASSWORD="your-api-token"

# Confluence认证
export CONFLUENCE_TOKEN="your-token"

# GitHub认证
export GITHUB_TOKEN="your-token"

# GitLab认证
export GITLAB_TOKEN="your-token"

# 飞书认证
export FEISHU_USER_ACCESS_TOKEN="your-token"
```

### 配置文件

创建 `.git-deep-analyzer.yaml` 配置文件：

```yaml
git:
  repo_path: /path/to/repo
  branch: main
  time_range:
    since: "2024-01-01"
    until: null
  time_basis: author_time

analysis:
  ai_provider: openai  # openai, anthropic, claude_cli, codex_cli
  ai_model: gpt-4
  dimensions:
    - technical
    - business
    - evolution
  execution_strategy: parallel

external:
  jira:
    url: https://your-domain.atlassian.net
    token: ${JIRA_TOKEN}
  confluence:
    url: https://your-domain.atlassian.net/wiki
    token: ${CONFLUENCE_TOKEN}
  github:
    url: https://api.github.com  # 可选
    token: ${GITHUB_TOKEN}
  gitlab:
    url: https://gitlab.com  # 可选
    token: ${GITLAB_TOKEN}

reporting:
  format: html  # html, markdown
  detail_level: standard  # concise, standard, detailed
  output_dir: ./reports
  interactive:
    enable_search: true
    enable_filter: true
    enable_collapse: true

logging:
  level: info
  log_to_console: true
  log_to_file: true
  log_file: ./git-deep-analyzer.log
```

## API使用

### 命令行接口

```bash
# 初始化配置文件
git-deep-analyze init

# 分析Git仓库
git-deep-analyze analyze --repo /path/to/repo --branch main

# 指定输出格式
git-deep-analyze analyze --repo /path/to/repo --format html --detail-level detailed

# 集成外部系统
git-deep-analyze analyze --repo /path/to/repo --jira-url https://your-domain.atlassian.net

# 指定时间范围
git-deep-analyze analyze --repo /path/to/repo --since "2024-01-01" --until "2024-12-31"
```

### Python API

#### Issue Tracker集成

```python
from git_deep_analyzer.integrations import JiraTracker, GitHubTracker, GitLabTracker

# Jira
jira_config = {
    "url": "https://your-domain.atlassian.net",
    "token": "your-token"
}
jira_tracker = JiraTracker(jira_config)
jira_tracker.connect()
issues = jira_tracker.fetch_issues(project_key="PROJ")

# GitHub
github_config = {
    "url": "https://api.github.com",
    "token": "your-token"
}
github_tracker = GitHubTracker(github_config)
github_tracker.connect()
issues = github_tracker.fetch_issues(owner="owner", repo="repo")

# GitLab
gitlab_config = {
    "url": "https://gitlab.com",
    "token": "your-token"
}
gitlab_tracker = GitLabTracker(gitlab_config)
gitlab_tracker.connect()
issues = gitlab_tracker.fetch_issues(project_id_or_path="owner/repo")
```

#### 文档系统集成

```python
from git_deep_analyzer.integrations import ConfluenceDocs, FeishuDocs
from git_deep_analyzer.integrations.docs import DocLLMParser

# Confluence
confluence_config = {
    "url": "https://your-domain.atlassian.net/wiki",
    "token": "your-token"
}
confluence = ConfluenceDocs(confluence_config)
confluence.connect()
documents = confluence.fetch_documents(space_key="SPACE")

# 飞书
feishu_config = {
    "url": "https://open.feishu.cn",
    "token": "your-token"
}
feishu = FeishuDocs(feishu_config)
feishu.connect()
documents = feishu.fetch_documents(space_id="your-space-id")

# DocLLM解析器
from git_deep_analyzer.ai import OpenAIClient
ai_client = OpenAIClient({"api_key": "your-api-key", "model": "gpt-4"})
doc_parser = DocLLMParser(ai_client)
parsed_doc = doc_parser.parse_document(document)
```

#### AI分析

```python
from git_deep_analyzer.ai import TechnicalAnalyzer, BusinessAnalyzer, EvolutionAnalyzer
from git_deep_analyzer.ai import OpenAIClient

ai_client = OpenAIClient({"api_key": "your-api-key", "model": "gpt-4"})

# 技术维度分析
tech_analyzer = TechnicalAnalyzer(ai_client)
tech_results = tech_analyzer.analyze(
    code="source code here",
    language="python",
    dimensions=["quality", "patterns", "performance"]
)

# 业务维度分析
business_analyzer = BusinessAnalyzer(ai_client)
business_results = business_analyzer.analyze(
    requirements="Requirements document here",
    code="source code here",
    language="python"
)

# 演进维度分析
evolution_analyzer = EvolutionAnalyzer(ai_client)
evolution_results = evolution_analyzer.analyze(
    commits=[...],  # CommitData list
    timeline_data=[...]
)
```

### 报告生成

```python
from git_deep_analyzer.reporting import HTMLGenerator, MarkdownGenerator, DataVisualizer

# HTML报告
html_gen = HTMLGenerator()
html_report = html_gen.generate(report_data)
with open("report.html", "w") as f:
    f.write(html_report)

# Markdown报告
md_gen = MarkdownGenerator()
md_report = md_gen.generate(report_data)
with open("report.md", "w") as f:
    f.write(md_report)

# 数据可视化
visualizer = DataVisualizer()
charts_html = visualizer.export_to_html([chart1, chart2, chart3])
```

## 数据模型

### Issue模型

```python
@dataclass
class Issue:
    id: str
    key: str  # 如 PROJ-123
    summary: str
    description: str
    status: IssueStatus  # BACKLOG, TODO, IN_PROGRESS, IN_REVIEW, DONE, CLOSED, CANCELLED
    priority: IssuePriority  # CRITICAL, HIGH, MEDIUM, LOW, LOWEST
    labels: List[str]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]
    reporter: str
    reporter_email: str
    assignee: Optional[str]
    assignee_email: Optional[str]
    comments: List[IssueComment]
    attachments: List[IssueAttachment]
    relations: List[IssueRelation]
    project_key: str
    project_name: str
```

### Document模型

```python
@dataclass
class Document:
    id: str
    title: str
    content: str
    type: DocumentType  # REQUIREMENT, DESIGN, SPEC, GUIDE, API, OTHER
    created_at: datetime
    updated_at: datetime
    author: str
    author_email: str
    space_key: Optional[str]
    folder_id: Optional[str]
    url: Optional[str]
    requirements: List[dict]  # LLM解析结果
```

## 分析维度

### 技术维度

- **代码质量分析**
  - 命名规范
  - 代码复杂度
  - 重复代码检测
  - 代码覆盖率

- **设计模式识别**
  - 单例模式
  - 工厂模式
  - 观察者模式
  - 策略模式
  - 等其他设计模式

- **并发分析**
  - 线程使用
  - 锁机制
  - async/await模式

- **性能分析**
  - 时间/空间复杂度
  - I/O优化
  - 算法效率

- **架构分析**
  - 代码组织
  - 耦合度
  - 内聚度

### 业务维度

- **需求提取**
  - 功能性需求
  - 非功能性需求
  - 优先级识别
  - 依赖关系
  - 验收标准

- **需求实现对齐**
  - 已实现需求
  - 部分实现需求
  - 缺失需求
  - 覆盖率分析
  - 额外功能

- **规格合规性**
  - API契约合规性
  - 数据格式合规性
  - 错误处理合规性
  - 性能要求合规性

- **业务目标识别**
  - 业务目标和目的
  - 目标-功能映射
  - 成功指标
  - 缺失功能

### 演进维度

- **时间线分析**
  - 开发阶段识别
  - 活动模式分析

- **影响分析**
  - 变更范围分析
  - 风险评估

- **技术债务识别**
  - 代码债务分类
  - 债务优先级

## 错误处理

### 常见错误

```python
# 连接失败
raise RuntimeError("Failed to connect to GitLab API")

# 认证失败
raise RuntimeError("GitLab API error: 401 Unauthorized")

# 配置错误
raise ValueError("project_id_or_path is required")

# API密钥缺失
raise ImportError("openai package is required. Install with: pip install openai")
```

### 重试机制

```python
from git_deep_analyzer.ai.retry_handler import retry

@retry(max_retries=3, base_delay=1.0, failure_behavior="continue")
def api_call():
    # 可能失败的API调用
    pass

# 自动重试最多3次
result = api_call()
```

## 性能优化

### 并发解析

```python
from concurrent.futures import ThreadPoolExecutor

def parse_files_parallel(file_paths):
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(parse_file, file_paths))
    return results
```

### 缓存机制

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_operation(key):
    # 结果会被缓存
    return compute_result(key)
```

## 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_gitlab_tracker.py -v

# 测试覆盖率
pytest --cov=src/git_deep_analyzer --cov-report=html
```

## 生产部署

### 自动化部署

```bash
sudo bash scripts/deploy_production.sh
```

### 手动部署

详见 `docs/DEPLOYMENT.md`

### 服务管理

```bash
# 启动服务
sudo systemctl start gitanalyzer

# 停止服务
sudo systemctl stop gitanalyzer

# 重启服务
sudo systemctl restart gitanalyzer

# 查看状态
sudo systemctl status gitanalyzer

# 查看日志
sudo journalctl -u gitanalyzer -f

# 启用定时任务
sudo systemctl start gitanalyzer.timer
```

## 常见问题

### Q: 如何选择AI提供商？

A: 根据你的需求选择：
- `openai`: 使用OpenAI GPT模型
- `anthropic`: 使用Anthropic Claude模型
- `claude_cli`: 使用本地Claude CLI工具
- `codex_cli`: 使用本地Codex CLI工具

### Q: 如何处理大仓库？

A:
- 使用时间范围限制分析范围
- 使用`--since`和`--until`参数
- 只分析指定分支

### Q: 如何提高分析速度？

A:
- 使用并行执行策略：`execution_strategy: parallel`
- 增加重试超时时间
- 使用缓存（如需实现）

### Q: 如何自定义报告？

A:
1. 创建自定义Jinja2模板
2. 在配置中指定模板路径
3. 使用`generate_with_template()`方法

## 许可证

Apache 2.0 License

## 支持

- GitHub Issues: [CodeKeeper Issues](https://github.com/njucslqq/CodeKeeper/issues)
- 文档: [Project README](https://github.com/njucslqq/CodeKeeper#readme)
