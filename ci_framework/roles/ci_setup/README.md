# ci_setup
Ensure you have the needed directories and packages for the rest of the tasks.

## Privilege escalation
None - we only create directories where the user is able to write.

## Parameters
* `cifmw_ci_setup_basedir`: Base directory for the directory tree. Default to ~/ci-framework

## Cleanup
You may call the `cleanup.yml` role in order to clear the directory tree.
