*** Settings ***
Documentation    Example using the space separated plain text format.

*** Test Cases ***
Test with bad bullet list
    [Documentation]     Some dummy title
    ...
    ...  Here comes the bullet list:
    ...
    ...  - Bullet point
    ...  - without a newline at the end
    ...  Some more text that should be on the next line.
    Log    Something
