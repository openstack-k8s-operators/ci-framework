# Custom ansible plugins and modules

## action_plugins/ci_make
This wraps `community.general.make` module, mostly. It requires an additional
parameter, `output_dir`, in order to output the `make` generated command.

It requires a pull-request to merge in the community.general collection:
https://github.com/ansible-collections/community.general/pull/6160
