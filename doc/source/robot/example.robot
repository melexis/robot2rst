*** Settings ***
Documentation    Example using the space separated plain text format.
Library          OperatingSystem

*** Variables ***
${MESSAGE}       Hello, world!

*** Test Cases ***
First Test
    [Documentation]     Thorough and relatively lengthy documentation for the first example
    ...  test case.
    [Tags]              SWRQT-SOME_RQT  ANOTHER-TAG  SWRQT-OTHER_RQT  SYSRQT-SOME_SYSTEM_RQT
                        Log    ${MESSAGE}
                        My Keyword    /tmp

Undocumented Test
                        Should Be Equal     ${MESSAGE}    Hello, world!

Test with documentation in RST syntax
    [Documentation]     An example docstring for which it's important its line endings get preserved.
    ...
    ...  - Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et
    ...    dolore magna aliqua.
    ...  - Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
    ...
    ...      - Nested bullet point
                        Log  The line endings and indents in a docstring get preserved.

Another Test
    [Documentation]
    ...  Short documentation string.
    [Tags]              RQT-SOME_RQT  SYSRQT-SOME_SYSTEM_RQT
                        Log    ${MESSAGE}
                        My Keyword    /tmp

*** Keywords ***
My Keyword
    [Documentation]     My keyword's documentation string.
    [Arguments]         ${path}
                        Directory Should Exist    ${path}
