from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QProgressBar,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QMessageBox,
)

from qfluentwidgets import (
    FluentIcon as FIF,
    LineEdit,
    PrimaryPushButton,
    PushButton,
    ComboBox,
    Slider,
    SwitchButton,
)

from app.ui.widgets import SectionCard


class GenerateView(QWidget):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller
        self.setObjectName("page")

        # ---------------------------------------------------------
        # SCROLL AREA
        # ---------------------------------------------------------

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )
        scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

        content = QWidget()
        content.setObjectName("pageContent")

        scroll.setWidget(content)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(scroll)

        # ---------------------------------------------------------
        # PAGE LAYOUT
        # ---------------------------------------------------------

        layout = QVBoxLayout(content)
        layout.setContentsMargins(
            20,
            18,
            20,
            24,
        )
        layout.setSpacing(12)

        # ---------------------------------------------------------
        # PAGE HEADER
        # ---------------------------------------------------------

        header = QFrame()
        header.setObjectName("pageHeader")
        header.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Maximum,
        )

        header_layout = QVBoxLayout(header)

        header_layout.setContentsMargins(
            16,
            10,
            16,
            10,
        )

        header_layout.setSpacing(1)

        title = QLabel(
            "Generate Audio"
        )

        title.setObjectName(
            "pageTitle"
        )

        subtitle = QLabel(
            "Create natural speech from text, scripts or dialogues."
        )

        subtitle.setObjectName(
            "pageSubtitle"
        )

        header_layout.addWidget(
            title
        )

        header_layout.addWidget(
            subtitle
        )

        layout.addWidget(
            header
        )

        # ---------------------------------------------------------
        # TWO COLUMNS
        # ---------------------------------------------------------

        columns = QHBoxLayout()
        columns.setSpacing(12)

        left = QVBoxLayout()
        left.setSpacing(12)

        right = QVBoxLayout()
        right.setSpacing(12)

        columns.addLayout(
            left,
            7,
        )

        columns.addLayout(
            right,
            4,
        )

        layout.addLayout(
            columns,
            1,
        )

        # ---------------------------------------------------------
        # BUILD LEFT COLUMN
        # ---------------------------------------------------------

        self._build_project(
            left
        )

        self._build_preview(
            left
        )

        self._build_generation(
            left
        )

        # ---------------------------------------------------------
        # BUILD RIGHT COLUMN
        # ---------------------------------------------------------

        self._build_options(
            right
        )

        self._build_engine(
            right
        )

        # IMPORTANT:
        # Keep empty space ONLY below Engine.
        right.addStretch(1)

        # ---------------------------------------------------------
        # PREVIEW SYNC
        # ---------------------------------------------------------

        self.input_edit.textChanged.connect(
            self._update_preview
        )

        self._update_preview(
            self.input_edit.text().strip()
        )

    # =========================================================
    # PROJECT
    # =========================================================

    def _build_project(
        self,
        parent,
    ):
        card = SectionCard(
            "Project",
            "INPUT → AUDIO",
        )

        parent.addWidget(
            card
        )

        body = card.body_layout()

        # -----------------------------------------------------
        # INPUT
        # -----------------------------------------------------

        self.input_edit = LineEdit()

        self.input_edit.setText(
            self.controller.input_path
        )

        self.input_edit.setPlaceholderText(
            "Path to .txt dialogue/script"
        )

        # -----------------------------------------------------
        # OUTPUT
        # -----------------------------------------------------

        self.output_edit = LineEdit()

        self.output_edit.setText(
            self.controller.output_path
        )

        self.output_edit.setPlaceholderText(
            "Output MP3 path"
        )

        self.controller.input_widget = (
            self.input_edit
        )

        self.controller.output_widget = (
            self.output_edit
        )

        # -----------------------------------------------------
        # FILE ROWS
        # -----------------------------------------------------

        body.addLayout(
            self._file_row(
                "Input File",
                self.input_edit,
                self.controller.choose_input,
            )
        )

        body.addLayout(
            self._file_row(
                "Output File",
                self.output_edit,
                self.controller.choose_output,
            )
        )

        # -----------------------------------------------------
        # AUTO PAUSES
        # -----------------------------------------------------

        row = QHBoxLayout()

        auto = PushButton(
            FIF.SPEED_OFF,
            "Auto-generate pauses",
        )

        auto.clicked.connect(
            self.controller.auto_generate_pauses
        )

        row.addWidget(
            auto
        )

        hint = QLabel(
            "Adds pauses only to lines that do not already have one"
        )

        hint.setObjectName(
            "muted"
        )

        row.addWidget(
            hint
        )

        row.addStretch()

        body.addLayout(
            row
        )

    # =========================================================
    # PREVIEW / EDITOR
    # =========================================================

    def _build_preview(
        self,
        parent,
    ):
        card = SectionCard(
            "Dialogue Preview",
            "EDITOR",
        )

        parent.addWidget(
            card
        )

        body = card.body_layout()

        body.setSpacing(
            8
        )

        # -----------------------------------------------------
        # TEXT EDITOR
        # -----------------------------------------------------

        self.preview = QPlainTextPreview()

        body.addWidget(
            self.preview
        )

        # -----------------------------------------------------
        # EDITOR TOOLBAR
        # -----------------------------------------------------

        toolbar = QHBoxLayout()

        toolbar.setSpacing(
            6
        )

        self.preview_status = QLabel(
            "Ready"
        )

        self.preview_status.setObjectName(
            "muted"
        )

        toolbar.addWidget(
            self.preview_status
        )

        toolbar.addStretch()

        # -----------------------------------------------------
        # SAVE
        # -----------------------------------------------------

        save_button = PushButton(
            FIF.SAVE,
            "Save",
        )

        save_button.setToolTip(
            "Save changes to the current input file"
        )

        save_button.clicked.connect(
            self._save_preview
        )

        toolbar.addWidget(
            save_button
        )

        # -----------------------------------------------------
        # SAVE AS
        # -----------------------------------------------------

        save_as_button = PushButton(
            FIF.SAVE_AS,
            "Save As",
        )

        save_as_button.setToolTip(
            "Save the dialogue as a new file"
        )

        save_as_button.clicked.connect(
            self._save_preview_as
        )

        toolbar.addWidget(
            save_as_button
        )

        body.addLayout(
            toolbar
        )

        # -----------------------------------------------------
        # MODIFICATION TRACKING
        # -----------------------------------------------------

        self.preview.text.document().modificationChanged.connect(
            self._preview_modified
        )

    # =========================================================
    # LOAD FILE INTO EDITOR
    # =========================================================

    def _update_preview(
        self,
        path,
    ):
        path = (
            path or ""
        ).strip()

        if not path:
            self.preview.setPlainText(
                "No input file selected."
            )

            self.preview.text.document().setModified(
                False
            )

            self._update_preview_status()

            return

        file_path = Path(
            path
        )

        if not file_path.exists():
            self.preview.setPlainText(
                f"File not found:\n{path}"
            )

            self.preview.text.document().setModified(
                False
            )

            self.preview_status.setText(
                "File not found"
            )

            return

        if not file_path.is_file():
            self.preview.setPlainText(
                f"Not a file:\n{path}"
            )

            self.preview.text.document().setModified(
                False
            )

            self.preview_status.setText(
                "Not a file"
            )

            return

        try:
            text = file_path.read_text(
                encoding="utf-8",
                errors="replace",
            )

            text = text.replace(
                "\r\n",
                "\n",
            ).replace(
                "\r",
                "\n",
            )

            self.preview.setPlainText(
                text
            )

            # Loading a file is not a user modification.
            self.preview.text.document().setModified(
                False
            )

            self._update_preview_status()

        except Exception as e:
            self.preview.setPlainText(
                f"Could not read input file:\n{e}"
            )

            self.preview.text.document().setModified(
                False
            )

            self.preview_status.setText(
                "Read error"
            )

    # =========================================================
    # EDITOR STATUS
    # =========================================================

    def _preview_modified(
        self,
        modified,
    ):
        self._update_preview_status()

    def _update_preview_status(
        self,
    ):
        if not hasattr(
            self,
            "preview_status",
        ):
            return

        document = (
            self.preview.text.document()
        )

        if document.isModified():
            self.preview_status.setText(
                "Unsaved changes"
            )

            return

        text = (
            self.preview.text.toPlainText()
        )

        if not text:
            self.preview_status.setText(
                "0 lines  •  0 characters"
            )

            return

        lines = len(
            text.splitlines()
        )

        chars = len(
            text
        )

        self.preview_status.setText(
            f"{lines:,} lines  •  {chars:,} characters"
        )

    # =========================================================
    # SAVE
    # =========================================================

    def _save_preview(
        self,
    ):
        path = self.input_edit.text().strip()

        if not path:
            self._save_preview_as()
            return

        file_path = Path(
            path
        )

        try:
            file_path.write_text(
                self.preview.text.toPlainText(),
                encoding="utf-8",
                newline="\n",
            )

            # Keep controller synchronized.
            self.controller.input_path = str(
                file_path
            )

            if hasattr(
                self.controller,
                "input_widget",
            ):
                self.controller.input_widget.setText(
                    str(file_path)
                )

            self.preview.text.document().setModified(
                False
            )

            self._update_preview_status()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Save Error",
                f"Could not save the file:\n\n{e}",
            )

    # =========================================================
    # SAVE AS
    # =========================================================

    def _save_preview_as(
        self,
    ):
        current_path = (
            self.input_edit.text().strip()
        )

        if current_path:
            default_path = current_path
        else:
            default_path = "dialogue.txt"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Dialogue As",
            default_path,
            "Text Files (*.txt);;All Files (*)",
        )

        if not file_path:
            return

        try:
            target = Path(
                file_path
            )

            target.write_text(
                self.preview.text.toPlainText(),
                encoding="utf-8",
                newline="\n",
            )

            # Update Input File field.
            self.input_edit.setText(
                str(target)
            )

            self.controller.input_path = str(
                target
            )

            if hasattr(
                self.controller,
                "input_widget",
            ):
                self.controller.input_widget.setText(
                    str(target)
                )

            self.preview.text.document().setModified(
                False
            )

            self._update_preview_status()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Save Error",
                f"Could not save the file:\n\n{e}",
            )

    # =========================================================
    # GENERATION
    # =========================================================

    def _build_generation(
        self,
        parent,
    ):
        card = SectionCard(
            "Generation",
            "LIVE",
        )

        parent.addWidget(
            card
        )

        body = card.body_layout()

        top = QHBoxLayout()

        self.generate_btn = PrimaryPushButton(
            FIF.PLAY,
            "Generate",
        )

        self.generate_btn.setObjectName(
            "generateButton"
        )

        self.generate_btn.setMinimumHeight(
            52
        )

        self.generate_btn.clicked.connect(
            self.controller.start_generation
        )

        top.addWidget(
            self.generate_btn
        )

        top.addStretch()

        status = QLabel(
            "Ready"
        )

        status.setObjectName(
            "statusLabel"
        )

        self.status_label = status

        top.addWidget(
            status
        )

        body.addLayout(
            top
        )

        # -----------------------------------------------------
        # PROGRESS
        # -----------------------------------------------------

        self.progress = QProgressBar()

        self.progress.setRange(
            0,
            1,
        )

        self.progress.setValue(
            0
        )

        body.addWidget(
            self.progress
        )

        # -----------------------------------------------------
        # PROGRESS INFO
        # -----------------------------------------------------

        bottom = QHBoxLayout()

        self.progress_label = QLabel(
            "0 / 0"
        )

        self.progress_label.setObjectName(
            "muted"
        )

        self.eta_label = QLabel(
            ""
        )

        self.eta_label.setObjectName(
            "muted"
        )

        bottom.addWidget(
            self.progress_label
        )

        bottom.addStretch()

        bottom.addWidget(
            self.eta_label
        )

        body.addLayout(
            bottom
        )

    # =========================================================
    # OPTIONS
    # =========================================================

    def _build_options(
        self,
        parent,
    ):
        card = SectionCard(
            "Options"
        )

        card.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Maximum,
        )

        card.setMaximumHeight(
            250
        )

        parent.addWidget(
            card
        )

        body = card.body_layout()

        body.setSpacing(
            5
        )

        # -----------------------------------------------------
        # SPEED
        # -----------------------------------------------------

        self.speed_slider, self.speed_value = (
            self._slider_row_compact(
                body,
                "Speed",
                70,
                120,
                int(
                    self.controller.speed * 100
                ),
                "x",
            )
        )

        # -----------------------------------------------------
        # VOLUME
        # -----------------------------------------------------

        self.volume_slider, self.volume_value = (
            self._slider_row_compact(
                body,
                "Volume",
                50,
                200,
                int(
                    self.controller.volume * 100
                ),
                "%",
            )
        )

        # -----------------------------------------------------
        # BITRATE
        # -----------------------------------------------------

        bitrate_row = QHBoxLayout()

        bitrate_row.setSpacing(
            6
        )

        label = QLabel(
            "MP3 Bitrate"
        )

        label.setObjectName(
            "fieldLabel"
        )

        label.setFixedWidth(
            78
        )

        bitrate_row.addWidget(
            label
        )

        self.bitrate_combo = ComboBox()

        self.bitrate_combo.addItems(
            [
                "128k",
                "160k",
                "192k",
                "256k",
                "320k",
            ]
        )

        self.bitrate_combo.setCurrentText(
            self.controller.bitrate
        )

        self.bitrate_combo.setMinimumWidth(
            110
        )

        bitrate_row.addWidget(
            self.bitrate_combo
        )

        bitrate_row.addStretch()

        body.addLayout(
            bitrate_row
        )

        # -----------------------------------------------------
        # KEEP TEMP FILES
        # -----------------------------------------------------

        self.temp_switch = SwitchButton()

        self.temp_switch.setChecked(
            False
        )

        body.addLayout(
            self._switch_row_compact(
                "Keep temp files",
                self.temp_switch,
            )
        )

        # -----------------------------------------------------
        # USE GPU
        # -----------------------------------------------------

        self.gpu_switch = SwitchButton()

        self.gpu_switch.setChecked(
            True
        )

        body.addLayout(
            self._switch_row_compact(
                "Use GPU (CUDA)",
                self.gpu_switch,
            )
        )

        # -----------------------------------------------------
        # LIVE VALUES
        # -----------------------------------------------------

        self.speed_slider.valueChanged.connect(
            self._on_engine_setting_changed
        )

        self.volume_slider.valueChanged.connect(
            self._on_engine_setting_changed
        )

        self.bitrate_combo.currentTextChanged.connect(
            self._on_engine_setting_changed
        )

    # =========================================================
    # ENGINE
    # =========================================================

    def _build_engine(
        self,
        parent,
    ):
        card = SectionCard(
            "Engine",
            "LOCAL",
        )

        card.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Maximum,
        )

        parent.addWidget(
            card
        )

        body = card.body_layout()

        body.setSpacing(
            6
        )

        # -----------------------------------------------------
        # ENGINE
        # -----------------------------------------------------

        engine_label = QLabel(
            "Chatterbox Turbo"
        )

        engine_label.setObjectName(
            "engineValue"
        )

        body.addLayout(
            self._value_row(
                FIF.ROBOT,
                "Engine",
                engine_label,
            )
        )

        # -----------------------------------------------------
        # DEVICE
        # -----------------------------------------------------

        device_label = QLabel(
            "CUDA"
        )

        device_label.setObjectName(
            "engineValue"
        )

        self.device_label = (
            device_label
        )

        body.addLayout(
            self._value_row(
                FIF.CONNECT,
                "Device",
                device_label,
            )
        )

        # -----------------------------------------------------
        # MODEL
        # -----------------------------------------------------

        model_label = QLabel(
            "Ready"
        )

        model_label.setObjectName(
            "engineValue"
        )

        self.model_label = (
            model_label
        )

        body.addLayout(
            self._value_row(
                FIF.ROBOT,
                "Model",
                model_label,
            )
        )

        # -----------------------------------------------------
        # INFERENCE
        # -----------------------------------------------------

        inference_label = QLabel(
            "Local"
        )

        inference_label.setObjectName(
            "engineValue"
        )

        body.addLayout(
            self._value_row(
                FIF.COMMAND_PROMPT,
                "Inference",
                inference_label,
            )
        )

        # -----------------------------------------------------
        # OUTPUT
        # -----------------------------------------------------

        output_label = QLabel(
            "MP3"
        )

        output_label.setObjectName(
            "engineValue"
        )

        body.addLayout(
            self._value_row(
                FIF.SAVE,
                "Output",
                output_label,
            )
        )

        # -----------------------------------------------------
        # VOICE
        # -----------------------------------------------------

        voice_label = QLabel(
            "Reference audio"
        )

        voice_label.setObjectName(
            "engineValue"
        )

        body.addLayout(
            self._value_row(
                FIF.MICROPHONE,
                "Voice",
                voice_label,
            )
        )

        # -----------------------------------------------------
        # SETTINGS SUMMARY
        # -----------------------------------------------------

        settings = QLabel()

        settings.setObjectName(
            "muted"
        )

        settings.setWordWrap(
            True
        )

        self.engine_settings_label = (
            settings
        )

        body.addWidget(
            settings
        )

        self._update_engine_info()

    def _update_engine_info(
        self,
    ):
        if not hasattr(
            self,
            "engine_settings_label",
        ):
            return

        # Read directly from the live controls so Engine always mirrors
        # the values currently selected by the user.
        speed = self.speed_slider.value() / 100
        volume = self.volume_slider.value() / 100
        bitrate = self.bitrate_combo.currentText()

        self.engine_settings_label.setText(
            f"Speed {speed:.2f}x  •  Volume {volume:.0%}  •  {bitrate} bitrate"
        )

    def _on_engine_setting_changed(self, value=None):
        # Update the small value badges next to the sliders immediately.
        # These labels are separate from the Engine summary, so they must
        # be updated explicitly whenever the slider emits valueChanged.
        if hasattr(self, "speed_value"):
            speed = self.speed_slider.value() / 100.0
            self.speed_value.setText(f"{speed:.2f}x")

        if hasattr(self, "volume_value"):
            volume = self.volume_slider.value()
            self.volume_value.setText(f"{volume}%")

        # Keep the Engine summary in sync with the controls as well.
        self._update_engine_info()

    # =========================================================
    # HELPERS
    # =========================================================

    def _file_row(
        self,
        label_text,
        edit,
        callback,
    ):
        row = QHBoxLayout()

        label = QLabel(
            label_text
        )

        label.setObjectName(
            "fieldLabel"
        )

        label.setFixedWidth(
            78
        )

        row.addWidget(
            label
        )

        row.addWidget(
            edit,
            1,
        )

        button = PushButton(
            FIF.FOLDER,
            "Browse",
        )

        button.clicked.connect(
            callback
        )

        row.addWidget(
            button
        )

        return row

    def _slider_row_compact(
        self,
        parent,
        label_text,
        low,
        high,
        value,
        suffix,
    ):
        row = QHBoxLayout()

        row.setSpacing(
            6
        )

        label = QLabel(
            label_text
        )

        label.setObjectName(
            "fieldLabel"
        )

        label.setFixedWidth(
            78
        )

        row.addWidget(
            label
        )

        slider = Slider(
            Qt.Horizontal
        )

        slider.setRange(
            low,
            high,
        )

        slider.setValue(
            value
        )

        slider.setFixedHeight(
            22
        )

        row.addWidget(
            slider,
            1,
        )

        value_label = QLabel(
            f"{value / 100:.2f}x"
            if suffix == "x"
            else f"{value}%"
        )

        value_label.setObjectName(
            "valueBadge"
        )

        value_label.setAlignment(
            Qt.AlignCenter
        )

        value_label.setFixedWidth(
            58
        )

        value_label.setFixedHeight(
            26
        )

        row.addWidget(
            value_label
        )

        parent.addLayout(
            row
        )

        return (
            slider,
            value_label,
        )

    def _switch_row_compact(
        self,
        text,
        switch,
    ):
        row = QHBoxLayout()

        row.setSpacing(
            6
        )

        label = QLabel(
            text
        )

        label.setObjectName(
            "fieldLabel"
        )

        row.addWidget(
            label
        )

        row.addStretch()

        row.addWidget(
            switch
        )

        return row

    def _value_row(
        self,
        icon,
        title,
        value,
    ):
        row = QHBoxLayout()

        row.setSpacing(
            7
        )

        icon_label = QLabel()

        icon_label.setPixmap(
            icon.icon().pixmap(
                17,
                17,
            )
        )

        icon_label.setFixedWidth(
            22
        )

        row.addWidget(
            icon_label
        )

        title_label = QLabel(
            title
        )

        title_label.setObjectName(
            "muted"
        )

        row.addWidget(
            title_label
        )

        row.addStretch()

        row.addWidget(
            value
        )

        return row

    # =========================================================
    # PUBLIC API
    # =========================================================

    def values(
        self,
    ):
        return {
            "input_file": (
                self.input_edit.text().strip()
            ),
            "output_file": (
                self.output_edit.text().strip()
            ),
            "speed": (
                self.speed_slider.value()
                / 100
            ),
            "volume": (
                self.volume_slider.value()
                / 100
            ),
            "bitrate": (
                self.bitrate_combo.currentText()
            ),
        }

    def set_status(
        self,
        text,
    ):
        self.status_label.setText(
            text
        )

    def set_progress(
        self,
        current,
        total,
        eta="",
    ):
        self.progress.setRange(
            0,
            max(
                total,
                1,
            ),
        )

        self.progress.setValue(
            current
        )

        self.progress_label.setText(
            f"{current} / {total}"
        )

        self.eta_label.setText(
            eta
        )

    def set_generating(
        self,
        generating,
    ):
        self.generate_btn.setEnabled(
            not generating
        )

        self.generate_btn.setText(
            "Generating…"
            if generating
            else "Generate"
        )


# =============================================================
# DIALOGUE EDITOR
# =============================================================

class QPlainTextPreview(QFrame):
    def __init__(
        self,
        parent=None,
    ):
        super().__init__(
            parent
        )

        self.setObjectName(
            "dialoguePreview"
        )

        self.setMinimumHeight(
            180
        )

        self.setMaximumHeight(
            320
        )

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            10,
            10,
            10,
            10,
        )

        layout.setSpacing(
            0
        )

        # -----------------------------------------------------
        # REAL TEXT EDITOR
        # -----------------------------------------------------

        self.text = QPlainTextEdit()

        self.text.setObjectName(
            "dialogueEditor"
        )

        self.text.setLineWrapMode(
            QPlainTextEdit.WidgetWidth
        )

        self.text.setUndoRedoEnabled(
            True
        )

        self.text.setTabChangesFocus(
            False
        )

        layout.addWidget(
            self.text
        )

    def setPlainText(
        self,
        text,
    ):
        self.text.setPlainText(
            text
        )

    def toPlainText(
        self,
    ):
        return self.text.toPlainText()