"""Bootstrap de la aplicación PySide6.

Se mantiene mínimo: crea la QApplication y la ventana principal.
La lógica de negocio vive en ``core`` y la presentación en ``ui``.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from hand_motion.ui.main_window import MainWindow


def main() -> int:
    """Inicializa y ejecuta la aplicación. Devuelve el código de salida."""
    app = QApplication(sys.argv)
    app.setApplicationName("Hand Motion")
    app.setOrganizationName("ED2 - Hand Motion")

    logo_path = Path(__file__).resolve().parent.parent / "resources" / "hand_motion_logo.png"
    if logo_path.is_file():
        app.setWindowIcon(QIcon(str(logo_path)))

    window = MainWindow()
    window.showFullScreen()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
