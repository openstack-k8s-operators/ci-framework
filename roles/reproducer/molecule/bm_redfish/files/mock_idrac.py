#!/usr/bin/env python3
"""Mock iDRAC Redfish server for molecule testing of bm_* Ansible tasks.

Implements stateful Redfish endpoints matching Dell iDRAC behavior:
- Power management (On/Off/ForceOff)
- BIOS settings (GenericUsbBoot)
- VirtualMedia insert/eject
- Boot override (UefiTarget, Once)
- Boot options enumeration
- Job queue management

State can be reset between tests via POST /test/reset.
"""
import json
import socket
import ssl
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler


class IDRACState:
    """In-memory iDRAC state that simulates power cycle semantics."""

    def __init__(self):
        self.reset()

    def reset(self, overrides=None):
        self.power_state = "Off"
        self.usb_boot = "Disabled"
        self.usb_boot_pending = None
        self.vmedia_inserted = False
        self.vmedia_image = ""
        self.boot_override_target = "None"
        self.boot_override_enabled = "Disabled"
        self.uefi_target = None
        self.pending_jobs = []
        if overrides:
            for k, v in overrides.items():
                if hasattr(self, k):
                    setattr(self, k, v)

    def apply_pending_bios(self):
        """Apply pending BIOS changes on power cycle (Off -> On)."""
        if self.usb_boot_pending is not None:
            self.usb_boot = self.usb_boot_pending
            self.usb_boot_pending = None
            self.pending_jobs = [j for j in self.pending_jobs if j != "bios_config"]


STATE = IDRACState()

BOOT_OPTIONS = {
    "Boot0001": {
        "@odata.id": "/redfish/v1/Systems/System.Embedded.1/BootOptions/Boot0001",
        "Id": "Boot0001",
        "Name": "PXE Device 1: Embedded NIC 1 Port 1 Partition 1",
        "DisplayName": "PXE Device 1: Embedded NIC 1 Port 1 Partition 1",
        "UefiDevicePath": "VenHw(3A191845-5F86-4E78-8FCE-C4CFF59F9DAA)",
        "BootOptionEnabled": True,
    },
    "Boot0003": {
        "@odata.id": "/redfish/v1/Systems/System.Embedded.1/BootOptions/Boot0003",
        "Id": "Boot0003",
        "Name": "Virtual Floppy Drive",
        "DisplayName": "Virtual Floppy Drive",
        "UefiDevicePath": "PciRoot(0x0)/Pci(0x14,0x0)/USB(0xD,0x0)/USB(0x0,0x0)/USB(0x2,0x0)/Unit(0x1)",
        "BootOptionEnabled": True,
    },
    "Boot0004": {
        "@odata.id": "/redfish/v1/Systems/System.Embedded.1/BootOptions/Boot0004",
        "Id": "Boot0004",
        "Name": "Virtual Optical Drive",
        "DisplayName": "Virtual Optical Drive",
        "UefiDevicePath": "PciRoot(0x0)/Pci(0x14,0x0)/USB(0xD,0x0)/USB(0x0,0x0)/USB(0x2,0x0)/Unit(0x0)",
        "BootOptionEnabled": True,
    },
    "Boot0005": {
        "@odata.id": "/redfish/v1/Systems/System.Embedded.1/BootOptions/Boot0005",
        "Id": "Boot0005",
        "Name": "Integrated RAID Controller 1: Red Hat Enterprise Linux",
        "DisplayName": "Integrated RAID Controller 1: Red Hat Enterprise Linux",
        "UefiDevicePath": "HD(2,GPT,FF726BC2-263F-EE4A-BAE7-7CACE574EBD8,0x1000,0x3F800)/\\EFI\\redhat\\shimx64.efi",
        "BootOptionEnabled": True,
    },
    "Boot0006": {
        "@odata.id": "/redfish/v1/Systems/System.Embedded.1/BootOptions/Boot0006",
        "Id": "Boot0006",
        "Name": "Generic USB Boot",
        "DisplayName": "Generic USB Boot",
        "UefiDevicePath": "VenHw(0C8CB6CC-13AE-45F4-BBCD-6A25E98AC250)",
        "BootOptionEnabled": True,
    },
}

VIRTUAL_OPTICAL_PATH = BOOT_OPTIONS["Boot0004"]["UefiDevicePath"]


class RedfishHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        sys.stderr.write("[mock-idrac] %s\n" % (format % args))

    def _send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length:
            return json.loads(self.rfile.read(length))
        return {}

    # ---- routing ----

    def do_GET(self):
        path = self.path.rstrip("/")

        if path == "/redfish/v1/Systems/System.Embedded.1":
            return self._get_system()

        if path == "/redfish/v1/Systems/System.Embedded.1/Bios":
            return self._get_bios()

        if path == "/redfish/v1/Systems/System.Embedded.1/BootOptions":
            return self._get_boot_options_collection()

        if path.startswith("/redfish/v1/Systems/System.Embedded.1/BootOptions/Boot"):
            boot_id = path.rsplit("/", 1)[-1]
            return self._get_boot_option(boot_id)

        if path == "/redfish/v1/Managers/iDRAC.Embedded.1/VirtualMedia/CD":
            return self._get_vmedia()

        if path == "/test/state":
            return self._get_test_state()

        self._send_json({"error": "not found", "path": path}, 404)

    def do_POST(self):
        path = self.path.rstrip("/")
        body = self._read_body()

        if path == "/test/reset":
            return self._post_test_reset(body)

        if path.endswith("Actions/ComputerSystem.Reset"):
            return self._post_reset(body)

        if path == "/redfish/v1/Managers/iDRAC.Embedded.1/Jobs":
            return self._post_create_job(body)

        if path.endswith("DellJobService/Actions/DellJobService.DeleteJobQueue"):
            return self._post_clear_jobs(body)

        if path.endswith("Actions/VirtualMedia.InsertMedia"):
            return self._post_insert_media(body)

        if path.endswith("Actions/VirtualMedia.EjectMedia"):
            return self._post_eject_media(body)

        self._send_json({"error": "not found", "path": path}, 404)

    def do_PATCH(self):
        path = self.path.rstrip("/")
        body = self._read_body()

        if path == "/redfish/v1/Systems/System.Embedded.1":
            return self._patch_system(body)

        if path == "/redfish/v1/Systems/System.Embedded.1/Bios/Settings":
            return self._patch_bios_settings(body)

        self._send_json({"error": "not found", "path": path}, 404)

    # ---- GET handlers ----

    def _get_system(self):
        self._send_json(
            {
                "@odata.id": "/redfish/v1/Systems/System.Embedded.1",
                "PowerState": STATE.power_state,
                "Boot": {
                    "BootSourceOverrideTarget": STATE.boot_override_target,
                    "BootSourceOverrideEnabled": STATE.boot_override_enabled,
                    "UefiTargetBootSourceOverride": STATE.uefi_target,
                    "BootOptions": {
                        "@odata.id": "/redfish/v1/Systems/System.Embedded.1/BootOptions"
                    },
                    "BootSourceOverrideTarget@Redfish.AllowableValues": [
                        "None",
                        "Pxe",
                        "Floppy",
                        "Cd",
                        "Hdd",
                        "BiosSetup",
                        "Utilities",
                        "UefiTarget",
                        "SDCard",
                        "UefiHttp",
                    ],
                },
            }
        )

    def _get_bios(self):
        self._send_json(
            {
                "@odata.id": "/redfish/v1/Systems/System.Embedded.1/Bios",
                "Attributes": {
                    "GenericUsbBoot": STATE.usb_boot,
                    "BootMode": "Uefi",
                },
            }
        )

    def _get_boot_options_collection(self):
        self._send_json(
            {
                "@odata.id": "/redfish/v1/Systems/System.Embedded.1/BootOptions",
                "Members": [
                    {"@odata.id": opt["@odata.id"]} for opt in BOOT_OPTIONS.values()
                ],
                "Members@odata.count": len(BOOT_OPTIONS),
            }
        )

    def _get_boot_option(self, boot_id):
        if boot_id in BOOT_OPTIONS:
            self._send_json(BOOT_OPTIONS[boot_id])
        else:
            self._send_json({"error": "not found"}, 404)

    def _get_vmedia(self):
        self._send_json(
            {
                "@odata.id": "/redfish/v1/Managers/iDRAC.Embedded.1/VirtualMedia/CD",
                "Inserted": STATE.vmedia_inserted,
                "Image": STATE.vmedia_image if STATE.vmedia_inserted else None,
                "ImageName": (
                    STATE.vmedia_image.rsplit("/", 1)[-1]
                    if STATE.vmedia_inserted and STATE.vmedia_image
                    else None
                ),
                "ConnectedVia": "URI" if STATE.vmedia_inserted else "NotConnected",
                "WriteProtected": True,
            }
        )

    def _get_test_state(self):
        self._send_json(
            {
                "power_state": STATE.power_state,
                "usb_boot": STATE.usb_boot,
                "usb_boot_pending": STATE.usb_boot_pending,
                "vmedia_inserted": STATE.vmedia_inserted,
                "vmedia_image": STATE.vmedia_image,
                "boot_override_target": STATE.boot_override_target,
                "boot_override_enabled": STATE.boot_override_enabled,
                "uefi_target": STATE.uefi_target,
                "pending_jobs": STATE.pending_jobs,
            }
        )

    # ---- POST handlers ----

    def _post_test_reset(self, body):
        STATE.reset(body)
        self._send_json({"status": "reset"})

    def _post_reset(self, body):
        reset_type = body.get("ResetType", "")
        if reset_type == "On":
            if STATE.power_state == "On":
                return self._send_json({"error": "already on"}, 409)
            STATE.apply_pending_bios()
            STATE.power_state = "On"
        elif reset_type in ("ForceOff", "GracefulShutdown"):
            STATE.power_state = "Off"
        elif reset_type == "ForceRestart":
            STATE.apply_pending_bios()
            STATE.power_state = "On"
        else:
            return self._send_json({"error": f"unknown ResetType: {reset_type}"}, 400)
        self._send_json({"status": "ok"}, 204)

    def _post_create_job(self, body):
        target = body.get("TargetSettingsURI", "")
        if "Bios" in target:
            STATE.pending_jobs.append("bios_config")
        self._send_json({"JobID": "JID_TEST_001"}, 200)

    def _post_clear_jobs(self, body):
        STATE.pending_jobs.clear()
        self._send_json({"status": "cleared"}, 200)

    def _post_insert_media(self, body):
        STATE.vmedia_inserted = True
        STATE.vmedia_image = body.get("Image", "http://test/test.iso")
        self._send_json({"status": "inserted"}, 204)

    def _post_eject_media(self, body):
        STATE.vmedia_inserted = False
        STATE.vmedia_image = ""
        self._send_json({"status": "ejected"}, 204)

    # ---- PATCH handlers ----

    def _patch_system(self, body):
        boot = body.get("Boot", {})
        if "BootSourceOverrideTarget" in boot:
            STATE.boot_override_target = boot["BootSourceOverrideTarget"]
        if "BootSourceOverrideEnabled" in boot:
            STATE.boot_override_enabled = boot["BootSourceOverrideEnabled"]
        if "UefiTargetBootSourceOverride" in boot:
            STATE.uefi_target = boot["UefiTargetBootSourceOverride"]
        self._send_json({"status": "ok"}, 200)

    def _patch_bios_settings(self, body):
        attrs = body.get("Attributes", {})
        if "GenericUsbBoot" in attrs:
            STATE.usb_boot_pending = attrs["GenericUsbBoot"]
        self._send_json({"status": "ok"}, 200)


class DualStackHTTPServer(HTTPServer):
    """HTTPServer that supports IPv4 and IPv6."""

    address_family = socket.AF_INET6
    allow_reuse_address = True

    def server_bind(self):
        self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        super().server_bind()


def run(port=8443, certfile=None, keyfile=None):
    try:
        server = DualStackHTTPServer(("::", port), RedfishHandler)
    except OSError:
        server = HTTPServer(("0.0.0.0", port), RedfishHandler)
    if certfile and keyfile:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(certfile, keyfile)
        server.socket = ctx.wrap_socket(server.socket, server_side=True)
        proto = "https"
    else:
        proto = "http"
    print(f"Mock iDRAC listening on {proto}://0.0.0.0:{port}")
    sys.stdout.flush()
    server.serve_forever()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8443)
    parser.add_argument("--cert", default=None)
    parser.add_argument("--key", default=None)
    args = parser.parse_args()
    run(port=args.port, certfile=args.cert, keyfile=args.key)
