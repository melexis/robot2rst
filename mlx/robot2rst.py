
''' Script to convert a robot test file to a reStructuredText file with traceable items '''
import argparse
import logging
from pathlib import Path
from io import FileIO, TextIOWrapper

from mako.exceptions import RichTraceback
from mako.runtime import Context
from mako.template import Template

TEMPLATE_FILE = Path(__file__).parent.joinpath('robot2rst.mako')
LOGGER = logging.getLogger(__name__)


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


def generate_robot_2_rst(robot_file, rst_file, prefix, relationship_to_tag_mapping, gen_matrix):
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
        suite=rst_file.stem,
        robot_file=str(robot_file.resolve(strict=True)),
        prefix=prefix,
        relationship_to_tag_mapping=relationship_to_tag_mapping,
        gen_matrix=gen_matrix,
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
    parser.add_argument("-p", "--prefix", action='store', default='ITEST-',
                        help="Overrides the default 'ITEST-' prefix.")
    parser.add_argument("-r", "--relationships", nargs='*',
                        help="Name(s) of the relationship(s) used to link to items in Tags section. The default value "
                             "is 'validates'.")
    parser.add_argument("-t", "--tags", nargs='*',
                        help="Regex(es) for matching tags to add a relationship link for. All tags get matched by "
                             "default.")
    parser.add_argument("--trim-suffix", action='store_true',
                        help="If the suffix of any prefix or --tags argument ends with '_-' it gets trimmed to '-'.")

    logging.basicConfig(level=logging.INFO)
    args = parser.parse_args()
    gen_matrix = True
    if not args.tags:
        args.tags = ['.*']
        gen_matrix = False
        LOGGER.warning(f"No traceability matrix will be generated because of the use of default tag regex "
                       f"{args.tags[0]!r}.")
    if not args.relationships:
        args.relationships = ['validates']

    prefix = _tweak_prefix(args.prefix) if args.trim_suffix else args.prefix
    tag_regexes = [_tweak_prefix(regex) if args.trim_suffix else regex for regex in args.tags]
    relationships = args.relationships

    if len(relationships) != len(tag_regexes):
        raise ValueError(f"Number of relationships ({len(relationships)}) is not equal to number of tag regexes "
                         f"({len(tag_regexes)}) given.")
    relationship_to_tag_mapping = dict(zip(relationships, tag_regexes))

    generate_robot_2_rst(Path(args.robot_file), Path(args.rst_file), prefix, relationship_to_tag_mapping, gen_matrix)


if __name__ == "__main__":
    main()
