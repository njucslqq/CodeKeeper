# 部署指南

本文档说明如何部署和使用 Git Deep Analyzer。

## 环境要求

### Python 版本
- Python 3.11 或更高

### 操作系统
- Linux / macOS / WSL
- Windows 10 或更高（使用 WSL2）

### 依赖
**核心依赖：**
- GitPython >= 3.1.40
- Jinja2 >= 3.1.2
- openai >= 1.0.0 或 anthropic >= 0.18.0
- requests >= 2.31.0
- PyYAML >= 6.0.0
- aiohttp >= 3.9.0
- joblib >= 1.3.0

**可选依赖：**
- libclang >= 16.0.0（用于C++代码解析）

## 安装步骤

### 1. 克隆仓库

```bash
git clone git@github.com:njucslqq/CodeKeeper.git
cd CodeKeeper
```

### 2. 创建虚拟环境（推荐）

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
# 基础安装
pip install -e .

# 完整安装（包含C++支持）
pip install -e ".[cpp]"

# 开发安装（包含测试工具）
pip install -e ".[dev, cpp]"
```

### 4. 验证安装

```bash
# 检查是否安装成功
git-deep-analyze --version

# 或
python3 -c "import git_deep_analyzer; print('OK')"
```

## 配置

### 方式1：配置文件（推荐）

1. 复制示例配置：
```bash
cp config.yaml.example .git-deep-analyzer.yaml
```

2. 编辑配置文件：
```bash
vim .git-deep-analyzer.yaml  # 或使用其他编辑器
```

3. 关键配置项：
   - `git.repo_path`: Git仓库路径
   - `analysis.ai_provider`: openai 或 anthropic
   - `analysis.ai_model`: AI模型名称
   - `external.jira.url`/`token`: Jira服务器和认证
   - `external.confluence.url`/`token`: Confluence服务器和认证
   - `external.feishu.user_access_token`: 飞书认证（如使用）

### 方式2：环境变量

```bash
# OpenAI API密钥
export OPENAI_API_KEY="your-api-key-here"

# Anthropic API密钥
export ANTHROPIC_API_KEY="your-api-key-here"

# Jira认证
export JIRA_TOKEN="your-jira-token"

# Confluence认证
export CONFLUENCE_TOKEN="your-confluence-token"

# 飞书认证
export FEISHU_USER_ACCESS_TOKEN="your-feishu-token"
```

### 方式3：命令行参数

```bash
git-deep-analyze analyze \
  --repo /path/to/repo \
  --branch main \
  --ai-provider openai \
  --ai-model gpt-4 \
  --format html \
  --detail-level standard
```

## 运行分析

### 基本用法

```bash
# 分析当前目录的Git仓库
git-deep-analyze analyze

# 分析指定仓库
git-deep-analyze analyze --repo /path/to/repo

# 指定分支和时间范围
git-deep-analyze analyze \
  --repo /path/to/repo \
  --branch main \
  --since "2024-01-01" \
  --until "2024-12-31"
```

### 集成外部系统

```bash
# 集成Jira和Confluence
git-deep-analyze analyze \
  --repo /path/to/repo \
  --jira-url https://your-domain.atlassian.net \
  --confluence-url https://your-domain.atlassian.net/wiki
```

### 指定输出

```bash
# 生成HTML报告
git-deep-analyze analyze \
  --repo /path/to/repo \
  --format html \
  --output ./reports/my-report.html

# 生成Markdown报告
git-deep-analyze analyze \
  --repo /path/to/repo \
  --format markdown \
  --output ./reports/my-report.md

# 指定详细程度
git-deep-analyze analyze \
  --repo /path/to/repo \
  --detail-level concise   # 简洁版
  # 或
  --detail-level standard  # 标准版
  # 或
  --detail-level detailed  # 详细版
```

## 运行测试

### 使用测试脚本

```bash
# 运行所有测试
./scripts/run_tests.sh

# 查看覆盖率报告
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### 直接使用pytest

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=src/git_deep_analyzer --cov-report=html

# 只运行单元测试
pytest -m unit

# 运行特定测试
pytest tests/test_git_collector.py

