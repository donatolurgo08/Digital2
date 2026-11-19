"""Aviso flotante con el gesto reconocido sobre el gráfico XYZ.

El aviso es un hijo flotante del gráfico: no participa del layout, no
intercepta el mouse y se reposiciona al cambiar el tamaño de la ventana. Se
muestra al confirmarse un gesto y se desvanece solo.
"""

from __future__ import annotations

from PySide6.QtCore import (
    QEvent,
    QObject,
    QPropertyAnimation,
    QTimer,
    Qt,
)
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from hand_motion.logic.gesture_recognition import (
    GESTURE_DESCRIPTIONS,
    GESTURE_LABELS,
)
from hand_motion.ui.styles.palette import (
    ACCENT_CYAN,
    GESTURE_COLORS,
    TEXT_MUTED,
    TEXT_SECONDARY,
)


class GestureToast(QFrame):
    """Pop-up transitorio con el último gesto confirmado.

    ``parent`` es el widget contenedor y ``anchor`` el área sobre la que se
    apoya el aviso (por defecto, todo el contenedor). ``duration_ms`` es el
    tiempo visible antes de desvanecerse; el desvanecido no elimina el widget,
    solo lo oculta.
    """

    def __init__(
        self,
        parent: QWidget,
        *,
        anchor: QWidget | None = None,
        duration_ms: int = 2500,
        margin: int = 16,
    ) -> None:
        super().__init__(parent)
        if duration_ms <= 0:
            raise ValueError("duration_ms debe ser mayor que cero")
        if margin < 0:
            raise ValueError("margin no puede ser negativo")

        self._anchor = anchor
        self._duration_ms = duration_ms
        self._margin = margin
        self._fading_out = False

        self.setObjectName("GestureToast")
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedWidth(250)
        self.setAccessibleName("Aviso de gesto reconocido")
        self.setVisible(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(2)

        self.caption_label = QLabel("GESTO")
        self.caption_label.setObjectName("ToastCaption")
        layout.addWidget(self.caption_label)

        self.gesture_label = QLabel("--")
        self.gesture_label.setObjectName("ToastValue")
        layout.addWidget(self.gesture_label)

        self.detail_label = QLabel("")
        self.detail_label.setObjectName("ToastDetail")
        self.detail_label.setWordWrap(True)
        layout.addWidget(self.detail_label)

        self._apply_style(ACCENT_CYAN)

        self._effect = QGraphicsOpacityEffect(self)
        self._effect.setOpacity(1.0)
        self.setGraphicsEffect(self._effect)

        self._fade = QPropertyAnimation(self._effect, b"opacity", self)
        self._fade.setDuration(180)
        self._fade.finished.connect(self._on_fade_finished)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._start_fade_out)

        parent.installEventFilter(self)
        if anchor is not None:
            anchor.installEventFilter(self)

    # --- API pública ---

    def show_gesture(self, gesture: str | None) -> None:
        """Muestra el gesto; ``None`` oculta el aviso de inmediato."""
        if gesture is None:
            self.dismiss()
            return

        self._apply_style(GESTURE_COLORS.get(gesture, ACCENT_CYAN))
        self.gesture_label.setText(GESTURE_LABELS.get(gesture, gesture))
        self.detail_label.setText(GESTURE_DESCRIPTIONS.get(gesture, ""))

        self._reposition()
        self.show()
        self.raise_()

        self._fading_out = False
        self._fade.stop()
        self._effect.setOpacity(0.0)
        self._fade.setStartValue(0.0)
        self._fade.setEndValue(1.0)
        self._fade.start()
        self._timer.start(self._duration_ms)

    def dismiss(self) -> None:
        """Oculta el aviso sin animación y cancela el temporizador."""
        self._timer.stop()
        self._fade.stop()
        self._fading_out = False
        self._effect.setOpacity(1.0)
        self.hide()

    # --- Interno ---

    def _apply_style(self, accent: str) -> None:
        self.setStyleSheet(
            f"""
            QFrame#GestureToast {{
                background-color: rgba(17, 24, 39, 240);
                border: 1px solid {accent};
                border-radius: 12px;
            }}
            QLabel#ToastCaption {{
                color: {TEXT_MUTED};
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 2px;
            }}
            QLabel#ToastValue {{
                color: {accent};
                font-family: "Cascadia Code", "Consolas", "Lucida Console", monospace;
                font-size: 24px;
                font-weight: 700;
            }}
            QLabel#ToastDetail {{
                color: {TEXT_SECONDARY};
                font-size: 11px;
            }}
            """
        )

    def _reposition(self) -> None:
        parent = self.parentWidget()
        if parent is None:
            return

        if self._anchor is not None and self._anchor.parentWidget() is parent:
            area = self._anchor.geometry()
        else:
            area = parent.rect()

        self.adjustSize()
        x = area.right() + 1 - self.width() - self._margin
        y = area.top() + self._margin
        self.move(max(0, x), max(0, y))

    def _start_fade_out(self) -> None:
        self._fading_out = True
        self._fade.stop()
        self._fade.setStartValue(self._effect.opacity())
        self._fade.setEndValue(0.0)
        self._fade.start()

    def _on_fade_finished(self) -> None:
        if not self._fading_out:
            return
        self._fading_out = False
        self.hide()
        self._effect.setOpacity(1.0)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() in (QEvent.Resize, QEvent.Show) and self.isVisible():
            self._reposition()
        return super().eventFilter(watched, event)
