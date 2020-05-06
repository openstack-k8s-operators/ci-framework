Validate yaml schema for tempest skip
=====================================

This role execute the validate command from tempest-skiplist to ensure that
the yaml file used to store the tempest tests to be skipped are
in the correct schema format.

**Role Variables**

.. zuul:rolevar:: tempest_skip_path
   :type: string

   A path to the openstack-tempest-skiplist directory
