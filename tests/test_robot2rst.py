import logging
import sys
from pathlib import Path
import tempfile
import os
import pytest

# Add the project root to the sys.path to allow importing mlx.robot2rst
sys.path.insert(0, str(Path(__file__).parent.parent))

from mlx.robot2rst.robot2rst import main as robot2rst_main, _tweak_prefix, render_template
from mlx.robot2rst.robot_parser import ParserApplication

INPUT_DIR = Path(__file__).parent / "input"


# Tests for _tweak_prefix function
def test_tweak_prefix_with_underscore_dash():
    """Test that _tweak_prefix removes underscore from '_-' suffix"""
    assert _tweak_prefix('ITEST_-') == 'ITEST-'
    assert _tweak_prefix('QTEST_-') == 'QTEST-'
    assert _tweak_prefix('FOO_BAR_-') == 'FOO_BAR-'


def test_tweak_prefix_without_underscore_dash():
    """Test that _tweak_prefix returns prefix unchanged if it doesn't end with '_-'"""
    assert _tweak_prefix('ITEST-') == 'ITEST-'
    assert _tweak_prefix('QTEST') == 'QTEST'
    assert _tweak_prefix('FOO_BAR-') == 'FOO_BAR-'
    assert _tweak_prefix('FOO_') == 'FOO_'


def test_tweak_prefix_empty_and_edge_cases():
    """Test _tweak_prefix with empty strings and edge cases"""
    assert _tweak_prefix('') == ''
    assert _tweak_prefix('_-') == '-'
    assert _tweak_prefix('-') == '-'
    assert _tweak_prefix('_') == '_'


# Tests for ParserApplication class
def test_parser_application_basic():
    """Test ParserApplication parses a simple robot file"""
    robot_file = INPUT_DIR / "multiline_doc.robot"
    parser = ParserApplication(robot_file, [])
    parser.run()

    assert len(parser.tests) == 1
    assert parser.tests[0].name == "My Test"
    assert "This is the first line" in parser.tests[0].doc
    assert "Bullet point 1" in parser.tests[0].doc


def test_parser_application_with_tags():
    """Test ParserApplication extracts tags correctly"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "test.robot"
        robot_file.write_text("""*** Test Cases ***
Test With Tags
    [Documentation]    Test documentation
    [Tags]    TAG1    TAG2    TAG3
    Log    Hello
""")
        parser = ParserApplication(robot_file, [])
        parser.run()

        assert len(parser.tests) == 1
        assert parser.tests[0].tags == ["TAG1", "TAG2", "TAG3"]


def test_parser_application_tag_filtering():
    """Test ParserApplication filters tests by tags"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "test.robot"
        robot_file.write_text("""*** Test Cases ***
Test With SWRQT
    [Documentation]    First test
    [Tags]    SWRQT-123
    Log    Hello

Test With SYSRQT
    [Documentation]    Second test
    [Tags]    SYSRQT-456
    Log    Hi

Test With Both
    [Documentation]    Third test
    [Tags]    SWRQT-789    SYSRQT-101
    Log    Hey
""")
        # Filter to only include tests with SWRQT tags
        parser = ParserApplication(robot_file, ["SWRQT-.*"])
        parser.run()

        assert len(parser.tests) == 2
        assert parser.tests[0].name == "Test With SWRQT"
        assert parser.tests[1].name == "Test With Both"


def test_parser_application_multiple_tag_filters():
    """Test ParserApplication with multiple tag filter regexes (all must match)"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "test.robot"
        robot_file.write_text("""*** Test Cases ***
Test With Both Tags
    [Documentation]    Has both required tags
    [Tags]    SWRQT-123    PRIORITY-HIGH
    Log    Hello

Test With Only SWRQT
    [Documentation]    Missing PRIORITY tag
    [Tags]    SWRQT-456
    Log    Hi

Test With Only Priority
    [Documentation]    Missing SWRQT tag
    [Tags]    PRIORITY-LOW
    Log    Hey
