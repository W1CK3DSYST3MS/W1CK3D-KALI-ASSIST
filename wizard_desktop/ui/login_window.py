"""Login + disclaimer gate (Blueprint §8.1). Blocks the wizard until passed."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from wizard_core.auth import LoginPolicy
from wizard_core.auth.login_policy import DISCLAIMER_TEXT

from ..resources import assets_dir

_ASSETS = assets_dir()


class LoginWindow(QDialog):
    """Returns the accepted username via ``username`` after a successful gate."""

    def __init__(self, policy: LoginPolicy | None = None) -> None:
        super().__init__()
        self._policy = policy or LoginPolicy()
        self.username: str = ""
        self.setWindowTitle("W1CK3D'S KALI ASSIST — Sign in")
        self.setMinimumWidth(520)
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(36, 28, 36, 28)
        root.setSpacing(14)

        # Wordmark (logo asset if present, else text).
        logo = _ASSETS / "W1CK3D-SYSTEMS-logo.png"
        if logo.exists():
            pix = QPixmap(str(logo)).scaledToHeight(84, Qt.SmoothTransformation)
            img = QLabel()
            img.setPixmap(pix)
            img.setAlignment(Qt.AlignCenter)
            root.addWidget(img)
        word = QLabel("W1CK3D'S KALI ASSIST")
        word.setObjectName("Wordmark")
        word.setAlignment(Qt.AlignCenter)
        root.addWidget(word)
        sub = QLabel("A W1CK3D SYST3MS PROJECT · GENERATE-ONLY")
        sub.setObjectName("Subwordmark")
        sub.setAlignment(Qt.AlignCenter)
        root.addWidget(sub)

        # Credentials.
        self._user = QLineEdit()
        self._user.setPlaceholderText("Username")
        self._pass = QLineEdit()
        self._pass.setPlaceholderText("Password")
        self._pass.setEchoMode(QLineEdit.Password)
        root.addWidget(self._user)
        root.addWidget(self._pass)

        # Disclaimer.
        disc_card = QFrame()
        disc_card.setObjectName("Warning")
        dl = QVBoxLayout(disc_card)
        dl.setContentsMargins(12, 10, 12, 10)
        dh = QLabel("DISCLAIMER")
        dh.setObjectName("H2")
        dl.addWidget(dh)
        body = QTextEdit()
        body.setObjectName("Mono")
        body.setReadOnly(True)
        body.setPlainText(DISCLAIMER_TEXT)
        body.setFixedHeight(120)
        dl.addWidget(body)
        root.addWidget(disc_card)

        self._ack = QCheckBox("I have read and accept the disclaimer.")
        root.addWidget(self._ack)

        self._error = QLabel("")
        self._error.setStyleSheet("color:#e51f1f;")
        self._error.setWordWrap(True)
        root.addWidget(self._error)

        row = QHBoxLayout()
        row.addStretch(1)
        cancel = QPushButton("Quit")
        cancel.clicked.connect(self.reject)
        cont = QPushButton("ENTER")
        cont.setObjectName("Primary")
        cont.clicked.connect(self._attempt)
        self._pass.returnPressed.connect(self._attempt)
        row.addWidget(cancel)
        row.addWidget(cont)
        root.addLayout(row)

    def _attempt(self) -> None:
        result = self._policy.validate(
            self._user.text().strip(), self._pass.text(), self._ack.isChecked()
        )
        if result.ok:
            self.username = self._user.text().strip()
            self.accept()
        else:
            self._error.setText("  •  ".join(result.errors))
