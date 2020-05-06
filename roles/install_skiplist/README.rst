Install tempest skiplist
========================

This role install tempest-siplist in a virtual environment.

**Role Variables**

.. zuul:rolevar:: virtualenvs.tempest_skip
   :type: string
   :default: ~/.virtualenvs/.tempest_skip

   A path to virtualenv used to install openstack-tempest-skiplist

.. zuul:rolevar:: tempest_skip_path
   :type: string

    A path to the openstack-tempest-skiplist directory
