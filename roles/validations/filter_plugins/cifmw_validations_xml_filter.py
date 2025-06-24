#!/usr/bin/python3

__metaclass__ = type

DOCUMENTATION = """
  name: cifmw_validations_xml_filter
  short_description: Maps the internal results structure to a JUnit XML string.
  description:
    - Maps the internal results structure to a JUnit XML string.
  options:
    _input:
      description:
        - The internal role test results.
      type: dict
      required: true
"""

EXAMPLES = """
- name: Define data to work on in the examples below
  vars:
    _internal_results:
      test-1:
        time: 2.54512
      test-2.yml:
        time: 4.5450345
        error: "error message"
  ansible.builtin.set_fact:
    _xml_string: >-
      {{
        _internal_results | cifmw_validations_xml_filter
      }}
"""

RETURN = """
  _value:
    description: The translated JUnit XML string.
    type: string
    sample: >-
      <?xml version='1.0' encoding='utf-8'?>
      <testsuites>
        <testsuite name="validations" failures="0" skipped="0" tests="2" errors="1" time="7.090">
          <testcase name="test-1" classname="validations" time="2.545" />
          <testcase name="test-2" classname="validations" time="4.545">
            <error message="error message" />
          </testcase>
        </testsuite>
      </testsuites>
"""


import xml.etree.ElementTree as ET


class FilterModule:

    @staticmethod
    def __float_conversion(x: float) -> str:
        return "{0:0.3f}".format(round(x, 3))

    @classmethod
    def __map_xml_results(cls, test_results):

        root_elm = ET.Element("testsuites")
        tree = ET.ElementTree(element=root_elm)
        total_time = sum(
            [data["time"] for data in test_results.values() if "time" in data]
        )
        ts_elm = ET.SubElement(
            root_elm,
            "testsuite",
            attrib={
                "name": "validations",
                "failures": str(
                    len([elem for elem in test_results.values() if "error" in elem])
                ),
                "skipped": "0",
                "tests": str(len(test_results)),
                "errors": "0",
                "time": cls.__float_conversion(total_time),
            },
        )
        for name, data in test_results.items():
            name = name.replace(".yml", "").replace(".yaml", "")
            attributes = {"name": name, "classname": "validations"}
            if "time" in data:
                attributes["time"] = cls.__float_conversion(data["time"])
            tc_elm = ET.SubElement(ts_elm, "testcase", attrib=attributes)
            if "error" in data:
                ET.SubElement(tc_elm, "failure", attrib={"message": data["error"]})
        ET.indent(tree, "  ")
        return ET.tostring(root_elm, encoding="utf-8", xml_declaration=True)

    def filters(self):
        return {
            "cifmw_validations_xml_filter": self.__map_xml_results,
        }
