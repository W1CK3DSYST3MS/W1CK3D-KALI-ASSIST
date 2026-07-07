"""Save points — local, per-lesson step-completion tracking.

Records which steps a learner has finished so a lesson can be resumed at the
first unfinished step instead of restarting. Stored as plain JSON on-device
(no secrets — only lesson_id/step_id + timestamps). UI-agnostic; the front-end
marks steps and asks for resume points.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence


class ProgressStore:
    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._data: dict = {"version": 1, "lessons": {}}
        self._load()

    # -- persistence ------------------------------------------------------- #
    def _load(self) -> None:
        if self._path.exists():
            try:
                loaded = json.loads(self._path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict) and "lessons" in loaded:
                    self._data = loaded
            except (json.JSONDecodeError, OSError):
                # Corrupt/unreadable progress must never block the app; start fresh.
                self._data = {"version": 1, "lessons": {}}

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._path.with_suffix(self._path.suffix + ".tmp")
        tmp.write_text(json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self._path)  # atomic on the same filesystem

    # -- queries ----------------------------------------------------------- #
    def completed_steps(self, lesson_id: str) -> set[str]:
        entry = self._data["lessons"].get(lesson_id, {})
        return set(entry.get("completed", []))

    def is_step_complete(self, lesson_id: str, step_id: str) -> bool:
        return step_id in self.completed_steps(lesson_id)

    def counts(self, lesson_id: str, step_ids: Sequence[str]) -> tuple[int, int]:
        """(#completed within this lesson's steps, total steps)."""
        done = self.completed_steps(lesson_id)
        return sum(1 for s in step_ids if s in done), len(step_ids)

    def is_lesson_complete(self, lesson_id: str, step_ids: Sequence[str]) -> bool:
        done = self.completed_steps(lesson_id)
        return bool(step_ids) and all(s in done for s in step_ids)

    def resume_index(self, lesson_id: str, step_ids: Sequence[str]) -> int:
        """Index of the first not-yet-completed step (0 if none done, len if all done)."""
        done = self.completed_steps(lesson_id)
        for i, s in enumerate(step_ids):
            if s not in done:
                return i
        return len(step_ids)

    # -- mutations --------------------------------------------------------- #
    def mark_complete(self, lesson_id: str, step_id: str) -> None:
        entry = self._data["lessons"].setdefault(lesson_id, {"completed": []})
        if step_id not in entry["completed"]:
            entry["completed"].append(step_id)
        entry["updated"] = datetime.now(timezone.utc).isoformat()
        self._save()

    def reset_lesson(self, lesson_id: str) -> None:
        if lesson_id in self._data["lessons"]:
            del self._data["lessons"][lesson_id]
            self._save()
