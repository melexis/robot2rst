
'''
Script to convert a robot test file to an RST file with traceability items
'''

import argparse
import logging
from pathlib import Path
from io import FileIO, TextIOWrapper

from mako.exceptions import RichTraceback
from mako.runtime import Context
from mako.template import Template

TEMPLATE_FILE = Path(__file__).parent.joinpath('robot2rst.mako')


def render_template(destination, **kwargs):
    """
    Renders the Mako template, and writes output file to the specified destination.

    Args:
        destination (Path):             Location of the output file.
        **kwargs (dict):                Variables to be used in the Mako template.
    Raises:
        CRITICAL:                       Error is raised by Mako template.
    """
    destination.parent.mkdir(parents=True, exist_ok=True)
    out = TextIOWrapper(FileIO(str(destination), 'w'), encoding='utf-8', newline='\n')
    template = Template(filename=str(TEMPLATE_FILE), output_encoding='utf-8', input_encoding='utf-8')
    try:
        template.render_context(Context(out, **kwargs))
    except OSError:
        traceback = RichTraceback()
        for (filename, lineno, function, line) in traceback.traceback:
            logging.critical("File %s, line %s, in %s", filename, lineno, function)
            logging.critical(line, "\n")
        logging.critical("%s: %s", str(traceback.error.__class__.__name__), traceback.error)
    finally:
        out.close()


def generate_robot_2_rst(robot_file, rst_file, prefixes, tag_regex):
    """
    Calls mako template function and passes all needed parameters.

    Args:
        robot_file (Path): Path to the input file (.robot).
        rst_file (Path): Path to the output file (.rst).
        prefixes (dict): Dictionary of prefixes for each category.
        tag_regex (str): Regular expression for matching tags to add a relationship link for.
    """
    render_template(
        rst_file,
        suite=rst_file.stem,
        robot_file=str(robot_file.resolve(strict=True)),
        prefixes=prefixes,
        tag_regex=tag_regex,
    )


def _tweak_prefix(prefix):
    """ If a prefix or regex ends with '_-', change it to end with '-' instead.

    Args:
        prefix (str): Prefix that might need tweaking.

    Returns:
        (str) Prefix that has been tweaked if it needed to.
    """
    if prefix.endswith('_-'):
        prefix = prefix.rstrip('_-') + '-'
    return prefix


def main():
    '''Main entry point for script: parse arguments and execute'''
    parser = argparse.ArgumentParser(description='Convert robot to RsT.')
    parser.add_argument("--robot", dest='robot_file', help='Input robot file', required=True,
                        action='store')
    parser.add_argument("--rst", dest='rst_file', help='Output RsT file', required=True,
                        action='store')
    parser.add_argument("-k", dest='keyword_prefix', action='store', default='KEYWORD-',
                        help="Overrides default 'KEYWORD-' prefix.")
    parser.add_argument("-s", dest='setting_prefix', action='store', default='SETTING-',
                        help="Overrides default 'SETTING-' prefix.")
    parser.add_argument("-t", dest='test_case_prefix', action='store', default='ITEST-',
                        help="Overrides default 'ITEST-' prefix.")
    parser.add_argument("-v", dest='variable_prefix', action='store', default='VARIABLE-',
                        help="Overrides default 'VARIABLE-' prefix.")
    parser.add_argument("--tags", dest='tag_regex', action='store', default='.*',
                        help="Regex for matching tags to add a relationship link for. All tags get matched by default.")
    parser.add_argument("--trim-suffix", action='store_true',
                        help="If the suffix of any prefix or --tags argument ends with '_-' it gets trimmed to '-'")

    args = parser.parse_args()

    prefixes = {
        'keyword': args.keyword_prefix,
        'setting': args.setting_prefix,
        'test_case': args.test_case_prefix,
        'variable': args.variable_prefix,
    }
    for key, prefix in prefixes.items():
        if args.trim_suffix:
            prefixes[key] = _tweak_prefix(prefix)

    tag_regex = args.tag_regex
    if args.trim_suffix:
        tag_regex = _tweak_prefix(tag_regex)

    generate_robot_2_rst(Path(args.robot_file), Path(args.rst_file), prefixes, tag_regex)


if __name__ == "__main__":
    main()
