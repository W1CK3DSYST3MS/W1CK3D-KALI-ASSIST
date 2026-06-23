"""W1CK3D SYSTEMS theme — tokens + generated Qt stylesheet (QSS).

Values are taken verbatim from ``docs/specs/Design-System-Tokens.md`` (the brand's
source of truth). Dark cyber/terminal aesthetic: near-black layered surfaces,
purple neon accent, status colors that double as category tints AND stepper states.
"""

from __future__ import annotations

# --- Color tokens (exact hexes from Design-System-Tokens.md) --------------- #
TOKENS: dict[str, str] = {
    # backgrounds
    "bg_void": "#030405",
    "bg_base": "#06080b",
    "bg_inset": "#07090c",
    "bg_surface": "#0b0e13",
    "bg_raised": "#11151b",
    "bg_hover": "#181d25",
    # text
    "text_strong": "#eef1f5",
    "text_body": "#c2c8d2",
    "text_muted": "#8b93a1",
    "text_faint": "#5a626f",
    "text_invert": "#06080b",
    # accent (purple)
    "purple": "#561593",
    "purple_glow": "#9a3eff",
    "purple_deep": "#320a63",
    # status / category palette
    "recon": "#561593",
    "secure": "#0f9446",
    "secure_glow": "#3df085",
    "warning": "#ee5a04",
    "warning_glow": "#ff8a3d",
    "critical": "#e51f1f",
    "critical_deep": "#7e1212",
    "info": "#147ec2",
    "info_glow": "#4fbdf5",
    # metallic
    "gold": "#c5a45a",
    "silver": "#c2c7cf",
    # lines
    "line_faint": "#1b1f26",
    "line": "#262c35",
    "line_strong": "#353c47",
}

# Status color per category tag (drives the tab/section tinting).
CATEGORY_COLOR: dict[str, str] = {
    "reconnaissance": TOKENS["recon"],
    "protect": TOKENS["secure"],
    "detect": TOKENS["secure"],
    "exploitation": TOKENS["critical"],
    "forensics": TOKENS["info"],
    "info": TOKENS["info"],
}

# Font stacks (Google Fonts; bundled webfonts are an outstanding asset item).
# Qt substitutes gracefully when a family isn't installed.
FONT_DISPLAY = '"Black Ops One", "Orbitron", Impact'
FONT_HEADING = '"Orbitron", "Oxanium", "Chakra Petch", sans-serif'
FONT_BODY = '"Chakra Petch", "Oxanium", sans-serif'
FONT_MONO = '"JetBrains Mono", "Share Tech Mono", "Consolas", monospace'


def category_color(category: str) -> str:
    return CATEGORY_COLOR.get(category.lower(), TOKENS["purple"])


