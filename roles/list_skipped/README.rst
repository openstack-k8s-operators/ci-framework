List skipped tempest tests
==========================

This role execute the tempest-skip tool and return the list of tests to be
skipped.

**Role Variables**

.. zuul:rolevar:: list_skipped_yaml_file
   :type: string

    Path to the yaml file containing the skipped tests

.. zuul:rolevar:: list_skipped_release
   :type: string

    Release name to be used in the filter if required.

.. zuul:rolevar:: list_skipped_job
   :type: string

    Job name to be used in the filter if required.
