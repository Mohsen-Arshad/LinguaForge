from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from qfluentwidgets import CardWidget


class SectionCard(CardWidget):
    """Product-styled card built on QFluentWidgets' real CardWidget."""

    def __init__(self, title="", subtitle="", parent=None):
        super().__init__(parent)
        self.setObjectName("sectionCard")
        self.setMinimumWidth(0)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 15, 18, 18)
        layout.setSpacing(10)

        if title:
            head = QHBoxLayout()
            head.setSpacing(8)
            title_label = QLabel(title)
            title_label.setObjectName("cardTitle")
            head.addWidget(title_label)
            head.addStretch()
            if subtitle:
                sub = QLabel(subtitle.upper())
                sub.setObjectName("cardSubtitle")
                head.addWidget(sub)
            layout.addLayout(head)

        self.body = QWidget(self)
        body_layout = QVBoxLayout(self.body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(10)
        layout.addWidget(self.body)

    def body_layout(self):
        return self.body.layout()


class EmptyState(QFrame):
    def __init__(self, title, description, icon=None, parent=None):
        super().__init__(parent)
        self.setObjectName("emptyState")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 36, 24, 36)
        layout.setSpacing(7)
        if icon is not None:
            icon_label = QLabel()
            icon_label.setPixmap(icon.pixmap(32, 32))
            icon_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(icon_label)
        title_label = QLabel(title)
        title_label.setObjectName("emptyTitle")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        desc = QLabel(description)
        desc.setObjectName("muted")
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)


class NavButton(QFrame):
    """Dedicated sidebar navigation control with stable icon/text spacing."""

    def __init__(self, icon, text, callback, parent=None):
        super().__init__(parent)
        self.setObjectName("navItem")
        self.setCursor(Qt.PointingHandCursor)
        self.setProperty("active", "false")
        self.callback = callback

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(12)

        self.icon_label = QLabel(self)
        self.icon_label.setFixedSize(20, 20)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setPixmap(icon.icon().pixmap(18, 18))
        self.icon_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        layout.addWidget(self.icon_label, 0, Qt.AlignVCenter)

        self.label = QLabel(text, self)
        self.label.setObjectName("navText")
        self.label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        layout.addWidget(self.label, 1, Qt.AlignVCenter)

    def set_active(self, active):
        self.setProperty("active", "true" if active else "false")

        font = self.label.font()
        font.setBold(active)
        self.label.setFont(font)

        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.callback()
            event.accept()
            return
        super().mousePressEvent(event)
