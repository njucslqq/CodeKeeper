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
prompt = template.render(
    code=code_content,
    language="cpp",
    context={"file_path": "src/core/engine.cpp"}
)
```

## Template Variables

Common variables available in templates:
- `code` - Code content to analyze
- `language` - Programming language
- `context` - Additional context (file_path, function_name, etc.)
- `commit_message` - Commit message
- `code_diff` - Code diff
- `document_content` - Document content

## Extending

To add new templates:
1. Create a new `.txt` file in the appropriate `templates/` subdirectory
2. Use Jinja2 syntax for variables: `{{ variable_name }}`
3. Return structured output in JSON format for easier parsing

## Output Format

All templates should return JSON for consistent parsing:
```json
{
  "field1": "value1",
  "field2": {
    "nested": "value2"
  }
}
```
