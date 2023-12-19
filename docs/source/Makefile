SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXAPI	  = sphinx-apidoc
BUILDDIR      = ../_build

ALLSPHINXOPTS   = -W -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .

.PHONY: clean
clean:
	rm -rf $(BUILDDIR)/*
	rm -f ./plugins/*
	rm -f ./roles/*
	rm -f ./module_utils/*

.PHONY: html
html: clean utils_doc plugin_doc role_doc
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

.PHONY: plugin_doc
plugin_doc:
	ansible-doc-extractor ./plugins ../../plugins/modules/*.py
	@echo
	@echo "Plugin doc generated."
	@echo

.PHONY: utils_doc
utils_doc: export SPHINX_APIDOC_OPTIONS=members,show-inheritance
utils_doc:
	#find ../../plugins/module_utils/ -type f -iname "*.py" -exec cp '{}' module_utils/ \;
	$(SPHINXAPI) -o ./module_utils -T --implicit-namespaces ../../plugins/module_utils/*/

.PHONY: role_doc
role_doc:
	for i in ../../roles/*/README.md; do \
		dir_name=`dirname $$i`; \
		role_name=`basename $$dir_name`; \
		test -L ./roles/$${role_name}.md || \
		ln -s ../$$i ./roles/$${role_name}.md; \
	done
