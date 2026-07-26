"""hashcat builder: hash-mode/attack-mode plumbing, combinator's two wordlists, -j/-k."""

import pytest

from wizard_core.builders import get_builder
from wizard_core.slots import Slot

build = get_builder("hashcat")


def test_wordlist_attack_positional_order():
    plan = build({"hash_mode": 0, "attack_mode": "0", "hashfile": "hashes.txt", "wordlist": "rockyou.txt"})
    assert plan.slot_values[Slot.POSITIONAL_ARGS] == ["hashes.txt", "rockyou.txt"]
    assert plan.slot_values[Slot.ACTION_OPTIONS] == ["-m", "0", "-a", "0"]


def test_benchmark_is_standalone():
    plan = build({"benchmark": True, "hashfile": "hashes.txt"})
    assert plan.slot_values[Slot.ACTION_OPTIONS] == ["-b"]
    assert Slot.POSITIONAL_ARGS not in plan.slot_values


def test_identify_is_standalone():
    plan = build({"identify": True, "hashfile": "hashes.txt"})
    assert plan.slot_values[Slot.ACTION_OPTIONS] == ["--identify"]
    assert plan.slot_values[Slot.POSITIONAL_ARGS] == ["hashes.txt"]


def test_list_devices_is_standalone():
    plan = build({"list_devices": True})
    assert plan.slot_values[Slot.ENV_INTERFACE] == ["-I"]


def test_combinator_attack_takes_two_wordlists_in_order():
    plan = build({
        "hash_mode": 0, "attack_mode": "1", "hashfile": "hashes.txt",
        "wordlist": "firstnames.txt", "wordlist2": "lastnames.txt",
    })
    assert plan.slot_values[Slot.POSITIONAL_ARGS] == [
        "hashes.txt", "firstnames.txt", "lastnames.txt",
    ]
    assert plan.bash_preview_string == (
        "hashcat -m 0 -a 1 hashes.txt firstnames.txt lastnames.txt"
    )


def test_combinator_missing_second_wordlist_is_noted():
    plan = build({
        "hash_mode": 0, "attack_mode": "1", "hashfile": "hashes.txt",
        "wordlist": "firstnames.txt",
    })
    assert plan.slot_values[Slot.POSITIONAL_ARGS] == ["hashes.txt", "firstnames.txt"]
    assert any("SECOND wordlist" in n for n in plan.notes)


def test_combinator_missing_first_wordlist_is_noted():
    plan = build({"hash_mode": 0, "attack_mode": "1", "hashfile": "hashes.txt"})
    assert any("first wordlist" in n for n in plan.notes)


def test_combinator_profile_prefills_attack_mode():
    plan = build({"profile": "combinator", "hash_mode": 0, "hashfile": "hashes.txt",
                 "wordlist": "a.txt", "wordlist2": "b.txt"})
    assert "-a" in plan.slot_values[Slot.ACTION_OPTIONS] and "1" in plan.slot_values[Slot.ACTION_OPTIONS]


def test_rule_left_and_rule_right():
    plan = build({
        "hash_mode": 0, "attack_mode": "1", "hashfile": "hashes.txt",
        "wordlist": "a.txt", "wordlist2": "b.txt",
        "rule_left": "c", "rule_right": "$9$9",
    })
    assert "-j" in plan.array_form and "c" in plan.array_form
    assert "-k" in plan.array_form and "$9$9" in plan.array_form


def test_mask_attack_still_uses_single_positional():
    plan = build({"hash_mode": 0, "attack_mode": "3", "hashfile": "hashes.txt", "mask": "?d?d?d?d"})
    assert plan.slot_values[Slot.POSITIONAL_ARGS] == ["hashes.txt", "?d?d?d?d"]


def test_no_hash_mode_is_noted():
    plan = build({"attack_mode": "0", "hashfile": "hashes.txt", "wordlist": "rockyou.txt"})
    assert any("hash mode" in n for n in plan.notes)


def test_unknown_profile_fails_loudly():
    with pytest.raises(ValueError):
        build({"profile": "ludicrous", "hashfile": "x"})
