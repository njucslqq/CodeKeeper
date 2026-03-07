# Git Deep Analyzer 用户指南

## 目录

1. [快速开始](#快速开始)
2. [基本使用](#基本使用)
3. [配置详解](#配置详解)
4. [外部系统集成](#外部系统集成)
5. [报告使用](#报告使用)
6. [常见问题](#常见问题)
7. [高级功能](#高级功能)
8. [故障排查](#故障排查)

---

## 快速开始

### 1. 安装

```bash
# 克隆仓库
git clone git@github.com:njucslqq/CodeKeeper.git
cd CodeKeeper

# 安装依赖
pip install -e .

# 或安装包含C++支持的完整版本
pip install -e ".[cpp]"
```

### 2. 配置

```bash
# 初始化配置文件
git-deep-analyze init
```

这将创建一个 `.git-deep-analyzer.yaml` 配置文件模板。

### 3. 首次分析

```bash
# 分析当前目录的Git仓库
git-deep-analyze analyze --repo . --branch main
```

## 基本使用

### 分析本地仓库

```bash
# 分析当前目录
git-deep-analyze analyze

# 指定仓库路径
git-deep-analyze analyze --repo /path/to/project

# 指定分支
git-deep-analyze analyze --repo /path/to/project --branch develop

# 指定时间范围
git-deep-analyze analyze --repo /path/to/project --since "2024-01-01" --until "2024-03-31"
```

### 选择输出格式

```bash
# HTML报告（推荐，包含交互功能）
git-deep-analyze analyze --repo /path/to/project --format html

# Markdown报告
git-deep-analyze analyze --repo /path/to/project --format markdown

# 指定输出目录
git-deep-analyze analyze --repo /path/to/project --output ./reports
```

### 控制详细程度

```bash
# 简洁报告
git-deep-analyze analyze --detail-level concise

# 标准报告（默认）
git-deep-analyze analyze --detail-level standard

# 详细报告
git-deep-analyze analyze --detail-level detailed
```

## 配置详解

### Git配置

```yaml
git:
  repo_path: /path/to/repo        # Git仓库路径
  branch: main                      # 要分析的分支
  time_range:
    since: "2024-01-01"        # 开始日期（可选）
    until: null                     # 结束日期（可选，null=现在）
  time_basis: author_time           # 时间基准：author_time, commit_time, merge_time
```

### AI分析配置

```yaml
analysis:
  ai_provider: openai               # AI提供商：openai, anthropic, claude_cli, codex_cli
  ai_model: gpt-4                # AI模型名称
  dimensions:                      # 分析维度
    - technical                   # 技术维度
    - business                    # 业务维度
    - evolution                   # 演进维度
  execution_strategy: parallel       # 执行策略：serial, parallel, layered, incremental

  retry:
    max_retries: 3                 # 最大重试次数
    base_delay: 1.0               # 基础延迟（秒）
    max_delay: 60.0               # 最大延迟（秒）
    failure_behavior: retry          # 失败行为：retry, continue, abort, fallback
```

### 外部系统配置

```yaml
external:
  jira:
    url: https://your-domain.atlassian.net
    token: ${JIRA_TOKEN}        # Personal Access Token
    jql: "project = YOUR_PROJECT"  # JQL查询

  confluence:
    url: https://your-domain.atlassian.net/wiki
    token: ${CONFLUENCE_TOKEN}
    space_key: YOUR_SPACE          # 空间Key

  github:
    url: https://api.github.com   # 可选，默认为官方API
    token: ${GITHUB_TOKEN}

  gitlab:
    url: https://gitlab.com       # 可选
    token: ${GITLAB_TOKEN}

  # 飞书配置
  feishu:
    url: https://open.feishu.cn
    token: ${FEISHU_USER_ACCESS_TOKEN}
```

### 报告配置

```yaml
reporting:
  format: html                    # 输出格式：html, markdown
  detail_level: standard            # 详细程度：concise, standard, detailed
  output_dir: ./reports          # 输出目录
  filename_format: "{repo}-{branch}-{timestamp}.{ext}"  # 文件名格式

  interactive:
    enable_search: true          # 启用搜索功能
    enable_filter: true          # 启用过滤功能
    enable_collapse: true         # 启用折叠/展开
    enable_detail_switch: true    # 启用详细程度切换
```

### 日志配置

```yaml
logging:
  level: info                    # 日志级别：debug, info, warning, error
  log_to_console: true           # 输出到控制台
  log_to_file: true              # 输出到文件
  log_file: ./git-deep-analyzer.log  # 日志文件路径
  log_ai_requests: true         # 记录AI请求
  log_ai_responses: true        # 记录AI响应
  log_performance: true           # 记录性能指标
```

## 外部系统集成

### Jira集成

**前提条件**：
1. 拥有Jira账号和项目访问权限
2. 生成Personal Access Token（推荐）或使用Basic Auth

**配置步骤**：

```bash
# 方法1：Personal Access Token
export JIRA_TOKEN="your-personal-access-token"

# 方法2：Basic Auth
export JIRA_USERNAME="your-email@example.com"
export JIRA_PASSWORD="your-api-token"
```

**使用场景**：
- 跟踪功能需求和Bug
- 关联Git提交到Jira Issue
- 分析需求实现进度
- 生成需求覆盖率报告

### Confluence集成

**前提条件**：
1. 拥有Confluence访问权限
2. 生成Personal Access Token

**配置步骤**：

```bash
export CONFLUENCE_TOKEN="your-personal-access-token"
```

**使用场景**：
- 提取产品文档和设计文档
- 分析文档与代码的对应关系
- 检查规格合规性
- 生成文档覆盖分析

### GitHub集成

**前提条件**：
1. 拥有GitHub账号
2. 生成Personal Access Token

**配置步骤**：

```bash
export GITHUB_TOKEN="github_pat_xxxxxxxxxxxx"
```

**使用场景**：
- 分析开源项目
- 跟踪Issues和Pull Requests
- 生成Issue-Commit关联报告
- 分析PR审查质量

### GitLab集成

**前提条件**：
1. 拥有GitLab账号
2. 生成Personal Access Token

**配置步骤**：

```bash
export GITLAB_TOKEN="glpat-xxxxxxxxxxxxxx"
```

**使用场景**：
- 分析内部GitLab项目
- 跟踪Issues和Milestones
- 生成Issue-Commit关联报告
- 分析代码演进趋势

### 飞书集成

**前提条件**：
1. 拥有飞书账号
2. 获取User Access Token

**配置步骤**：

```bash
export FEISHU_USER_ACCESS_TOKEN="your-user-access-token"
```

**使用场景**：
- 提取飞书文档
- 分析业务目标和需求
- 生成需求-文档映射
- 智能需求提取

## 报告使用

### HTML报告

HTML报告提供完整的交互功能：

- **搜索功能**：在报告内搜索关键词
- **过滤功能**：按维度、状态、优先级过滤
- **折叠/展开**：展开/折叠章节查看详情
- **图表可视化**：折线图、饼图、柱状图、热力图、甘特图
- **多详细程度**：在报告内切换详细程度

**查看报告**：
```bash
# 在浏览器中打开
open reports/my-report.html

# 或使用Python HTTP服务器
python -m http.server 8000
# 访问 http://localhost:8000/reports/my-report.html
```

### Markdown报告

Markdown报告适合：

- 版本控制系统
- 文档集成
- CI/CD流程
- 在GitHub/GitLab/GitLab上直接查看

### 数据可视化

报告包含以下图表类型：

1. **折线图**：显示趋势（提交数量、代码复杂度变化等）
2. **饼图**：显示分布（优先级、状态、语言使用等）
3. **柱状图**：显示对比（作者贡献、维度得分等）
4. **热力图**：显示矩阵关系（文件-复杂度、时间-活动等）
5. **甘特图**：显示时间线（开发阶段、里程碑进度）

## 常见问题

### 安装问题

**Q: pip install失败，提示依赖错误**

A: 升级pip和setuptools：
```bash
pip install --upgrade pip setuptools
```

**Q: C++解析不支持**

A: 安装libclang：
```bash
# macOS
brew install llvm

# Linux (Ubuntu/Debian)
sudo apt-get install libclang-dev

# 验证安装
python -c "import clang; print('Clang installed')"
```

### 认证问题

**Q: API返回401 Unauthorized**

A: 检查认证信息：
1. 确认API密钥/Token正确
2. 检查环境变量是否正确设置
3. 检查配置文件中的认证配置

**Q: 环境变量不生效**

A: 检查配置文件中的引用：
```yaml
# 错误方式（直接使用变量名）
token: GITHUB_TOKEN

# 正确方式（使用${}引用环境变量）
token: ${GITHUB_TOKEN}
```

### 性能问题

**Q: 分析大仓库很慢**

A: 优化策略：
1. 使用时间范围限制：`--since`和`--until`
2. 使用并行执行策略：`execution_strategy: parallel`
3. 只分析特定分支
4. 增加重试超时时间

**Q: AI API调用超时**

A: 调整重试配置：
```yaml
analysis:
  retry:
    max_retries: 5           # 增加重试次数
    base_delay: 2.0          # 增加基础延迟
    max_delay: 120.0         # 增加最大延迟
```

### 输出问题

**Q: 报告没有生成**

A: 检查：
1. 输出目录是否存在且有写入权限
2. 配置的`output_dir`是否正确
3. 查看日志文件获取错误信息

**Q: HTML报告图表不显示**

A: 确保：
1. 使用Chart.js CDN可访问
2. 浏览器允许JavaScript执行
3. 查看浏览器控制台是否有错误

## 高级功能

### 并发分析

使用并行执行策略提升分析速度：

```yaml
analysis:
  execution_strategy: parallel  # 并行执行所有维度
```

### 分层分析

先执行基础分析，再执行高级分析：

```yaml
analysis:
  execution_strategy: layered  # 分层执行
```

### 增量分析

只分析变更的部分，提高增量更新速度：

```yaml
analysis:
  execution_strategy: incremental  # 增量执行
```

### 自定义AI提示词

创建自定义提示词模板：

```python
from git_deep_analyzer.ai import TemplateManager

# 创建提示词模板
template = TemplateManager()
custom_prompt = template.get_template("custom_analysis")
```

### DocLLM深度解析

使用LLM深度解析文档：

```python
from git_deep_analyzer.integrations.docs import DocLLMParser

# 需求提取
requirements = doc_parser.extract_requirements(document_content)

# 业务目标识别
goals = doc_parser.identify_goals(document_content)

# 需求-实现对齐
alignment = doc_parser.analyze_alignment(requirements, code, language)

# 规格合规性检查
compliance = doc_parser.analyze_compliance(spec, code, language)
```

## 故障排查

### 调试模式

启用调试日志获取详细信息：

```yaml
logging:
  level: debug  # 记录所有调试信息
  log_ai_requests: true  # 记录AI请求详情
  log_ai_responses: true  # 记录AI响应详情
  log_performance: true  # 记录性能指标
```

### 常见错误及解决方案

**错误：`FileNotFoundError: Repository path not found`**
- 解决：确认`repo_path`正确
- 解决：使用绝对路径或相对路径
- 解决：检查路径权限

**错误：`Not a git repository`**
- 解决：确认路径是Git仓库
- 解决：检查`.git`目录是否存在

**错误：`Failed to connect to API`**
- 解决：检查网络连接
- 解决：确认API URL正确
- 解决：验证认证信息

**错误：`OpenAI/Anthropic API error`**
- 解决：检查API密钥有效性
- 解决：确认账户余额
- 解决：检查模型名称

**错误：`Failed to parse JSON response`**
- 解决：AI响应格式异常
- 解决：重试请求
- 解决：查看日志中的完整响应

### 获取帮助

```bash
# 命令行帮助
git-deep-analyze --help

# 查看版本
git-deep-analyze --version
```

## 最佳实践

1. **使用环境变量管理密钥**：避免在配置文件中硬编码敏感信息
2. **配置时间范围**：对于大型仓库，使用时间范围限制分析范围
3. **选择合适的执行策略**：并行分析快但消耗更多资源，串行分析慢但资源占用少
4. **定期更新依赖**：保持依赖包为最新版本
5. **备份配置文件**：保存配置文件的备份
6. **审查报告**：生成报告后检查结果是否符合预期
7. **监控日志**：定期查看日志文件及时发现异常
8. **使用版本控制**：将配置文件纳入版本控制（除去敏感信息）

## 示例工作流

### 工作流1：日常分析

```bash
# 每天分析昨天的提交
yesterday=$(date -d "yesterday" +%Y-%m-%d)
git-deep-analyze analyze --repo /path/to/project --since "$yesterday" --until yesterday

# 自动化（添加到cron）
0 2 * * * /usr/bin/bash /path/to/analyze-daily.sh
```

### 工作流2：发布前分析

```bash
# 分析最近一个月的代码
one_month_ago=$(date -d "1 month ago" +%Y-%m-%d)
git-deep-analyze analyze --repo /path/to/project --since "$one_month_ago" \
  --format html --detail-level detailed
```

### 工作流3：集成Jira跟踪

```bash
# 配置Jira集成
export JIRA_TOKEN="your-token"

# 分析并生成报告
git-deep-analyze analyze --repo /path/to/project \
  --jira-url https://your-domain.atlassian.net

# 在Jira中查看Issue-Commit关联报告
```

## 获取支持

- GitHub Issues: [CodeKeeper Issues](https://github.com/njucslqq/CodeKeeper/issues)
- 文档: [Project README](https://github.com/njucslqq/CodeKeeper#readme)
- 部署指南: [DEPLOYMENT.md](DEPLOYMENT.md)
- API文档: [API.md](API.md)
