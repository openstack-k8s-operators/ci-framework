Validate yaml schema for tempest skip
=====================================

This role install openstack-tempest-skiplist and execute the validate command
to ensure that the yaml file used to store the tempest tests to be skipped are
in the correct schema format.


**Role Variables**

.. zuul:rolevar:: tempest_skip
   :type: string
   :default: ~/.virtualenvs/.tempest_skip

   A path to virtualenv used to install openstack-tempest-skiplist
