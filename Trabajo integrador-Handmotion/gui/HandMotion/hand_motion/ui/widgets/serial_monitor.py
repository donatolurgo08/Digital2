"""Conexión USB-TTL, estado del protocolo y controles PIC v1."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QComboBox, QPushButton,
    QLabel, QTextEdit, QSpinBox,
)

from hand_motion.core.controller import AppController
from hand_motion.communication.protocol import (
    DEFAULT_DATA_PERIOD_MS, MAX_DATA_PERIOD_MS, MIN_DATA_PERIOD_MS,
    AckPacket, Command, DataPacket, StatusPacket,
)
from hand_motion.ui.widgets.card import Card
from hand_motion.ui.styles.palette import ALARM_RED, OK_GREEN, WARNING_AMBER


class SerialMonitor(QWidget):
    """Permite conectar el PIC y enviar comandos del protocolo serie v1."""

    def __init__(self, controller: AppController, parent=None) -> None:
        super().__init__(parent)
        self.controller = controller

        card = Card("PIC · Serie v1")
        layout = card.content_layout()

        port_row = QHBoxLayout()
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(80)
        self.refresh_btn = QPushButton("⟳")
        self.refresh_btn.setObjectName("Secondary")
        self.refresh_btn.setToolTip("Actualizar lista de puertos")
        self.refresh_btn.setFixedWidth(32)
        self.connect_btn = QPushButton("Conectar")
        self.connect_btn.setObjectName("Primary")
        self.connect_btn.setFixedWidth(90)
        port_label = QLabel("Puerto")
        port_label.setFixedWidth(48)
        port_row.addWidget(port_label)
        port_row.addWidget(self.port_combo, 1)
        port_row.addWidget(self.refresh_btn)
        port_row.addWidget(self.connect_btn)
        layout.addLayout(port_row)

        self.link_info = QLabel("Enlace fijo: 9600 Bd · 8N1")
        self.link_info.setWordWrap(True)
        self.link_info.setStyleSheet(f"color:{WARNING_AMBER}; font-size:11px;")
        layout.addWidget(self.link_info)

        self.connection_status = QLabel("Estado: Desconectado")
        self.connection_status.setWordWrap(True)
        self.connection_status.setStyleSheet(f"color:{ALARM_RED};")
        layout.addWidget(self.connection_status)

        controls = QGridLayout()
        self.period_spin = QSpinBox()
        self.period_spin.setRange(MIN_DATA_PERIOD_MS, MAX_DATA_PERIOD_MS)
        self.period_spin.setValue(DEFAULT_DATA_PERIOD_MS)
        self.period_spin.setFixedWidth(92)
        self.period_spin.setSuffix(" ms")
        self.start_btn = QPushButton("START")
        self.stop_btn = QPushButton("STOP")
        self.stop_btn.setObjectName("Danger")
        self.status_btn = QPushButton("GET STATUS")
        self.ping_btn = QPushButton("PING")
        self.start_btn.setFixedWidth(72)
        self.stop_btn.setFixedWidth(72)
        self.status_btn.setFixedWidth(92)
        self.ping_btn.setFixedWidth(68)
        period_label = QLabel("Período")
        period_label.setFixedWidth(58)
        controls.addWidget(period_label, 0, 0)
        controls.addWidget(self.period_spin, 0, 1)
        controls.addWidget(self.start_btn, 0, 2)
        controls.addWidget(self.stop_btn, 0, 3)

        self.threshold_spin = QSpinBox()
        self.threshold_spin.setRange(0, 99)
        self.threshold_spin.setValue(40)
        self.threshold_spin.setFixedWidth(92)
        self.threshold_spin.setSuffix(" °C")
        self.threshold_btn = QPushButton("Fijar umbral")
        self.threshold_btn.setFixedWidth(145)
        alarm_label = QLabel("Alarma")
        alarm_label.setFixedWidth(58)
        controls.addWidget(alarm_label, 1, 0)
        controls.addWidget(self.threshold_spin, 1, 1)
        controls.addWidget(self.threshold_btn, 1, 2, 1, 2)

        self.offset_spin = QSpinBox()
        self.offset_spin.setRange(0, 1023)
        self.offset_spin.setValue(338)
        self.offset_spin.setFixedWidth(92)
        self.offset_btn = QPushButton("Fijar offset X")
        self.offset_btn.setFixedWidth(145)
        offset_label = QLabel("Offset X")
        offset_label.setFixedWidth(58)
        controls.addWidget(offset_label, 2, 0)
        controls.addWidget(self.offset_spin, 2, 1)
        controls.addWidget(self.offset_btn, 2, 2, 1, 2)
        controls.addWidget(self.status_btn, 3, 2)
        controls.addWidget(self.ping_btn, 3, 3)
        layout.addLayout(controls)

        self.device_info = QLabel("Esperando STATUS del PIC · X en mg nominales · Y/Z reservados")
        self.device_info.setWordWrap(True)
        self.device_info.setStyleSheet(f"color:{WARNING_AMBER}; font-size:11px;")
        layout.addWidget(self.device_info)

        self.last_data = QLabel("Sin tramas DATA recibidas")
        self.last_data.setWordWrap(True)
        self.last_data.setStyleSheet(f"color:{OK_GREEN}; font-size:11px;")
        layout.addWidget(self.last_data)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(100)
        layout.addWidget(self.log)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(card)

        self.refresh_btn.clicked.connect(self._refresh_ports)
        self.connect_btn.clicked.connect(self._toggle_connection)
        self.start_btn.clicked.connect(self._start)
        self.stop_btn.clicked.connect(self._stop)
        self.status_btn.clicked.connect(self._request_status)
        self.ping_btn.clicked.connect(self._ping)
        self.threshold_btn.clicked.connect(self._set_threshold)
        self.offset_btn.clicked.connect(self._set_offset)

        state = self.controller.state
        state.connection_changed.connect(self._on_connection_changed)
        state.data_packet_received.connect(self._on_data_packet)
        state.status_packet_received.connect(self._on_status_packet)
        state.ack_received.connect(self._on_ack)
        self.controller.message.connect(self._log)

        self._set_controls_enabled(False)
        self._refresh_ports()

    def _refresh_ports(self) -> None:
        previous = self.port_combo.currentData()
        ports = self.controller.serial.refresh_ports()
        self.port_combo.clear()
        for port in ports:
            self.port_combo.addItem(f"{port.device} — {port.description}", port.device)
        if not ports:
            self.port_combo.addItem("Sin puertos disponibles", None)
            self._log("No se detectaron puertos serie.")
        elif previous:
            index = self.port_combo.findData(previous)
            if index >= 0:
                self.port_combo.setCurrentIndex(index)
        else:
            self._log(f"Puertos detectados: {len(ports)}")

    def _toggle_connection(self) -> None:
        if self.controller.serial.connected:
            self.controller.close()
            self._log("Desconectado por el usuario.")
            return
        device = self.port_combo.currentData()
        if not device:
            self._log("No hay un puerto seleccionado para conectar.")
            self.connection_status.setText("Estado: Sin puerto disponible")
            self.connection_status.setStyleSheet(f"color:{WARNING_AMBER};")
            return
        self._log(f"Conectando a {device} @ 9600 Bd, 8N1...")
        self.controller.open(device)

    def _on_connection_changed(self, connected: bool) -> None:
        if connected:
            self.connect_btn.setText("Desconectar")
            self.connect_btn.setObjectName("Danger")
            self.connection_status.setText("Estado: Conectado")
            self.connection_status.setStyleSheet(f"color:{OK_GREEN};")
            self._log("Enlace abierto. Consultando STATUS...")
            self.controller.request_status()
        else:
            self.connect_btn.setText("Conectar")
            self.connect_btn.setObjectName("Primary")
            self.connection_status.setText("Estado: Desconectado")
            self.connection_status.setStyleSheet(f"color:{ALARM_RED};")
        self.connect_btn.style().unpolish(self.connect_btn)
        self.connect_btn.style().polish(self.connect_btn)
        self._set_controls_enabled(connected)

    def _set_controls_enabled(self, enabled: bool) -> None:
        for widget in (
            self.period_spin, self.start_btn, self.stop_btn, self.status_btn,
            self.ping_btn,
            self.threshold_spin, self.threshold_btn, self.offset_spin,
            self.offset_btn,
        ):
            widget.setEnabled(enabled)

    def _start(self) -> None:
        period = self.period_spin.value()
        if self.controller.start_stream(period):
            self._log(f"START enviado: período {period} ms.")

    def _stop(self) -> None:
        if self.controller.stop_stream():
            self._log("STOP enviado.")

    def _request_status(self) -> None:
        if self.controller.request_status():
            self._log("GET_STATUS enviado.")

    def _ping(self) -> None:
        if self.controller.ping():
            self._log("PING enviado.")

    def _set_threshold(self) -> None:
        value = self.threshold_spin.value()
        if self.controller.set_threshold(value):
            self._log(f"SET_THRESHOLD enviado: {value} °C.")

    def _set_offset(self) -> None:
        value = self.offset_spin.value()
        if self.controller.set_x_offset(value):
            self._log(f"SET_OFFSET enviado: {value} cuentas ADC.")

    def _on_data_packet(self, packet: DataPacket) -> None:
        alarm = "alarma activa" if packet.alarm_active else "alarma apagada"
        self.last_data.setText(
            f"DATA #{packet.sequence} · {packet.temperature_c} °C · "
            f"X {packet.x_mg:+d} mg · {alarm}"
        )

    def _on_status_packet(self, packet: StatusPacket) -> None:
        self.period_spin.setValue(
            max(MIN_DATA_PERIOD_MS, min(MAX_DATA_PERIOD_MS, packet.period_ms))
        )
        self.threshold_spin.setValue(packet.threshold_c)
        self.offset_spin.setValue(packet.x_offset_counts)
        mode = "streaming activo" if packet.streaming else "streaming detenido"
        self.device_info.setText(
            f"Firmware v{packet.version} · {packet.period_ms} ms · "
            f"umbral {packet.threshold_c} °C · offset X {packet.x_offset_counts} · {mode}"
        )
        self.device_info.setStyleSheet(f"color:{OK_GREEN}; font-size:11px;")
        self._log(f"STATUS recibido: firmware v{packet.version}, {mode}.")

    def _on_ack(self, packet: AckPacket) -> None:
        results = {0: "aceptado", 1: "parámetro inválido", 2: "comando desconocido"}
        result_text = results.get(packet.result, f"resultado {packet.result}")
        self._log(f"ACK 0x{packet.command:02X}: {result_text}.")
        if packet.result == 0 and packet.command in {
            Command.START, Command.STOP, Command.SET_THRESHOLD, Command.SET_OFFSET,
        }:
            self.controller.request_status()

    def _log(self, message: str) -> None:
        self.log.append(message)
