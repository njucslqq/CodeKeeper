"""CLI interface for git deep analyzer."""

import click
from pathlib import Path
from datetime import datetime
from .config import Config, GitConfig, AnalysisConfig, OutputConfig, AIProviderConfig, AIConfig, ReportingConfig


@click.group()
def main():
    """Git Deep Analyzer - AI-powered deep analysis of git repositories."""
    pass


@main.command()
@click.option(
    "--config", "-c",
    type=click.Path(exists=True, path_type=Path),
    default="config.yaml",
    help="Path to configuration file (default: config.yaml)"
)
@click.option(
    "--repo", "-r",
    type=click.Path(exists=True, path_type=Path),
    help="Override git repository path"
)
@click.option(
    "--branch", "-b",
    help="Override branch name"
)
@click.option(
    "--since",
    help="Override start date (YYYY-MM-DD)"
)
@click.option(
    "--until",
    help="Override end date (YYYY-MM-DD)"
)
@click.option(
    "--days",
    type=int,
    help="Override: last N days"
)
@click.option(
    "--time-basis",
    type=click.Choice(["author_time", "commit_time", "merge_time"]),
    help="Override time basis for commit filtering"
)
@click.option(
    "--format",
    help="Override output formats (comma-separated)"
)
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    help="Override output directory"
)
@click.option(
    "--ai-provider",
    type=click.Choice(["openai", "anthropic"]),
    help="Override AI provider"
)
@click.option(
    "--ai-model",
    help="Override AI model"
)
@click.option(
    "--ai-key",
    help="Override AI API key"
)
def analyze(config, repo, branch, since, until, days, time_basis, format, output_dir, ai_provider, ai_model, ai_key):
    """
    Analyze git repository with AI.

    Example:
        git-deep-analyze analyze --config config.yaml --repo /path/to/repo
    """
    # 加载配置文件
    click.echo(f"Loading config from: {config}")
    loaded_config = Config.load_from_file(config)

    # CLI参数覆盖
    if repo:
        loaded_config.analysis.git.repo_path = repo
    if branch:
        loaded_config.analysis.git.branch = branch
    if time_basis:
        loaded_config.analysis.git.time_basis = time_basis
    if days:
        loaded_config.analysis.git.time_filter_mode = "last_n_days"
        loaded_config.analysis.git.time_filter_last_n_days = days
    if since:
        loaded_config.analysis.git.time_filter_mode = "date_range"
        loaded_config.analysis.git.time_filter_date_range_since = since
    if until:
        loaded_config.analysis.git.time_filter_date_range_until = until
    if format:
        loaded_config.analysis.output.formats = [f.strip() for f in format.split(",")]
    if output_dir:
        loaded_config.analysis.output.directory = str(output_dir)
    if ai_provider:
        loaded_config.ai.provider.name = ai_provider
    if ai_model:
        loaded_config.ai.provider.model = ai_model
    if ai_key:
        loaded_config.ai.provider.api_key = ai_key

    # 验证配置
    errors = loaded_config.validate()
    if errors:
        click.echo("Configuration errors:")
        for error in errors:
            click.echo(f"  - {error}")
        return

    click.echo("Configuration validated successfully")
    click.echo(f"  Repository: {loaded_config.analysis.git.repo_path}")
    click.echo(f"  Branch: {loaded_config.analysis.git.branch}")
    click.echo(f"  Output formats: {loaded_config.analysis.output.formats}")
    click.echo("\n🚀 Analysis would start here...")
    # TODO: 实现分析逻辑


@main.command()
def init():
    """Initialize configuration interactively."""
    try:
        from .config.interactive import interactive_setup
        interactive_setup()
    except ImportError:
        click.echo("Click is required for interactive setup. Install with: pip install click")


if __name__ == "__main__":
    main()
