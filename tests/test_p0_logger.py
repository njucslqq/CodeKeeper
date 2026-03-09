"""P0 logging tests."""
import tempfile
from pathlib import Path

def test_logger_creation():
    from issue_analyzer.logger import get_logger
    logger = get_logger("test")
    assert logger is not None

def test_file_logging():
    from issue_analyzer.logger import Logger
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / "test.log"
        logger = Logger("test", file_path=log_path, level="INFO")
        logger.info("Test message")
        assert log_path.exists()
        content = log_path.read_text()
        assert "Test message" in content

def test_task_context():
    from issue_analyzer.logger import get_logger, set_task_id, get_task_id
    set_task_id("test-task-123")
    assert get_task_id() == "test-task-123"
    logger = get_logger("test")
    logger.info("Test message with task context")
    set_task_id(None)
