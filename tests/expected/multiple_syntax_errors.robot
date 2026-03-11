*** Settings ***
Documentation    Example of multiple syntax errors in a single test case.

*** Test Cases ***
Test with bad bullet list
    [Documentation]  Some dummy title
    ...
    ...  Here comes the bullet list:
    ...
    ...  - Bullet point
    ...  - without a newline at the end
    ...
    ...  Some more text that should be on the next line.
    ...
    ...  here is another error: `` some value should be wrapped in double backticks.
    ...
    Log    Something

