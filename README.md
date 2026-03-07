# Git Deep Analyzer

基于AI驱动的Git提交深度分析工具，提供技术、业务和演进三个维度的深度洞察。

## 功能特性

### 核心功能
- ✅ Git仓库采集和代码分析
- ✅ 多语言支持（Python、C++、JavaScript等20+种语言）
- ✅ AI驱动的智能分析（技术质量、业务价值、演进趋势）
- ✅ 多格式报告生成（HTML、Markdown）
- ✅ 数据可视化（折线图、饼图、柱状图、热力图等）
- ✅ 外部系统集成（Jira、Confluence）

### AI分析维度

#### 技术维度
- 代码质量分析（命名规范、复杂度、重复代码）
- 设计模式识别（单例、工厂、观察者等）
- 并发分析（线程、锁、async/await）
- 性能分析（时间/空间复杂度、I/O优化）
- 架构分析（代码组织、耦合度、内聚度）

#### 业务维度
- 需求提取（功能性、非功能性需求）
- 需求实现对齐（覆盖率、差距分析）
- 规格合规性（API规范、数据格式）
- 业务目标分析（目标-功能映射）

#### 演进维度
- 时间线分析（开发阶段、活动模式）
- 影响分析（变更范围、风险评估）
- 技术债务识别（代码债务分类）

### 报告功能
- 多详细程度支持（简洁/标准/详细）
- 交互功能（搜索、过滤、折叠展开）
- 响应式设计（支持移动端）
- 数据可视化（Chart.js集成）

## 安装

### 基础安装

```bash
pip install -e .
```

### 完整安装（包含C++支持）

```bash
pip install -e ".[cpp]"
```

### 开发安装

```bash
pip install -e ".[dev, cpp]"
```

## 配置

### 快速开始

```bash
# 初始化配置文件
git-deep-analyze init

# 分析Git仓库
git-deep-analyze analyze --repo /path/to/repo --branch main
```

### 配置文件

创建 `.git-deep-analyzer.yaml`：

```yaml
git:
  repo_path: /path/to/repo
  branch: main
  time_range:
    since: "2024-01-01"
    until: "2024-12-31"
  time_basis: author_time

analysis:
  ai_provider: openai
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

output:
  format: html
  detail_level: standard
  output_dir: ./reports
```

### AI API配置

**OpenAI:**
```bash
export OPENAI_API_KEY="your-api-key"
```

**Anthropic (Claude):**
```bash
export ANTHROPIC_API_KEY="your-api-key"
```

### 外部系统认证

**Jira:**
```bash
export JIRA_TOKEN="your-personal-access-token"
# 或
export JIRA_USERNAME="your-email"
export JIRA_PASSWORD="your-api-token"
```

**Confluence:**
```bash
export CONFLUENCE_TOKEN="your-personal-access-token"
```

## 使用示例

### 基本分析

```bash
git-deep-analyze analyze \
  --repo /path/to/repo \
  --branch main \
  --since "2024-01-01"
```

### 指定输出格式

```bash
git-deep-analyze analyze \
  --repo /path/to/repo \
  --format html \
  --detail-level detailed \
  --output ./reports/my-report.html
```

### 集成外部系统

```bash
git-deep-analyze analyze \
  --repo /path/to/repo \
  --jira-url https://your-domain.atlassian.net \
  --confluence-url https://your-domain.atlassian.net/wiki
```

## 测试

```bash
# 安装测试依赖
pip install -e ".[dev, cpp]"

# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=src/git_deep_analyzer --cov-report=html

# 只运行单元测试
pytest -m unit

# 运行特定测试
pytest tests/test_git_collector.py -v
```

## 项目结构

```
git_deep_analyzer/
├── ai/                    # AI分析层
│   ├── clients.py          # AI客户端（OpenAI、Anthropic）
│   ├── technical_analyzer.py    # 技术维度分析
│   ├── business_analyzer.py     # 业务维度分析
│   ├── evolution_analyzer.py     # 演进维度分析
│   ├── retry_handler.py         # 错误处理和重试
│   ├── logger.py                # 日志记录
│   └── analysis_strategy.py      # 分析执行策略
├── git_collector/          # Git采集层
│   ├── collector.py        # Git仓库采集
│   ├── time_analyzer.py    # 时间分析
│   └── diff_extractor.py   # 差异提取
├── code_parser/           # 代码解析层
│   ├── parser_python.py    # Python解析器
│   ├── parser_cpp.py      # C++解析器
│   ├── pattern_matcher.py  # 设计模式匹配
│   └── concurrency_detector.py  # 并发检测
├── integrations/          # 外部系统集成
│   ├── issue_tracker/     # Issue跟踪器（Jira）
│   ├── docs/             # 文档系统（Confluence）
│   └── issue_commit_linker.py  # Issue-Commit关联
├── reporting/            # 报告生成层
│   ├── html_generator.py   # HTML报告
│   ├── markdown_generator.py  # Markdown报告
│   ├── data_visualizer.py     # 数据可视化
│   └── multi_detail_reports.py # 多详细程度报告
├── config/               # 配置管理
│   ├── config.py         # 配置模型和加载
│   └── cli.py           # CLI命令
└── cli.py              # 主CLI入口
```

