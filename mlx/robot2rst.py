
'''
Script to convert a robot test file to a traceable RST file
'''

import os
import re
import argparse
import robot

RST_HEADER = '''
.. _{link}:

{titlechars}
{title}
{titlechars}

.. contents:: `Contents`
    :depth: 2
    :local:
'''

RST_FOOTER = '''
'''

SETTINGS_HEADER = '''
--------
Settings
--------
'''

VARIABLES_HEADER = '''
---------
Variables
---------
'''

TEST_CASES_HEADER = '''
----------
Test cases
----------
'''

KEYWORDS_HEADER = '''
--------
Keywords
--------
'''

prefixes = {
    'setting': 'SETTING-',
    'variable': 'VARIABLE-',
    'test_case': 'ITEST-',
    'keyword': 'KEYWORD-',
}

SETTING_TEMPLATE = '''
.. item:: {item} Settings for {caption}

    .. robot-settings::
        :source: {file}
'''

VARIABLE_TEMPLATE = '''
.. item:: {item} Variables for {caption}

    .. robot-variables::
        :source: {file}
'''

TEST_CASE_TEMPLATE = '''
.. item:: {item} {caption}

    .. robot-tests:: ^{name}$
        :source: {file}
'''

KEYWORD_TEMPLATE = '''
.. item:: {item} {caption}

    .. robot-keywords:: {name}
        :source: {file}
'''

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

def add_settings_to_rst(suite, robot_file, h_rst):
    '''
    Add settings to the RsT file

    Args:
        suite (str):        Name of the test suite
        robot_file (str):   Path to the input robot file
        h_rst               Handle to the RsT file
    '''
    h_rst.write(SETTINGS_HEADER)

    h_rst.write(SETTING_TEMPLATE.format(item=to_traceable_item(suite, prefixes['setting']),
                                        caption=suite,
                                        file=os.path.abspath(robot_file)))

def add_variables_to_rst(suite, robot_file, h_rst):
    '''
    Add variables to the RsT file

    Args:
        suite (str):        Name of the test suite
        robot_file (str):   Path to the input robot file
        h_rst               Handle to the RsT file
    '''
    h_rst.write(VARIABLES_HEADER)

    h_rst.write(VARIABLE_TEMPLATE.format(item=to_traceable_item(suite, prefixes['variable']),
                                         caption=suite,
                                         file=os.path.abspath(robot_file)))
def add_tests_to_rst(robot_file, h_rst):
    '''
    Add test cases to the RsT file

    Args:
        robot_file (str):   Path to the input robot file
        h_rst               Handle to the RsT file
    '''

    suite = robot.parsing.TestData(source=robot_file)

    h_rst.write(TEST_CASES_HEADER)

    for test in suite.testcase_table.tests:
        h_rst.write(TEST_CASE_TEMPLATE.format(item=to_traceable_item(test.name, prefixes['test_case']),
                                              caption=test.name,
                                              name=test.name,
                                              file=os.path.abspath(robot_file)))

def add_keywords_to_rst(robot_file, h_rst):
    '''
    Add keywords to the RsT file

    Args:
        robot_file (str):   Path to the input robot file
        h_rst               Handle to the RsT file
    '''

    try:
        resource = robot.parsing.TestData(source=robot_file)
    except robot.errors.DataError:
        resource = robot.parsing.ResourceFile(source=robot_file)
        resource.populate()

    h_rst.write(KEYWORDS_HEADER)

    for keyword in resource.keywords:
        h_rst.write(KEYWORD_TEMPLATE.format(item=to_traceable_item(keyword.name, prefixes['keyword']),
                                            caption=keyword.name,
                                            name=keyword.name,
                                            file=os.path.abspath(robot_file)))

def generate_robot_2_rst(robot_file, rst_file):
    '''
    Generate a rst_file from a given robot_file

    Args:
        robot_file (str):   Path to the input robot file
        rst_file (str):     Path to the output RsT file
    '''

    with open(rst_file, 'w') as h_rst:
        suitename = os.path.splitext(os.path.basename(rst_file))[0]
        h_rst.write(RST_HEADER.format(link=suitename.replace(' ', '_'),
                                      titlechars='='*len(suitename),
                                      title=suitename))
        add_settings_to_rst(suitename, robot_file, h_rst)
        add_variables_to_rst(suitename, robot_file, h_rst)
        add_tests_to_rst(robot_file, h_rst)
        add_keywords_to_rst(robot_file, h_rst)
        h_rst.write(RST_FOOTER)

def main():
    '''Main entry point for script: parse arguments and execute'''
    parser = argparse.ArgumentParser(description='Convert robot to RsT.')
    parser.add_argument("--robot", dest='robot_file', help='Input robot file', required=True,
                        action='store')
    parser.add_argument("--rst", dest='rst_file', help='Output RsT file', required=True,
                        action='store')
    parser.add_argument("-k", dest='keyword_prefix', action='store',
                        help="Overrides default 'KEYWORD-' prefix.")
    parser.add_argument("-s", dest='setting_prefix', action='store',
                        help="Overrides default 'SETTING-' prefix.")
    parser.add_argument("-t", dest='test_case_prefix', action='store',
                        help="Overrides default 'ITEST-' prefix.")
    parser.add_argument("-v", dest='variable_prefix', action='store',
                        help="Overrides default 'VARIABLE-' prefix.")

    args = parser.parse_args()

    options = {
        'keyword': args.keyword_prefix,
        'setting': args.setting_prefix,
        'test_case': args.test_case_prefix,
        'variable': args.variable_prefix,
    }
    for key, option in options.items():
        if option is not None:
            prefixes[key] = option

    generate_robot_2_rst(args.robot_file, args.rst_file)

if __name__ == "__main__":
    main()
