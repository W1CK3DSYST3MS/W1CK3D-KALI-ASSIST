"""Authorization gate — blocking red dialog shown before any offensive command."""

from __future__ import annotations

from PySide6.QtWidgets import QMessageBox, QWidget


def confirm_authorization(parent: QWidget, tool_name: str, text: str) -> bool:
    """Return True if the user acknowledges the authorization warning."""
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Warning)
    box.setWindowTitle(f"Authorization required — {tool_name}")
    box.setText(f"<b>{tool_name} acts on live systems.</b>")
    box.setInformativeText(text)
    proceed = box.addButton("I am authorized — continue", QMessageBox.AcceptRole)
    box.addButton("Cancel", QMessageBox.RejectRole)
    box.setDefaultButton(proceed)
    box.exec()
    return box.clickedButton() is proceed
