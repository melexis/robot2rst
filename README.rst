.. image:: https://api.travis-ci.com/melexis/robot2rst.svg?branch=master
    :target: https://travis-ci.com/melexis/robot2rst
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

.. _`mlx.traceability`: https://pypi.org/project/mlx.traceability/
.. _`documentation of mlx.traceability`: https://melexis.github.io/sphinx-traceability-extension/readme.html
