# Makefile for building example of robot2rst output in Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = _build
ROBOT2RST	  = robot2rst
ROBOT2RST_OPTS += -i $(SOURCEDIR)/robot/example.robot
ROBOT2RST_OPTS += -o $(SOURCEDIR)/example_usage_qtp.rst
ROBOT2RST_OPTS += -t ^SWRQT- ^SYSRQT-
ROBOT2RST_OPTS += -c 100 40.0
ROBOT2RST_OPTS += -r validates ext_toolname
ROBOT2RST_OPTS += --only FLASH

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean:
	@rm -rf $(BUILDDIR) $(SOURCEDIR)/*_qtp.rst

.PHONY: help Makefile clean

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile clean
	@$(ROBOT2RST) $(ROBOT2RST_OPTS)
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
