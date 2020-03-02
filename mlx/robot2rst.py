
''' Script to convert a robot test file to a reStructuredText file with traceable items '''
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


def generate_robot_2_rst(robot_file, rst_file, prefix, tag_regex, relationship):
    """
    Calls mako template function and passes all needed parameters.

    Args:
        robot_file (Path): Path to the input file (.robot).
        rst_file (Path): Path to the output file (.rst).
        prefix (str): Prefix of generated item IDs.
        tag_regex (str): Regular expression for matching tags to add a relationship link for.
        relationship (str): Name of the relationship.
    """
    render_template(
        rst_file,
        suite=rst_file.stem,
        robot_file=str(robot_file.resolve(strict=True)),
        prefix=prefix,
        tag_regex=tag_regex,
        relationship=relationship,
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
    parser.add_argument("-i", "--robot", dest='robot_file', help='Input robot file', required=True,
                        action='store')
    parser.add_argument("-o", "--rst", dest='rst_file', help='Output RsT file', required=True,
                        action='store')
    parser.add_argument("-t", dest='test_case_prefix', action='store', default='ITEST-',
                        help="Overrides default 'ITEST-' prefix.")
    parser.add_argument("-r", "--relationship", action='store', default='validates',
                        help="Name of the relationship used to link to items in Tags section.")
    parser.add_argument("--tags", dest='tag_regex', action='store', default='.*',
                        help="Regex for matching tags to add a relationship link for. All tags get matched by default.")
    parser.add_argument("--trim-suffix", action='store_true',
                        help="If the suffix of any prefix or --tags argument ends with '_-' it gets trimmed to '-'.")

    args = parser.parse_args()

    prefix = args.test_case_prefix
    if args.trim_suffix:
        prefix = _tweak_prefix(prefix)

    tag_regex = args.tag_regex
    if args.trim_suffix:
        tag_regex = _tweak_prefix(tag_regex)

    generate_robot_2_rst(Path(args.robot_file), Path(args.rst_file), prefix, tag_regex, args.relationship)


if __name__ == "__main__":
    main()
