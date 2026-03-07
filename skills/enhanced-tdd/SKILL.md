# Enhanced TDD Testing Skill

## Overview

这是一个增强的TDD（测试驱动开发）Skill，包含代码覆盖率要求、异常处理测试、边界条件覆盖等最佳实践。

## 核心原则

### 1. TDD基本流程

```
Red → Green → Refactor
```

每个开发任务都遵循：
1. **写失败的测试** - 明确需求
2. **运行测试确认失败** - 验证测试能正确检测问题
3. **写最小化代码** - 只让测试通过，不多不少
4. **运行测试确认通过** - 验证实现正确
5. **重构优化** - 改进代码质量
6. **提交代码** - 小步提交，频繁提交

### 2. 代码覆盖率要求

| 类型 | 目标覆盖率 | 说明 |
|------|------------|------|
| **行覆盖率** | ≥ 90% | 所有代码行至少执行一次 |
| **分支覆盖率** | ≥ 85% | 所有条件分支至少执行一次 |
| **函数覆盖率** | 100% | 所有公开函数必须有测试 |
| **核心模块** | 100% | 核心业务逻辑必须全覆盖 |

**运行覆盖率检查**：
```bash
pytest --cov=src --cov-report=html --cov-report=term
```

### 3. 测试组织

```
tests/
├── unit/              # 单元测试
│   ├── test_config.py
│   ├── test_git_collector.py
│   └── ...
├── integration/       # 集成测试
│   ├── test_full_workflow.py
│   └── ...
├── e2e/               # 端到端测试
│   └── test_cli.py
└── conftest.py        # pytest配置和fixtures
```

## 测试模板

### 基础测试模板

```python
import pytest
from pathlib import Path
from your_module import YourClass

class TestYourClass:
    """测试YourClass"""

    def test_normal_case(self):
        """测试正常情况"""
        # Given
        input_data = {...}

        # When
        result = YourClass.process(input_data)

        # Then
        assert result is not None
        assert result.status == "success"

    def test_exception_handling(self):
        """测试异常处理"""
        # Given
        invalid_input = None

        # When & Then
        with pytest.raises(ValueError, match="input cannot be None"):
            YourClass.process(invalid_input)

    def test_boundary_conditions(self):
        """测试边界条件"""
        # Test empty input
        result1 = YourClass.process([])
        assert result1.count == 0

        # Test single item
        result2 = YourClass.process([1])
        assert result2.count == 1

        # Test large input
        result3 = YourClass.process(list(range(1000)))
        assert result3.count == 1000

    @pytest.mark.parametrize("input,expected", [
        (1, "one"),
        (2, "two"),
        (3, "three"),
    ])
    def test_parameterized_cases(self, input, expected):
        """测试参数化用例"""
        result = YourClass.process(input)
        assert result.value == expected

    def test_edge_cases(self):
        """测试边缘情况"""
        # Test None
        with pytest.raises(ValueError):
            YourClass.process(None)

        # Test empty string
        with pytest.raises(ValueError):
            YourClass.process("")

        # Test very long string
        result = YourClass.process("a" * 10000)
        assert len(result.processed) == 10000
```

## 测试检查清单

每个测试用例应该满足：

### ✅ 基本要求
- [ ] 测试名称清晰描述测试内容
- [ ] 使用 Given-When-Then 或 Arrange-Act-Assert 结构
- [ ] 每个测试只验证一个行为
- [ ] 测试独立，不依赖执行顺序
- [ ] 测试可重复运行
- [ ] 使用有意义的断言

### ✅ 覆盖要求
- [ ] 正常路径已测试
- [ ] 异常情况已测试
- [ ] 边界条件已测试
- [ ] 空值/None已测试
- [ ] 错误输入已测试
- [ ] 大数据量已测试

### ✅ 异常处理测试
```python
def test_exception_scenarios(self):
    # 测试各种异常情况
    with pytest.raises(ValueError):
        func(None)

    with pytest.raises(FileNotFoundError):
        func("/nonexistent/file")

    with pytest.raises(PermissionError):
        func("/root/protected")
```

