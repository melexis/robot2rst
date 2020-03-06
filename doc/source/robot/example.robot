*** Settings ***
Documentation    Example using the space separated plain text format.
Library          OperatingSystem

*** Variables ***
${MESSAGE}       Hello, world!

*** Test Cases ***
First Test
    [Documentation]     Thorough and relatively lengthy documentation for the first example
    ...                 test case.
    [Tags]              SWRQT-SOME_RQT  ANOTHER-TAG  SWRQT-OTHER_RQT  SYSRQT-SOME_SYSTEM_RQT
                        Log    ${MESSAGE}
                        My Keyword    /tmp

Undocumented Test
                        Should Be Equal     ${MESSAGE}    Hello, world!

Another Test
    [Documentation]     Short documentation string.
    [Tags]              RQT-SOME_RQT  SYSRQT-SOME_SYSTEM_RQT
                        Log    ${MESSAGE}
                        My Keyword    /tmp

*** Keywords ***
My Keyword
    [Documentation]     My keyword's documentation string.
    [Arguments]         ${path}
                        Directory Should Exist    ${path}
