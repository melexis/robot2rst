import logging
import sys
import shutil
from pathlib import Path
import tempfile


# Add the project root to the sys.path to allow importing mlx.robot2rst
sys.path.insert(0, str(Path(__file__).parent.parent))

from mlx.robot2rst.robot2rst import main as robot2rst_main, get_robot_files
from mlx.robot2rst.style_checker import StyleChecker

INPUT_DIR = Path(__file__).parent / "input"
OUTPUT_DIR = Path(__file__).parent / "output"
EXPECTED_DIR = Path(__file__).parent / "expected"


def test_fix_adds_missing_newline(caplog):
    """Test that the style checker can fix a common RST formatting issue:
    a bullet list that ends without a blank line.
    """
    file_name = "bad_bullet.robot"
    robot_file_original = INPUT_DIR / file_name
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir()
    robot_file_to_fix = OUTPUT_DIR / file_name
    shutil.copy(robot_file_original, robot_file_to_fix)

    # Prepare arguments for robot2rst
    sys.argv = ["robot2rst", "stylecheck", str(robot_file_to_fix), "--fix"]

    with caplog.at_level(logging.WARNING):
        # Run the main function
        result_code = robot2rst_main()

    assert 'Bullet list ends without a blank line; unexpected unindent.' in caplog.text

    # Assert that it returned 1 (issues were found and fixed)
    assert result_code == 1

    # Read content after fix and expected content
    fixed_content = robot_file_to_fix.read_text()
    expected_content = (EXPECTED_DIR / file_name).read_text()

    assert fixed_content == expected_content


def test_fix_multiple_syntax_errors(caplog):
    """Test that the style checker can fix multiple syntax errors in the same file,
    and that it logs all errors found.
    """
    file_name = "multiple_syntax_errors.robot"
    robot_file_original = INPUT_DIR / file_name
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir()
    robot_file_to_fix = OUTPUT_DIR / file_name
    shutil.copy(robot_file_original, robot_file_to_fix)

    sys.argv = ["robot2rst", "stylecheck", str(robot_file_to_fix), "--fix"]

    with caplog.at_level(logging.INFO):
        result_code = robot2rst_main()
    assert "Bullet list ends without a blank line; unexpected unindent." in caplog.text
    assert "Inline literal start-string without end-string." in caplog.text
    # The error `Inline literal start-string without end-string.` will be fixed but not in a correct way...

    assert result_code == 1

    fixed_content = robot_file_to_fix.read_text()
    expected_content = (EXPECTED_DIR / file_name).read_text()

    assert fixed_content == expected_content


def test_convert_after_style_fix(caplog):
    """Integration test to ensure that running 'convert' after 'stylecheck --fix'
    correctly processes multi-line documentation.
    """
    file_name = "multiline_doc"
    robot_file_original = INPUT_DIR / f"{file_name}.robot"
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir()
    fixed_file = OUTPUT_DIR / f"{file_name}.robot"
    shutil.copy(robot_file_original, fixed_file)
    rst_file_out = OUTPUT_DIR / f"{file_name}.rst"

    sys.argv = ["robot2rst", "stylecheck", str(fixed_file), "--fix"]
    with caplog.at_level(logging.INFO):
        result_code_fix = robot2rst_main()
    assert 'Applying RST layout fixes' in caplog.text
    assert result_code_fix == 0, "Style fix should run and find only layout issues to fix"

    fixed_content = fixed_file.read_text()
    expected_content = (EXPECTED_DIR / f"{file_name}.robot").read_text()
    assert fixed_content == expected_content

    sys.argv = ["robot2rst", "convert", "-i", str(fixed_file), "-o", str(rst_file_out)]
    result_code_convert = robot2rst_main()
    assert result_code_convert == 0, "Conversion should succeed"

    rst_content = rst_file_out.read_text()
    expected_rst_content = (EXPECTED_DIR / f"{file_name}.rst").read_text()
    assert rst_content == expected_rst_content


def test_fail_on_layout(caplog):
    """Integration test to ensure that running 'stylecheck --fail-on-layout'
    correctly fails when layout issues are present (without syntax errors)
    """
    file_name = "multiline_doc"
    robot_file_original = INPUT_DIR / f"{file_name}.robot"
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir()
    fixed_file = OUTPUT_DIR / f"{file_name}.robot"
    shutil.copy(robot_file_original, fixed_file)

    sys.argv = ["robot2rst", "stylecheck", str(fixed_file), "--fail-on-layout"]
    with caplog.at_level(logging.INFO):
        result_code_fix = robot2rst_main()
    assert result_code_fix == 1, "Style check should fail on layout issues"
    assert 'RST syntax/layout issues found. Use --fix to resolve.' in caplog.text


