# Issue Deep Analyzer 项目进展

## 版本历史

### v0.1.0 (2026-03-10)

## 实施进度

### ✅ 已完成
- 需求分析和确认
- PRD 需求文档创建（117 个需求点）
- 实施计划创建（6 个阶段详细规划）
- Q1-Q5 选择确认
- PRD 文档更新（反映正确的选择）
- P0: 核心基础设施（已完成）
- P1: 数据获取能力（已完成）

### 🔄 进行中
- 无

### 📋 后续计划
- P2: Prompt 配置与 LLM（Prompt 系统 + Claude CLI 集成）
- P3: 核心分析能力（业务 + 技术 + 流程维度）
- P4: 并发与输出管理（WebSocket + 报告生成）
- P5: 测试与优化（先构建完整框架后统一测试，覆盖率 85%+）
- P6: 部署支持（先本地运行，Docker + K8s 后续）

## 📋 需求清单

详见 `docs/plans/2026-03-09-issue-deep-analyzer-prd.md`（117 个需求点）

### 关键架构决策

- **服务类型**: FastAPI Web 服务
- **LLM 调用优先级**: Claude CLI > CodeX CLI > OpenAI API > Anthropic API
- **初始支持**:
  - Git 仓库: GitHub + GitLab (Q1=B 选择)
  - 文档系统: Confluence + 飞书 + Jira (Q2=C 选择，包含 Issue 数据)
  - LLM 调用: 优先 Claude CLI (Q5 新增)
- **测试策略**: 先构建完整框架后统一进行测试 (Q3=B 选择)
- **部署优先级**: 先本地运行，Docker 和 K8s 后续 (Q4 选择)
- **计划粒度**: 完整的 bite-sized 计划 (Q5=A 选择)

### 扩展机制

- **插件系统**: 目录扫描，独立运行
- **Prompt 自定义**: Markdown 格式，支持用户扩展
- **Git 仓库扩展**: 可注册新的仓库类型
- **文档系统扩展**: 可注册新的文档系统
- **分析维度扩展**: 可注册新的分析维度
- **子维度扩展**: 可注册新的子维度

---

## 📌 技术栈

- FastAPI（Web 服务）
- Python 3.9+
- OpenAI/Anthropic SDK
- asyncio（异步）
- websockets（WebSocket）
- prometheus_client（监控）
- uvicorn（ASGI 服务器）
- GitPython
- python-gitlab
- Jinja2（模板引擎）

---

## ✅ 已完成阶段：P0 核心基础设施

**完成时间**: 2026-03-09

### 任务列表（6 个任务，全部完成）

| 任务 | 描述 | 状态 |
|------|------|------|
| 0.1 | 项目结构与依赖配置 | ✅ 完成 |
| 0.2 | 配置管理系统 | ✅ 完成 |
| 0.3 | 数据模型（Issue, Commit, Document, Analysis） | ✅ 完成 |
| 0.4 | 日志系统（支持任务上下文） | ✅ 完成 |
| 0.5 | 健康检查端点（/health） | ✅ 完成 |
| 0.6 | 监控指标（Prometheus + Telemetry） | ✅ 完成 |

### P0 详细文档

见 `docs/plans/2026-03-09-issue-deep-analyzer-implementation.md` 中的 P0 部分。

### P0 测试结果

- 测试数量: 14 个
- 通过率: 100%
- 代码覆盖率: 92%

---

## ✅ 已完成阶段：P1 数据获取能力

**完成时间**: 2026-03-10

### 任务列表（10 个任务，全部完成）

| 任务 | 描述 | 状态 |
|------|------|------|
| 1.1 | Git 仓库基础架构 | ✅ 完成 |
| 1.2 | GitHub 客户端实现 | ✅ 完成 |
| 1.3 | GitLab 客户端实现 | ✅ 完成 |
| 1.4 | 仓库列表获取机制 | ✅ 完成 |
| 1.5 | Commit 消息解析器 | ✅ 完成 |
| 1.6 | 文档系统基础架构 | ✅ 完成 |
| 1.7 | Confluence 客户端实现 | ✅ 完成 |
| 1.8 | 飞书客户端实现 | ✅ 完成 |
| 1.9 | 文档命名解析器 | ✅ 完成 |
| 1.10 | Issue 信息获取接口 | ✅ 完成 |

### P1 测试结果

- 测试数量: 17 个
- 通过率: 100%

### P1 实现内容

- GitClient 抽象基类
- GitCollector 多仓库收集器
- GitHubClient 完整实现
- GitLabClient 完整实现
- 仓库配置文件解析
- Submodule 仓库扫描
- CommitParserRegistry 解析器注册机制
- 内置 GitHub/GitLab/通用解析器
- DocClient 抽象基类
- DocCollector 多系统文档收集器
- ConfluenceClient 完整实现
- FeishuClient 完整实现
- DocNameParserRegistry 命名解析器注册机制
- GitHubIssueClient/GitLabIssueClient/JiraIssueClient 完整实现

---

## 📊 需求统计

| 分类 | 需求数量 |
|--------|---------|
| 服务与配置 | 14 |
| 请求参数（API 调用） | 6 |
| 数据获取 | 14 | (+1, 新增 Jira) |
| 并发与输出管理 | 17 |
| Prompt 配置与 LLM 分析 | 11 |
| 核心部分（深度分析） | 8 |
| 架构部分（系统设计） | 31 |
| 部署部分 | 12 |
| 进展记录 | 4 |
| **总计** | **117** | (+2, 新增 Jira 和) |

---

## 🎯 下一步：P2 Prompt 配置与 LLM

**P2 Prompt 配置与 LLM** 包含的任务：
1. Prompt 模板系统
2. Claude CLI 集成（优先）
3. Prompt 自定义支持
4. LLM 调用抽象
5. 降级策略实现

**预期成果**:
- Prompt 模板管理（Markdown + Jinja2）
- Claude CLI 调用实现
- OpenAI/Anthropic API 回退
- LLM 抽象接口
- 降级和重试机制
