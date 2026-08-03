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


def test_list_link_types_needs_interface():
    with pytest.raises(ValueError):
        build({"list_link_types": True})


def test_list_link_types_is_standalone():
    plan = build({"list_link_types": True, "source_iface": "eth0"})
    assert plan.slot_values[Slot.TARGET_PIVOT] == ["-i", "eth0"]
    assert plan.slot_values[Slot.ENV_INTERFACE] == ["-L"]


def test_read_filter_auto_adds_two_pass():
    plan = build({"read_file": "cap.pcap", "read_filter": "tcp"})
    assert "-R" in plan.array_form and "tcp" in plan.array_form
    assert "-2" in plan.slot_values[Slot.GLOBAL_OPTIONS]
    assert any("Added -2" in n for n in plan.notes)


def test_two_pass_explicit_not_duplicated_by_read_filter():
    plan = build({"read_file": "cap.pcap", "two_pass": True, "read_filter": "tcp"})
    assert plan.slot_values[Slot.GLOBAL_OPTIONS].count("-2") == 1
    assert not any("Added -2" in n for n in plan.notes)


def test_name_resolve_flags_and_quiet_errors_only():
    plan = build({"read_file": "cap.pcap", "name_resolve_flags": "mnNtdv", "quiet_errors_only": True})
    assert "-N" in plan.array_form and "mnNtdv" in plan.array_form
    assert "-Q" in plan.slot_values[Slot.GLOBAL_OPTIONS]


def test_output_type_without_fields():
    plan = build({"read_file": "cap.pcap", "output_type": "json"})
    assert plan.slot_values[Slot.ACTION_OPTIONS] == ["-T", "json"]


def test_output_type_ignored_when_fields_set():
    plan = build({"read_file": "cap.pcap", "fields": "ip.src", "output_type": "json"})
    assert plan.slot_values[Slot.ACTION_OPTIONS] == ["-T", "fields", "-e", "ip.src"]
    assert any("Output type is ignored" in n for n in plan.notes)


def test_protocol_filters_note_without_qualifying_output_type():
    plan = build({"read_file": "cap.pcap", "protocol_filter": "http tcp"})
    assert "-j" in plan.array_form
    assert any("ek, pdml or json" in n for n in plan.notes)

    plan2 = build({"read_file": "cap.pcap", "output_type": "json", "protocol_filter_top": "http"})
    assert "-J" in plan2.array_form
    assert not any("ek, pdml or json" in n for n in plan2.notes)


def test_timestamp_and_seconds_format():
    plan = build({"read_file": "cap.pcap", "timestamp_format": "ad", "seconds_format": "hms"})
    assert plan.slot_values[Slot.ACTION_OPTIONS] == ["-t", "ad", "-u", "hms"]


def test_verbose_tree_and_detail_protocols():
    plan = build({"read_file": "cap.pcap", "verbose_tree": True, "detail_protocols": "http,tcp"})
    assert plan.slot_values[Slot.ACTION_OPTIONS] == ["-V", "-O", "http,tcp"]
    assert not plan.notes


def test_detail_protocols_without_verbose_tree_is_noted():
    plan = build({"read_file": "cap.pcap", "detail_protocols": "http"})
    assert any("normally used together with -V" in n for n in plan.notes)


def test_hex_dump_and_hexdump_opts():
    plan = build({"read_file": "cap.pcap", "hexdump_opts": "noascii"})
    assert plan.slot_values[Slot.ACTION_OPTIONS] == ["-x", "--hexdump", "noascii"]


def test_print_even_writing_without_write_is_noted():
    plan = build({"read_file": "cap.pcap", "print_even_writing": True})
    assert "-P" in plan.array_form
    assert any("no extra effect without" in n for n in plan.notes)


def test_color_output_and_dissection_controls():
    plan = build({
        "read_file": "cap.pcap", "color_output": True,
        "only_protocols": "http,tcp", "enable_protocol": "http2",
        "disable_protocol": "quic",
    })
    assert plan.slot_values[Slot.ACTION_OPTIONS] == [
        "--color", "--only-protocols", "http,tcp",
        "--enable-protocol", "http2", "--disable-protocol", "quic",
    ]


def test_ring_duration_alongside_filesize_and_files():
    plan = build({
        "source_iface": "eth0", "write": "~/roll.pcapng",
        "ring_filesize": 1000, "ring_duration": 3600, "ring_files": 5,
    })
    assert plan.slot_values[Slot.OUTPUT_OPTIONS] == [
        "-w", "~/roll.pcapng",
        "-b", "filesize:1000", "-b", "duration:3600", "-b", "files:5",
    ]


def test_output_format_save_network_addrs_export_objects():
    plan = build({
        "read_file": "cap.pcap", "output_format": "pcap",
        "save_network_addrs": True, "export_objects": "http,/tmp/out",
    })
    assert plan.slot_values[Slot.OUTPUT_OPTIONS] == [
        "-F", "pcap", "-W", "n", "--export-objects", "http,/tmp/out",
    ]


def test_monitor_mode_and_buffer_size_in_env():
    plan = build({"source_iface": "wlan0", "monitor_mode": True, "buffer_size": 4})
    assert plan.slot_values[Slot.ENV_INTERFACE] == ["-I", "-B", "4"]
