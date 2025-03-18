import os
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("all")


@pytest.mark.parametrize("var_value,expected", [(True, True), (False, False)])
def test_debug_task_execution(host, var_value, expected):
    # Fetch Ansible facts
    ansible_facts = host.ansible("setup")["ansible_facts"]

    # Retrieve our custom fact set in `set_fact`
    debug_executed = ansible_facts.get("cifmw_dlrn_report_force_executed", None)

    assert (
        debug_executed == expected
    ), f"Expected cifmw_dlrn_report_force_executed={expected}, but got {debug_executed}"
