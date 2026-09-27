"""LinguaForge visual theme.

Application palette and global QSS.
QFluentWidgets controls keep their native icon/text layout.
"""

BG = "#090f1f"
SIDEBAR = "#0e1730"
PANEL = "#121d39"
PANEL_2 = "#162442"
CARD = "#1a2a4d"
CARD_HOVER = "#20345e"
BORDER = "#263b64"

TEXT = "#f3f6ff"
MUTED = "#91a0bd"

ACCENT = "#2e8cff"
ACCENT_2 = "#7155ff"

SUCCESS = "#35d07f"
DANGER = "#ff5d78"
WARNING = "#ffbf5c"


APP_QSS = f"""
QWidget {{
    color: {TEXT};
    font-family: "Segoe UI";
    font-size: 12pt;
}}

QMainWindow,
QDialog {{
    background: {BG};
}}


/* =========================================================
   Scrollbars
   ========================================================= */

QScrollArea {{
    border: none;
    background: transparent;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 4px 2px 4px 0;
}}

QScrollBar::handle:vertical {{
    background: #263a60;
    min-height: 32px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical:hover {{
    background: #35517f;
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {{
    background: transparent;
    height: 0;
}}


/* =========================================================
   Text inputs
   ========================================================= */

QLineEdit,
QPlainTextEdit,
QTextEdit {{
    background: {CARD};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    selection-background-color: {ACCENT};
    padding: 7px 10px;
}}

QLineEdit:focus,
QPlainTextEdit:focus,
QTextEdit:focus {{
    border: 1px solid {ACCENT};
}}


/* =========================================================
   Combo box
   ========================================================= */

QComboBox {{
    background: {CARD};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 7px 10px;
    min-height: 20px;
}}

QComboBox:hover {{
    border: 1px solid #3a5685;
}}

QComboBox QAbstractItemView {{
    background: {PANEL};
    color: {TEXT};
    border: 1px solid {BORDER};
    selection-background-color: {ACCENT};
}}


/* =========================================================
   Tooltips
   ========================================================= */

QToolTip {{
    background: #0d1730;
    color: {TEXT};
    border: 1px solid {BORDER};
    padding: 6px 8px;
}}


/* =========================================================
   Progress bar
   ========================================================= */

QProgressBar {{
    background: #263758;
    border: none;
    border-radius: 5px;
    text-align: center;
    color: transparent;
    min-height: 8px;
    max-height: 8px;
}}

QProgressBar::chunk {{
    border-radius: 5px;
    background: #2e8cff;
}}


/* =========================================================
   Main application
   ========================================================= */

#root {{
    background: {BG};
}}

#topBar {{
    background: #0c1428;
    border-bottom: 1px solid {BORDER};
}}

#sidebar {{
    background: {SIDEBAR};
    border-right: 1px solid {BORDER};
}}

#contentStack {{
    background: {BG};
}}

#page,
#pageContent {{
    background: {BG};
}}


/* =========================================================
   Page titles
   ========================================================= */

#pageTitle {{
    color: {TEXT};
    font-size: 26px;
    font-weight: 700;
}}

#pageSubtitle {{
    color: {MUTED};
    font-size: 12px;
}}


/* =========================================================
   Header branding
   ========================================================= */

#brandName {{
    color: {TEXT};
    font-size: 17px;
    font-weight: 700;
    margin: 0px;
    padding: 0px;
}}

#brandTagline {{
    color: {MUTED};
    font-size: 11px;
    margin: 0px;
    padding: 0px;
}}

#sidebarBrand,
#muted {{
    color: {MUTED};
    font-size: 11px;
}}


/* =========================================================
   Header status pills
   ========================================================= */

#headerPill,
#headerPillMuted {{
    background: #172746;
    color: {MUTED};
    border: 1px solid #29436e;
    border-radius: 8px;
    padding: 2px 8px;
    margin: 0px;
    font-size: 14px;
    font-weight: 700;
}}

/* =========================
   Status colors
   ========================= */

#headerPill[status="ready"],
#headerPillMuted[status="ready"] {{
    background: #123b2a;
    color: #5ee99b;
    border: 1px solid #23764b;
}}

#headerPill[status="error"],
#headerPillMuted[status="error"] {{
    background: #401c27;
    color: #ff7188;
    border: 1px solid #85354a;
}}

#headerPill[status="checking"],
#headerPillMuted[status="checking"] {{
    background: #172746;
    color: {MUTED};
    border: 1px solid #29436e;
}}


/* =========================================================
   Cards
   ========================================================= */

#sectionCard {{
    background: {PANEL_2};
    border: 1px solid {BORDER};
    border-radius: 10px;
}}

#cardTitle {{
    color: {TEXT};
    font-size: 13px;
    font-weight: 700;
}}

#cardSubtitle {{
    color: {MUTED};
    font-size: 10px;
    font-weight: 600;
}}


/* =========================================================
   Field labels
   ========================================================= */

#fieldLabel {{
    color: {MUTED};
    font-size: 11px;
    font-weight: 600;
}}

#valueBadge {{
    background: #1d3157;
    color: {TEXT};
    border: 1px solid #2a4776;
    border-radius: 7px;
    padding: 5px;
    font-weight: 700;
}}


/* =========================================================
   Dialogue preview
   ========================================================= */

#dialoguePreview {{
    background: #0d1830;
    border: 1px solid #20365f;
    border-radius: 8px;
}}

#dialogueEditor {{
    background: #0d1830;
    color: #dfe7fb;
    border: none;
    border-radius: 6px;
    padding: 8px;
    selection-background-color: #2e8cff;
}}

/* =========================================================
   Generate button
   ========================================================= */

#generateButton {{
    background: qlineargradient(
        x1: 0,
        y1: 0,
        x2: 1,
        y2: 0,
        stop: 0 #6b3cff,
        stop: 0.52 #4d73ff,
        stop: 1 #168ff5
    );

    color: white;
    border: none;
    border-radius: 10px;
    padding: 0 28px;
    font-size: 14px;
    font-weight: 700;
}}

#generateButton:hover {{
    background: qlineargradient(
        x1: 0,
        y1: 0,
        x2: 1,
        y2: 0,
        stop: 0 #7a50ff,
        stop: 0.52 #5a80ff,
        stop: 1 #2aa2ff
    );
}}

#generateButton:pressed {{
    padding-top: 2px;
}}



#sidebarFooterText {{
    color: {MUTED};
    font-size: 10pt;
    font-weight: 500;
}}

#sidebarGitHub {{
    color: {ACCENT};
    font-size: 10pt;
    font-weight: 600;
}}

#sidebarGitHub:hover {{
    color: #75b7ff;
}}

/* =========================================================
   Sidebar navigation
   =========================================================

   Navigation uses a dedicated widget, so icon/text spacing is controlled
   by its own layout and is independent of QFluentWidgets button geometry.
   */

#navItem {{
    background: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
}}

#navItem QLabel#navText {{
    color: {MUTED};
    font-size: 12pt;
    font-weight: 600;
}}

#navItem:hover {{
    background: #142342;
    border: 1px solid #1e3153;
}}

#navItem:hover QLabel#navText {{
    color: {TEXT};
}}

#navItem[active="true"] {{
    background: #1558c8;
    border: 1px solid #2f79e6;
}}

#navItem[active="true"] QLabel#navText {{
    color: white;
    font-weight: 700;
}}


/* =========================================================
   Speaker
   ========================================================= */

#speakerBadge {{
    background: #1e3158;
    color: #55a9ff;
    border-radius: 10px;
    font-size: 17px;
    font-weight: 700;
}}

#speakerName {{
    color: {TEXT};
    font-family: "Consolas";
    font-size: 12px;
    font-weight: 700;
}}


/* =========================================================
   Danger button
   ========================================================= */

#dangerButton {{
    color: {DANGER};
}}

#dangerButton:hover {{
    background: #3a1b2b;
}}


/* =========================================================
   Empty state
   ========================================================= */

#emptyState {{
    background: {PANEL_2};
    border: 1px solid {BORDER};
    border-radius: 10px;
}}

#emptyTitle {{
    color: {TEXT};
    font-size: 16px;
    font-weight: 700;
}}


/* =========================================================
   System
   ========================================================= */

#systemValue {{
    color: {TEXT};
    font-size: 13px;
    font-weight: 700;
}}

#mono {{
    color: {MUTED};
    font-family: "Consolas";
    font-size: 11px;
}}

#statusLabel {{
    color: {TEXT};
    font-size: 11px;
    font-weight: 700;
}}
"""


def page_title(title, subtitle):
    from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

    box = QWidget()

    layout = QVBoxLayout(box)
    layout.setContentsMargins(0, 0, 0, 18)
    layout.setSpacing(2)

    title_label = QLabel(title)
    title_label.setObjectName("pageTitle")

    subtitle_label = QLabel(subtitle)
    subtitle_label.setObjectName("pageSubtitle")

    layout.addWidget(title_label)
    layout.addWidget(subtitle_label)

    return box