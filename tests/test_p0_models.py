"""P0 data model tests."""
from issue_analyzer.models import Issue, Commit, Document, AnalysisTask, TaskStatus

def test_issue_model():
    issue = Issue(
        id="PROJ-123",
        key="PROJ-123",
        summary="Test issue",
        status="todo"
    )
    assert issue.id == "PROJ-123"
    assert issue.status == "todo"

def test_commit_model():
    commit = Commit(
        hash="abc123def456",
        message="Test commit",
        author="Test Author",
        author_email="test@example.com"
    )
    assert commit.hash == "abc123def456"
    assert commit.short_hash == "abc123d"

def test_document_model():
    document = Document(
        id="doc-123",
        type="requirements",
        title="Requirements Doc",
        content="Requirements content",
        issue_id="PROJ-123",
        source="confluence"
    )
    assert document.id == "doc-123"
    assert document.type == "requirements"

def test_analysis_task_model():
    task = AnalysisTask(
        id="task-123",
        issue_id="PROJ-123",
        status="pending"
    )
    assert task.id == "task-123"
    assert task.status == "pending"
    assert task.progress == 0.0