""")
        # Require both SWRQT and PRIORITY tags
        parser = ParserApplication(robot_file, ["SWRQT-.*", "PRIORITY-.*"])
        parser.run()

        # Only the first test has both required tag patterns
        assert len(parser.tests) == 1
        assert parser.tests[0].name == "Test With Both Tags"


def test_parser_application_variables():
    """Test ParserApplication extracts variables"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "test.robot"
        robot_file.write_text("""*** Variables ***
${MESSAGE}    Hello World
${NUMBER}     42

*** Test Cases ***
Test With Variable
    [Documentation]    Documentation with ${MESSAGE}
    Log    ${MESSAGE}
""")
        parser = ParserApplication(robot_file, [])
        parser.run()

        assert "${MESSAGE}" in parser.variables
        assert parser.variables["${MESSAGE}"] == "Hello World"
        assert "${NUMBER}" in parser.variables
        assert parser.variables["${NUMBER}"] == "42"


def test_parser_application_env_variables(monkeypatch):
    """Test ParserApplication substitutes environment variables in documentation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "test.robot"
        robot_file.write_text("""*** Test Cases ***
Test With Env Var
    [Documentation]    Environment variable: %{TEST_VAR}
    Log    Hello
""")
        # Set environment variable
        monkeypatch.setenv("TEST_VAR", "test_value")

        parser = ParserApplication(robot_file, [])
        parser.run()

        assert len(parser.tests) == 1
        assert "Environment variable: test_value" in parser.tests[0].doc


def test_parser_application_empty_file():
    """Test ParserApplication with file containing no test cases"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "empty.robot"
        robot_file.write_text("""*** Settings ***
Documentation    A file with no test cases
""")
        parser = ParserApplication(robot_file, [])
        parser.run()

        assert len(parser.tests) == 0
        assert parser.variables == {}


# Tests for robot2rst conversion workflow
def test_conversion_basic(caplog):
    """Test basic robot to rst conversion"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "test.robot"
        rst_file = tmppath / "test.rst"
        robot_file.write_text("""*** Test Cases ***
My Test Case
    [Documentation]    This is a test case
    [Tags]    SWRQT-123
    Log    Hello
""")
        sys.argv = ["robot2rst", "convert", "-i", str(robot_file), "-o", str(rst_file)]

        with caplog.at_level(logging.INFO):
            result_code = robot2rst_main()

        assert result_code == 0
        assert rst_file.exists()
        rst_content = rst_file.read_text()
        assert "QTEST-MY_TEST_CASE" in rst_content
        assert "My Test Case" in rst_content
        assert "This is a test case" in rst_content


def test_conversion_with_custom_prefix():
    """Test conversion with custom prefix"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "test.robot"
        rst_file = tmppath / "test.rst"
        robot_file.write_text("""*** Test Cases ***
Integration Test
    [Documentation]    Integration test documentation
    Log    Hello
""")
        sys.argv = ["robot2rst", "convert", "-i", str(robot_file), "-o", str(rst_file),
                    "-p", "ITEST-"]

        result_code = robot2rst_main()

        assert result_code == 0
        rst_content = rst_file.read_text()
        assert "ITEST-INTEGRATION_TEST" in rst_content


def test_conversion_with_trim_suffix():
    """Test conversion with --trim-suffix flag"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "test.robot"
        rst_file = tmppath / "test.rst"
        robot_file.write_text("""*** Test Cases ***
My Test
    [Documentation]    Test documentation
    Log    Hello
