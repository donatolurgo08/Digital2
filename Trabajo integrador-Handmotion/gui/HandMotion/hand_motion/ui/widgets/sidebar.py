"""Barra lateral compacta de navegación."""

from __future__ import annotations

from PySide6.QtCore import (
    QAbstractAnimation,
    QEasingCurve,
    QParallelAnimationGroup,
    QPropertyAnimation,
    QSize,
    Qt,
    Signal,
)
from PySide6.QtGui import QCursor, QIcon, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QSizePolicy, QWidget, QVBoxLayout, QToolButton

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
  <path d="M3 12h3l3-6 4 12 4-12 3 6h2"/>
</svg>"""),
    ("Reconocimiento", """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none"
     stroke="{{color}}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M8 12V7a2 2 0 1 1 4 0v5m0-3V6a2 2 0 1 1 4 0v6m0-4V8a2 2 0 1 1 4 0v8c0 3-2 5-5 5H9c-3 0-5-2-5-5v-3a2 2 0 1 1 4 0"/>
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
    width_changed = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self._collapsed_width = 60
        self._expanded_width = 184
        self._expanded = False
        self.setMinimumWidth(self._collapsed_width)
        self.setMaximumWidth(self._collapsed_width)

        layout = QVBoxLayout(self)
        self._layout = layout
        layout.setContentsMargins(8, 12, 8, 12)
        layout.setSpacing(8)

        self._buttons: list[QToolButton] = []
        for index, (name, svg) in enumerate(_SECTIONS):
            button = QToolButton()
            button.setObjectName("SidebarButton")
            button.setText(name)
            button.setToolTip(name)
            button.setCheckable(True)
            button.setAutoExclusive(True)
            button.setToolButtonStyle(Qt.ToolButtonIconOnly)
            button.setIcon(_make_icon(svg, TEXT_SECONDARY))
            button.setIconSize(QSize(20, 20))
            button.setCursor(QCursor(Qt.PointingHandCursor))
            button.setMinimumHeight(42)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            button.clicked.connect(
                lambda checked=False, i=index: self.select_section(i)
            )
            layout.addWidget(button, alignment=Qt.AlignHCenter)
            self._buttons.append(button)

        layout.addStretch(1)
        self._animations = QParallelAnimationGroup(self)
        self._width_animations = []
        for property_name in (b"minimumWidth", b"maximumWidth"):
            animation = QPropertyAnimation(self, property_name, self._animations)
            animation.setDuration(180)
            animation.setEasingCurve(QEasingCurve.OutCubic)
            self._animations.addAnimation(animation)
            self._width_animations.append(animation)
        self._animations.finished.connect(self.width_changed.emit)

        if self._buttons:
            self._buttons[0].setChecked(True)
            self._buttons[0].setIcon(_make_icon(_SECTIONS[0][1], ACCENT_CYAN))

    def set_expanded(self, expanded: bool) -> None:
        """Anima el ancho y muestra etiquetas sin cubrir el contenido vecino."""
        if (
            expanded == self._expanded
            and self._animations.state() != QAbstractAnimation.Running
        ):
            return

        self._expanded = expanded
        self._animations.stop()
        target_width = (
            self._expanded_width if expanded else self._collapsed_width
        )
        current_width = self.width()
        for animation in self._width_animations:
            animation.setStartValue(current_width)
            animation.setEndValue(target_width)

        for button in self._buttons:
            button.setToolButtonStyle(
                Qt.ToolButtonTextBesideIcon if expanded else Qt.ToolButtonIconOnly
            )
            self._layout.setAlignment(
                button,
                Qt.AlignLeft | Qt.AlignVCenter if expanded else Qt.AlignHCenter,
            )
        self._animations.start()

    def enterEvent(self, event) -> None:
        self.set_expanded(True)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        # Ignora salidas sintéticas al pasar entre la barra y sus botones.
        if not self.rect().contains(self.mapFromGlobal(QCursor.pos())):
            self.set_expanded(False)
        super().leaveEvent(event)

    def select_section(self, index: int) -> None:
        """Selecciona una sección desde un control fuera de la barra lateral."""
        if not 0 <= index < len(self._buttons):
            raise IndexError("Índice de sección fuera de rango")
        self._buttons[index].setChecked(True)
        for i, btn in enumerate(self._buttons):
            color = ACCENT_CYAN if i == index else TEXT_SECONDARY
            btn.setIcon(_make_icon(_SECTIONS[i][1], color))
        self.section_changed.emit(index)
