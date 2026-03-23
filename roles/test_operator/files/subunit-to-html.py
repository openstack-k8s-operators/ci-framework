#!/usr/bin/env python3

import os
import json
import datetime
import argparse
from subunit import ByteStreamToStreamResult
from testtools import StreamResult


class ReportAccumulator(StreamResult):
    def __init__(self):
        super().__init__()
        self.tests = {}  # key: test_id
        self.events = []

    def status(
        self,
        test_id=None,
        test_status=None,
        test_tags=None,
        runnable=True,
        file_name=None,
        file_bytes=None,
        eof=False,
        mime_type=None,
        route_code=None,
        timestamp=None,
    ):
        if not test_id:
            return

        if test_id not in self.tests:
            self.tests[test_id] = {
                "id": test_id,
                "status": None,
                "start_time": None,
                "end_time": None,
                "worker": "unknown",
                "tags": set(),
                "details": [],
            }

        test = self.tests[test_id]

        if timestamp:
            ts = timestamp.timestamp()
            if test_status == "inprogress":
                test["start_time"] = ts
            elif test_status in (
                "success",
                "fail",
                "skip",
                "xfail",
                "uxsuccess",
            ):
                test["end_time"] = ts
                # If we missed the start time, try to infer or leave incomplete
                if not test["start_time"]:
                    # Some streams might not have explicit inprogress?
                    pass

        if test_status:
            # Map statuses
            # success, fail, skip are the main ones we care about
            if test_status == "inprogress":
                pass
            else:
                test["status"] = test_status

        if test_tags:
            test["tags"].update(test_tags)
            # Try to extract worker from tags
            for tag in test_tags:
                if tag.startswith("worker-"):
                    test["worker"] = tag

        if file_bytes:
            # Accumulate output/tracebacks
            try:
                content = bytes(file_bytes).decode("utf-8", errors="replace")
                test["details"].append(content)
            except:
                test["details"].append(str(file_bytes))

    def get_results(self):
        # Convert to list and clean up
        final_tests = []

        summary = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "duration": 0.0,
        }

        # Calculate global duration (min start to max end)
        all_starts = []
        all_ends = []

        for test_id, data in self.tests.items():
            if not data["status"]:
                # Maybe it started but didn't finish, or just log output?
                # If no status, skip or mark as unknown
                continue

            entry = {
                "id": data["id"],
                "status": data["status"],
                "worker": data["worker"],
                "start_ts": data["start_time"],
                "end_ts": data["end_time"],
                "duration": 0.0,
                "details": "".join(data["details"]),
            }

            # Timestamp formatting
            if data["start_time"]:
                entry["start_time"] = datetime.datetime.fromtimestamp(
                    data["start_time"]
                ).strftime("%Y-%m-%d %H:%M:%S.%f")
                all_starts.append(data["start_time"])

            if data["end_time"]:
                entry["end_time"] = datetime.datetime.fromtimestamp(
                    data["end_time"]
                ).strftime("%Y-%m-%d %H:%M:%S.%f")
                all_ends.append(data["end_time"])

            if data["start_time"] and data["end_time"]:
                entry["duration"] = data["end_time"] - data["start_time"]

            # Summary counts
            summary["total"] += 1
            if data["status"] == "success":
                summary["passed"] += 1
            elif data["status"] == "fail":
                summary["failed"] += 1
            elif data["status"] == "skip":
                summary["skipped"] += 1

            final_tests.append(entry)

        if all_starts and all_ends:
            summary["duration"] = max(all_ends) - min(all_starts)

        return {"summary": summary, "tests": final_tests}


def process_file(input_file, output_file):
    accumulator = ReportAccumulator()

    with open(input_file, "rb") as f:
        parser = ByteStreamToStreamResult(f)
        parser.run(accumulator)

    data = accumulator.get_results()

    template_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "report-template.html"
    )
    with open(template_path, "r") as f:
        template = f.read()

    json_data = json.dumps(data)
    html_content = template.replace("{{ REPORT_DATA }}", json_data)

    with open(output_file, "w") as f:
        f.write(html_content)

    print(f"Generated {output_file} with {data['summary']['total']} tests.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input .subunit file")
    parser.add_argument(
        "output",
        nargs="?",
        default="tempest-viz.html",
        help="Output .html file (default: tempest-viz.html)",
    )

    args = parser.parse_args()
    process_file(args.input, args.output)
