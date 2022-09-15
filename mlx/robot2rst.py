
''' Script to convert a robot test file to a reStructuredText file with traceable items '''
import argparse
import logging
from textwrap import indent
from pathlib import Path

from mako.exceptions import RichTraceback
from mako.template import Template

from .robot_parser import extract_tests

TEMPLATE_FILE = Path(__file__).parent.joinpath('robot2rst.mako')
LOGGER = logging.getLogger(__name__)


def render_template(destination, only="", **kwargs):
    """
    Renders the Mako template, and writes output file to the specified destination.

    Args:
        destination (Path): Location of the output file.
        only (str): Expression for 'only' directive, which will only be added when this string is not empty.
        **kwargs (dict): Variables to be used in the Mako template.
    Raises:
        CRITICAL: Error was raised by Mako template.
    """
    destination.parent.mkdir(parents=True, exist_ok=True)
    template = Template(filename=str(TEMPLATE_FILE))
    try:
        rst_content = template.render(**kwargs)
    except Exception:
        traceback = RichTraceback()
        for entry in traceback.traceback[-2:]:
            LOGGER.critical("File %s, line %s, in %s: %r", *entry)
    else:
        if only:
            rst_content = f".. only:: {only}\n\n{indent(rst_content, ' ' * 4)}"
        with open(str(destination), 'w', encoding='utf-8', newline='\n') as rst_file:
            rst_file.write(rst_content)


def generate_robot_2_rst(robot_file, rst_file, prefix, relationship_to_tag_mapping, gen_matrix, **kwargs):
    """
    Calls mako template function and passes all needed parameters.

    Args:
        robot_file (Path): Path to the input file (.robot).
        rst_file (Path): Path to the output file (.rst).
        prefix (str): Prefix of generated item IDs.
        relationship_to_tag_mapping (dict): Dictionary that maps each relationship to the corresponding tag regex.
        gen_matrix (bool): True if traceability matrices are to be generated, False if not.
    """
    render_template(
        rst_file,
        tests=extract_tests(str(robot_file.resolve(strict=True))),
        suite=rst_file.stem,
        prefix=prefix,
        relationship_to_tag_mapping=relationship_to_tag_mapping,
        gen_matrix=gen_matrix,
        **kwargs,
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
    parser = argparse.ArgumentParser(description='Convert robot test cases to reStructuredText with traceable items.')
    parser.add_argument("-i", "--robot", dest='robot_file', help='Input robot file', required=True,
                        action='store')
    parser.add_argument("-o", "--rst", dest='rst_file', help='Output RST file', required=True,
                        action='store')
    parser.add_argument("--only", dest="expression", default="",
                        help="Expression of tags for Sphinx' `only` directive that surrounds all RST content. "
                        "By default, no `only` directive is generated.")
    parser.add_argument("-p", "--prefix", action='store', default='QTEST-',
                        help="Overrides the default 'QTEST-' prefix.")
    parser.add_argument("-r", "--relationships", nargs='*',
                        help="Name(s) of the relationship(s) used to link to items in Tags section. The default value "
                             "is 'validates'.")
    parser.add_argument("-t", "--tags", nargs='*',
                        help="Regex(es) for matching tags to add a relationship link for. All tags get matched by "
                             "default.")
    parser.add_argument("--type", default='q',
                        help="Give value that starts with 'q' or 'i' (case-insensitive) to explicitly define "
                             "the type of test: qualification/integration test. The default is 'qualification'.")
    parser.add_argument("--trim-suffix", action='store_true',
                        help="If the suffix of any prefix or --tags argument ends with '_-' it gets trimmed to '-'.")

    logging.basicConfig(level=logging.INFO)
    args = parser.parse_args()
    gen_matrix = True
    if not args.tags:
        args.tags = ['.*']
        gen_matrix = False
        LOGGER.warning("No traceability matrix will be generated because of the use of default tag regex %r.",
                       args.tags[0])
    if not args.relationships:
        args.relationships = ['validates']

    type_map = {
        'i': 'integration',
        'q': 'qualification',
    }
    if args.type and args.type.lower()[0] in type_map:
        test_type = type_map[args.type.lower()[0]]
    else:
        raise ValueError(f"The --type argument is invalid: expected a value that starts with {' or '.join(type_map)}; "
                         f"got {args.type.lower()!r}.")

    prefix = _tweak_prefix(args.prefix) if args.trim_suffix else args.prefix
    tag_regexes = [_tweak_prefix(regex) if args.trim_suffix else regex for regex in args.tags]
    relationships = args.relationships

    if len(relationships) != len(tag_regexes):
        raise ValueError(f"Number of relationships ({len(relationships)}) is not equal to number of tag regexes "
                         f"({len(tag_regexes)}) given.")
    relationship_to_tag_mapping = dict(zip(relationships, tag_regexes))

    generate_robot_2_rst(Path(args.robot_file), Path(args.rst_file), prefix, relationship_to_tag_mapping, gen_matrix,
                         test_type=test_type, only=args.expression)


if __name__ == "__main__":
    main()
