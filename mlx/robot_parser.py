from ast import NodeVisitor
from collections import namedtuple

from robot.api import get_model, Token


def extract_tests(robot_file):
    """ Extracts all useful information from the tests in the .robot file.

    Args:
        robot_file (str): Path to the .robot file.

    Returns:
        list: List of objects with attributes name (str), doc (str) and tags (list).
    """
    model = get_model(robot_file)
    parser = TestCaseParser()
    parser.visit(model)
    return parser.tests


class TestCaseParser(NodeVisitor):
    """ Class used to extract all useful info from test cases.

    See https://robot-framework.readthedocs.io/en/latest/autodoc/robot.parsing.html#parsing-data-to-model
    """
    TestAttributes = namedtuple('TestAttributes', 'name doc tags')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tests = []

    def visit_TestCase(self, node):
        doc = ''
        tags = []
        for element in node.body:
            if not hasattr(element, 'type'):
                continue
            if element.type == Token.DOCUMENTATION:
                in_docstring = False
                previous_token = None
                for token in element.tokens:
                    if in_docstring and token.type in (Token.ARGUMENT, Token.EOL, Token.SEPARATOR):
                        if previous_token is None or previous_token.type != Token.CONTINUATION:
                            doc += token.value
                        elif len(token.value) > 2:
                            doc += token.value[2:]  # remove two leading spaces, which are needed to separate the text
                    elif token.type == Token.CONTINUATION:
                        doc = doc.rstrip(' ')
                    elif token.type == Token.DOCUMENTATION:
                        in_docstring = True
                    previous_token = token
            elif element.type == Token.TAGS:
                tags = [el.value for el in element.tokens if el.type == Token.ARGUMENT]

        self.tests.append(self.TestAttributes(node.name, doc, tags))
