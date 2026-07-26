"""tshark builder (wireshark tool): source exclusivity, ring buffer, autostop, decode-as."""

import pytest

from wizard_core.builders import get_builder
from wizard_core.slots import Slot

build = get_builder("tshark")


def test_live_source_in_target_pivot():
    plan = build({"source_iface": "eth0"})
    assert plan.slot_values[Slot.TARGET_PIVOT] == ["-i", "eth0"]


def test_read_file_source_in_target_pivot():
    plan = build({"read_file": "cap.pcap"})
    assert plan.slot_values[Slot.TARGET_PIVOT] == ["-r", "cap.pcap"]


def test_both_sources_rejected():
    with pytest.raises(ValueError):
        build({"source_iface": "eth0", "read_file": "cap.pcap"})


def test_no_source_is_noted_not_crashed():
    plan = build({})
    assert any("No source" in n for n in plan.notes)
    assert Slot.TARGET_PIVOT not in plan.slot_values or plan.slot_values[Slot.TARGET_PIVOT] == []


def test_list_interfaces_is_standalone():
    plan = build({"list_interfaces": True, "source_iface": "eth0"})
    assert plan.slot_values[Slot.ENV_INTERFACE] == ["-D"]
    # standalone form ignores everything else
    assert Slot.TARGET_PIVOT not in plan.slot_values


def test_write_saves_to_output_options():
    plan = build({"source_iface": "eth0", "write": "~/cap.pcapng"})
    assert plan.slot_values[Slot.OUTPUT_OPTIONS] == ["-w", "~/cap.pcapng"]


def test_ring_buffer_filesize_and_files_combine():
    plan = build({
        "source_iface": "eth0", "write": "~/rolling.pcapng",
        "ring_filesize": 1000, "ring_files": 5,
    })
    assert plan.slot_values[Slot.OUTPUT_OPTIONS] == [
        "-w", "~/rolling.pcapng", "-b", "filesize:1000", "-b", "files:5",
    ]
    assert not plan.notes


def test_ring_buffer_without_write_is_noted():
    plan = build({"source_iface": "eth0", "ring_files": 5})
    assert "-b" in plan.array_form
    assert any("rotates the file named by -w" in n for n in plan.notes)


def test_autostop_filesize_and_files_are_separate_a_flags():
    plan = build({
        "source_iface": "eth0", "autostop_filesize": 10000, "autostop_files": 5,
    })
    assert plan.slot_values[Slot.GLOBAL_OPTIONS] == [
        "-a", "filesize:10000", "-a", "files:5",
    ]


def test_autostop_duration_still_works():
    plan = build({"source_iface": "eth0", "duration": 30})
    assert plan.slot_values[Slot.GLOBAL_OPTIONS] == ["-a", "duration:30"]


def test_decode_as_in_action_options():
    plan = build({"read_file": "cap.pcap", "decode_as": "tcp.port==8888,http"})
    assert "-d" in plan.array_form and "tcp.port==8888,http" in plan.array_form


def test_fields_with_csv_header():
    plan = build({
        "read_file": "cap.pcap", "fields": "ip.src,ip.dst",
        "csv_header": True,
    })
    assert plan.slot_values[Slot.ACTION_OPTIONS] == [
        "-T", "fields", "-e", "ip.src", "-e", "ip.dst",
    ]
    assert plan.slot_values[Slot.OUTPUT_OPTIONS] == ["-E", "header=y", "-E", "separator=,"]


def test_snaplen_and_no_promiscuous_in_env():
    plan = build({"source_iface": "eth0", "snaplen": 96, "no_promiscuous": True})
    assert plan.slot_values[Slot.ENV_INTERFACE] == ["-s", "96", "-p"]


def test_capture_filter_on_read_file_is_noted():
    plan = build({"read_file": "cap.pcap", "capture_filter": "tcp port 80"})
    assert any("only applies to live capture" in n for n in plan.notes)
