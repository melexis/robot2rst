<%
import re
import textwrap

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

    Args:
        input_string (str): Raw docstring.

    Returns:
        str: Indented body, which has been word wrapped to not exceed 120 characters
    '''
    indent = ' ' * 4
    newline = '\n'
    line_separator = newline + indent
    input_string = input_string.replace(r'\r', '')
    if input_string.startswith('*RAW*'):
        line_ending = r'\n'
    else:
        input_string = input_string.replace(r'\n', ' ')
        input_string = textwrap.fill(input_string, 115)
        line_ending = '\n'
    lines = input_string.split(line_ending)
    intermediate_output = line_separator.join(map(str.strip, lines))
    intermediate_output = intermediate_output.replace(newline + indent + newline, newline * 2)
    return indent + intermediate_output.strip()
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
${generate_body(str(test.doc).strip())}

%endif
% endfor

% if gen_matrix:
Traceability matrix
===================

% for relationship, tag_regex in relationship_to_tag_mapping.items():
The below table traces the integration test cases to the ${relationship} requirements.

.. item-matrix:: Linking these integration test cases to the ${relationship} requirements
    :source: ${prefix}
    :target: ${tag_regex}
    :sourcetitle: Integration test case
    :targettitle: ${relationship} requirement
    :type: ${relationship}
    :stats:
    :group:
    :nocaptions:

% endfor
% endif
