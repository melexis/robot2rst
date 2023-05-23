<%
import re

title = suite
match = re.match(r"(.+)_[qi]tp", suite)
if match:
    title = f"{test_type.capitalize()} Test Plan for {match.group(1)}"

def to_traceable_item(name, prefix=''):
    '''
    Converts a name, to the name of a traceabile item

    Args:
        name (str): The string to convert

    Returns:
        str: The name of the traceable item name of the given anything
    '''
    # Apply prefix
    name = prefix + name
    # Move to capitals
    name = name.upper()
    # Replace ' : ' (or alike) by '-'
    name = re.sub('\s*:\s*', '-', name)
    # Replace '&' by 'AND'
    name = name.replace('&', 'AND')
    # Remove other special characters
    name = re.sub('[^\w\s_-]', '', name)
    # Replace spaces with single underscore
    name = re.sub('\s+', '_', name)
    return name


def generate_body(input_string):
    ''' Generates the body of the item based on the raw docstring of the robot test case.

    Indents and line endings are preserved, except for the indent of the first line, which gets removed.

    Args:
        input_string (str): Raw docstring.

    Returns:
        str: Body of the item, which is the input string with an added indent of four spaces
    '''
    indent = ' ' * 4
    newline = '\n'
    line_separator = newline + indent
    for variable, value in parser.variables.items():
        if variable in input_string:
            input_string = input_string.replace(variable, value)
    input_string = input_string.replace(r'\r', '').strip()
    lines = input_string.split(newline)
    intermediate_output = indent
    for line in lines:
        if line:
            intermediate_output += line.rstrip()
        else:
            intermediate_output =  intermediate_output.rstrip(' ')
        intermediate_output += line_separator
    return intermediate_output.rstrip()
%>\
.. _${suite.replace(' ', '_')}:

${'='*len(title)}
${title}
${'='*len(title)}

.. contents:: `Contents`
    :depth: 2
    :local:


% for test in parser.tests:
.. item:: ${to_traceable_item(test.name, prefix)} ${test.name}
% for relationship, tag_regex, _ in relationship_config:
<%
filtered_tags = [tag for tag in test.tags if re.search(tag_regex, tag)]
%>\
    % if filtered_tags:
    :${relationship}: ${' '.join(filtered_tags)}
    % endif
% endfor

% if str(test.doc):
${generate_body(str(test.doc))}

%endif
% endfor

% if gen_matrix:
Traceability Matrix
===================

% for relationship, tag_regex, coverage in relationship_config:
The below table traces the ${test_type} test cases to the ${relationship} requirements.

.. item-matrix:: Linking these ${test_type} test cases to the ${relationship} requirements
    :source: ${prefix}
    :target: ${tag_regex}
    :sourcetitle: ${test_type.capitalize()} test case
    :targettitle: ${relationship} requirement
    :type: ${relationship}
    :stats:
    :group: top
    :nocaptions:
    % if coverage:
    :coverage: >= ${coverage}
    % endif

% endfor
% endif
