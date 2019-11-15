<%
import robot
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
%>\
.. _${suite.replace(' ', '_')}:

${'='*len(suite)}
${suite}
${'='*len(suite)}

.. contents:: `Contents`
    :depth: 2
    :local:

--------
Settings
--------

.. item:: ${to_traceable_item(suite, prefixes['setting'])} Settings for ${suite}

    .. robot-settings::
        :source: ${robot_file}

---------
Variables
---------

.. item:: ${to_traceable_item(suite, prefixes['variable'])} Variables for ${suite}

    .. robot-variables::
        :source: ${robot_file}

----------
Test cases
----------

% for test in robot.parsing.TestData(source=robot_file).testcase_table.tests:
.. item:: ${to_traceable_item(test.name, prefixes['test_case'])} ${test.name}
% if test.tags:
    :validates: ${' '.join([tag for tag in test.tags if re.search(tag_regex, tag)])}
% endif

    .. robot-tests:: ^${test.name}$
        :source: ${robot_file}

% endfor
--------
Keywords
--------
<%
try:
    resource = robot.parsing.TestData(source=robot_file)
except robot.errors.DataError:
    resource = robot.parsing.ResourceFile(source=robot_file)
    resource.populate()
%>
% for keyword in resource.keywords:
.. item:: ${to_traceable_item(keyword.name, prefixes['keyword'])} ${keyword.name}

    .. robot-keywords:: ${keyword.name}
        :source: ${robot_file}
% endfor