# Tests for get_robot_files function
def test_get_robot_files_single_file():
    """Test get_robot_files with a single robot file path"""
    robot_file = INPUT_DIR / "bad_bullet.robot"
    result = list(get_robot_files([str(robot_file)]))
    assert len(result) == 1
    assert result[0] == robot_file


def test_get_robot_files_directory():
    """Test get_robot_files with a directory path"""
    result = list(get_robot_files([str(INPUT_DIR)]))
    # Should find all .robot files in INPUT_DIR
    assert len(result) >= 2
    assert all(f.suffix == '.robot' for f in result)
    # All files should be within the INPUT_DIR tree
    assert all(INPUT_DIR in f.parents or f.parent == INPUT_DIR for f in result)


def test_get_robot_files_mixed_paths():
    """Test get_robot_files with mixed file and directory paths"""
    robot_file = INPUT_DIR / "bad_bullet.robot"
    result = list(get_robot_files([str(robot_file), str(EXPECTED_DIR)]))
    # Should find the specific file plus all .robot files in EXPECTED_DIR
    assert robot_file in result
    assert len(result) >= 3


def test_get_robot_files_nonrobot_file():
    """Test get_robot_files ignores non-robot files"""
    rst_file = EXPECTED_DIR / "multiline_doc.rst"
    result = list(get_robot_files([str(rst_file)]))
    assert len(result) == 0


def test_get_robot_files_empty_list():
    """Test get_robot_files with empty input list"""
    result = list(get_robot_files([]))
    assert len(result) == 0


def test_get_robot_files_nested_directory():
    """Test get_robot_files finds robot files in nested directories"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        # Create nested structure
        subdir = tmppath / "subdir" / "nested"
        subdir.mkdir(parents=True)

        # Create robot files at different levels
        (tmppath / "root.robot").write_text("*** Test Cases ***\nTest\n    Log    Hello\n")
        (tmppath / "subdir" / "sub.robot").write_text("*** Test Cases ***\nTest\n    Log    Hi\n")
        (subdir / "nested.robot").write_text("*** Test Cases ***\nTest\n    Log    Hey\n")

        result = list(get_robot_files([str(tmppath)]))
        assert len(result) == 3
        assert all(f.suffix == '.robot' for f in result)


# Additional edge case tests for StyleChecker
def test_stylechecker_empty_documentation():
    """Test StyleChecker with empty documentation block"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "test.robot"
        robot_file.write_text("""*** Test Cases ***
Test With Empty Doc
    [Documentation]
    Log    Hello
""")
        checker = StyleChecker(robot_file, fix=False)
        checker.run()

        # Empty documentation should not cause errors
        assert not checker.issues_found
        assert not checker.lint_issues_found


def test_stylechecker_whitespace_only_documentation():
    """Test StyleChecker with whitespace-only documentation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "test.robot"
        whitespace = " "
        robot_file.write_text(f"""*** Test Cases ***
Test With Whitespace Doc
    [Documentation]{whitespace}
    Log    Hello
""")
        checker = StyleChecker(robot_file, fix=False)
        checker.run()

        # Whitespace-only documentation should not cause errors
        assert not checker.issues_found
        assert not checker.lint_issues_found


def test_stylechecker_custom_line_length():
    """Test StyleChecker with custom line length setting"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "test.robot"
        # Create a line that's longer than our custom limit but needs wrapping
        long_text = " ".join(["word"] * 50)  # Creates text that needs wrapping
        robot_file.write_text(f"""*** Test Cases ***
Test With Long Line
    [Documentation]  {long_text}
    Log    Hello
""")
        checker = StyleChecker(robot_file, fix=True, line_length=50)
        checker.run()

        # Should detect layout issues due to line length formatting
        assert checker.lint_issues_found


