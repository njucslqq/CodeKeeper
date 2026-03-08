# 测试策略

## �认的测试环境

### 1. GitHub测试环境
- 仓库：/Users/vincent/ai/openclaw（真实仓库）
- 认证：使用真实GitHub API需要：
  - GITHUB_TOKEN 环境变量
  - 或者本地 ~/.config/gh/hosts.yml 中配置token
- 测试范围：
  - Issue/PR列表获取
  - Issue详情获取
  - 评论获取
  - 鉴权验证
- 不测试：不需要真实环境的部分（mock即可）

### 2. Feishu测试环境
- 认证：使用Feishu API需要：
  - FEISHU_APP_ID 环境变量
  - FEISHU_APP_SECRET 环境变量
- 测试范围：
  - 文档列表获取
  - 文档内容获取
- 不测试：mock即可

### 3. AI测试环境
- 认证：使用Claude CLI需要：
  - ANTHROPIC_API_KEY 环境变量
- 测试范围：
  - 技术分析
  - 业务分析
  - 演进分析
  - 模板管理器
  - 重试处理器
- 真实配置：使用mock响应模拟API调用

## 测试实施计划

### Phase 1: 清理和确认

#### 任务1.1：删除废弃测试文件
- [ ] 查找并删除重复的测试文件
- [ ] 确认当前使用的测试文件列表

#### 任务1.2：确认核心依赖
- [ ] 确认GitPython在requirements.txt中
- [ ] 确认pytest、cov等测试工具

#### 任务1.3：确认测试环境
- [ ] 确认GitHub仓库路径：/Users/vincent/ai/openclaw
- [ ] 确认Claude CLI可用性

#### 任务1.4：制定详细测试计划
- [ ] 每个模块的测试优先级
- [ ] 确定外部服务集成测试策略

### Phase 2: 单元测试完善

#### 任务2.1：Issue模型测试
- [x] test_issue_tracker.py（已完成）
- [ ] 边界情况测试
- [ ] 空常情况处理

#### 任务2.2：报告生成测试
- [x] test_html_generator.py
- [x] test_markdown_generator.py
- [x] test_data_visualizer.py
- [x] test_template_manager.py
- [ ] test_report_models.py

#### 任务2.3：配置测试
- [x] test_config_errors.py
- [x] test_config_interactive.py
- [x] test_edge_cases.py

#### 任务2.4：分析器测试
- [x] test_technical_analyzer.py
- [x] test_analysis_strategy.py
- [x] test_business_analyzer.py
- [x] test_evolution_analyzer.py
- [x] test_ai_client.py

#### 任务2.5：工具类测试
- [x] test_retry_handler.py
- [ ] 扩充边界情况测试

### Phase 3：集成测试

#### 任务3.1：GitHub Tracker集成测试（真实API）
- [ ] 创建test_github_tracker_real.py
- [ ] 使用/openclaw仓库
- [ ] 需要GITHUB_TOKEN环境变量
- [ ] 测试：Issue列表、评论、详情获取
- [ ] 不测试：认证失败、网络错误等

#### 任务3.2：Feishu文档测试（真实API）
- [ ] 创建test_feishu_docs_real.py
- [ ] 使用真实API
- [ ] 需要FEISHU相关环境变量
- [ ] 测试：文档列表、内容获取

#### 任务3.3：AI分析器测试（mock API）
- [ ] 创建test_ai_analyzers_mock.py
- [ ] 使用真实Claude CLI
- [ ] 测试：技术、业务、演进分析
- [ ] mock AI API响应

### Phase 4：文档更新

#### 任务4.1：更新README
- [ ] 添加测试运行说明
- [ ] 添加测试覆盖率目标
- [ ] 添加贡献指南

#### 任务4.2：更新docs/todo-remaining-features.md
- [ ] 记录测试进展
- [ ] 标记待完成功能

#### 任务4.3：创建testing-progress.md
- [ ] 持续跟踪测试覆盖率

### Phase 5：覆盖率目标

- **短期目标（1周）**：80%覆盖率
- **中期目标（1个月）**：85%覆盖率
- **长期目标（持续）**：90%+覆盖率

## 测试文件清单

### 单元测试（已实现）
- [x] test_issue_tracker.py
- [x] test_technical_analyzer.py
- [x] test_html_generator.py
- [x] test_markdown_generator.py
- [x] test_report_models.py
- [x] test_analysis_strategy.py
- [x] test_business_analyzer.py
- [x] test_evolution_analyzer.py
- [x] test_time_analyzer.py
- [x] test_diff_extractor.py
- [x] test_language_detector.py
- [x] test_ai_client.py
- [x] test_data_visualizer.py
- [x] test_template_manager.py
- [x] test_multi_detail_reports.py
- [x] test_report_interactions.py
- [x] test_retry_handler.py
- [x] test_config_errors.py
- [x] test_edge_cases.py

### 边界情况测试（已实现）
- [x] test_edge_cases.py

### 集成测试（待创建）
- [ ] test_gitcollector_integration.py（真实Git仓库）
- [ ] test_github_tracker_real.py（真实API）
- [ ] test_feishu_docs_real.py（真实API）
- [ ] test_ai_analyzers_mock.py（Claude CLI）
