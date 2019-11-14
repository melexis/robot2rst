=======
Summary
=======

This script can convert your .robot files from Robot Framework to reStructuredText (.rst) files with traceable items.
This allows you to connect your requirements to test cases via the `mlx.traceability`_ Sphinx extension.
The `sphinxcontrib-robotdoc`_ Sphinx extension is responsible for embedding the Robot Framework content.

.. _`mlx.traceability`: https://pypi.org/project/mlx.traceability/

=============
Configuration
=============

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
