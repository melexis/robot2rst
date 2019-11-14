.. image:: https://travis-ci.com/melexis/robot2rst.png?branch=master
    :target: https://travis-ci.com/melexis/robot2rst
    :alt: Build status

.. image:: https://img.shields.io/badge/Documentation-published-brightgreen.png
    :target: https://melexis.github.io/robot2rst/
    :alt: Documentation

.. image:: https://img.shields.io/badge/contributions-welcome-brightgreen.png
    :target: https://github.com/melexis/robot2rst/issues
    :alt: Contributions welcome

=======================
Documentation robot2rst
=======================

This script can convert your .robot files from Robot Framework to reStructuredText (.rst) files with traceable items.

.. contents:: `Contents`
    :depth: 2
    :local:

.. _`mlx.traceability`: https://pypi.org/project/mlx.traceability/

----
Goal
----

This script allows you to connect your requirements to test cases via the `mlx.traceability`_ Sphinx extension.
The `sphinxcontrib-robotdoc`_ Sphinx extension is responsible for embedding the Robot Framework content with syntax
highlighting.

-------------
Configuration
-------------

To include the script's output in your documentation you want to add the two aforementioned extensions to your
``extensions`` list in your *conf.py* like so:

.. code-block:: python

    extensions = [
        'sphinxcontrib_robotdoc',
        'mlx.traceability',
    ]

Please read the `documentation of mlx.traceability`_ and `LaTeX configuration for sphinxcontrib-robotdoc`_ for
additional configuration steps.

.. _`mlx.traceability`: https://pypi.org/project/mlx.traceability/
.. _`sphinxcontrib-robotdoc`: https://pypi.org/project/sphinxcontrib-robotdoc/
.. _`documentation of mlx.traceability`: https://melexis.github.io/sphinx-traceability-extension/readme.html
.. _`LaTeX configuration for sphinxcontrib-robotdoc`: https://github.com/datakurre/sphinxcontrib-robotdoc#latex-output
