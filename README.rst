.. image:: https://github.com/melexis/robot2rst/actions/workflows/python-package.yml/badge.svg?branch=master
    :target: https://github.com/melexis/robot2rst/actions/workflows/python-package.yml
    :alt: Build status

.. image:: https://img.shields.io/badge/Documentation-published-brightgreen.svg
    :target: https://melexis.github.io/robot2rst/
    :alt: Documentation

.. image:: https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat
    :target: https://github.com/melexis/robot2rst/issues
    :alt: Contributions welcome

=======================
Documentation robot2rst
=======================

This script can convert your .robot files from Robot Framework to reStructuredText (.rst) files with traceable items.

.. contents:: `Contents`
    :depth: 2
    :local:

----
Goal
----

This script allows you to connect your requirements to test cases via the `mlx.traceability`_ Sphinx extension.
Test cases get converted to traceable items. The documentation of each test gets used to generate the body of the item.
Test case names get converted to item IDs with a configurable prefix. Tags can be used to link to other traceable items.

-----
Usage
-----

.. code-block:: console

    $ robot2rst --help

    usage: robot2rst [-h] {convert,stylecheck} ...

    Convert robot test cases to reStructuredText with traceable items.

    positional arguments:
    {convert,stylecheck}  Available commands
        convert             Converts a Robot Framework file to a reStructuredText (.rst) file (default).
        stylecheck          Checks and fixes RST style in Robot documentation blocks.

    options:
    -h, --help            show this help message and exit

    examples:
    # Convert a file (default command)
    robot2rst -i input.robot -o output.rst

    # Explicitly call convert
    robot2rst convert -i input.robot -o output.rst

    # Check style of all .robot files in the current directory and subdirectories
    robot2rst stylecheck --fix


Conversion (Default)
====================

To convert a Robot file to RST:

.. code-block:: console

    robot2rst -i example.robot -o test_plan.rst --prefix ITEST_MY_LIB- \
        --tags SWRQT- SYSRQT- --relationships validates ext_toolname --coverage 100 66.66

    $ robot2rst convert --help

    usage: robot2rst convert [-h] -i ROBOT_FILE -o RST_FILE [--only EXPRESSION] [-p PREFIX]
                            [-r [RELATIONSHIPS ...]] [-t [TAGS ...]] [--include [INCLUDE ...]]
                            [-c [COVERAGE ...]] [--type TYPE] [--trim-suffix]

    options:
    -h, --help            show this help message and exit
    -i ROBOT_FILE, --robot ROBOT_FILE
                            Input robot file
    -o RST_FILE, --rst RST_FILE
                            Output RST file, e.g. my_component_qtp.rst
    --only EXPRESSION     Expression of tags for Sphinx' `only` directive that surrounds all RST content.
    -p PREFIX, --prefix PREFIX
                            Overrides the default 'QTEST-' prefix.
    -r [RELATIONSHIPS ...], --relationships [RELATIONSHIPS ...]
                            Name(s) of the relationship(s) used to link to items in Tags section. Default:
                            'validates'.
    -t [TAGS ...], --tags [TAGS ...]
                            Python regexes for matching tags to treat as traceable targets. Matches all by
                            default.
    --include [INCLUDE ...]
                            Python regexes for matching tags to filter test cases.
    -c [COVERAGE ...], --coverage [COVERAGE ...]
                            Minimum coverage percentages for the item-matrix(es); 1 value per tag in --tags.
    --type TYPE           Type of test ('q' for qualification, 'i' for integration). Default:
                            'qualification'.
    --trim-suffix         If the suffix of any prefix or --tags argument ends with '_-' it gets trimmed to
                            '-'.

Style Checker & Fixer
=====================

You can also check and automatically fix the RST syntax and layout within the ``[Documentation]`` blocks of your Robot files.
This functionality is provided for test case documentation only.

.. code-block:: console

    # Check all .robot files in the current directory
    robot2rst stylecheck

    # Automatically fix issues and set a custom line length
    robot2rst stylecheck --fix --line-length 120

    $ robot2rst stylecheck --help

    usage: robot2rst stylecheck [-h] [--fix] [--fail-on-layout] [--line-length LINE_LENGTH]
                                [--enable-bold-headers] [--trailing-continuation]
                                [paths ...]

    positional arguments:
      paths                 One or more paths to files or folders to check. Default: current
                            directory.

    options:
      -h, --help            show this help message and exit
      --fix                 Automatically fix RST formatting inside Robot documentation
                            blocks.
      --fail-on-layout      Fail on RST layout issues as well as syntax issues.
      --line-length LINE_LENGTH
                            Max line length for RST blocks (note: the line length does not
                            include the length of the [Documentation] tag for example).
                            Default: 100.
      --enable-bold-headers
                            Make sure that bold lines are seen as header.
      --trailing-continuation
                            Add a trailing '...' continuation to preserve a blank line at the
                            end of the docstring.



.. note::
    The style checker will only process documentation within ``[Test Case]`` sections. It ignores suite-level and
    keyword documentation.


---------------
Pre-commit Hook
---------------

You can use ``robot2rst`` as a pre-commit hook to ensure your Robot documentation stays correctly formatted.
Add this to your ``.pre-commit-config.yaml``:

.. code-block:: yaml

    repos:
      - repo: https://github.com/melexis/robot2rst
        rev: 3.7.0  # Use the latest stable release
        hooks:
          - id: robot2rst-stylecheck
            args: ["--fix", "--line-length", "100"]

-------------
Configuration
-------------

To include the script's output in your documentation you want to add the aforementioned extension to your
``extensions`` list in your *conf.py* like so:

.. code-block:: python

    extensions = [
        'mlx.traceability',
    ]

Please read the `documentation of mlx.traceability`_ for additional configuration steps.

If you use the ``--only`` input argument, you should also add |sphinx_selective_exclude.eager_only|_ to the
``extensions`` list to prevent mlx.traceability from parsing the content and ignoring the effect of the
``only`` directive.

.. _`mlx.traceability`: https://pypi.org/project/mlx.traceability/
.. _`documentation of mlx.traceability`: https://melexis.github.io/sphinx-traceability-extension/readme.html
.. |sphinx_selective_exclude.eager_only| replace:: ``'sphinx_selective_exclude.eager_only'``
.. _sphinx_selective_exclude.eager_only: https://pypi.org/project/sphinx-selective-exclude/
