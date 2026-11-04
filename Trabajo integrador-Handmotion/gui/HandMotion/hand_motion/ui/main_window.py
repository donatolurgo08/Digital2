"""Ventana principal de Hand Motion."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QScrollArea, QStackedWidget, QPushButton,
)

from hand_motion.processing.simulated_source import SimulatedAccelSource
from hand_motion.ui.styles.palette import ACCENT_CYAN, TEXT_SECONDARY, WARNING_AMBER
from hand_motion.ui.widgets.connection_indicator import ConnectionIndicator
from hand_motion.ui.widgets.temperature_indicator import TemperatureIndicator
from hand_motion.ui.widgets.accelerometer_panel import AccelerometerPanel
from hand_motion.ui.widgets.accelerometer_graph import AccelerometerGraph
from hand_motion.ui.widgets.gesture_panel import GesturePanel
from hand_motion.ui.widgets.serial_monitor import SerialMonitor
from hand_motion.ui.widgets.alarm_panel import AlarmPanel
from hand_motion.ui.widgets.status_bar import StatusBar
from hand_motion.ui.widgets.sidebar import Sidebar
from hand_motion.ui.views.placeholder_view import PlaceholderView


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Hand Motion")
        self._logo_path = Path(__file__).resolve().parents[2] / "resources" / "hand_motion_logo.png"
        if self._logo_path.is_file():
            self.setWindowIcon(QIcon(str(self._logo_path)))
        self.resize(1180, 760)
        self.setMinimumSize(960, 640)

        self._load_theme()

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_top_bar())

        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        self.sidebar = Sidebar()
        body_layout.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        body_layout.addWidget(self.stack, 1)

        # --- Dashboard (contenido existente, encapsulado) ---
        self.dashboard_page = QWidget()
        dash_layout = QVBoxLayout(self.dashboard_page)
        dash_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        scroll.setWidget(content)
        dash_layout.addWidget(scroll)

        grid = QGridLayout(content)
        grid.setContentsMargins(16, 16, 16, 16)
        grid.setSpacing(16)

        self.temp_panel = TemperatureIndicator()
        self.accel_panel = AccelerometerPanel()
        self.alarm_panel = AlarmPanel()
        self.gesture_panel = GesturePanel()
        self.serial_panel = SerialMonitor()
        self.accel_source = SimulatedAccelSource()
        self.accel_graph = AccelerometerGraph(source=self.accel_source)

        grid.addWidget(self.temp_panel, 0, 0)
        grid.addWidget(self.accel_panel, 0, 1)
        grid.addWidget(self.alarm_panel, 0, 2)
        grid.addWidget(self.gesture_panel, 1, 0, 1, 2)
        grid.addWidget(self.serial_panel, 1, 2)
        grid.addWidget(self.accel_graph, 2, 0, 1, 3)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        grid.setRowStretch(1, 1)
        grid.setRowStretch(2, 2)

        self.stack.addWidget(self.dashboard_page)

        # --- Secciones provisionales ---
        for name in ("Adquisición", "Reconocimiento", "Historial", "Configuración"):
            self.stack.addWidget(PlaceholderView(name))

        body_layout.setStretch(1, 1)
        root.addWidget(body, 1)

        self.status_bar = StatusBar()
        root.addWidget(self.status_bar)

        self.sidebar.section_changed.connect(self.stack.setCurrentIndex)

    def _toggle_mode(self, device_mode: bool) -> None:
        """Alterna entre fuente simulada y dispositivo real (protocolo pendiente)."""
        if device_mode:
            self.mode_button.setText("DISPOSITIVO")
            self.status_bar.set_mode("MODO: DISPOSITIVO", ACCENT_CYAN)
            self.status_bar.set_message("Modo dispositivo: protocolo pendiente de definir")
            self.accel_source.stop()
        else:
            self.mode_button.setText("SIMULACIÓN")
            self.status_bar.set_mode("MODO: SIMULACIÓN", WARNING_AMBER)
            self.status_bar.set_message("Modo simulación activo")

    def _build_top_bar(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("TopBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 12, 20, 12)

        brand_mark = QLabel()
        brand_mark.setObjectName("BrandLogo")
        brand_mark.setFixedSize(72, 48)
        brand_mark.setAccessibleName("Logo HAND MOTION")
        if self._logo_path.is_file():
            logo = QPixmap(str(self._logo_path))
            if not logo.isNull():
                brand_mark.setPixmap(
                    logo.scaled(72, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )
        layout.addWidget(brand_mark)

        title_box = QWidget()
        title_layout = QVBoxLayout(title_box)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(2)

        title = QLabel("HAND MOTION")
        title.setObjectName("AppTitle")
        title_layout.addWidget(title)

        accent = QFrame()
        accent.setFixedHeight(2)
        accent.setFixedWidth(48)
        accent.setStyleSheet("background:#d946ef; border:none;")
        title_layout.addWidget(accent)

        layout.addWidget(title_box)

        subtitle = QLabel("Sistema de reconocimiento de movimientos de la mano")
        subtitle.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:13px; margin-left:12px;")
        layout.addWidget(subtitle)

        layout.addStretch()

        self.mode_button = QPushButton("SIMULACIÓN")
        self.mode_button.setObjectName("Secondary")
        self.mode_button.setCheckable(True)
        self.mode_button.setChecked(False)
        self.mode_button.setToolTip("Alternar entre Simulación y Dispositivo")
        self.mode_button.clicked.connect(self._toggle_mode)
        layout.addWidget(self.mode_button)

        self.status = ConnectionIndicator("Desconectado", False)
        layout.addWidget(self.status)
        return bar

    def _load_theme(self) -> None:
        qss_path = Path(__file__).resolve().parent / "styles" / "theme.qss"
        try:
            self.setStyleSheet(qss_path.read_text(encoding="utf-8"))
        except OSError as exc:
            print(f"[Hand Motion] No se pudo cargar el tema: {exc}", file=sys.stderr)
