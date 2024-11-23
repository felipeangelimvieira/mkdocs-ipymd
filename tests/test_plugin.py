from unittest.mock import MagicMock

import pytest
from mkdocs.config import Config
from mkdocs.config.defaults import MkDocsConfig, get_schema
from mkdocs.structure.files import File
from mkdocs.structure.pages import Page

from mkdocs_pymd.plugin import ExecCodePlugin


# Mock the necessary MkDocs components
class MockFile:
    def __init__(self, src_path):
        self.abs_src_path = src_path


@pytest.fixture
def plugin():
    # Create an instance of the plugin with default config
    plugin = ExecCodePlugin()
    plugin.load_config({})
    return plugin


@pytest.fixture
def mkdocs_config():
    # Create a minimal MkDocs config
    cfg = Config(schema=get_schema())
    # Validate and set default values for the configuration
    cfg.load_dict({})
    cfg.validate()
    return cfg


def test_simple_code_execution(plugin, mkdocs_config):
    # Test simple code execution
    markdown = """
    ```{python}
    x = 2
    y = 3
    print(x + y)
    ```
    """
    page = Page("Test Page", MockFile("test.md"), mkdocs_config)
    result = plugin.on_page_markdown(markdown, page, mkdocs_config, files=[])
    expected_output = """
    ```python
    x = 2
    y = 3
    print(x + y)
    ```

    ```
    5
    ```
    """
    assert result.strip() == expected_output.strip()


def test_execution_context(plugin, mkdocs_config):
    # Test that variables persist across code blocks in the same file
    markdown = """
    ```{python}
    a = 10
    ```
    ```{python}
    print(a * 2)
    ```
    """
    page = Page("Test Page", MockFile("test.md"), mkdocs_config)
    result = plugin.on_page_markdown(markdown, page, mkdocs_config, files=[])
    expected_output = """
    ```python
    a = 10
    ```

    ```
    ```
    ```python
    print(a * 2)
    ```

    ```
    20
    ```
    """
    assert result.strip() == expected_output.strip()


def test_error_handling(plugin, mkdocs_config):
    # Test that errors are captured and reported
    markdown = """
    ```{python}
    print(undefined_variable)
    ```
    """
    page = Page("Test Page", MockFile("test.md"), mkdocs_config)
    result = plugin.on_page_markdown(markdown, page, mkdocs_config, files=[])
    assert "Error executing code" in result


def test_multiple_files(plugin, mkdocs_config):
    # Test that execution contexts are isolated per file
    markdown1 = """
    ```{python}
    x = 5
    ```
    """
    markdown2 = """
    ```{python}
    print(x)
    ```
    """
    page1 = Page("Page 1", MockFile("file1.md"), mkdocs_config)
    page2 = Page("Page 2", MockFile("file2.md"), mkdocs_config)

    result1 = plugin.on_page_markdown(markdown1, page1, mkdocs_config, files=[])
    result2 = plugin.on_page_markdown(markdown2, page2, mkdocs_config, files=[])

    # The second file should not have access to 'x' defined in the first file
    assert "Error executing code" in result2 or "NameError" in result2


def test_disabled_plugin(plugin, mkdocs_config):
    # Test that plugin does nothing when disabled
    plugin.config["enabled"] = False
    markdown = """
    ```{python}
    x = 2
    print(x)
    ```
    """
    page = Page("Test Page", MockFile("test.md"), mkdocs_config)
    result = plugin.on_page_markdown(markdown, page, mkdocs_config, files=[])
    assert result.strip() == markdown.strip()


def test_non_python_code_blocks(plugin, mkdocs_config):
    # Test that code blocks not marked as {python} are ignored
    markdown = """
    ```javascript
    console.log("Hello, World!");
    ```
    """
    page = Page("Test Page", MockFile("test.md"), mkdocs_config)
    result = plugin.on_page_markdown(markdown, page, mkdocs_config, files=[])
    assert result.strip() == markdown.strip()
