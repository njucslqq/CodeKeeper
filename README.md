# Git Deep Analyzer

AI-powered deep analysis of git repositories.

## Features

- Multi-language code analysis (C++, Python, and more)
- Integration with external systems (Jira, GitLab, Confluence, Feishu)
- AI-driven technical, business, and evolution analysis
- Multiple output formats (HTML, Markdown)
- Interactive reports with visualization

## Installation

```bash
pip install -e .
```

## Usage

Basic usage:

```bash
git-deep-analyze --repo /path/to/repo --since "2024-01-01"
```

With all options:

```bash
git-deep-analyze \
  --repo /path/to/repo \
  --branch main \
  --since "2024-01-01" \
  --until "2024-12-31" \
  --format html,markdown \
  --ai-provider openai \
  --ai-model gpt-4o
```

## Configuration

Create a `config.yaml` file:

```yaml
analysis:
  git:
    repo_path: /path/to/repo
    branch: main
    time_filter:
      mode: date_range
      date_range:
        since: "2024-01-01"

ai:
  enabled: true
  provider:
    type: api
    name: openai
    model: gpt-4o
    api_key: ${OPENAI_API_KEY}

reporting:
  language: zh-CN
  detail_level: standard
```

## Development

Run tests:

```bash
python3 -m pytest
```

## License

MIT
