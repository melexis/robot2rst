import re
from collections import namedtuple

from robot.api import get_model, Token
from robot.parsing import ModelVisitor


class ParserApplication(ModelVisitor):
    """ Class used to extract all useful info from the .robot file.

    See https://robot-framework.readthedocs.io/en/v6.0.2/autodoc/robot.api.html#inspecting-model

    Attributes:
        tests (list): List of objects with attributes name (str), doc (str) and tags (list).
        variables (dict): Dictionary mapping variables, e.g. '${MESSAGE}', to their values
    """
    TestAttributes = namedtuple('TestAttributes', 'name doc tags')

    def __init__(self, robot_file, *args, **kwargs):
        """ Constructor

        Args:
            robot_file (Path): Path to the .robot file.
        """
        super().__init__(*args, **kwargs)
        self.robot_file = str(robot_file.resolve(strict=True))
        self.model = get_model(self.robot_file)
        self.tests = []
        self.variables = {}

    def run(self):
        self.visit(self.model)

    def visit_VariableSection(self, node):
        for element in node.body:
            element_type = getattr(element, 'type', None)
            if element_type == Token.VARIABLE:
                name = element.get_value(Token.VARIABLE)
                value = ' '.join(element.get_values(Token.ARGUMENT))
                match = re.fullmatch(r"\${(.+)}", value)
                if match:
                    value = match.group(1)
                self.variables[name] = value

    def visit_TestCase(self, node):
        doc = ''
        tags = []
        for element in node.body:
            element_type = getattr(element, 'type', None)
            if element_type == Token.DOCUMENTATION:
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
            elif element_type == Token.TAGS:
                tags = [el.value for el in element.tokens if el.type == Token.ARGUMENT]

        self.tests.append(self.TestAttributes(node.name, doc, tags))
