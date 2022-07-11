<%
import re

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
    # Move ' : ' (or alike) to '-'
    name = re.sub('\s*:\s*', '-', name)
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

${'='*len(suite)}
${suite}
${'='*len(suite)}

.. contents:: `Contents`
    :depth: 2
    :local:


% for test in tests:
.. item:: ${to_traceable_item(test.name, prefix)} ${test.name}
% for relationship, tag_regex in relationship_to_tag_mapping.items():
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

% for relationship, tag_regex in relationship_to_tag_mapping.items():
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

% endfor
% endif
