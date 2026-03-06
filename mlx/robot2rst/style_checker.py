"""
RST style checker and fixer for Robot Framework documentation.
"""

import logging
import itertools
import sys

from docstrfmt.docstrfmt import Manager, IgnoreMessagesReporter, pairwise
from docstrfmt.main import Reporter
from docstrfmt.exceptions import InvalidRstError, InvalidRstErrors
from docutils import nodes

from robot.api import Token, get_model
from robot.parsing import ModelVisitor

LOGGER = logging.getLogger("robot2rst")


class StyleManager(Manager):
    """Overrides the default docstrfmt Manager to be more aggressive in fixing formatting issues,
    but also more tolerant of errors.
    """
    def __init__(self, current_file):
        super().__init__(current_file=current_file, reporter=Reporter())
        # Override settings for aggressive formatting but high error tolerance
        self.settings.report_level = 5  # Only Critical
        self.settings.halt_level = 6    # Never Halt

    def _pre_process(self, node: nodes.Node, line_offset: int, block_length: int) -> None:
        """Preprocess nodes.

        This does some preprocessing to all nodes that is generic across node types and
        is therefore most convenient to do as a simple recursive function rather than as
        part of the big dispatcher class.

        """
        # Strip all system_message nodes. (Just formatting them with no markup isn't enough, since that
        # could lead to extra spaces or empty lines between other elements.)
        errors = [
            child
            for child in node.children
            if isinstance(child, nodes.system_message)
            and child.attributes["type"] != "INFO"  # type: ignore[attr]
            and child.children[0].astext()
            not in IgnoreMessagesReporter.ignored_messages
        ]
        if errors:
            self.error_count += len(errors)
            # Instead of raising, just log a warnings of the errors found.
            # This allows us to be more tolerant of formatting issues, while still notifying the user.
            if not self.settings.halt_level > 5:
                raise InvalidRstErrors(
                    [
                        InvalidRstError(
                            self.current_file,
                            error.attributes["type"],
                            (block_length - 1 if error.line is None else error.line)
                            + line_offset,
                            error.children[0].children[0].astext(),  # type: ignore[attr]
                        )
                        for error in errors
                    ]
                )
            else:
                for error in errors:
                    LOGGER.warning(
                        "%s:%d: %s",
                        self.current_file,
                        (block_length - 1 if error.line is None else error.line) + line_offset,
                        error.children[0].children[0].astext(),  # type: ignore[attr]
                    )
        node.children = [
            child
            for child in node.children
            if not isinstance(child, nodes.system_message)
        ]

        # Match references to targets, which helps later with distinguishing whether they're anonymous.
        for reference, target in pairwise(node.children):
            if isinstance(reference, nodes.reference) and isinstance(
                target, nodes.target
            ):
                reference.attributes["target"] = target
        start = None
        for i, child in enumerate(itertools.chain(node.children, [None])):  # type: ignore[attr]
            in_run = start is not None
            is_target = isinstance(child, nodes.target)
            if in_run and not is_target:
                # Anonymous targets have a value of `[]` for "names", which will sort to the top. Also,
                # it's important here that `sorted` is stable, or anonymous targets could break.
                node.children[start:i] = sorted(  # type: ignore[arg-type]
                    node.children[start:i],
                    key=lambda t: t.attributes["names"],  # type: ignore[arg-type]
                )
                start = None
            elif not in_run and is_target:
                start = i

        # Recurse.
        for child in node.children:
            self._pre_process(child, line_offset, block_length)


class StyleChecker(ModelVisitor):
    """ Class used to extract all Documentation nodes from the .robot file.

    See https://robot-framework.readthedocs.io/en/v6.0.2/autodoc/robot.api.html#inspecting-model

    Attributes:
        issues_found (bool): Whether any RST syntax issues were found.
        lint_issues_found (bool): Whether any RST layout issues were found.
    """
    def __init__(self, robot_file, fix=False):
        """Constructor

        Args:
            robot_file (Path): Path to the robot file.
            fix (bool): Whether to automatically fix issues. Defaults to False.
        """
        self.robot_file = robot_file
        self.fix = fix
        self.model = get_model(robot_file)

        self.issues_found = False
        self.lint_issues_found = False

    def run(self):
        self.visit(self.model)

    def visit_Documentation(self, node):
        doc_string = node.value
        if not doc_string.strip():
            return

        manager = StyleManager(current_file=self.robot_file)

        doc_node = manager.parse_string(doc_string, line_offset=node.lineno-1)  # , file=self.robot_file
        formatted_doc = manager.format_node(103, doc_node).rstrip()
        if manager.error_count > 0:
            self.issues_found = True

        if doc_string.strip() == formatted_doc.strip():
            return

        self.lint_issues_found = True
        if self.fix:
            LOGGER.info("%s:%d: Applying RST layout fixes", self.robot_file, node.lineno)
            self._rewrite_tokens(node, formatted_doc)
        else:
            LOGGER.info("%s:%d: RST syntax/layout issues found. Use --fix to resolve.", self.robot_file, node.lineno)

    def _rewrite_tokens(self, node, formatted_doc):
        """Rebuilds the Documentation node tokens for Robot Framework to save later.

        Args:
            node: The Documentation node to rewrite.
            formatted_doc: The new documentation string to use for the node.
        """
        lines = formatted_doc.splitlines()

        # Start with the [Documentation] header
        new_tokens = [
            Token(Token.SEPARATOR, "    "),
            Token(Token.DOCUMENTATION, "[Documentation]"),
            Token(Token.SEPARATOR, "  " if lines else ""),
        ]

        if lines:
            # First line
            new_tokens.extend([
                Token(Token.ARGUMENT, lines[0]),
                Token(Token.EOL, "\n")
            ])
            # Subsequent lines use the '...' continuation
            for line in lines[1:]:
                new_tokens.extend([
                    Token(Token.SEPARATOR, "    "),
                    Token(Token.CONTINUATION, "..."),
                    Token(Token.SEPARATOR, " " if line else ""),
                    Token(Token.ARGUMENT, line),
                    Token(Token.EOL, "\n")
                ])
            # End with a continuation to preserve blank line at the end of the docstring
            new_tokens.extend([
                    Token(Token.SEPARATOR, "    "),
                    Token(Token.CONTINUATION, "..."),
                    Token(Token.EOL, "\n")
            ])
        else:
            new_tokens.append(Token(Token.EOL, "\n"))

        node.tokens = tuple(new_tokens)
