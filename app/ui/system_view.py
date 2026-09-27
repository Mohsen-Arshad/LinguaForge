import sys
from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from qfluentwidgets import (
    FluentIcon as FIF,
    PrimaryPushButton,
    PushButton,
)

from app.ui.widgets import SectionCard
from app.ui import theme


class SystemView(QWidget):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller
        self.setObjectName("page")

        # =====================================================
        # OUTER VIEW
        # =====================================================

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # =====================================================
        # SCROLL AREA
        # =====================================================

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        outer.addWidget(scroll)

        # =====================================================
        # SCROLL CONTENT
        # =====================================================

        content = QWidget()
        content.setObjectName("pageContent")

        scroll.setWidget(content)

        layout = QVBoxLayout(content)

        layout.setContentsMargins(
            20,
            18,
            20,
            24,
        )

        layout.setSpacing(12)

        # =====================================================
        # PAGE HEADER
        # =====================================================

        title = QLabel("System")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "Check CUDA, Chatterbox, FFmpeg and installed dependencies."
        )
        subtitle.setObjectName("pageSubtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        # =====================================================
        # GPU CARD
        # =====================================================

        gpu_card = SectionCard(
            "GPU",
            "CUDA",
        )

        gpu_card.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Fixed,
        )

        layout.addWidget(gpu_card)

        body = gpu_card.body_layout()
        body.setSpacing(7)

        self.gpu_label = QLabel(
            "Checking CUDA…"
        )

        self.gpu_label.setObjectName(
            "systemValue"
        )

        body.addWidget(
            self.gpu_label
        )

        self.gpu_details = QLabel(
            ""
        )

        self.gpu_details.setObjectName(
            "mono"
        )

        self.gpu_details.setWordWrap(
            True
        )

        body.addWidget(
            self.gpu_details
        )

        actions = QHBoxLayout()
        actions.setSpacing(8)

        check = PrimaryPushButton(
            FIF.CONNECT,
            "Check GPU",
        )

        check.clicked.connect(
            self.controller.check_gpu
        )

        actions.addWidget(
            check
        )

        repair = PushButton(
            FIF.SETTING,
            "Install / Repair All",
        )

        repair.clicked.connect(
            self.controller.fix_gpu
        )

        self.fix_gpu_btn = repair

        actions.addWidget(
            repair
        )

        actions.addStretch()

        body.addLayout(
            actions
        )

        # =====================================================
        # RUNTIME CARD
        # =====================================================

        runtime_card = SectionCard(
            "Runtime",
            "LOCAL",
        )

        runtime_card.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Fixed,
        )

        layout.addWidget(
            runtime_card
        )

        rbody = runtime_card.body_layout()
        rbody.setSpacing(7)

        self.model_label = QLabel(
            "Chatterbox: checking…"
        )

        self.model_label.setObjectName(
            "systemValue"
        )

        rbody.addWidget(
            self.model_label
        )

        self.runtime_label = QLabel(
            ""
        )

        self.runtime_label.setObjectName(
            "mono"
        )

        self.runtime_label.setWordWrap(
            True
        )

        rbody.addWidget(
            self.runtime_label
        )

        # =====================================================
        # DEPENDENCIES CARD
        # =====================================================

        dep_card = SectionCard(
            "Dependencies",
            "ENVIRONMENT",
        )

        dep_card.setMinimumHeight(
            250
        )

        dep_card.setMaximumHeight(
            270
        )

        dep_card.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Fixed,
        )

        layout.addWidget(
            dep_card
        )

        dbody = dep_card.body_layout()
        dbody.setSpacing(7)

        # -----------------------------------------------------
        # DEPENDENCY HEADER
        # -----------------------------------------------------

        top = QHBoxLayout()
        top.setSpacing(8)

        self.dep_summary = QLabel(
            "Checking dependencies…"
        )

        self.dep_summary.setObjectName(
            "systemValue"
        )

        top.addWidget(
            self.dep_summary
        )

        top.addStretch()

        refresh = PushButton(
            FIF.ROTATE,
            "Refresh",
        )

        refresh.clicked.connect(
            self.controller.refresh_dependencies
        )

        self.refresh_btn = refresh

        top.addWidget(
            refresh
        )

        install = PrimaryPushButton(
            FIF.DOWNLOAD,
            "Install / Repair",
        )

        install.clicked.connect(
            self.controller.install_missing
        )

        self.install_btn = install

        top.addWidget(
            install
        )

        dbody.addLayout(
            top
        )

        # -----------------------------------------------------
        # DEPENDENCY TABLE
        # -----------------------------------------------------

        self.dep_text = QPlainTextEdit()

        self.dep_text.setReadOnly(
            True
        )

        self.dep_text.setMinimumHeight(
            165
        )

        self.dep_text.setMaximumHeight(
            185
        )

        self.dep_text.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed,
        )

        dbody.addWidget(
            self.dep_text
        )

        # =====================================================
        # ACTIVITY LOG CARD
        # =====================================================

        log_card = SectionCard(
            "Activity Log",
            "LATEST",
        )

        log_card.setMinimumHeight(
            145
        )

        log_card.setMaximumHeight(
            165
        )

        log_card.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Fixed,
        )

        layout.addWidget(
            log_card
        )

        lbody = log_card.body_layout()
        lbody.setSpacing(7)

        self.log_text = QPlainTextEdit()

        self.log_text.setReadOnly(
            True
        )

        self.log_text.setMinimumHeight(
            95
        )

        self.log_text.setMaximumHeight(
            110
        )

        self.log_text.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed,
        )

        lbody.addWidget(
            self.log_text
        )

        # =====================================================
        # BOTTOM SPACE
        # =====================================================

        layout.addStretch(1)

    # =========================================================
    # INSTALL STATE
    # =========================================================

    def set_installing(
        self,
        installing,
    ):
        buttons = (
            self.fix_gpu_btn,
            self.install_btn,
            self.refresh_btn,
        )

        for btn in buttons:
            btn.setEnabled(
                not installing
            )

        self.install_btn.setText(
            "Installing…"
            if installing
            else "Install / Repair"
        )

        self.fix_gpu_btn.setText(
            "Repairing…"
            if installing
            else "Install / Repair All"
        )

    # =========================================================
    # GPU
    # =========================================================

    def update_gpu(
        self,
        ok,
        short,
        details,
    ):
        self.gpu_label.setText(
            short
        )

        self.gpu_label.setStyleSheet(
            f"color: "
            f"{theme.SUCCESS if ok else theme.DANGER}; "
            f"font-weight: 700;"
        )

        self.gpu_details.setText(
            details
        )

    # =========================================================
    # MODEL / RUNTIME
    # =========================================================

    def update_model(
        self,
        ok,
        details,
    ):
        self.model_label.setText(
            ("✓ " if ok else "✕ ") + details
        )

        self.model_label.setStyleSheet(
            f"color: "
            f"{theme.SUCCESS if ok else theme.DANGER}; "
            f"font-weight: 700;"
        )

        try:
            ffmpeg = (
                self.controller.system.ffmpeg_path()
                or "NOT FOUND"
            )

            wheels = (
                "available"
                if self.controller.system.local_wheels_available
                else "not found"
            )

            self.runtime_label.setText(
                f"Python: {sys.version.split()[0]}\n"
                f"Executable: {sys.executable}\n"
                f"Local wheels: {wheels}\n"
                f"FFmpeg: {ffmpeg}"
            )

        except Exception:
            pass

    # =========================================================
    # DEPENDENCIES
    # =========================================================

    def update_dependencies(
        self,
        rows,
        all_ok,
    ):
        lines = [
            f"{'PACKAGE':24} {'VERSION':18} STATUS",
            "-" * 78,
        ]

        for (
            dist,
            installed,
            status,
            ok,
        ) in rows:
            lines.append(
                f"{dist:24} {installed:18} {status}"
            )

        self.dep_text.setPlainText(
            "\n".join(lines)
        )

        self.dep_summary.setText(
            "✓ ALL DEPENDENCIES READY"
            if all_ok
            else "CHECK REQUIRED — press INSTALL / REPAIR"
        )

        self.dep_summary.setStyleSheet(
            f"color: "
            f"{theme.SUCCESS if all_ok else theme.WARNING}; "
            f"font-weight: 700;"
        )

    # =========================================================
    # LOG
    # =========================================================

    def append_log(
        self,
        text,
    ):
        self.log_text.appendPlainText(
            text
        )
