import os
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from qfluentwidgets import FluentIcon as FIF, LineEdit, PrimaryPushButton, PushButton

from app.models.speaker import Speaker
from app.ui.widgets import EmptyState, SectionCard
from app.ui import theme


class SpeakersView(QWidget):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.setObjectName("page")
        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(20, 18, 20, 24)
        self.root_layout.setSpacing(12)
        self.rebuild()

    def rebuild(self):
        while self.root_layout.count():
            item = self.root_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Voice Library")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Manage reference recordings used for each speaker.")
        subtitle.setObjectName("pageSubtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch()

        add = PrimaryPushButton(FIF.ADD, "Add Speaker")
        add.clicked.connect(self.controller.add_speaker)
        header.addWidget(add)
        self.root_layout.addLayout(header)

        self.container = QWidget()
        self.list_layout = QVBoxLayout(self.container)
        self.list_layout.setContentsMargins(0, 6, 0, 0)
        self.list_layout.setSpacing(10)
        self.root_layout.addWidget(self.container, 1)
        self.render()

    def render(self):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.controller.speakers:
            self.list_layout.addWidget(
                EmptyState(
                    "No speakers yet",
                    "Add a speaker and attach a reference WAV/MP3 recording.",
                    FIF.PEOPLE.icon()
                )
            )
            self.list_layout.addStretch()
            return

        for speaker in self.controller.speakers:
            self._render_speaker(speaker)

        self.list_layout.addStretch()

    def _render_speaker(self, speaker: Speaker):
        card = SectionCard()
        body = card.body_layout()

        row = QHBoxLayout()
        badge = QLabel(speaker.name.replace("speaker", "S"))
        badge.setObjectName("speakerBadge")
        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedSize(54, 54)
        row.addWidget(badge)

        center = QVBoxLayout()
        name = QLabel(f"[{speaker.name}]")
        name.setObjectName("speakerName")
        center.addWidget(name)

        edit = LineEdit()
        edit.setText(speaker.path)
        edit.setPlaceholderText("Reference audio file")
        edit.textChanged.connect(
            lambda path, s=speaker: self._save_path(s, path)
        )
        center.addWidget(edit)
        row.addLayout(center, 1)

        browse = PushButton(FIF.FOLDER, "Browse")
        browse.clicked.connect(lambda _, s=speaker, e=edit: self._choose(s, e))
        row.addWidget(browse)

        remove = PushButton(FIF.DELETE, "Remove")
        remove.setObjectName("dangerButton")
        remove.clicked.connect(lambda _, s=speaker: self.controller.remove_speaker(s))
        row.addWidget(remove)

        body.addLayout(row)
        self.list_layout.addWidget(card)

    def _save_path(self, speaker, path):
        speaker.path = path.strip()
        self.controller.save_speakers()

    def _choose(self, speaker, edit):
        path, _ = QFileDialog.getOpenFileName(
            self, f"Reference audio — {speaker.name}", "",
            "Audio (*.wav *.mp3 *.m4a *.flac *.ogg);;All files (*.*)"
        )
        if path:
            edit.setText(path)
