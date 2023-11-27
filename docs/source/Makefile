SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
BUILDDIR      = ../_build

ALLSPHINXOPTS   = -W -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .

.PHONY: clean
clean:
	rm -rf $(BUILDDIR)/*

.PHONY: html
html: clean plugin_doc role_doc
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

.PHONY: plugin_doc
plugin_doc:
	ansible-doc-extractor ./plugins ../../plugins/modules/*.py
	@echo
	@echo "Plugin doc generated."
	@echo

.PHONY: role_doc
role_doc:
	for i in ../../ci_framework/roles/*/README.md; do \
		dir_name=`dirname $$i`; \
		role_name=`basename $$dir_name`; \
		test -L ./roles/$${role_name}.md || \
		ln -s ../$$i ./roles/$${role_name}.md; \
	done
