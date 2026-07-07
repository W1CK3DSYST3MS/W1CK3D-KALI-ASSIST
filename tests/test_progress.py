"""Save points: ProgressStore persistence, resume, counts."""

from wizard_core.progress import ProgressStore


def test_mark_and_counts_persist(tmp_path):
    p = tmp_path / "progress.json"
    store = ProgressStore(p)
    steps = ["s1", "s2", "s3"]
    assert store.counts("les", steps) == (0, 3)
    store.mark_complete("les", "s1")
    store.mark_complete("les", "s2")
    assert store.counts("les", steps) == (2, 3)
    # a fresh store reads the saved file
    assert ProgressStore(p).counts("les", steps) == (2, 3)


def test_resume_index_points_at_first_incomplete(tmp_path):
    store = ProgressStore(tmp_path / "p.json")
    steps = ["a", "b", "c", "d"]
    assert store.resume_index("les", steps) == 0
    store.mark_complete("les", "a")
    store.mark_complete("les", "b")
    assert store.resume_index("les", steps) == 2
    for s in steps:
        store.mark_complete("les", s)
    assert store.resume_index("les", steps) == len(steps)  # all done
    assert store.is_lesson_complete("les", steps)


def test_mark_is_idempotent(tmp_path):
    store = ProgressStore(tmp_path / "p.json")
    store.mark_complete("les", "s1")
    store.mark_complete("les", "s1")
    assert store.counts("les", ["s1"]) == (1, 1)


def test_reset_lesson(tmp_path):
    store = ProgressStore(tmp_path / "p.json")
    store.mark_complete("les", "s1")
    store.reset_lesson("les")
    assert store.counts("les", ["s1"]) == (0, 1)


def test_corrupt_file_does_not_crash(tmp_path):
    p = tmp_path / "p.json"
    p.write_text("{ not valid json", encoding="utf-8")
    store = ProgressStore(p)  # must not raise
    assert store.counts("les", ["s1"]) == (0, 1)
