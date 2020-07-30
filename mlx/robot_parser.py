from ast import NodeVisitor
from collections import namedtuple


def extract_tests(robot_file):
    """ Extracts all useful information from the tests in the .robot file.

    Args:
        robot_file (str): Path to the .robot file.

    Returns:
        list: List of objects with attributes name (str), doc (str) and tags (list).
    """
    try:
        from robot.api import get_model  # pylint: disable=import-outside-toplevel
        model = get_model(robot_file)
        parser = TestCaseParser()
        parser.visit(model)
        return parser.tests
    except ImportError:
        from robot.parsing.model import TestData  # pylint: disable=import-outside-toplevel
        return TestData(source=robot_file).testcase_table.tests


class TestCaseParser(NodeVisitor):
    """ Class used to extract all useful info from test cases.

    See https://robot-framework.readthedocs.io/en/latest/autodoc/robot.parsing.html#parsing-data-to-model
    """
    TestAttributes = namedtuple('TestAttributes', 'name doc tags')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tests = []

    def visit_TestCase(self, node):
        from robot.api import Token  # pylint: disable=import-outside-toplevel
        doc = ''
        tags = []
        for element in node.body:
            if element.type == Token.DOCUMENTATION:
                for token in element.tokens:
                    if token.type == Token.ARGUMENT:
                        doc += token.value + ' '
                    elif token.type == Token.EOL:
                        doc += r'\n'
            elif element.type == Token.TAGS:
                tags = [el.value for el in element.tokens if el.type == Token.ARGUMENT]

        self.tests.append(self.TestAttributes(node.name, doc, tags))
