# Makefile for building example of robot2rst output in Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = _build
PYTHON		  = python3
ROBOT2RST	  = $(PYTHON) -m mlx.robot2rst

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(ROBOT2RST) -i $(SOURCEDIR)/robot/example.robot -o $(SOURCEDIR)/example_usage.rst -t ^SWRQT- ^SYSRQT- -r validates ext_toolname
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
