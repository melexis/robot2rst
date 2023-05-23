*** Settings ***
Documentation    Example using the space separated plain text format.
Library          OperatingSystem

*** Variables ***
${NAMES}   Create List   First Name  Family Name  Email
${NAD}    ${0x63}
${MESSAGE}     Hello,
...    world!

*** Test Cases ***
First Test
    [Documentation]     Thorough and relatively lengthy documentation for the example test case that
    ...  logs ${MESSAGE} and ${NAD} and ${NAMES}.
    [Tags]              SWRQT-SOME_RQT  ANOTHER-TAG  SWRQT-OTHER_RQT  SYSRQT-SOME_SYSTEM_RQT
                        Log    ${MESSAGE}
                        Log    ${NAD}
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
    ...  Test case with for-loop.
    [Tags]              RQT-SOME_RQT  SYSRQT-SOME_SYSTEM_RQT
                        FOR     ${var}  IN  @{NAMES}
                                Log     ${var}

Comp1: testing 'Special" characters & prefix (with brackets)
    [Documentation]     The item ID will contain COMP1-TESTING_SPECIAL_CHARACTERS_AND_PREFIX_WITH_BRACKETS.
                        Log     Special characters in test case names are supported but not recommended.

*** Keywords ***
My Keyword
    [Documentation]     My keyword's documentation string.
    [Arguments]         ${path}
                        Directory Should Exist    ${path}
