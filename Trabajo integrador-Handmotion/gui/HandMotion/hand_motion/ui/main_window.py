"""Ventana principal de Hand Motion."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QKeySequence, QPixmap, QShortcut
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QScrollArea, QStackedWidget, QPushButton,
)

from hand_motion.config import (
    GESTURE_HOLD_SAMPLES,
    GESTURE_THRESHOLD_G,
    GESTURE_WINDOW_SAMPLES,
)
from hand_motion.core.controller import AppController
from hand_motion.core.state import AppState
from hand_motion.logic.gesture_recognition import (
    GestureRecognizer,
    TiltBaseline,
    TiltThresholds,
)
from hand_motion.processing.simulated_source import SimulatedAccelSource
from hand_motion.ui.styles.palette import ACCENT_CYAN, TEXT_SECONDARY, WARNING_AMBER
from hand_motion.ui.widgets.connection_indicator import ConnectionIndicator
from hand_motion.ui.widgets.temperature_indicator import TemperatureIndicator
from hand_motion.ui.widgets.accelerometer_panel import AccelerometerPanel
from hand_motion.ui.widgets.accelerometer_graph import AccelerometerGraph
from hand_motion.ui.widgets.gesture_panel import GesturePanel, GestureSummary
from hand_motion.ui.widgets.serial_monitor import SerialMonitor
from hand_motion.ui.widgets.alarm_panel import AlarmPanel
from hand_motion.ui.widgets.status_bar import StatusBar
from hand_motion.ui.widgets.sidebar import Sidebar
from hand_motion.ui.views.placeholder_view import PlaceholderView
from hand_motion.ui.views.recognition_view import RecognitionView


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
        self._fullscreen_shortcut = QShortcut(QKeySequence("F11"), self)
        self._fullscreen_shortcut.activated.connect(self._toggle_fullscreen)
        self._escape_shortcut = QShortcut(QKeySequence("Escape"), self)
        self._escape_shortcut.activated.connect(self._leave_fullscreen)
        self.state = AppState(self)
        self.controller = AppController(self.state, self)
        self._device_mode = False

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
        self.accel_panel = AccelerometerPanel("X")
        self.accel_y_panel = AccelerometerPanel("Y")
        self.accel_z_panel = AccelerometerPanel("Z")
        self.alarm_panel = AlarmPanel()
        self.gesture_summary = GestureSummary()
        self.gesture_panel = GesturePanel()
        self.serial_panel = SerialMonitor(self.controller)
        self.accel_source = SimulatedAccelSource()
        self.accel_graph = AccelerometerGraph(source=self.accel_source)
        self.accel_source.sample_xyz.connect(self._on_simulated_sample)

        self.gesture_recognizer = GestureRecognizer(
            thresholds=TiltThresholds(
                x_g=GESTURE_THRESHOLD_G,
                y_g=GESTURE_THRESHOLD_G,
                z_g=GESTURE_THRESHOLD_G,
            ),
            window_samples=GESTURE_WINDOW_SAMPLES,
            hold_samples=GESTURE_HOLD_SAMPLES,
        )
        self._gesture_calibrated = False
        self._last_gesture: str | None = None

        self._dashboard_grid = grid
        self._dashboard_widgets = (
            self.temp_panel,
            self.accel_panel,
            self.accel_y_panel,
            self.accel_z_panel,
            self.alarm_panel,
            self.gesture_summary,
            self.serial_panel,
        )
        self._dashboard_compact: bool | None = None
        self._arrange_dashboard()

        self.stack.addWidget(self.dashboard_page)

        # --- Adquisición XYZ en tiempo real ---
        self.acquisition_page = QWidget()
        acquisition_layout = QVBoxLayout(self.acquisition_page)
        acquisition_layout.setContentsMargins(16, 16, 16, 16)
        acquisition_layout.addWidget(self.accel_graph, 1)
        self.stack.addWidget(self.acquisition_page)

        # --- Reconocimiento de gestos ---
        self.recognition_page = RecognitionView(self.gesture_panel)
        self.stack.addWidget(self.recognition_page)

        # --- Secciones provisionales ---
        for name in ("Historial", "Configuración"):
            self.stack.addWidget(PlaceholderView(name))

        body_layout.setStretch(1, 1)
        root.addWidget(body, 1)

        self.status_bar = StatusBar()
        root.addWidget(self.status_bar)

        self.sidebar.section_changed.connect(self.stack.setCurrentIndex)
        self.state.connection_changed.connect(self._on_connection_changed)
        self.state.data_packet_received.connect(self._on_live_data)
        self.state.status_packet_received.connect(self._on_device_status)
        self.state.gesture_changed.connect(self._on_gesture_changed)
        self.gesture_panel.thresholds_changed.connect(
            self._on_gesture_thresholds_changed
        )
        self.gesture_panel.baseline_changed.connect(
            self._on_gesture_baseline_changed
        )
        self.gesture_panel.capture_rest_requested.connect(self._capture_gesture_rest)
        self.gesture_panel.reset_requested.connect(self._reset_gesture)

    def _toggle_mode(self, device_mode: bool) -> None:
        """Alterna la visualización entre la simulación y las tramas del PIC."""
        self._set_mode(device_mode)

    def _toggle_fullscreen(self) -> None:
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _leave_fullscreen(self) -> None:
        if self.isFullScreen():
            self.showNormal()

    def _set_mode(self, device_mode: bool) -> None:
        self._device_mode = device_mode
        self.accel_graph.set_device_mode(device_mode)
        # No mezclar muestras ni reposo de simulación y dispositivo.
        was_calibrated = self._gesture_calibrated
        self.gesture_recognizer.clear_baseline()
        self._gesture_calibrated = False
        self._last_gesture = None
        self.state.set_gesture(None)
        self.gesture_panel.reset_baseline()
        self.gesture_panel.set_calibrated(False)
        self.gesture_panel.set_data_unavailable()
        if was_calibrated:
            self.gesture_panel.append_log(
                "Cambió la fuente de datos: recapturá el reposo."
            )
        if device_mode:
            self.mode_button.setText("DISPOSITIVO")
            self.status_bar.set_mode("MODO: DISPOSITIVO", ACCENT_CYAN)
            if self.state.data.data_received:
                self._show_latest_device_data()
                self.status_bar.set_message("Mostrando la última medición recibida del PIC")
            else:
                self.temp_panel.clear_reading()
                self.accel_panel.clear_value()
                self.accel_y_panel.clear_value()
                self.accel_z_panel.clear_value()
                self.alarm_panel.set_waiting()
                if self.state.data.connected:
                    self.status_bar.set_message(
                        "Conectado: esperando tramas DATA del PIC"
                    )
                else:
                    self.status_bar.set_message(
                        "Modo dispositivo: conectá el PIC desde Monitor serial"
                    )
        else:
            self.mode_button.setText("SIMULACIÓN")
            self.status_bar.set_mode("MODO: SIMULACIÓN", WARNING_AMBER)
            self.temp_panel.clear_reading()
            self.accel_panel.clear_value()
            self.accel_y_panel.clear_value()
            self.accel_z_panel.clear_value()
            self.alarm_panel.set_waiting()
            self.status_bar.set_message(
                "Modo simulación activo · fuente XYZ determinista"
            )

    def _show_latest_device_data(self) -> None:
        data = self.state.data
        if data.temperature_c is None or data.accel_x is None:
            return
        self.temp_panel.update_temperature(data.temperature_c, data.alarm_active)
        self.accel_panel.update_value(data.accel_x, live=True)
        if data.accel_y is None:
            self.accel_y_panel.clear_value()
        else:
            self.accel_y_panel.update_value(data.accel_y, live=True)
        self.accel_z_panel.update_value(data.accel_z, live=True)
        self.alarm_panel.update_alarm(data.alarm_active, data.alarm_threshold_c)
        if data.accel_y is not None:
            self._feed_gesture(data.accel_x, data.accel_y, data.accel_z)

    def _on_live_data(self, packet) -> None:
        if not self._device_mode:
            return
        data = self.state.data
        self.temp_panel.update_temperature(packet.temperature_c, packet.alarm_active)
        self.accel_panel.update_value(packet.x_g, live=True)
        self.accel_y_panel.update_value(packet.y_g, live=True)
        self.accel_z_panel.update_value(packet.z_g, live=True)
        self.alarm_panel.update_alarm(packet.alarm_active, data.alarm_threshold_c)
        self.accel_graph.add_live_sample(
            packet.x_g,
            period_ms=data.period_ms,
            y_g=packet.y_g,
            z_g=packet.z_g,
        )
        self._feed_gesture(packet.x_g, packet.y_g, packet.z_g)
        z_text = "--" if packet.z_mg is None else f"{packet.z_mg:+d} mg"
        self.status_bar.set_message(
            f"PIC DATA #{packet.sequence} · X {packet.x_mg:+d} mg · "
            f"Y {packet.y_mg:+d} mg · Z {z_text} · "
            f"{packet.temperature_c} °C"
        )

    def _on_device_status(self, packet) -> None:
        self.temp_panel.set_threshold(packet.threshold_c)
        if self._device_mode:
            if self.state.data.data_received:
                self.alarm_panel.update_alarm(
                    self.state.data.alarm_active, packet.threshold_c
                )
            self.status_bar.set_message(
                f"PIC v{packet.version} · período {packet.period_ms} ms · "
                f"umbral {packet.threshold_c} °C"
            )

    def _on_connection_changed(self, connected: bool) -> None:
        self.status.set_connected(connected)
        if connected and not self._device_mode:
            self.mode_button.setChecked(True)
            self._set_mode(True)
        elif not connected and self._device_mode:
            self.mode_button.setChecked(False)
            self._set_mode(False)

    def _on_simulated_sample(
        self, x_g: float, y_g: float, z_g: float
    ) -> None:
        if not self._device_mode:
            self.accel_panel.update_value(x_g, live=False)
            self.accel_y_panel.update_value(y_g, live=False)
            self.accel_z_panel.update_value(z_g, live=False)
            self._feed_gesture(x_g, y_g, z_g)

    def _feed_gesture(
        self, x_g: float, y_g: float, z_g: float | None
    ) -> None:
        """Alimenta el clasificador con la fuente activa (simulación o PIC)."""
        self.gesture_panel.set_live_values(x_g, y_g, z_g)
        # Sin reposo capturado igual se acumulan muestras para poder capturarlo.
        gesture = self.gesture_recognizer.add_sample(x_g, y_g, z_g)
        if not self._gesture_calibrated or gesture is None:
            return
        if gesture != self._last_gesture:
            self._last_gesture = gesture
            self.state.set_gesture(gesture)

    def _on_gesture_changed(self, gesture: str) -> None:
        value = gesture or None
        self.gesture_panel.set_gesture(value)
        self.gesture_summary.set_gesture(value)

    def _on_gesture_thresholds_changed(self) -> None:
        x_g, y_g, z_g = self.gesture_panel.thresholds()
        self.gesture_recognizer.set_thresholds(
            TiltThresholds(x_g=x_g, y_g=y_g, z_g=z_g)
        )
        self.gesture_recognizer.set_window_samples(
            self.gesture_panel.window_samples()
        )

    def _on_gesture_baseline_changed(self) -> None:
        x_g, y_g, z_g = self.gesture_panel.baseline()
        self._apply_gesture_baseline(
            TiltBaseline(x_g=x_g, y_g=y_g, z_g=z_g),
            source="Reposo manual",
        )

    def _capture_gesture_rest(self) -> None:
        mean = self.gesture_recognizer.current_mean()
        if mean is None:
            self.gesture_panel.append_log(
                "Sin muestras: iniciá la simulación o conectá el PIC."
            )
            self.status_bar.set_message(
                "No hay muestras para capturar el reposo"
            )
            return

        x_g, y_g, z_g = mean
        baseline_z = 0.0 if z_g is None else z_g
        self.gesture_panel.set_baseline(x_g, y_g, baseline_z)
        self._apply_gesture_baseline(
            TiltBaseline(x_g=x_g, y_g=y_g, z_g=baseline_z),
            source="Reposo capturado",
        )
        if z_g is None:
            self.gesture_panel.append_log(
                "DATA v2 sin Z: el gesto se limita a los ejes X e Y."
            )

    def _apply_gesture_baseline(
        self, baseline: TiltBaseline, *, source: str
    ) -> None:
        self.gesture_recognizer.set_baseline(baseline)
        self._gesture_calibrated = True
        self._last_gesture = None
        self.state.set_gesture(None)
        self.gesture_panel.set_calibrated(True)
        self.gesture_panel.append_log(
            f"{source}: X {baseline.x_g:+.3f} · Y {baseline.y_g:+.3f} · "
            f"Z {baseline.z_g:+.3f} g"
        )

    def _reset_gesture(self) -> None:
        self.gesture_recognizer.reset()
        self._last_gesture = None
        self.state.set_gesture(None)
        self.gesture_panel.append_log("Reconocimiento reiniciado.")

    def _arrange_dashboard(self) -> None:
        """Refluye las tarjetas al ancho compacto sin rediseñar el dashboard."""
        compact = self.width() < 1150
        if compact == self._dashboard_compact:
            return

        grid = self._dashboard_grid
        for widget in self._dashboard_widgets:
            grid.removeWidget(widget)
        for column in range(5):
            grid.setColumnStretch(column, 0)
        for row in range(3):
            grid.setRowStretch(row, 0)

        if compact:
            grid.addWidget(self.temp_panel, 0, 0)
            grid.addWidget(self.accel_panel, 0, 1)
            grid.addWidget(self.accel_y_panel, 0, 2)
            grid.addWidget(self.gesture_summary, 1, 0, 1, 2)
            grid.addWidget(self.serial_panel, 1, 2)
            grid.addWidget(self.accel_z_panel, 2, 0)
            grid.addWidget(self.alarm_panel, 2, 1)
            for column in range(3):
                grid.setColumnStretch(column, 1)
            grid.setRowStretch(1, 1)
        else:
            grid.addWidget(self.temp_panel, 0, 0)
            grid.addWidget(self.accel_panel, 0, 1)
            grid.addWidget(self.accel_y_panel, 0, 2)
            grid.addWidget(self.accel_z_panel, 0, 3)
            grid.addWidget(self.alarm_panel, 0, 4)
            grid.addWidget(self.gesture_summary, 1, 0, 1, 3)
            grid.addWidget(self.serial_panel, 1, 3, 1, 2)
            for column in range(5):
                grid.setColumnStretch(column, 1)
            grid.setRowStretch(1, 1)

        self._dashboard_compact = compact

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if hasattr(self, "_dashboard_grid"):
            self._arrange_dashboard()

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

        subtitle = QLabel("Supervisión térmica · adquisición del acelerómetro XYZ")
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

    def closeEvent(self, event) -> None:
        self.accel_source.stop()
        self.controller.close()
        super().closeEvent(event)
