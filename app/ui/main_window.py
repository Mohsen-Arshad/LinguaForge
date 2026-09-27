import os
import queue
import time
import webbrowser
from pathlib import Path

from PySide6.QtCore import QTimer, Qt, QSize
from PySide6.QtGui import QPixmap, QPainter, QPen, QIcon
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QStackedWidget,
    QFrame,
)

from qfluentwidgets import (
    FluentIcon as FIF,
    PushButton,
    Theme,
    setTheme,
    setThemeColor,
)

from app.models.events import AppEvent
from app.models.generation import GenerationConfig
from app.models.speaker import Speaker
from app.services.audio_generator import AudioGenerator
from app.services.dialogue_parser import DialogueParser
from app.services.pause_service import PauseService
from app.services.speaker_repository import SpeakerRepository
from app.services.system_service import SystemService
from app.ui import theme
from app.ui.generate_view import GenerateView
from app.ui.speakers_view import SpeakersView
from app.ui.system_view import SystemView
from app.ui.widgets import NavButton
from app.utils.threading_utils import run_background


APP_TITLE = "LinguaForge"
APP_VERSION = "1.0.0"
APP_GITHUB_URL = "https://github.com/"  # Replace with the project's repository URL.


# ================================================================
# LOADING SPINNER
# ================================================================

class LoadingSpinner(QWidget):
    """Animated circular spinner used by the startup overlay."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.angle = 0
        self.setFixedSize(42, 42)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._rotate)
        self.timer.start(80)

    def _rotate(self):
        self.angle = (self.angle + 30) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        center = self.rect().center()

        radius = 14
        pen_width = 3

        for i in range(12):
            angle = self.angle - (i * 30)

            opacity = 1.0 - (i / 12.0)

            if opacity < 0.15:
                opacity = 0.15

            color = self.palette().highlight().color()
            color.setAlphaF(opacity)

            pen = QPen(color)
            pen.setWidth(pen_width)
            pen.setCapStyle(Qt.RoundCap)

            painter.setPen(pen)

            painter.save()
            painter.translate(center)
            painter.rotate(angle)

            painter.drawLine(
                0,
                -radius + 4,
                0,
                -radius + 10,
            )

            painter.restore()


# ================================================================
# STARTUP OVERLAY
# ================================================================

class StartupOverlay(QFrame):
    """Full-window startup overlay."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("startupOverlay")

        self.setStyleSheet(
            """
            #startupOverlay {
                background: rgba(9, 15, 31, 245);
            }

            #startupTitle {
                color: #f3f6ff;
                font-size: 26px;
                font-weight: 700;
            }

            #startupStatus {
                color: #91a0bd;
                font-size: 13px;
            }

            #startupHint {
                color: #667693;
                font-size: 11px;
            }
            """
        )

        self.spinner = LoadingSpinner(self)

        self.title = QLabel("LinguaForge")
        self.title.setObjectName("startupTitle")
        self.title.setAlignment(Qt.AlignCenter)

        self.status = QLabel("Starting application…")
        self.status.setObjectName("startupStatus")
        self.status.setAlignment(Qt.AlignCenter)

        self.hint = QLabel(
            "Please wait while the local runtime is checked."
        )
        self.hint.setObjectName("startupHint")
        self.hint.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)

        layout.addWidget(
            self.spinner,
            alignment=Qt.AlignCenter,
        )

        layout.addWidget(self.title)
        layout.addWidget(self.status)

        layout.addSpacing(4)

        layout.addWidget(self.hint)

        self.raise_()

    def set_status(self, text):
        self.status.setText(text)

    def resize_to_parent(self):
        if self.parentWidget():
            self.setGeometry(
                self.parentWidget().rect()
            )
            self.raise_()


# ================================================================
# GENERATION OVERLAY
# ================================================================

