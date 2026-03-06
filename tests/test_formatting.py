import logging
import sys
import shutil
from pathlib import Path

# Add the project root to the sys.path to allow importing mlx.robot2rst
sys.path.insert(0, str(Path(__file__).parent.parent))

from mlx.robot2rst.robot2rst import main as robot2rst_main

INPUT_DIR = Path(__file__).parent / "input"
OUTPUT_DIR = Path(__file__).parent / "output"
EXPECTED_DIR = Path(__file__).parent / "expected"


def test_fix_adds_missing_newline(caplog):
    file_name = "bad_bullet.robot"
    robot_file_original = INPUT_DIR / file_name
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir()
    robot_file_to_fix = OUTPUT_DIR / file_name
    shutil.copy(robot_file_original, robot_file_to_fix)

    # Prepare arguments for robot2rst
    sys.argv = ["robot2rst", "-i", str(robot_file_to_fix), "--fix"]

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
