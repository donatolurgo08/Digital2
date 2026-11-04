"""Monitor de comunicación serial con el PIC (pyserial)."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton,
    QLabel, QTextEdit,
)

from hand_motion.communication.serial_port import SerialPortManager
from hand_motion.ui.widgets.card import Card
from hand_motion.ui.styles.palette import ALARM_RED, OK_GREEN, WARNING_AMBER


class SerialMonitor(QWidget):
    """Permite seleccionar un puerto y conectar/desconectar el enlace."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._manager = SerialPortManager(self)

        card = Card("Monitor serial")
        layout = card.content_layout()

        row = QHBoxLayout()
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(120)

        self.baud_combo = QComboBox()
        self.baud_combo.addItems(["9600", "19200", "38400", "115200"])

        self.refresh_btn = QPushButton("⟳")
        self.refresh_btn.setObjectName("Secondary")
        self.refresh_btn.setToolTip("Actualizar lista de puertos")
        self.refresh_btn.setFixedWidth(36)

        self.connect_btn = QPushButton("Conectar")
        self.connect_btn.setObjectName("Primary")

        row.addWidget(QLabel("Puerto"))
        row.addWidget(self.port_combo)
        row.addWidget(self.refresh_btn)
        row.addWidget(QLabel("Baud"))
        row.addWidget(self.baud_combo)
        row.addWidget(self.connect_btn)
        row.addStretch()
        layout.addLayout(row)

        self.status = QLabel("Estado: Desconectado")
        self.status.setStyleSheet(f"color:{ALARM_RED};")
        layout.addWidget(self.status)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log, 1)

        note = QLabel("⚠ La lectura de tramas quedará activa al definir el protocolo")
        note.setStyleSheet(f"color: {WARNING_AMBER}; font-size: 11px;")
        layout.addWidget(note)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(card)

        self.refresh_btn.clicked.connect(self._refresh_ports)
        self.connect_btn.clicked.connect(self._toggle_connection)
        self._manager.connection_changed.connect(self._on_connection_changed)
        self._manager.error_occurred.connect(self._log)

        self._refresh_ports()

    def _refresh_ports(self) -> None:
        ports = self._manager.refresh_ports()
        self.port_combo.clear()
        if ports:
            for port in ports:
                self.port_combo.addItem(f"{port.device} — {port.description}", port.device)
            self._log(f"Puertos detectados: {len(ports)}")
        else:
            self.port_combo.addItem("Sin puertos disponibles", None)
            self._log("No se detectaron puertos serie.")

    def _toggle_connection(self) -> None:
        if self._manager.connected:
            self._manager.close()
            self._log("Desconectado por el usuario.")
            return

        device = self.port_combo.currentData()
        if not device:
            self._log("No hay un puerto seleccionado para conectar.")
            self.status.setText("Estado: Sin puerto disponible")
            self.status.setStyleSheet(f"color:{WARNING_AMBER};")
            return

        baud_rate = int(self.baud_combo.currentText())
        self._log(f"Conectando a {device} @ {baud_rate}...")
        self._manager.open(device, baud_rate)

    def _on_connection_changed(self, connected: bool) -> None:
        if connected:
            self.connect_btn.setText("Desconectar")
            self.connect_btn.setObjectName("Danger")
            self.connect_btn.style().unpolish(self.connect_btn)
            self.connect_btn.style().polish(self.connect_btn)
            self.status.setText("Estado: Conectado")
            self.status.setStyleSheet(f"color:{OK_GREEN};")
        else:
            self.connect_btn.setText("Conectar")
            self.connect_btn.setObjectName("Primary")
            self.connect_btn.style().unpolish(self.connect_btn)
            self.connect_btn.style().polish(self.connect_btn)
            self.status.setText("Estado: Desconectado")
            self.status.setStyleSheet(f"color:{ALARM_RED};")

    def _log(self, message: str) -> None:
        self.log.append(message)
