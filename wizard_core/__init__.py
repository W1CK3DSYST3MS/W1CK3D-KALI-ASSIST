"""W1CK3D'S KALI ASSIST — UI-agnostic engine (``wizard_core``).

HARD RULE: this package NEVER executes target commands and NEVER imports any
GUI/Qt library. It builds, explains and walks commands as data so it can be
reused by both the desktop (PySide6) and a future Termux TUI front-end.
"""

# Stable engine API version. Module manifests declare the base_api they target;
# the loader checks compatibility against this. Bump the major on breaking
# changes to the spec models.
BASE_API_VERSION = "1.0"

__all__ = ["BASE_API_VERSION"]