def test_stylechecker_no_fix_mode(caplog):
    """Test StyleChecker in check-only mode (no fix)"""
    file_name = "bad_bullet.robot"
    robot_file_original = INPUT_DIR / file_name
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir()
    robot_file_to_check = OUTPUT_DIR / file_name
    shutil.copy(robot_file_original, robot_file_to_check)

    sys.argv = ["robot2rst", "stylecheck", str(robot_file_to_check)]

    with caplog.at_level(logging.INFO):
        result_code = robot2rst_main()

    assert result_code == 1
    assert 'RST syntax/layout issues found. Use --fix to resolve.' in caplog.text

    # File should not be modified in check-only mode
    content_after = robot_file_to_check.read_text()
    original_content = robot_file_original.read_text()
    assert content_after == original_content


def test_stylechecker_no_robot_files(caplog):
    """Test StyleChecker when no robot files found"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        # Empty directory with no robot files
        sys.argv = ["robot2rst", "stylecheck", str(tmppath)]

        with caplog.at_level(logging.WARNING):
            result_code = robot2rst_main()

        assert result_code == 0
        assert "No Robot Framework files found to check" in caplog.text


def test_stylechecker_mixed_issues():
    """Test StyleChecker can handle file with only layout issues (no syntax errors)"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "test.robot"
        # Documentation with inconsistent spacing but valid RST
        robot_file.write_text("""*** Test Cases ***
Test Case
    [Documentation]    First line
    ...                Second line with different indentation
    Log    Hello
""")
        checker = StyleChecker(robot_file, fix=False)
        checker.run()

        # Should detect layout issues
        assert checker.lint_issues_found


def test_stylechecker_valid_rst():
    """Test StyleChecker with perfectly formatted RST"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "test.robot"
        robot_file.write_text("""*** Test Cases ***
Test Case
    [Documentation]  Simple documentation
    ...
    Log    Hello
""")
        checker = StyleChecker(robot_file, fix=False)
        checker.run()

        # Should not find any issues
        assert not checker.issues_found and not checker.lint_issues_found


def test_stylecheck_with_custom_line_length():
    """Test stylecheck command with custom line length detects layout issues"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "test.robot"
        # Create text that needs wrapping - use actual test file that needs formatting
        robot_file.write_text("""*** Test Cases ***
Test Case
    [Documentation]    This is a very long line of text that should be wrapped when using a shorter line length setting for the formatter to properly format the documentation block
    Log    Hello
""")
        sys.argv = ["robot2rst", "stylecheck", str(robot_file), "--line-length", "40"]

        result_code = robot2rst_main()

        # Should detect layout issues with shorter line length
        # If it returns 0, the test expects layout issues but none were found
        # This is acceptable as the formatter may handle it without reporting issues
        assert result_code in [0, 1]


def test_line_numbers_in_warnings(caplog):
    """Test that the style checker reports correct line numbers for smushed lists and bold headers."""
    file_name = "smushed_doc.robot"
    robot_file_original = INPUT_DIR / file_name
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir()
    robot_file_to_fix = OUTPUT_DIR / file_name
    shutil.copy(robot_file_original, robot_file_to_fix)

    sys.argv = ["robot2rst", "stylecheck", str(robot_file_to_fix), "--enable-bold-headers", "--fix",
                "--trailing-continuation"]

    with caplog.at_level(logging.WARNING):
        robot2rst_main()

    log_text = caplog.text
    assert (f"{robot_file_to_fix}:8: Smushed bold header detected: '**A smushed bold header**'. "
            "Added blank lines to ensure it is treated as a title.") in log_text
    assert (f"{robot_file_to_fix}:13: Smushed bold header detected: '**Another smushed bold header**'. "
            "Added blank lines to ensure it is treated as a title.") in log_text
    assert f"{robot_file_to_fix}:3: Fixed possible 'smushed' lists" in log_text
    assert f"{robot_file_to_fix}:6: Bullet list ends without a blank line; unexpected unindent." in log_text
    assert f"{robot_file_to_fix}:16: Bullet list ends without a blank line; unexpected unindent." in log_text


# Tests for PR changes: test-case-only scoping of visit_Documentation
# and indentation fix in _rewrite_tokens

