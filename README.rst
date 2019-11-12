=======
Summary
=======

This script can convert your .robot files from Robot Framework to reStructuredText (.rst) files with traceable items.
This allows you to connect your requirements to test cases via the `mlx.traceability`_ Sphinx extension.
The `sphinxcontrib_robotdoc`_ Sphinx extension is responsible for embedding the Robot Framework content.

=============
Configuration
=============

To include the script's output in your documentation you want to add the two aforementioned extensions to your
``extensions`` list in your *conf.py* like so:

.. code-block:: python

    extensions = [
        'mlx.traceability',
        'sphinxcontrib_robotdoc',
    ]

.. _`mlx.traceability`: https://pypi.org/project/mlx.traceability/
.. _`sphinxcontrib_robotdoc`: https://pypi.org/project/sphinxcontrib-robotdoc/