""")
        sys.argv = ["robot2rst", "convert", "-i", str(robot_file), "-o", str(rst_file),
                    "-p", "ITEST_-", "--trim-suffix"]

        result_code = robot2rst_main()

        assert result_code == 0
        rst_content = rst_file.read_text()
        # Prefix should be trimmed from ITEST_- to ITEST-
        assert "ITEST-MY_TEST" in rst_content


def test_conversion_with_relationships_and_tags():
    """Test conversion with custom relationships and tag regexes"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "test.robot"
        rst_file = tmppath / "test.rst"
        robot_file.write_text("""*** Test Cases ***
Test Case One
    [Documentation]    First test
    [Tags]    SWRQT-123    SYSRQT-456
    Log    Hello

Test Case Two
    [Documentation]    Second test
    [Tags]    SWRQT-789
    Log    Hi
""")
        sys.argv = ["robot2rst", "convert", "-i", str(robot_file), "-o", str(rst_file),
                    "-r", "validates", "implements",
                    "-t", "SWRQT-.*", "SYSRQT-.*"]

        result_code = robot2rst_main()

        assert result_code == 0
        rst_content = rst_file.read_text()
        assert ":validates: SWRQT-123" in rst_content
        assert ":implements: SYSRQT-456" in rst_content
        assert "Traceability Matrix" in rst_content


def test_conversion_no_tests_matching_filter(caplog):
    """Test conversion when no tests match the include filter"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "test.robot"
        rst_file = tmppath / "test.rst"
        robot_file.write_text("""*** Test Cases ***
Test Without Tag
    [Documentation]    Test without required tag
    Log    Hello
""")
        sys.argv = ["robot2rst", "convert", "-i", str(robot_file), "-o", str(rst_file),
                    "--include", "REQUIRED-.*"]

        with caplog.at_level(logging.INFO):
            result_code = robot2rst_main()

        assert result_code == 0
        assert not rst_file.exists()
        assert "does not contain any test cases with tags matching all regexes" in caplog.text


def test_conversion_with_only_directive():
    """Test conversion with --only directive for conditional content"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "test.robot"
        rst_file = tmppath / "test.rst"
        robot_file.write_text("""*** Test Cases ***
Test Case
    [Documentation]    Test documentation
    Log    Hello
""")
        sys.argv = ["robot2rst", "convert", "-i", str(robot_file), "-o", str(rst_file),
                    "--only", "html"]

        result_code = robot2rst_main()

        assert result_code == 0
        rst_content = rst_file.read_text()
        assert ".. only:: html" in rst_content


def test_conversion_integration_type():
    """Test conversion with integration test type"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "test.robot"
        rst_file = tmppath / "test.rst"
        robot_file.write_text("""*** Test Cases ***
Integration Test
    [Documentation]    Integration test
    Log    Hello
""")
        sys.argv = ["robot2rst", "convert", "-i", str(robot_file), "-o", str(rst_file),
                    "--type", "integration"]

        result_code = robot2rst_main()

        assert result_code == 0
        rst_file.read_text()
        # Should use "integration" type in the output
        assert rst_file.exists()


def test_conversion_invalid_type():
    """Test conversion with invalid test type raises ValueError"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "test.robot"
        rst_file = tmppath / "test.rst"
        robot_file.write_text("""*** Test Cases ***
Test Case
    [Documentation]    Test
    Log    Hello
""")
        # Use a type that doesn't start with 'i' or 'q' (which would match integration/qualification)
        sys.argv = ["robot2rst", "convert", "-i", str(robot_file), "-o", str(rst_file),
                    "--type", "xyz"]

        # The implementation raises ValueError which is not caught
        with pytest.raises(ValueError, match="xyz"):
            robot2rst_main()


def test_conversion_coverage_percentages():
    """Test conversion with coverage percentages"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "test.robot"
        rst_file = tmppath / "test.rst"
        robot_file.write_text("""*** Test Cases ***
Test Case
    [Documentation]    Test documentation
    [Tags]    SWRQT-123
    Log    Hello
""")
        sys.argv = ["robot2rst", "convert", "-i", str(robot_file), "-o", str(rst_file),
                    "-r", "validates",
                    "-t", "SWRQT-.*",
                    "-c", "100"]

        result_code = robot2rst_main()

        assert result_code == 0
        rst_content = rst_file.read_text()
        assert ":coverage: >= 100" in rst_content


# Tests for render_template function
def test_render_template_basic():
    """Test render_template creates output file"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        output_file = tmppath / "output.rst"
        robot_file = INPUT_DIR / "multiline_doc.robot"

        parser = ParserApplication(robot_file, [])
        parser.run()

        result = render_template(
            output_file,
            parser=parser,
            suite="test_suite",
            prefix="QTEST-",
            relationship_config=[("validates", ".*", 0)],
            gen_matrix=False,
            test_type="qualification",
            coverages=[0]
        )

        assert result == 0
        assert output_file.exists()


