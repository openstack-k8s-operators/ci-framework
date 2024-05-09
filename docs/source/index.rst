..  documentation master file

ci-framework
============

Welcome to the documentation for Ci-Framework. This documentation is designed
to help you get up and running with our project as quickly and smoothly as
possible. We'll walk you through everything from setting up your development
environment to understanding our code structure and contributing to the
project.

Project purpose
###############

CI-Framework is a way to bootstrap development and CI environments for RHOSO_.
It is not intended for a production use, and should not be treated as a persistent deployment.

.. _RHOSO: https://www.redhat.com/en/blog/red-hat-openstack-services-openshift-next-generation-red-hat-openstack-platform

Found a bug or need a new feature?
##################################

The project is under constant development, bugs happen.

If you have such a bad encounter, please fill an `issue in Jira`_.

Chose **OSPRH**  project, add **cifmw** label, and set the Workstream to **CI Framework** and the Team to **OSP CI Framework**.

Please provide the following information:

- your environment (OS version, ``ansible --version``)
- commit hash of the ci-framework repository you're using (``git log -1``)
- your environment files (yes, *all* of them - you may want to ensure the **security** field of the issue is properly set to not leak internal data)
- the command you issued
- task name raising the error
- the error itself (please use the internal pastebin if it's too long)

In case of emergency, or if we didn't come back to you in a reasonable time (expect a couple of days), you can ping us on our `Slack channel`_.


.. _`issue in Jira`: https://issues.redhat.com/
.. _`Slack channel`: https://redhat.enterprise.slack.com/archives/C03MD4LG22Z


.. toctree::
   :maxdepth: 1
   :caption: Quickstart
   :glob:

   quickstart/*

.. toctree::
   :maxdepth: 1
   :caption: Architecture
   :glob:

   architecture/*

.. toctree::
   :maxdepth: 1
   :caption: Reproducers
   :glob:

   reproducers/*

.. toctree::
   :maxdepth: 1
   :caption: Usage
   :glob:

   usage/*


.. toctree::
   :maxdepth: 1
   :caption: Cookbooks
   :glob:

   cookbooks/*

.. toctree::
   :maxdepth: 1
   :caption: Baremetal
   :glob:

   baremetal/*

.. toctree::
   :maxdepth: 1
   :caption: Development
   :glob:

   development/*

.. toctree::
   :maxdepth: 1
   :caption: Available plugins
   :glob:

   plugins/*

.. toctree::
   :maxdepth: 1
   :caption: Module utils
   :glob:

   module_utils/*

.. toctree::
   :maxdepth: 1
   :caption: Available roles
   :glob:

   roles/*

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
