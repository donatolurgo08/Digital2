"""Página de reconocimiento de gestos: panel interactivo y explicación."""

from __future__ import annotations

from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QWidget, QLabel

from hand_motion.ui.styles.palette import TEXT_SECONDARY
from hand_motion.ui.widgets.card import Card
from hand_motion.ui.widgets.gesture_panel import GesturePanel


class RecognitionView(QWidget):
    def __init__(self, panel: GesturePanel, parent=None) -> None:
        super().__init__(parent)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        layout.addWidget(panel)
        layout.addWidget(self._build_help_card())
        layout.addStretch(1)

        scroll.setWidget(content)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    @staticmethod
    def _build_help_card() -> Card:
        card = Card("Cómo funciona")
        layout = card.content_layout()
        text = QLabel(
            "Se promedia una ventana corta de X/Y/Z y se compara contra el reposo "
            "capturado. El eje con la mayor desviación define el gesto "
            "(X+, X-, Y+, Y-, Z+, Z-); si ninguno supera su umbral, el resultado "
            "es REPOSO.\n\n"
            "Los umbrales, la ventana y el reposo son ajustables y provisionales: "
            "no son una calibración del MMA7361. Capturá el reposo con la mano "
            "quieta antes de probar inclinaciones. En simulación, presioná "
            "Iniciar en Adquisición para generar muestras.\n\n"
            "El reconocimiento corre en la GUI; el firmware solo transmite X/Y/Z. "
            "Con DATA v2 (sin Z) el gesto se limita a los ejes X e Y. Z+ solo "
            "aparece si el reposo deja margen en Z (sensor invertido o "
            "aceleración dinámica)."
        )
        text.setWordWrap(True)
        text.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        layout.addWidget(text)
        return card