def test_render_template_with_only_directive():
    """Test render_template with only directive"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        output_file = tmppath / "output.rst"
        robot_file = INPUT_DIR / "multiline_doc.robot"

        parser = ParserApplication(robot_file, [])
        parser.run()

        result = render_template(
            output_file,
            only="html",
            parser=parser,
            suite="test_suite",
            prefix="QTEST-",
            relationship_config=[("validates", ".*", 0)],
            gen_matrix=False,
            test_type="qualification",
            coverages=[0]
        )

        assert result == 0
        assert output_file.exists()
        content = output_file.read_text()
        assert ".. only:: html" in content


def test_render_template_creates_parent_directory():
    """Test render_template creates parent directories if needed"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        output_file = tmppath / "subdir" / "nested" / "output.rst"
        robot_file = INPUT_DIR / "multiline_doc.robot"

        parser = ParserApplication(robot_file, [])
        parser.run()

        result = render_template(
            output_file,
            parser=parser,
            suite="test_suite",
            prefix="QTEST-",
            relationship_config=[("validates", ".*", 0)],
            gen_matrix=False,
            test_type="qualification",
            coverages=[0]
        )

        assert result == 0
        assert output_file.exists()
        assert output_file.parent.exists()


# Additional integration tests
def test_default_command_is_convert():
    """Test that convert is the default command when no command specified"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "test.robot"
        rst_file = tmppath / "test.rst"
        robot_file.write_text("""*** Test Cases ***
Test Case
    [Documentation]    Test
    Log    Hello
""")
        # Don't specify 'convert' command explicitly
        sys.argv = ["robot2rst", "-i", str(robot_file), "-o", str(rst_file)]

        result_code = robot2rst_main()

        assert result_code == 0
        assert rst_file.exists()


def test_mismatched_relationship_and_tag_count():
    """Test conversion fails when relationship and tag counts don't match"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "test.robot"
        rst_file = tmppath / "test.rst"
        robot_file.write_text("""*** Test Cases ***
Test Case
    [Documentation]    Test
    [Tags]    SWRQT-123
    Log    Hello
""")
        # 2 relationships but 1 tag regex
        sys.argv = ["robot2rst", "convert", "-i", str(robot_file), "-o", str(rst_file),
                    "-r", "validates", "implements",
                    "-t", "SWRQT-.*"]

        # Should raise ValueError for mismatched counts
        with pytest.raises(ValueError, match="Number of relationships"):
            robot2rst_main()


def test_mismatched_coverage_count():
    """Test conversion fails when coverage count doesn't match relationships"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "test.robot"
        rst_file = tmppath / "test.rst"
        robot_file.write_text("""*** Test Cases ***
Test Case
    [Documentation]    Test
    [Tags]    SWRQT-123
    Log    Hello
""")
        # 1 relationship but 2 coverage values
        sys.argv = ["robot2rst", "convert", "-i", str(robot_file), "-o", str(rst_file),
                    "-r", "validates",
                    "-t", "SWRQT-.*",
                    "-c", "100", "50"]

        # Should raise ValueError for mismatched coverage count
        with pytest.raises(ValueError, match="coverage"):
            robot2rst_main()


def test_no_traceability_matrix_without_tags():
    """Test that no traceability matrix is generated when no tags specified"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "test.robot"
        rst_file = tmppath / "test.rst"
        robot_file.write_text("""*** Test Cases ***
Test Case
    [Documentation]    Test
    Log    Hello
""")
        # No --tags argument
        sys.argv = ["robot2rst", "convert", "-i", str(robot_file), "-o", str(rst_file)]

        result_code = robot2rst_main()

        assert result_code == 0
        rst_content = rst_file.read_text()
        # Should not include traceability matrix
        assert "Traceability Matrix" not in rst_content
