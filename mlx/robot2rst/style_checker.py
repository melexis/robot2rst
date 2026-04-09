"""
RST style checker and fixer for Robot Framework documentation.
"""

import logging
import itertools
import re

from docstrfmt.docstrfmt import Manager, IgnoreMessagesReporter, pairwise
from docstrfmt.main import Reporter
from docutils import nodes

from robot.api import Token, get_model
from robot.parsing import ModelVisitor

LOGGER = logging.getLogger("robot2rst")


class StyleManager(Manager):
    """Overrides the default docstrfmt Manager to be more aggressive in fixing formatting issues,
    but also more tolerant of errors.
    """
    def __init__(self, current_file, line_map=None):
        super().__init__(current_file=current_file, reporter=Reporter())
        self.line_map = line_map
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
            and child.children
            and child.children[0].astext()
            not in IgnoreMessagesReporter.ignored_messages
        ]
        if errors:
            self.error_count += len(errors)
            # Log warnings instead of raising to be more tolerant of formatting issues.
            for error in errors:
                # relative_line is 1-indexed from docutils
                relative_line = error.line if error.line is not None else 1
                # Convert 1-indexed error line to 0-indexed map index
                map_idx = relative_line - 1
                # Map back to original relative line
                if self.line_map and 0 <= map_idx < len(self.line_map):
                    corrected_relative_line = self.line_map[map_idx] + 1
                else:
                    corrected_relative_line = relative_line
                # Calculate absolute line in .robot file
                absolute_line = corrected_relative_line + line_offset
                LOGGER.warning(
                    "%s:%d: %s",
                    self.current_file,
                    absolute_line,
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
    def __init__(self, robot_file, fix=False, **kwargs):
        """Constructor

        Args:
            robot_file (Path): Path to the robot file.
            fix (bool): Whether to automatically fix issues. Defaults to False.
            **kwargs: Arbitrary keyword arguments, including 'line_length'.
        """
        self.robot_file = robot_file
        self.fix = fix
        self.line_length = kwargs.get('line_length', 100)
        self.enable_bold_headers = kwargs.get('enable_bold_headers', False)
        self.trailing_continuation = kwargs.get('trailing_continuation', False)
        self.model = get_model(robot_file)

        self.issues_found = False
        self.lint_issues_found = False

    def run(self):
        self.visit(self.model)

    def visit_Documentation(self, node):
        original_doc_string = node.value
        doc_string = original_doc_string
        if not doc_string.strip():
            return

        original_lines = doc_string.splitlines(keepends=True)
        current_map = list(range(len(original_lines)))

        if self.enable_bold_headers:
            # 1. Fix 'smushed' bold lines/headers (**text** on its own line will be seen as a header/title).
            bold_insertions = 0

            def fix_bold_header(match):
                nonlocal bold_insertions
                if not match.group('before') or not match.group('after'):
                    self.lint_issues_found = True
                    start_pos = match.start()
                    line_idx = doc_string[:start_pos].count('\n') + bold_insertions
                    current_map.insert(line_idx + 1, current_map[line_idx])
                    if not match.group('before') and not match.group('after'):
                        current_map.insert(line_idx + 2, current_map[line_idx])
                        bold_insertions += 2
                    else:
                        bold_insertions += 1
                    extra = 2 if match.group('before') else 1
                    line_number = node.lineno + doc_string[:match.start()].count("\n") + extra
                    LOGGER.warning("%s:%d: Smushed bold header detected: '%s'. Added blank lines to ensure it is "
                                   "treated as a title.", self.robot_file, line_number, match.group("header"))

                return f"\n\n{match.group('indent')}{match.group('header')}\n\n"

            pattern = r'(?P<before>[\n])?\n(?P<indent>[ \t]*)(?P<header>\*\*(?:(?!\*\*).)+\*\*)\n(?P<after>\n)?'
            doc_string = re.sub(pattern, fix_bold_header, doc_string)

        if self.fix:
            # 2. Fix 'smushed' lists
            list_insertions = 0

            def fix_smushed_lists(match):
                nonlocal list_insertions
                list_item = match.group(3)
                start_pos = match.start()
                line_idx = doc_string[:start_pos].count('\n') + list_insertions
                current_map.insert(line_idx + 1, current_map[line_idx])
                list_insertions += 1

                return f"{match.group(1)}\n\n{match.group(2)}{list_item} "

            doc_string, count = re.subn(r'([^\n])\n([ \t]*)([-*+]) ', fix_smushed_lists, doc_string)
            if count > 0:
                LOGGER.warning("%s:%d: Fixed possible 'smushed' lists", self.robot_file, node.lineno)

        manager = StyleManager(current_file=self.robot_file, line_map=current_map)
        try:
            doc_node = manager.parse_string(doc_string, line_offset=node.lineno-1)
            doc_node.settings.tab_width = 4
            formatted_doc = manager.format_node(self.line_length, doc_node).rstrip()
        except Exception as exc:
            LOGGER.error("%s:%d: Failed to parse/format documentation: %s", self.robot_file, node.lineno, exc)
            self.issues_found = True
            return

        if manager.error_count > 0:
            self.issues_found = True

        if original_doc_string.strip() == formatted_doc.strip():
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
        original_tokens = node.tokens

        indentation = "    "
        if original_tokens:
            # Get indentation from the first separator
            if original_tokens[0].type == Token.SEPARATOR:
                indentation = original_tokens[0].value

        doc_keyword = "[Documentation]"
        for token in original_tokens:
            if token.type == Token.DOCUMENTATION:
                doc_keyword = token.value
                break

        # Start with the original documentation header
        new_tokens = [
            Token(Token.SEPARATOR, indentation),
            Token(Token.DOCUMENTATION, doc_keyword),
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
                    Token(Token.SEPARATOR, indentation),
                    Token(Token.CONTINUATION, "..."),
                    Token(Token.SEPARATOR, "  " if line else ""),
                    Token(Token.ARGUMENT, line),
                    Token(Token.EOL, "\n")
                ])
            if self.trailing_continuation:
                # End with a continuation to preserve blank line at the end of the docstring
                new_tokens.extend([
                        Token(Token.SEPARATOR, indentation),
                        Token(Token.CONTINUATION, "..."),
                        Token(Token.EOL, "\n")
                ])
        else:
            new_tokens.append(Token(Token.EOL, "\n"))

        node.tokens = tuple(new_tokens)