def build_qss() -> str:
    """Generate the application stylesheet from the tokens."""
    t = TOKENS
    return f"""
    QWidget {{
        background-color: {t['bg_base']};
        color: {t['text_body']};
        font-family: {FONT_BODY};
        font-size: 14px;
    }}
    QMainWindow, QDialog {{ background-color: {t['bg_void']}; }}

    QLabel#Wordmark {{
        font-family: {FONT_DISPLAY};
        color: {t['text_strong']};
        font-size: 30px;
        letter-spacing: 3px;
        padding: 4px 0;
    }}
    QLabel#Subwordmark {{ color: {t['gold']}; font-family: {FONT_HEADING}; letter-spacing: 4px; font-size: 11px; }}
    QLabel#H1 {{ font-family: {FONT_HEADING}; color: {t['text_strong']}; font-size: 20px; letter-spacing: 1px; }}
    QLabel#H2 {{ font-family: {FONT_HEADING}; color: {t['text_strong']}; font-size: 16px; letter-spacing: 1px; }}
    QLabel#Muted {{ color: {t['text_muted']}; }}
    QLabel#Faint {{ color: {t['text_faint']}; }}

    /* Cards / panels */
    QFrame#Card {{
        background-color: {t['bg_surface']};
        border: 1px solid {t['line']};
        border-radius: 8px;
    }}
    QFrame#Raised {{ background-color: {t['bg_raised']}; border: 1px solid {t['line_strong']}; border-radius: 8px; }}

    /* Command / terminal mono views */
    QLabel#Mono, QTextEdit#Mono, QPlainTextEdit#Mono {{
        background-color: {t['bg_inset']};
        color: {t['secure_glow']};
        font-family: {FONT_MONO};
        font-size: 14px;
        border: 1px solid {t['line']};
        border-radius: 5px;
        padding: 8px;
    }}
    QLabel#Skeleton {{ color: {t['text_faint']}; font-family: {FONT_MONO}; }}

    /* Inputs */
    QLineEdit, QComboBox {{
        background-color: {t['bg_inset']};
        border: 1px solid {t['line']};
        border-radius: 5px;
        padding: 7px 9px;
        color: {t['text_strong']};
        selection-background-color: {t['purple']};
    }}
    QLineEdit:focus, QComboBox:focus {{ border: 1px solid {t['purple_glow']}; }}
    QCheckBox {{ color: {t['text_body']}; }}
    QCheckBox::indicator {{ width: 16px; height: 16px; border: 1px solid {t['line_strong']}; border-radius: 3px; background: {t['bg_inset']}; }}
    QCheckBox::indicator:checked {{ background: {t['purple']}; border: 1px solid {t['purple_glow']}; }}

    /* Buttons */
    QPushButton {{
        background-color: {t['bg_raised']};
        border: 1px solid {t['line_strong']};
        border-radius: 5px;
        padding: 8px 16px;
        color: {t['text_strong']};
        font-family: {FONT_HEADING};
        letter-spacing: 1px;
    }}
    QPushButton:hover {{ background-color: {t['bg_hover']}; border-color: {t['purple_glow']}; }}
    QPushButton:disabled {{ color: {t['text_faint']}; border-color: {t['line_faint']}; }}

    QPushButton#Primary {{ background-color: {t['purple']}; border: 1px solid {t['purple_glow']}; color: {t['text_strong']}; }}
    QPushButton#Primary:hover {{ background-color: {t['purple_deep']}; }}
    QPushButton#Yes {{ background-color: {t['secure']}; border: 1px solid {t['secure_glow']}; color: {t['text_strong']}; }}
    QPushButton#No {{ background-color: {t['critical_deep']}; border: 1px solid {t['critical']}; color: {t['text_strong']}; }}

    /* Tabs (category coding applied per-tab in code) */
    QTabWidget::pane {{ border: 1px solid {t['line']}; border-radius: 6px; top: -1px; }}
    QTabBar::tab {{
        background: {t['bg_surface']};
        color: {t['text_muted']};
        font-family: {FONT_HEADING};
        letter-spacing: 1px;
        padding: 9px 18px;
        border: 1px solid {t['line']};
        border-bottom: none;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
    }}
    QTabBar::tab:selected {{ color: {t['text_strong']}; background: {t['bg_raised']}; border-color: {t['purple']}; }}

    QListWidget {{ background: {t['bg_surface']}; border: 1px solid {t['line']}; border-radius: 6px; outline: none; }}
    QListWidget::item {{ padding: 9px 10px; border-bottom: 1px solid {t['line_faint']}; }}
    QListWidget::item:selected {{ background: {t['purple_deep']}; color: {t['text_strong']}; }}

    /* Status callouts */
    QFrame#Critical {{ background: {t['bg_surface']}; border: 1px solid {t['critical']}; border-left: 4px solid {t['critical']}; border-radius: 5px; }}
    QFrame#Warning  {{ background: {t['bg_surface']}; border: 1px solid {t['warning']};  border-left: 4px solid {t['warning']};  border-radius: 5px; }}
    QFrame#Secure   {{ background: {t['bg_surface']}; border: 1px solid {t['secure']};   border-left: 4px solid {t['secure']};   border-radius: 5px; }}
    QFrame#Info     {{ background: {t['bg_surface']}; border: 1px solid {t['info']};     border-left: 4px solid {t['info']};     border-radius: 5px; }}

    QScrollBar:vertical {{ background: {t['bg_base']}; width: 10px; }}
    QScrollBar::handle:vertical {{ background: {t['line_strong']}; border-radius: 5px; min-height: 24px; }}
    """