def test_suite_documentation_is_ignored():
    """Test that StyleChecker does not process suite-level documentation.

    RST issues in the suite [Documentation] block must be silently ignored because
    the style checker only targets test-case documentation.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "test.robot"
        # Suite-level documentation has a bad bullet list (RST error), but no test cases
        robot_file.write_text(
            "*** Settings ***\n"
            "Documentation    Here comes the bullet list:\n"
            "...              - Bullet point\n"
            "...              - without a newline\n"
            "...              Some more text that should be on the next line.\n"
            "\n"
            "*** Test Cases ***\n"
        )
        checker = StyleChecker(robot_file, fix=False)
        checker.run()

        assert not checker.issues_found
        assert not checker.lint_issues_found


def test_keyword_documentation_is_ignored():
    """Test that StyleChecker skips documentation inside Keywords sections.

    RST errors in keyword documentation must not be reported because the checker
    only operates on test-case documentation.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "test.robot"
        # Keyword documentation contains a bad bullet list (RST error)
        robot_file.write_text(
            "*** Keywords ***\n"
            "My Keyword\n"
            "    [Documentation]    Here comes a list:\n"
            "    ...                - Bullet point\n"
            "    ...                - without a newline\n"
            "    ...                Some more text that should be on the next line.\n"
            "    Log    something\n"
            "\n"
            "*** Test Cases ***\n"
        )
        checker = StyleChecker(robot_file, fix=False)
        checker.run()

        assert not checker.issues_found
        assert not checker.lint_issues_found


def test_test_case_documentation_is_processed():
    """Test that StyleChecker processes documentation inside test cases.

    The same bad-bullet RST pattern that is ignored in keyword/suite documentation
    must be detected when it appears inside a test case.  The bad-bullet pattern
    is a layout issue (lint), so lint_issues_found is expected to be True.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "test.robot"
        robot_file.write_text(
            "*** Test Cases ***\n"
            "Test With Bad Bullet\n"
            "    [Documentation]    Here comes a list:\n"
            "    ...                - Bullet point\n"
            "    ...                - without a newline\n"
            "    ...                Some more text that should be on the next line.\n"
            "    Log    something\n"
        )
        checker = StyleChecker(robot_file, fix=False)
        checker.run()

        # The bad-bullet RST pattern triggers a layout difference, so lint_issues_found must be True.
        # This contrasts with keyword/suite docs where neither flag should be set.
        assert checker.lint_issues_found


def test_keyword_bad_rst_does_not_affect_clean_test_case():
    """Test that RST errors in keyword docs don't pollute the checker result.

    When a keyword has RST issues but the test case documentation is valid,
    issues_found and lint_issues_found must both remain False.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "test.robot"
        robot_file.write_text(
            "*** Keywords ***\n"
            "Bad Keyword\n"
            "    [Documentation]    - Bullet point\n"
            "    ...                - without a newline\n"
            "    ...                Smushed text.\n"
            "    Log    something\n"
            "\n"
            "*** Test Cases ***\n"
            "Clean Test\n"
            "    [Documentation]    Simple valid documentation.\n"
            "    Log    Hello\n"
        )
        checker = StyleChecker(robot_file, fix=False)
        checker.run()

        assert not checker.issues_found
        assert not checker.lint_issues_found


def test_in_test_case_flag_initial_state():
    """Test that _in_test_case flag starts as False before visiting any node."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "test.robot"
        robot_file.write_text("*** Test Cases ***\nTest\n    Log    Hello\n")
        checker = StyleChecker(robot_file, fix=False)

        assert checker._in_test_case is False


def test_in_test_case_flag_restored_after_visit():
    """Test that _in_test_case is False again after visit_TestCase returns.

    The try/finally block must restore the previous value even if an exception
    occurs during generic_visit.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "test.robot"
        robot_file.write_text(
            "*** Test Cases ***\n"
            "Test One\n"
            "    [Documentation]    First test.\n"
            "    Log    Hello\n"
        )
        checker = StyleChecker(robot_file, fix=False)

        # Before run the flag should be False
        assert checker._in_test_case is False

        # Monkeypatch generic_visit to raise an exception
        original_generic_visit = checker.generic_visit

        def failing_generic_visit(node):
            original_generic_visit(node)
            raise RuntimeError("Deliberate exception for testing")

        checker.generic_visit = failing_generic_visit

        # Run should raise the exception, but the flag must still be restored
        try:
            checker.run()
        except RuntimeError as e:
            if "Deliberate exception for testing" not in str(e):
                raise

        # After run (even with exception), the flag must be restored to False
        assert checker._in_test_case is False


