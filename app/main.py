import sys
import ctypes
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app.ui.main_window import MainWindow
from app.ui import theme


def _configure_windows_identity():
    """Give Windows a stable AppUserModelID so the taskbar uses LinguaForge.

    This must run before QApplication creates any top-level window.
    """
    if sys.platform != "win32":
        return

    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "LinguaForge.Desktop.1"
        )
    except (AttributeError, OSError):
        pass


def main():
    _configure_windows_identity()

    app = QApplication(sys.argv)
    QApplication.setStyle("Fusion")
    app.setApplicationName("LinguaForge")
    app.setApplicationDisplayName("LinguaForge")

    icon_path = Path(__file__).resolve().parents[1] / "assets" / "linguaforge_logo.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    app.setStyleSheet(theme.APP_QSS)

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