## 开发指南

### 代码规范

```bash
# 格式化代码
black src/ tests/

# 排序导入
isort src/ tests/

# 类型检查
mypy src/

# 代码检查
ruff check src/
```

### 添加新的分析器

1. 在 `ai/` 目录创建新的分析器类
2. 继承 `BaseAnalyzer`
3. 实现 `analyze()` 方法
4. 在对应的 `Analyzer` 类中注册

### 添加新的外部系统集成

1. 在 `integrations/issue_tracker/` 或 `integrations/docs/` 创建新的集成
2. 继承 `IssueTrackerBase` 或 `DocsSystemBase`
3. 实现必需的抽象方法

## 依赖

### 核心依赖
- GitPython >= 3.1.40 - Git仓库操作
- Jinja2 >= 3.1.2 - 模板引擎
- openai >= 1.0.0 - OpenAI API
- anthropic >= 0.18.0 - Anthropic API
- requests >= 2.31.0 - HTTP客户端
- aiohttp >= 3.9.0 - 异步HTTP

### 可选依赖
- libclang >= 16.0.0 - C++代码解析

### 开发依赖
- pytest >= 7.4.0 - 测试框架
- pytest-cov >= 4.1.0 - 覆盖率报告
- black >= 23.7.0 - 代码格式化
- isort >= 5.12.0 - 导入排序

## 已知限制

1. **C++解析**：需要安装 clang/libclang 才能完整解析C++代码
2. **外部系统认证**：需要有效的认证信息才能连接Jira/Confluence
3. **AI API**：需要有效的API密钥才能使用AI分析功能

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

Apache 2.0 License - 详见 [LICENSE](LICENSE) 文件

## 生产环境部署

### 自动化部署

项目包含自动化部署脚本，支持 Linux/macOS 系统：

```bash
# 克隆仓库
git clone git@github.com:njucslqq/CodeKeeper.git
cd CodeKeeper

# 运行部署脚本（需要 root 权限）
sudo bash scripts/deploy_production.sh
```

### 部署脚本功能

部署脚本会自动完成以下操作：

1. **安装系统依赖**：Python 3、Git、虚拟环境工具
2. **创建服务用户**：`gitanalyzer`
3. **安装仓库**：`/opt/git-deep-analyzer`
4. **配置虚拟环境**：自动创建和激活
5. **安装依赖**：包括可选的 C++ 支持包
6. **创建配置目录**：`/etc/gitanalyzer/`
7. **创建日志目录**：`/var/log/gitanalyzer`
8. **配置 systemd 服务**：`/etc/systemd/system/gitanalyzer.service`
9. **配置定时任务**：每天凌晨 2 点自动运行
10. **配置日志轮转**：自动管理日志文件

### 服务管理

```bash
# 启动服务
sudo systemctl start gitanalyzer

# 停止服务
sudo systemctl stop gitanalyzer

# 重启服务
sudo systemctl restart gitanalyzer

# 查看服务状态
sudo systemctl status gitanalyzer

# 查看服务日志
sudo journalctl -u gitanalyzer -f

# 启用定时任务
sudo systemctl start gitanalyzer.timer

# 禁用定时任务
sudo systemctl stop gitanalyzer.timer
```

### 配置文件

**环境变量文件**：`/etc/gitanalyzer/.env`

```bash
# 编辑环境配置
sudo vim /etc/gitanalyzer/.env

# 配置 AI API 密钥
OPENAI_API_KEY=your-key-here
# ANTHROPIC_API_KEY=your-key-here

# 配置外部系统认证
JIRA_TOKEN=your-jira-token
CONFLUENCE_TOKEN=your-confluence-token
```

**主配置文件**：`/etc/gitanalyzer/.git-deep-analyzer.yaml`

```bash
# 编辑主配置
sudo vim /etc/gitanalyzer/.git-deep-analyzer.yaml

# 指定要分析的仓库
git:
  repo_path: /path/to/your/repo
  branch: main

# 配置 AI 分析
analysis:
  ai_provider: openai  # 或 claude_cli, codex_cli
  ai_model: gpt-4

# 集成外部系统
external:
  jira:
    url: https://your-domain.atlassian.net
    token: ${JIRA_TOKEN}
  confluence:
    url: https://your-domain.atlassian.net/wiki
    token: ${CONFLUENCE_TOKEN}
```

### 手动部署

如需手动部署，请参考 `docs/DEPLOYMENT.md` 中的详细步骤。

### Docker 部署（可选）

如需使用 Docker 部署，请创建 `Dockerfile`：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    git \
    python3-pip

# 复制项目文件
COPY . /app

# 安装 Python 依赖
RUN pip3 install --no-cache-dir -e ".[cpp]"

# 创建非 root 用户
RUN useradd -m -s /bin/bash appuser

# 切换到非 root 用户
USER appuser

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["git-deep-analyze", "--help"]
```

```bash
# 构建镜像
docker build -t git-deep-analyzer .

# 运行容器
docker run -v /path/to/repo:/data \
  -v /path/to/config/.git-deep-analyzer.yaml:/config \
  git-deep-analyzer
```

---

EOF
cat /Users/vincent/ai/gcr/README.md