### ✅ 边界条件测试
```python
def test_boundary_conditions(self):
    # 空集合
    assert func([]) == 0

    # 单元素
    assert func([1]) == 1

    # 最大值
    assert func([sys.maxsize]) == sys.maxsize

    # 最小值
    assert func([-sys.maxsize]) == -sys.maxsize

    # 零
    assert func([0]) == 0

    # 负数
    assert func([-1]) == -1
```

## Pytest配置

### conftest.py

```python
import pytest
import sys
from pathlib import Path

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# 共享fixtures
@pytest.fixture
def sample_config():
    """示例配置fixture"""
    return {
        "repo_path": "/tmp/test",
        "branch": "main"
    }

@pytest.fixture
def temp_file(tmp_path):
    """临时文件fixture"""
    file_path = tmp_path / "test.txt"
    file_path.write_text("test content")
    return file_path

# 异常测试helper
@pytest.fixture
def assert_raises(exception_class):
    """断言抛出异常的helper"""
    def _assert_raises(*args, **kwargs):
        with pytest.raises(exception_class) as exc_info:
            yield
        return exc_info
    return _assert_raises

# Mock helper
@pytest.fixture
def mock_git_repo(tmp_path):
    """创建模拟git仓库的fixture"""
    import subprocess
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()

    subprocess.run(["git", "init"], cwd=repo_path, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_path, check=True
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_path, check=True
    )

    # 创建初始提交
    test_file = repo_path / "test.txt"
    test_file.write_text("initial content")
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo_path, check=True
    )

    yield repo_path
```

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --tb=short
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=85

markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
```

## 测试命令

### 基本测试
```bash
# 运行所有测试
pytest

# 运行特定文件
pytest tests/test_config.py

# 运行特定测试
pytest tests/test_config.py::test_load_yaml_config

# 运行特定类
pytest tests/test_config.py::TestConfig
```

### 覆盖率
```bash
# 生成覆盖率报告
pytest --cov=src --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html

# 终端显示覆盖率
pytest --cov=src --cov-report=term-missing

# 设置最低覆盖率要求
pytest --cov=src --cov-fail-under=85
```

### 调试
```bash
# 在第一个失败时停止
pytest -x

# 显示详细输出
pytest -vvs

# 进入调试器
pytest --pdb

# 只运行失败的测试
pytest --lf

# 只运行上一次失败的测试
```

## 测试最佳实践

### 1. 命名约定

```python
def test_[method_name]_[scenario]():
    """好的命名"""
    pass

def test_load_config_with_valid_yaml():
    """好的命名"""
    pass

def test_1():
    """不好的命名"""
    pass
```

### 2. 使用pytest.raises

```python
# ✅ 好
with pytest.raises(ValueError):
    func()

# ❌ 不好
try:
    func()
except ValueError:
    pass
```

### 3. 使用parametrize

```python
# ✅ 好
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_multiply(input, expected):
    assert multiply(input, 2) == expected

# ❌ 不好
def test_multiply_1():
    assert multiply(1, 2) == 2

def test_multiply_2():
    assert multiply(2, 2) == 4
```

### 4. 使用fixtures

```python
# ✅ 好
def test_with_fixture(sample_config):
    config = Config(sample_config)
    assert config.is_valid()

# ❌ 不好
def test_without_fixture():
    sample_config = {...}  # 重复代码
    config = Config(sample_config)
    assert config.is_valid()
```

### 5. 模拟外部依赖

```python
from unittest.mock import patch, MagicMock

def test_with_mock():
    with patch('module.external_function') as mock_func:
        mock_func.return_value = "mocked_value"
        result = your_function()
        assert result == "expected"
        mock_func.assert_called_once()
```

## 持续集成

### GitHub Actions

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 常见问题

### Q: 如何测试私有方法？
A: 通过测试公开接口间接测试，或使用 `from module import _private`（不推荐）

### Q: 如何处理随机性？
A: 使用固定的seed或mock随机函数

### Q: 如何测试异步代码？
A: 使用 `pytest-asyncio` 或 `pytest.mark.asyncio`

### Q: 如何测试CLI工具？
A: 使用 `click.testing.CliRunner` 或捕获subprocess输出

## 参考资料

- [Pytest Documentation](https://docs.pytest.org/)
- [Test Coverage](https://coverage.readthedocs.io/)
- [TDD Best Practices](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
