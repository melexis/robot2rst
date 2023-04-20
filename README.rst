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

    robot2rst -i example.robot -o test_plan.rst --prefix ITEST_MY_LIB- \
        --tags SWRQT- SYSRQT- --relationships validates ext_toolname --coverage 100 66.66

    $ robot2rst --help

    usage: robot2rst [-h] -i ROBOT_FILE -o RST_FILE [--only EXPRESSION] [-p PREFIX]
                     [-r [RELATIONSHIPS [RELATIONSHIPS ...]]] [-t [TAGS [TAGS ...]]]
                     [--type TYPE] [--trim-suffix]

    Convert robot test cases to reStructuredText with traceable items.

    options:
      -h, --help            show this help message and exit
      -i ROBOT_FILE, --robot ROBOT_FILE
                            Input robot file
      -o RST_FILE, --rst RST_FILE
                            Output RST file, e.g. my_component_qtp.rst
      --only EXPRESSION     Expression of tags for Sphinx' `only` directive that surrounds all RST
                            content. By default, no `only` directive is generated.
      -p PREFIX, --prefix PREFIX
                            Overrides the default 'QTEST-' prefix.
      -r [RELATIONSHIPS ...], --relationships [RELATIONSHIPS ...]
                            Name(s) of the relationship(s) used to link to items in Tags section.
                            The default value is 'validates'.
      -t [TAGS ...], --tags [TAGS ...]
                            Regex(es) for matching tags to add a relationship link for. All tags
                            get matched by default.
      -c [COVERAGE ...], --coverage [COVERAGE ...]
                            Minumum coverage percentages for the item-matrix(es); 1 value per tag
                            in -t, --tags.
      --type TYPE           Give value that starts with 'q' or 'i' (case-insensitive) to
                            explicitly define the type of test: qualification/integration test.
                            The default is 'qualification'.
      --trim-suffix         If the suffix of any prefix or --tags argument ends with '_-' it gets
                            trimmed to '-'.


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