# 运行特定测试方法
pytest tests/test_git_collector.py::TestGitCollector::test_collect_commits
```

## 已知问题和解决方案

### 问题1：GitPython未安装

**症状：**
```
ModuleNotFoundError: No module named 'git'
```

**解决方案：**
```bash
pip install GitPython>=3.1.40
```

### 问题2：C++代码解析失败

**症状：**
```
RuntimeError: C++ parsing requires clang/libclang
```

**解决方案：**

**macOS:**
```bash
brew install llvm
```

**Ubuntu/Debian:**
```bash
sudo apt-get install clang libclang-dev
```

**CentOS/RHEL:**
```bash
sudo yum install clang-devel
```

或跳过C++代码：
```bash
# 在配置中指定要分析的语言
languages:
  primary: [python, javascript]
  fallback: auto
```

### 问题3：AI API密钥无效

**症状：**
```
RuntimeError: Invalid API key
```

**解决方案：**
1. 检查环境变量是否正确设置：
```bash
echo $OPENAI_API_KEY
```

2. 在配置文件中使用环境变量：
```yaml
analysis:
  ai_provider: openai
  ai_model: gpt-4
  api_key: ${OPENAI_API_KEY}
```

### 问题4：外部系统连接失败

**症状：**
```
RuntimeError: Failed to connect to Jira/Confluence
```

**解决方案：**

1. 检查URL是否正确
2. 检查Token是否有效
3. 检查网络连接
4. 查看日志文件获取详细错误信息

```bash
# 查看日志
tail -f git-deep-analyzer.log
```

## 故障排查

### 1. 启用调试日志

编辑配置文件：
```yaml
logging:
  level: debug
  log_to_console: true
  log_to_file: true
```

### 2. 检查Git仓库

```bash
# 验证仓库是否有效
git -C /path/to/repo status

# 检查是否有提交
git -C /path/to/repo log --oneline | head -5
```

### 3. 验证AI API连接

```bash
# 测试OpenAI连接
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models

# 或使用Python
python3 -c "
import openai
client = openai.OpenAI(api_key='$OPENAI_API_KEY')
models = client.models.list()
print('OK' if models else 'FAIL')
"
```

### 4. 检查磁盘空间

```bash
# 检查可用空间
df -h

# 检查报告目录空间
du -sh reports/
```

## 性能优化建议

### 1. 使用增量分析

只分析变更的文件，节省时间和AI调用：

```yaml
analysis:
  execution_strategy: incremental
```

### 2. 使用并行分析

同时运行多个分析器（需要足够的AI API配额）：

```yaml
analysis:
  execution_strategy: parallel
```

### 3. 调整详细程度

对于大型仓库，使用简洁或标准详细程度：

```yaml
reporting:
  detail_level: standard  # 或 concise
```

### 4. 限制分析范围

只分析特定时间段或特定目录：

```yaml
git:
  time_range:
    since: "2024-06-01"
    until: "2024-12-31"
```

## 生产环境部署

### 1. 使用系统级安装

```bash
sudo pip3 install -e .
```

### 2. 配置服务账户

```bash
# 创建服务账户
sudo useradd -m -s /bin/bash gitanalyzer

# 配置环境变量
sudo vim /etc/gitanalyzer.env
```

### 3. 创建systemd服务（Linux）

创建 `/etc/systemd/system/gitanalyzer.service`:
```ini
[Unit]
Description=Git Deep Analyzer
After=network.target

[Service]
Type=simple
User=gitanalyzer
WorkingDirectory=/opt/git-deep-analyzer
EnvironmentFile=/etc/gitanalyzer.env
ExecStart=/opt/git-deep-analyzer/venv/bin/git-deep-analyze analyze
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

启用服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable gitanalyzer
sudo systemctl start gitanalyzer
```

### 4. 定时任务

使用cron定期运行：
```bash
# 编辑crontab
crontab -e

# 添加定时任务（每天凌晨2点运行）
0 2 * * * cd /opt/git-deep-analyzer && ./venv/bin/git-deep-analyze analyze >> /var/log/gitanalyzer.log 2>&1
```

## 支持与反馈

- 查看文档：`docs/`
- 查看示例：`config.yaml.example`
- 报告问题：在 GitHub 提交 Issue
- 查看日志：`git-deep-analyzer.log`
