List allowed tempest tests
==========================

This role executes the tempest-skip tool and returns the list of tests to be
executed.

**Role Variables**

.. zuul:rolevar:: list_allowed_yaml_file
   :type: string

    Path to the yaml file containing the skipped tests

.. zuul:rolevar:: list_allowed_job
   :type: string

    Job name to be used in the filter if required

.. zuul:rolevar:: list_allowed_group
   :type: string

    Group to be used in the filter. It has more precedence than
    list_allowed_job.