class GenerationOverlay(QFrame):
    """Full-window overlay shown while generation is being prepared/running."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("generationOverlay")
        self.setStyleSheet(
            """
            #generationOverlay {
                background: rgba(9, 15, 31, 245);
            }

            #generationTitle {
                color: #f3f6ff;
                font-size: 24px;
                font-weight: 700;
            }

            #generationStatus {
                color: #91a0bd;
                font-size: 13px;
            }

            #generationHint {
                color: #667693;
                font-size: 11px;
            }
            """
        )

        self.spinner = LoadingSpinner(self)

        self.title = QLabel("Loading generation model…")
        self.title.setObjectName("generationTitle")
        self.title.setAlignment(Qt.AlignCenter)

        self.status = QLabel("Initializing Chatterbox Turbo…")
        self.status.setObjectName("generationStatus")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setWordWrap(True)

        self.hint = QLabel(
            "The app is working in the background. This window will stay responsive."
        )
        self.hint.setObjectName("generationHint")
        self.hint.setAlignment(Qt.AlignCenter)
        self.hint.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)
        layout.addWidget(self.spinner, alignment=Qt.AlignCenter)
        layout.addWidget(self.title)
        layout.addWidget(self.status)
        layout.addSpacing(4)
        layout.addWidget(self.hint)

    def set_status(self, text):
        self.status.setText(text)

    def resize_to_parent(self):
        if self.parentWidget():
            self.setGeometry(self.parentWidget().rect())
            self.raise_()


# ================================================================
# MAIN WINDOW
# ================================================================

class MainWindow(QMainWindow):
    """Presentation shell coordinating views, application services, and runtime state."""

    def __init__(self):
        super().__init__()

        # ---------------------------------------------------------
        # THEME
        # ---------------------------------------------------------

        setTheme(Theme.DARK)
        setThemeColor(theme.ACCENT)

        # ---------------------------------------------------------
        # WINDOW
        # ---------------------------------------------------------

        self.setWindowTitle(APP_TITLE)

        logo_path = (
            Path(__file__).resolve().parents[2]
            / "assets"
            / "linguaforge_logo.png"
        )

        if logo_path.exists():
            self.setWindowIcon(
                QIcon(str(logo_path))
            )

        self.resize(1180, 760)
        self.setMinimumSize(960, 640)
        self.setObjectName("mainWindow")

        # ---------------------------------------------------------
        # ROOT
        # ---------------------------------------------------------

        root = QWidget()
        root.setObjectName("root")

        self.setCentralWidget(root)

        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ---------------------------------------------------------
        # SERVICES / STATE
        # ---------------------------------------------------------

        self.events = queue.Queue()

        self.repo = SpeakerRepository()
        self.pause_service = PauseService()
        self.system = SystemService()
        self.parser = DialogueParser()
        self.speakers = self.repo.load()

        self.generating = False
        self.start_time = None
        self.current_tab = "generate"

        # =========================================================
        # CACHED SYSTEM STATE
        # =========================================================

        self.gpu_ok = None
        self.gpu_result = None
        self.model_result = None
        self.dependencies_result = None

        # =========================================================
        # STARTUP CHECK STATE
        # =========================================================

        self.startup_gpu_done = False
        self.startup_dependencies_done = False
        self.startup_sequence_active = True

        self.dependencies_checking = False
        self.gpu_checking = False

        self.recheck_after_dependencies = False

        self.installing_dependencies = False

        # ---------------------------------------------------------
        # DEFAULT PATHS / SETTINGS
        # ---------------------------------------------------------

        self.input_path = "input.txt"

        self.output_path = os.path.join(
            "output",
            "shadowing.mp3",
        )

        self.speed = 0.95
        self.volume = 1.30
        self.bitrate = "192k"

        # ---------------------------------------------------------
        # AUDIO GENERATOR
        # ---------------------------------------------------------

        self.audio_generator = AudioGenerator(
            parser=self.parser,

            log=lambda text:
            self.events.put(
                AppEvent(
                    "log",
                    text,
                )
            ),

            status=lambda text:
            self.events.put(
                AppEvent(
                    "status",
                    text,
                )
            ),

            progress=lambda current, total:
            self.events.put(
                AppEvent(
                    "progress",
                    (current, total),
                )
            ),

            model_ready=lambda text:
            self.events.put(
                AppEvent(
                    "model",
                    text,
                )
            ),
        )

        # ---------------------------------------------------------
        # BUILD UI
        # ---------------------------------------------------------

        self._build_shell(root_layout)

        # ---------------------------------------------------------
        # STARTUP OVERLAY
        # ---------------------------------------------------------

        self.startup_overlay = StartupOverlay(root)

        self.startup_overlay.resize_to_parent()

        self.startup_overlay.show()
        self.startup_overlay.raise_()

        # Generation overlay is kept hidden until Generate is pressed.
        self.generation_overlay = GenerationOverlay(root)
        self.generation_overlay.resize_to_parent()
        self.generation_overlay.hide()

        # ---------------------------------------------------------
        # EVENT TIMER
        # ---------------------------------------------------------

        self._process_events_timer = QTimer(self)

        self._process_events_timer.timeout.connect(
            self._process_events
        )

        self._process_events_timer.start(120)

        # ---------------------------------------------------------
        # STARTUP SEQUENCE
        # ---------------------------------------------------------

        QTimer.singleShot(
            150,
            self._start_runtime_diagnostics,
        )

    def _start_runtime_diagnostics(self):
        """Load the validated runtime snapshot or perform the one-time scan."""
        cached = self.system.load_cached_diagnostics()
        if cached is not None:
            self._apply_diagnostics(cached)
            self.startup_sequence_active = False
            self.startup_gpu_done = True
            self.startup_dependencies_done = True
            self._finish_startup_overlay()
            return

        self.startup_overlay.set_status("First launch: checking local runtime…")
        run_background(
            lambda: self.system.diagnostics(persist=True),
            on_success=lambda result: self.events.put(AppEvent("diagnostics", result)),
            on_error=lambda exc: self.events.put(
                AppEvent("diagnostics_error", str(exc))
            ),
        )

    def _apply_diagnostics(self, diagnostics):
        deps = diagnostics["deps"]
        all_ok = diagnostics["deps_ok"]
        self.dependencies_result = (deps, all_ok)
        self.gpu_ok = diagnostics["gpu_ok"]
        self.gpu_result = (
            diagnostics["gpu_ok"],
            diagnostics["gpu_short"],
            diagnostics["gpu_details"],
        )
        self.model_result = (
            diagnostics["model_ok"],
            diagnostics["model_details"],
        )

        self._set_status_pill(
            self.header_gpu,
            "CUDA • READY" if diagnostics["gpu_ok"] else "CUDA • OFFLINE",
            "ready" if diagnostics["gpu_ok"] else "error",
        )
        self._set_status_pill(
            self.header_model,
            "Chatterbox • READY" if diagnostics["model_ok"] else "Chatterbox • ERROR",
            "ready" if diagnostics["model_ok"] else "error",
        )

        if isinstance(self.current_view, SystemView):
            self.current_view.update_gpu(*self.gpu_result)
            self.current_view.update_model(*self.model_result)
            self.current_view.update_dependencies(deps, all_ok)

    # =============================================================
    # UI BUILDING
    # =============================================================

    def _build_shell(self, root_layout):

        # ---------------------------------------------------------
        # HEADER
        # ---------------------------------------------------------

        header = QFrame()
        header.setObjectName("topBar")
        header.setFixedHeight(58)

        h = QHBoxLayout(header)

        h.setContentsMargins(18, 0, 18, 0)
        h.setSpacing(8)

        # ---------------------------------------------------------
        # LOGO
        # ---------------------------------------------------------

        logo = QLabel()
        logo.setFixedSize(50, 50)
        logo.setAlignment(Qt.AlignCenter)

        logo_path = (
            Path(__file__).resolve().parents[2]
            / "assets"
            / "linguaforge_logo.png"
        )

        if logo_path.exists():
            logo.setPixmap(
                QPixmap(
                    str(logo_path)
                ).scaled(
                    50,
                    50,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )

        h.addWidget(logo)

        # ---------------------------------------------------------
        # BRAND
        # ---------------------------------------------------------

        brand = QVBoxLayout()
        brand.setContentsMargins(0, 0, 0, 0)
        brand.setSpacing(0)

        name = QLabel("LinguaForge")
        name.setObjectName("brandName")
        name.setMargin(0)

        tagline = QLabel(
            "Local speech & dialogue studio"
        )
        tagline.setObjectName("brandTagline")
        tagline.setMargin(0)

        brand.addWidget(
            name,
            0,
            Qt.AlignBottom,
        )

        brand.addWidget(
            tagline,
            0,
            Qt.AlignTop,
        )

        h.addLayout(brand)

        # =========================================================
        # STATUS GROUP
        # =========================================================

        status_group = QFrame()
        status_group.setObjectName("statusGroup")

        # Force the group itself to remain compact.
        status_group.setFixedHeight(34)

        status_layout = QHBoxLayout(status_group)

        # 5px around the status pills.
        status_layout.setContentsMargins(
            5,
            5,
            5,
            5,
        )

        status_layout.setSpacing(8)

        # ---------------------------------------------------------
        # GPU STATUS
        # ---------------------------------------------------------

        self.header_gpu = QLabel(
            "CUDA • checking…"
        )

        self.header_gpu.setObjectName(
            "headerPill"
        )

        # Force the green pill to a compact height.
        self.header_gpu.setFixedHeight(24)

        # Center text horizontally and vertically.
        self.header_gpu.setAlignment(
            Qt.AlignCenter
        )

        status_layout.addWidget(
            self.header_gpu
        )

        # ---------------------------------------------------------
        # MODEL STATUS
        # ---------------------------------------------------------

        self.header_model = QLabel(
            "Chatterbox • checking…"
        )

        self.header_model.setObjectName(
            "headerPillMuted"
        )

        # Force the green pill to a compact height.
        self.header_model.setFixedHeight(24)

        # Center text horizontally and vertically.
        self.header_model.setAlignment(
            Qt.AlignCenter
        )

        status_layout.addWidget(
            self.header_model
        )

        # Keep the status group compact.
        h.addWidget(
            status_group,
            0,
            Qt.AlignVCenter,
        )

        root_layout.addWidget(header)

        # =========================================================
        # BODY
        # =========================================================

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        root_layout.addLayout(body, 1)

        # =========================================================
        # SIDEBAR
        # =========================================================

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(210)

        s = QVBoxLayout(sidebar)

        s.setContentsMargins(
            12,
            16,
            12,
            12,
        )

        s.setSpacing(5)

        self.nav_buttons = {}

        items = [
            (
                "generate",
                FIF.PLAY,
                "Generate",
            ),
            (
                "speakers",
                FIF.PEOPLE,
                "Speakers",
            ),
            (
                "system",
                FIF.SETTING,
                "System",
            ),
        ]

        for name_key, icon, text in items:
            btn = NavButton(
                icon,
                text,
                lambda n=name_key: self.show_tab(n),
            )

            btn.setFixedHeight(44)
            btn.setMinimumWidth(186)
            btn.setProperty("active", "false")

            self.nav_buttons[name_key] = btn
            s.addWidget(btn)

        s.addStretch()

        # ---------------------------------------------------------
        # BOTTOM BRANDING / PROJECT INFO
        # ---------------------------------------------------------

        footer = QVBoxLayout()
        footer.setContentsMargins(8, 10, 8, 2)
        footer.setSpacing(5)

        brand_bottom = QHBoxLayout()
        brand_bottom.setContentsMargins(0, 0, 0, 0)
        brand_bottom.setSpacing(8)

        logo_small = QLabel()
        logo_small.setFixedSize(28, 28)
        logo_small.setAlignment(Qt.AlignCenter)

        if logo_path.exists():
            logo_small.setPixmap(
                QPixmap(str(logo_path)).scaled(
                    28,
                    28,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )

        brand_bottom.addWidget(logo_small)

        brand_name = QLabel("LinguaForge")
        brand_name.setObjectName("sidebarBrand")
        brand_bottom.addWidget(brand_name)
        brand_bottom.addStretch()

        footer.addLayout(brand_bottom)

        version = QLabel(
            f"v{APP_VERSION}  •  Free & Open Source"
        )
        version.setObjectName("sidebarFooterText")
        version.setWordWrap(True)
        footer.addWidget(version)

        github = QLabel(
            f'<a href="{APP_GITHUB_URL}">GitHub</a>'
        )
        github.setObjectName("sidebarGitHub")
        github.setOpenExternalLinks(True)
        github.setTextInteractionFlags(
            Qt.TextBrowserInteraction
        )
        footer.addWidget(github)

        s.addLayout(footer)

        body.addWidget(sidebar)

        # =========================================================
        # CONTENT
        # =========================================================

        self.stack = QStackedWidget()

        self.stack.setObjectName(
            "contentStack"
        )

        body.addWidget(
            self.stack,
            1,
        )

        # ---------------------------------------------------------
        # DEFAULT TAB
        # ---------------------------------------------------------

        self.show_tab("generate")

    # =============================================================
    # STARTUP OVERLAY
    # =============================================================

    def _finish_startup_overlay(self):

        if not self.startup_gpu_done:
            return

        if not self.startup_dependencies_done:
            return

        if not hasattr(
            self,
            "startup_overlay",
        ):
            return

        if self.startup_overlay is None:
            return

        self.startup_overlay.set_status(
            "System check complete ✓"
        )

        QTimer.singleShot(
            450,
            self._hide_startup_overlay,
        )

    def _hide_startup_overlay(self):

        if not hasattr(
            self,
            "startup_overlay",
        ):
            return

        if self.startup_overlay is None:
            return

        self.startup_overlay.hide()

        self.startup_overlay.deleteLater()

        self.startup_overlay = None

        self.startup_sequence_active = False

    # =============================================================
    # WINDOW EVENTS
    # =============================================================

    def resizeEvent(self, event):

        super().resizeEvent(event)

        if hasattr(
            self,
            "startup_overlay",
        ):

            if self.startup_overlay is not None:
                self.startup_overlay.resize_to_parent()

    # =============================================================
    # TAB MANAGEMENT
    # =============================================================

    def show_tab(self, name):

        self.current_tab = name

        while self.stack.count():

            widget = self.stack.widget(0)

            self.stack.removeWidget(
                widget
            )

            widget.deleteLater()

        if name == "generate":

            view = GenerateView(
                self.stack,
                self,
            )

        elif name == "speakers":

            view = SpeakersView(
                self.stack,
                self,
            )

        else:

            view = SystemView(
                self.stack,
                self,
            )

        self.current_view = view

        self.stack.addWidget(view)

        self.stack.setCurrentWidget(
            view
        )

        if isinstance(
            view,
            SystemView,
        ):

            self._restore_system_view_state()

        elif isinstance(
            view,
            GenerateView,
        ):

            self._restore_generate_view_state()

        for key, button in self.nav_buttons.items():
            active = key == name
            button.set_active(active)

    # =============================================================
    # RESTORE SYSTEM VIEW
    # =============================================================

    def _restore_system_view_state(self):

        view = self.current_view

        if not isinstance(
            view,
            SystemView,
        ):
            return

        if self.gpu_result is not None:

            ok, short, details = (
                self.gpu_result
            )

            view.update_gpu(
                ok,
                short,
                details,
            )

        if self.model_result is not None:

            model_ok, model_details = (
                self.model_result
            )

            view.update_model(
                model_ok,
                model_details,
            )

        if self.dependencies_result is not None:

            rows, all_ok = (
                self.dependencies_result
            )

            view.update_dependencies(
                rows,
                all_ok,
            )

    # =============================================================
    # RESTORE GENERATE VIEW
    # =============================================================

    def _restore_generate_view_state(self):
        return

    # =============================================================
    # FILE SELECTION
    # =============================================================

    def choose_input(self):

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select input text",
            "",
            "Text (*.txt);;All files (*.*)",
        )

        if path:

            self.input_path = path

            if hasattr(
                self,
                "input_widget",
            ):

                self.input_widget.setText(
                    path
                )

    def choose_output(self):

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save MP3",
            "shadowing.mp3",
            "MP3 (*.mp3)",
        )

        if path:

            self.output_path = path

            if hasattr(
                self,
                "output_widget",
            ):

                self.output_widget.setText(
                    path
                )

    # =============================================================
    # SPEAKERS
    # =============================================================

    def save_speakers(self):

        self.repo.save(
            self.speakers
        )

    def add_speaker(self):

        existing = {
            s.name
            for s in self.speakers
        }

        n = 1

        while f"speaker{n}" in existing:
            n += 1

        self.speakers.append(
            Speaker(
                f"speaker{n}"
            )
        )

        self.save_speakers()

        self.show_tab(
            "speakers"
        )

    def remove_speaker(self, speaker):

        answer = QMessageBox.question(
            self,
            "Remove speaker",
            f"Remove [{speaker.name}] "
            "from the voice library?",
            QMessageBox.Yes
            | QMessageBox.No,
        )

        if answer == QMessageBox.Yes:

            self.speakers.remove(
                speaker
            )

            self.save_speakers()

            self.show_tab(
                "speakers"
            )

    # =============================================================
    # PAUSES
    # =============================================================

    def auto_generate_pauses(self):

        input_file = (
            self.input_path.strip()
        )

        if hasattr(
            self,
            "input_widget",
        ):

            input_file = (
                self.input_widget.text().strip()
            )

        if (
            not input_file
            or not os.path.isfile(
                input_file
            )
        ):

            QMessageBox.critical(
                self,
                "Input",
                "Input text file was not found. "
                "Select a valid .txt file first.",
            )

            return

        try:

            added, skipped, backup = (
                self.pause_service
                .add_missing_pauses(
                    input_file
                )
            )

            if added == 0:

                QMessageBox.information(
                    self,
                    "Automatic Pauses",
                    f"No missing pauses were found.\n\n"
                    f"Existing pauses kept: {skipped}",
                )

                return

            QMessageBox.information(
                self,
                "Automatic Pauses",
                f"Added pauses to {added} line(s).\n"
                f"Existing pauses kept: {skipped}.\n\n"
                f"Backup created:\n{backup}",
            )

            if isinstance(
                self.current_view,
                GenerateView,
            ):

                self.current_view._update_preview(
                    input_file
                )

        except Exception as exc:

            QMessageBox.critical(
                self,
                "Automatic Pauses",
                "Could not update the input file.\n\n"
                f"{exc}",
            )

    # =============================================================
    # GENERATION
    # =============================================================

    def start_generation(self):

        if (
            self.generating
            or not isinstance(
                self.current_view,
                GenerateView,
            )
        ):
            return

        values = self.current_view.values()

        self.input_path = values["input_file"]
        self.output_path = values["output_file"]
        self.speed = values["speed"]
        self.volume = values["volume"]
        self.bitrate = values["bitrate"]

        # These checks are intentionally kept on the GUI thread because they
        # are cheap filesystem/UI validation and should fail immediately.
        if not os.path.isfile(self.input_path):
            QMessageBox.critical(
                self,
                "Input",
                "Input text file was not found.",
            )
            return

        configured = {
            s.name: s.path
            for s in self.speakers
            if s.path and os.path.isfile(s.path)
        }

        if not configured:
            QMessageBox.critical(
                self,
                "Speakers",
                "Add at least one speaker and select a valid reference audio.",
            )
            self.show_tab("speakers")
            return

        config = GenerationConfig(
            input_file=self.input_path,
            output_file=self.output_path,
            speakers=configured,
            speed=self.speed,
            volume=self.volume,
            bitrate=self.bitrate,
        )

        # IMPORTANT: model_status() can import/inspect heavy ML packages.
        # Never call it directly from the Qt GUI thread. Show the overlay
        # first, let Qt paint it, then run the check in the background.
        self.generating = True
        self.start_time = time.time()

        self.current_view.set_generating(True)
        self.current_view.set_status("Preparing…")
        self.current_view.set_progress(0, 0, "")

        self.generation_overlay.set_status(
            "Initializing Chatterbox Turbo…"
        )
        self.generation_overlay.resize_to_parent()
        self.generation_overlay.show()
        self.generation_overlay.raise_()

        # Give Qt one event-loop turn to paint the overlay before starting
        # any expensive work.
        QTimer.singleShot(0, lambda: self._prepare_generation(config))

    def _prepare_generation(self, config):
        """Check the model off the GUI thread before starting generation."""
        run_background(
            self.system.model_status,
            on_success=lambda result: self.events.put(
                AppEvent(
                    "generation_model_check",
                    (result, config),
                )
            ),
            on_error=lambda exc: self.events.put(
                AppEvent(
                    "generation_prepare_error",
                    str(exc),
                )
            ),
        )

    # =============================================================
    # STATUS PILL
    # =============================================================

    def _set_status_pill(
        self,
        widget,
        text,
        status,
    ):

        widget.setText(text)

        widget.setProperty(
            "status",
            status,
        )

        widget.style().unpolish(
            widget
        )

        widget.style().polish(
            widget
        )

        widget.update()

    # =============================================================
    # GPU
    # =============================================================

    def check_gpu(self):

        if self.gpu_checking:
            return

        self.gpu_checking = True

        self._set_status_pill(
            self.header_gpu,
            "CUDA • CHECKING…",
            "checking",
        )

        if (
            hasattr(
                self,
                "startup_overlay",
            )
            and self.startup_overlay is not None
        ):

            self.startup_overlay.set_status(
                "Checking CUDA / GPU…"
            )

        run_background(
            self.system.check_gpu,

            on_success=lambda result:
            self.events.put(
                AppEvent(
                    "gpu",
                    result,
                )
            ),

            on_error=lambda exc:
            self.events.put(
                AppEvent(
                    "gpu",
                    (
                        False,
                        "GPU CHECK FAILED",
                        str(exc),
                    ),
                )
            ),
        )

    # =============================================================
    # DEPENDENCIES
    # =============================================================

    def fix_gpu(self):

        self.install_missing(
            full=True
        )

    def install_missing(self):
        """Install or repair only dependencies that are missing or invalid."""
        if self.installing_dependencies:
            return
        self.installing_dependencies = True
        if isinstance(self.current_view, SystemView):
            self.current_view.set_installing(True)
            self.current_view.append_log("Starting dependency repair…")
        run_background(
            lambda: self.system.install_missing(log=lambda text: self.events.put(AppEvent("log", text))),
            on_success=lambda result: self.events.put(AppEvent("install_done", result)),
            on_error=lambda exc: self.events.put(AppEvent("install_error", str(exc))),
        )

    def repair_all(self):
        """Reinstall the complete declared runtime when explicitly requested."""
        if self.installing_dependencies:
            return
        self.installing_dependencies = True
        if isinstance(self.current_view, SystemView):
            self.current_view.set_installing(True)
            self.current_view.append_log("Starting full runtime repair…")
        run_background(
            lambda: self.system.repair_all(log=lambda text: self.events.put(AppEvent("log", text))),
            on_success=lambda result: self.events.put(AppEvent("install_done", result)),
            on_error=lambda exc: self.events.put(AppEvent("install_error", str(exc))),
        )

    def refresh_dependencies(self):
        """Force a full runtime diagnostic and refresh the persisted snapshot."""
        if self.dependencies_checking:
            return

        self.dependencies_checking = True
        self.startup_sequence_active = False

        if isinstance(self.current_view, SystemView):
            self.current_view.dep_summary.setText("Checking local runtime…")

        run_background(
            lambda: self.system.diagnostics(persist=True),
            on_success=lambda result: self.events.put(AppEvent("diagnostics", result)),
            on_error=lambda exc: self.events.put(
                AppEvent("diagnostics_error", str(exc))
            ),
        )

    # =============================================================
    # EVENT QUEUE
    # =============================================================

    def _process_events(self):

        try:

            while True:

                event = self.events.get_nowait()

                self._handle_event(
                    event
                )

        except queue.Empty:
            pass

    # =============================================================
    # EVENT HANDLER
    # =============================================================

    def _handle_event(self, event):

        kind = event.kind
        value = event.payload

        # ---------------------------------------------------------
        # LOG
        # ---------------------------------------------------------

        if kind == "log":

            print(value)

            if isinstance(
                self.current_view,
                SystemView,
            ):

                self.current_view.append_log(
                    value
                )

        # ---------------------------------------------------------
        # STATUS
        # ---------------------------------------------------------

        elif kind == "status":

            if isinstance(
                self.current_view,
                GenerateView,
            ):

                self.current_view.set_status(value)

            if (
                hasattr(self, "generation_overlay")
                and self.generation_overlay.isVisible()
            ):
                self.generation_overlay.set_status(value)

        # ---------------------------------------------------------
        # MODEL EVENT
        # ---------------------------------------------------------

        elif kind == "model":

            self.header_model.setText(
                value
            )

            # The generation overlay is only for the expensive model
            # initialization phase. As soon as Chatterbox is ready,
            # hand the UI back to the normal GenerateView progress bar.
            if (
                value == "Chatterbox Ready"
                and hasattr(self, "generation_overlay")
                and self.generation_overlay.isVisible()
            ):
                self.generation_overlay.hide()

        # ---------------------------------------------------------
        # PROGRESS
        # ---------------------------------------------------------

        elif kind == "progress":

            current, total = value

            if isinstance(
                self.current_view,
                GenerateView,
            ):

                elapsed = (
                    time.time()
                    - self.start_time
                    if self.start_time
                    else 0
                )

                remaining = (
                    (elapsed / current)
                    * (total - current)
                    if current
                    else 0
                )

                self.current_view.set_progress(
                    current,
                    total,
                    f"ETA {self.format_time(remaining)}",
                )

        # ---------------------------------------------------------
        # DEPENDENCY INSTALL / REPAIR
        # ---------------------------------------------------------

        if kind == "install_done":
            self.installing_dependencies = False
            if isinstance(self.current_view, SystemView):
                self.current_view.set_installing(False)
                self.current_view.append_log("Dependency repair completed. Refreshing runtime state…")
            self.refresh_dependencies()
            return

        if kind == "install_error":
            self.installing_dependencies = False
            if isinstance(self.current_view, SystemView):
                self.current_view.set_installing(False)
                self.current_view.append_log(f"Dependency repair failed: {value}")
            QMessageBox.warning(self, "Dependency repair", str(value))
            return

        # ---------------------------------------------------------
        # FULL DIAGNOSTICS
        # ---------------------------------------------------------

        elif kind == "diagnostics":
            self.dependencies_checking = False
            self.startup_dependencies_done = True
            self.startup_gpu_done = True
            self._apply_diagnostics(value)
            self._finish_startup_overlay()

        elif kind == "diagnostics_error":
            self.dependencies_checking = False
            self.startup_dependencies_done = True
            self.startup_gpu_done = True
            self._set_status_pill(self.header_gpu, "CUDA • UNKNOWN", "checking")
            self._set_status_pill(self.header_model, "Chatterbox • UNKNOWN", "checking")
            if isinstance(self.current_view, SystemView):
                self.current_view.dep_summary.setText("Runtime diagnostic failed")
            self._finish_startup_overlay()
            QMessageBox.warning(
                self,
                "Runtime check",
                f"Could not validate the local runtime.\n\n{value}",
            )

        # ---------------------------------------------------------
        # GPU
        # ---------------------------------------------------------

        elif kind == "gpu":

            ok, short, details = value

            self.gpu_checking = False

            self.gpu_ok = ok

            self.gpu_result = (
                ok,
                short,
                details,
            )

            self.startup_gpu_done = True

            self._set_status_pill(
                self.header_gpu,
                "CUDA • READY"
                if ok
                else "CUDA • OFFLINE",
                "ready"
                if ok
                else "error",
            )

            self._check_model_status()

            if isinstance(
                self.current_view,
                SystemView,
            ):

                self.current_view.update_gpu(
                    ok,
                    short,
                    details,
                )

                if self.model_result is not None:

                    model_ok, model_details = (
                        self.model_result
                    )

                    self.current_view.update_model(
                        model_ok,
                        model_details,
                    )

            self._finish_startup_overlay()

        # ---------------------------------------------------------
        # DEPENDENCIES
        # ---------------------------------------------------------

        elif kind == "deps":

            rows, all_ok = value

            self.dependencies_checking = False

            self.dependencies_result = (
                rows,
                all_ok,
            )

            self.startup_dependencies_done = True

            if isinstance(
                self.current_view,
                SystemView,
            ):

                self.current_view.update_dependencies(
                    rows,
                    all_ok,
                )

            if self.startup_sequence_active:

                if not self.startup_gpu_done:

                    if (
                        hasattr(
                            self,
                            "startup_overlay",
                        )
                        and self.startup_overlay is not None
                    ):

                        self.startup_overlay.set_status(
                            "Dependencies checked. "
                            "Checking CUDA / GPU…"
                        )

                    QTimer.singleShot(
                        100,
                        self.check_gpu,
                    )

                    return

            if self.recheck_after_dependencies:

                self.recheck_after_dependencies = False

                QTimer.singleShot(
                    100,
                    self.check_gpu,
                )

                return

            self._finish_startup_overlay()

        # ---------------------------------------------------------
        # DEPENDENCY ERROR
        # ---------------------------------------------------------

        elif kind == "deps_error":

            self.dependencies_checking = False

            self.startup_dependencies_done = True

            if isinstance(
                self.current_view,
                SystemView,
            ):

                self.current_view.dep_summary.setText(
                    "DEPENDENCY CHECK FAILED"
                )

            if self.startup_sequence_active:

                if not self.startup_gpu_done:

                    QTimer.singleShot(
                        100,
                        self.check_gpu,
                    )

            elif self.recheck_after_dependencies:

                self.recheck_after_dependencies = False

                QTimer.singleShot(
                    100,
                    self.check_gpu,
                )

            QMessageBox.critical(
                self,
                "Dependency check failed",
                value,
            )

        # ---------------------------------------------------------
        # INSTALL COMPLETE
        # ---------------------------------------------------------

        elif kind == "install_done":

            self.installing_dependencies = False

            if isinstance(
                self.current_view,
                SystemView,
            ):

                self.current_view.set_installing(
                    False
                )

            mode = (
                value.get(
                    "mode",
                    "unknown",
                )
                if isinstance(
                    value,
                    dict,
                )
                else "unknown"
            )

            if isinstance(
                self.current_view,
                SystemView,
            ):

                self.current_view.append_log(
                    "Dependency installation finished "
                    f"using {mode} mode."
                )

            self.dependencies_result = None
            self.model_result = None

            self.recheck_after_dependencies = True

            self.refresh_dependencies()

        # ---------------------------------------------------------
        # INSTALL ERROR
        # ---------------------------------------------------------

        elif kind == "install_error":

            self.installing_dependencies = False

            if isinstance(
                self.current_view,
                SystemView,
            ):

                self.current_view.set_installing(
                    False
                )

            QMessageBox.critical(
                self,
                "Dependency installation failed",
                value,
            )

        # ---------------------------------------------------------
        # GENERATION MODEL CHECK
        # ---------------------------------------------------------

        elif kind == "generation_model_check":

            (model_result, config) = value
            model_ok, model_details = model_result

            if not model_ok:
                self.generating = False
                self.generation_overlay.hide()

                if isinstance(self.current_view, GenerateView):
                    self.current_view.set_generating(False)
                    self.current_view.set_status("Ready")

                QMessageBox.critical(
                    self,
                    "LinguaForge runtime",
                    model_details,
                )
                self.show_tab("system")
                return

            self.model_result = (model_ok, model_details)
            self.generation_overlay.set_status(
                "Initializing Chatterbox Turbo…"
            )

            run_background(
                lambda: self.audio_generator.generate(config),
                on_success=lambda output: self.events.put(
                    AppEvent("done", output)
                ),
                on_error=lambda exc: self.events.put(
                    AppEvent("error", str(exc))
                ),
            )

        # ---------------------------------------------------------
        # GENERATION PREPARATION ERROR
        # ---------------------------------------------------------

        elif kind == "generation_prepare_error":

            self.generating = False
            self.generation_overlay.hide()

            if isinstance(self.current_view, GenerateView):
                self.current_view.set_generating(False)
                self.current_view.set_status("Error")

            QMessageBox.critical(
                self,
                "Generation preparation failed",
                value,
            )

        # ---------------------------------------------------------
        # GENERATION COMPLETE
        # ---------------------------------------------------------

        elif kind == "done":

            self.generating = False
            self.generation_overlay.hide()

            if isinstance(
                self.current_view,
                GenerateView,
            ):

                self.current_view.set_generating(
                    False
                )

                self.current_view.set_status(
                    "Complete ✓"
                )

                self.current_view.set_progress(
                    self.current_view.progress.value(),
                    self.current_view.progress.maximum(),
                    "",
                )

            answer = QMessageBox.information(
                self,
                "Complete",
                "Audio generated successfully.\n\n"
                f"{value}",
                QMessageBox.Open
                | QMessageBox.Close,
            )

            if answer == QMessageBox.Open:

                webbrowser.open(
                    os.path.dirname(
                        os.path.abspath(
                            value
                        )
                    )
                )

        # ---------------------------------------------------------
        # ERROR
        # ---------------------------------------------------------

        elif kind == "error":

            self.generating = False
            self.generation_overlay.hide()

            if isinstance(
                self.current_view,
                GenerateView,
            ):

                self.current_view.set_generating(
                    False
                )

                self.current_view.set_status(
                    "Error"
                )

            QMessageBox.critical(
                self,
                "Error",
                value,
            )

    # =============================================================
    # MODEL STATUS
    # =============================================================

    def _check_model_status(self):

        try:

            model_ok, model_details = (
                self.system.model_status()
            )

            self.model_result = (
                model_ok,
                model_details,
            )

            self._set_status_pill(
                self.header_model,
                "Chatterbox • READY"
                if model_ok
                else "Chatterbox • ERROR",
                "ready"
                if model_ok
                else "error",
            )

            if isinstance(
                self.current_view,
                SystemView,
            ):

                self.current_view.update_model(
                    model_ok,
                    model_details,
                )

        except Exception as exc:

            self.model_result = (
                False,
                str(exc),
            )

            self._set_status_pill(
                self.header_model,
                "Chatterbox • ERROR",
                "error",
            )

            if isinstance(
                self.current_view,
                SystemView,
            ):

                self.current_view.update_model(
                    False,
                    str(exc),
                )

    # =============================================================
    # UTILITIES
    # =============================================================

    @staticmethod
    def format_time(seconds):

        seconds = max(
            0,
            int(seconds),
        )

        if seconds < 60:
            return f"{seconds}s"

        return (
            f"{seconds // 60}m "
            f"{seconds % 60:02d}s"
        )