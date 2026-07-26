"""sqlmap builder: data-extraction flags added in the 2026-07-25 depth audit."""

from wizard_core.builders import get_builder
from wizard_core.slots import Slot

build = get_builder("sqlmap")


def test_banner_and_current_user_build():
    plan = build({"url": "http://x/?id=1", "banner": True, "current_user": True})
    assert "--banner" in plan.array_form
    assert "--current-user" in plan.array_form


def test_enumeration_flags_build():
    plan = build({
        "url": "http://x/?id=1", "users": True, "passwords": True,
        "privileges": True, "roles": True, "schema": True, "hostname": True,
        "is_dba": True, "count": True,
    })
    for flag in ["--users", "--passwords", "--privileges", "--roles",
                 "--schema", "--hostname", "--is-dba", "--count"]:
        assert flag in plan.array_form


def test_dump_all_and_all_and_search():
    plan = build({"url": "http://x/?id=1", "dump_all": True, "all": True,
                  "exclude_sysdbs": True, "search": "password"})
    assert "--dump-all" in plan.array_form
    assert "--all" in plan.array_form
    assert "--exclude-sysdbs" in plan.array_form
    assert "--search" in plan.array_form and "password" in plan.array_form
    assert any("--all retrieves everything" in n for n in plan.notes)


def test_os_pwn_warns_high_impact():
    plan = build({"url": "http://x/?id=1", "os_pwn": True})
    assert "--os-pwn" in plan.array_form
    assert any("out-of-band shell" in n for n in plan.notes)
