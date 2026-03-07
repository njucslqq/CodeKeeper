import click
from pathlib import Path
from typing import Optional
from .config import (
    Config, GitConfig, OutputConfig, AnalysisConfig,
    AIProviderConfig, AIConfig, ReportingConfig
)


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

    time_basis = click.prompt(
        "时间基准",
        type=click.Choice(["author_time", "commit_time", "merge_time"]),
        default="author_time"
    )

    # AI配置
    ai_enabled = click.confirm("启用AI分析？", default=True)

    ai_provider = "openai"
    ai_model = "gpt-4o"
    api_key = None

    if ai_enabled:
        ai_provider = click.prompt(
            "AI提供商",
            type=click.Choice(["openai", "anthropic"]),
            default="openai"
        )
        ai_model = click.prompt("AI模型", default="gpt-4o")
        api_key_input = click.prompt("API Key (留空使用环境变量)", default="", show_default=False)
        api_key = api_key_input if api_key_input else None

    # 报告配置
    formats_input = click.prompt(
        "输出格式 (逗号分隔)",
        default="html,markdown"
    )
    formats = [f.strip() for f in formats_input.split(",")]

    report_language = click.prompt(
        "报告语言",
        type=click.Choice(["zh-CN", "en"]),
        default="zh-CN"
    )

    # 创建配置
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
                api_key=api_key
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