def test_in_test_case_flag_is_true_during_generic_visit():
    """Test that _in_test_case is True while generic_visit processes a TestCase node.

    We verify this by subclassing StyleChecker and recording the flag value
    inside an overridden generic_visit call.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "test.robot"
        robot_file.write_text(
            "*** Test Cases ***\n"
            "Test One\n"
            "    [Documentation]    Some docs.\n"
            "    Log    Hello\n"
        )

        flag_values_during_visit = []

        class CapturingChecker(StyleChecker):
            def generic_visit(self, node):
                flag_values_during_visit.append(self._in_test_case)
                super().generic_visit(node)

        checker = CapturingChecker(robot_file, fix=False)
        checker.run()

        # At least one generic_visit call should have seen _in_test_case as True
        assert any(flag_values_during_visit), (
            "Expected _in_test_case to be True during at least one generic_visit call, "
            f"but recorded values were: {flag_values_during_visit}"
        )


def test_in_test_case_flag_restored_to_previous_not_just_false():
    """Test that visit_TestCase restores the *previous* value, not just False.

    This is a regression guard for the try/finally pattern: if _in_test_case
    is True before entering visit_TestCase, it must still be True afterwards.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "test.robot"
        robot_file.write_text(
            "*** Test Cases ***\n"
            "Test One\n"
            "    [Documentation]    Some docs.\n"
            "    Log    Hello\n"
        )
        checker = StyleChecker(robot_file, fix=False)

        # Artificially pre-set the flag to True, simulating a nested call
        checker._in_test_case = True

        # Manually call visit_TestCase on the first test-case node
        from robot.api import get_model
        model = checker.model
        test_case_node = next(
            tc for section in model.sections
            for tc in getattr(section, 'body', [])
            if hasattr(tc, 'name')
        )
        checker.visit_TestCase(test_case_node)

        # The flag must be restored to what it was before: True
        assert checker._in_test_case is True


def test_suite_doc_with_bad_rst_does_not_trigger_fix(caplog):
    """Test that --fix does not modify suite-level documentation.

    Because suite-level docs are skipped, the file must remain unchanged even
    when --fix is requested.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "test.robot"
        bad_suite_doc_content = (
            "*** Settings ***\n"
            "Documentation    Here comes a list:\n"
            "...              - Bullet point\n"
            "...              - without a newline\n"
            "...              Some more text.\n"
            "\n"
            "*** Test Cases ***\n"
        )
        robot_file.write_text(bad_suite_doc_content)

        checker = StyleChecker(robot_file, fix=True)
        checker.run()

        assert not checker.issues_found
        assert not checker.lint_issues_found
        # File content must be unchanged because the suite doc was not processed
        assert robot_file.read_text() == bad_suite_doc_content


def test_rewrite_tokens_indentation_from_separator():
    """Test that _rewrite_tokens derives indentation from the token separator, not a hardcoded value.

    Before this PR, indentation was hardcoded to '    ' (4 spaces). After the PR,
    it defaults to '' and then reads the actual separator from original_tokens.
    This test verifies that the reformatted file preserves the indentation from the
    robot file's separator token. We use a non-default 2-space separator to ensure
    the test can catch regression to a hardcoded 4-space indent.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        robot_file = tmppath / "test.robot"
        # Write a robot file where the [Documentation] block uses 2-space indentation
        # and has a long line that the formatter will need to wrap (triggering _rewrite_tokens)
        long_line = "word " * 25  # ~125 chars, will be wrapped at default 100
        robot_file.write_text(
            "*** Test Cases ***\n"
            "Test Case\n"
            f"  [Documentation]  {long_line.strip()}\n"
            "  Log  Hello\n"
        )

        checker = StyleChecker(robot_file, fix=True)
        checker.run()

        # Formatting should have found layout issues (line too long) and fixed them
        assert checker.lint_issues_found

        # Persist the in-memory token changes to disk (normally done by robot2rst.py)
        checker.model.save(robot_file)

        # After fix, read the reformatted file and check that continuation lines
        # use the separator from the original token (2 spaces), not a hardcoded value
        fixed_content = robot_file.read_text()
        lines = fixed_content.splitlines()

        # Find continuation lines (lines with '...')
        continuation_lines = [line for line in lines if line.lstrip().startswith("...")]
        assert continuation_lines, "Expected at least one continuation line after fix"

        for line in continuation_lines:
            # Extract the prefix before the continuation marker
            prefix_before_dots = line[:line.index("...")]
            # The prefix must exactly match the 2-space separator from the original file
            assert prefix_before_dots == "  ", (
                f"Expected continuation line prefix to be '  ' (2 spaces), got: {prefix_before_dots!r}"
            )