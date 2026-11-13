"""Barra lateral compacta de navegación."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolButton

from hand_motion.ui.styles.palette import ACCENT_CYAN, TEXT_SECONDARY


_SECTIONS = [
    ("Dashboard", """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none"
     stroke="{{color}}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <rect x="3" y="3" width="7" height="7" rx="1"/>
  <rect x="14" y="3" width="7" height="7" rx="1"/>
  <rect x="3" y="14" width="7" height="7" rx="1"/>
  <rect x="14" y="14" width="7" height="7" rx="1"/>
</svg>"""),
    ("Adquisición", """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none"
     stroke="{{color}}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M12 3v12m0 0l-4-4m4 4l4-4M5 21h14"/>
</svg>"""),
    ("Reconocimiento", """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none"
     stroke="{{color}}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M8 12V7a2 2 0 1 1 4 0v5m0-3V6a2 2 0 1 1 4 0v6m0-4V8a2 2 0 1 1 4 0v8c0 3-2 5-5 5H9c-3 0-5-2-5-5v-3a2 2 0 1 1 4 0"/>
</svg>"""),
    ("Historial", """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none"
     stroke="{{color}}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="9"/>
  <path d="M12 7v5l3 3"/>
</svg>"""),
    ("Configuración", """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none"
     stroke="{{color}}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="3"/>
  <path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/>
</svg>"""),
]


def _make_icon(svg_template: str, color: str, size: int = 20) -> QIcon:
    svg = svg_template.replace("{{color}}", color)
    renderer = QSvgRenderer(svg.encode("utf-8"))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)


class Sidebar(QWidget):
    section_changed = Signal(int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(60)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 12, 8, 12)
        layout.setSpacing(8)

        self._buttons: list[QToolButton] = []
        for index, (name, svg) in enumerate(_SECTIONS):
            button = QToolButton()
            button.setObjectName("SidebarButton")
            button.setToolTip(name)
            button.setCheckable(True)
            button.setAutoExclusive(True)
            button.setIcon(_make_icon(svg, TEXT_SECONDARY))
            button.setIconSize(QSize(20, 20))
            button.clicked.connect(
                lambda checked=False, i=index, b=button, s=svg: self._on_clicked(i, b, s)
            )
            layout.addWidget(button, alignment=Qt.AlignHCenter)
            self._buttons.append(button)

        layout.addStretch(1)

        if self._buttons:
            self._buttons[0].setChecked(True)
            self._buttons[0].setIcon(_make_icon(_SECTIONS[0][1], ACCENT_CYAN))

    def _on_clicked(self, index: int, button: QToolButton, svg: str) -> None:
        for i, btn in enumerate(self._buttons):
            color = ACCENT_CYAN if i == index else TEXT_SECONDARY
            btn.setIcon(_make_icon(_SECTIONS[i][1], color))
        self.section_changed.emit(index)