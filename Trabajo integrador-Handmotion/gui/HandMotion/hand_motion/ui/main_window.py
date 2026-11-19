"""Ventana principal de Hand Motion."""

from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PySide6.QtGui import QIcon, QKeySequence, QPixmap, QShortcut
from PySide6.QtWidgets import (
    QAbstractButton, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QGraphicsOpacityEffect, QScrollArea, QStackedWidget,
    QPushButton,
)

from hand_motion.core.controller import AppController
from hand_motion.core.state import AppState
from hand_motion.logic.gesture_recognition import (
    GestureRecognizer,
    TiltBaseline,
    TiltThresholds,
)
from hand_motion.processing.simulated_source import SimulatedAccelSource
from hand_motion.preferences import GuiPreferences, GuiPreferencesStore
from hand_motion.ui.styles.palette import (
    ACCENT_CYAN,
    ACCENT_MAGENTA,
    TEXT_SECONDARY,
    WARNING_AMBER,
)
from hand_motion.ui.button_feedback import ButtonFeedback
from hand_motion.ui.widgets.connection_indicator import ConnectionIndicator
from hand_motion.ui.widgets.temperature_indicator import TemperatureIndicator
from hand_motion.ui.widgets.accelerometer_panel import AccelerometerPanel
from hand_motion.ui.widgets.accelerometer_graph import AccelerometerGraph
from hand_motion.ui.widgets.gesture_panel import GesturePanel, GestureSummary
from hand_motion.ui.widgets.gesture_toast import GestureToast
from hand_motion.ui.widgets.serial_monitor import SerialMonitor
from hand_motion.ui.widgets.alarm_panel import AlarmPanel
from hand_motion.ui.widgets.status_bar import StatusBar
from hand_motion.ui.widgets.sidebar import Sidebar
from hand_motion.ui.widgets.card import Card
from hand_motion.ui.views.configuration_view import ConfigurationView
from hand_motion.ui.views.recognition_view import RecognitionView


class MainWindow(QMainWindow):
    def __init__(
        self, preferences_store: GuiPreferencesStore | None = None
    ) -> None:
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
        self.preferences_store = preferences_store or GuiPreferencesStore()
        self.preferences = self.preferences_store.load()

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
        self.accel_panel = AccelerometerPanel("X", show_note=False)
        self.accel_y_panel = AccelerometerPanel("Y", show_note=False)
        self.accel_z_panel = AccelerometerPanel("Z", show_note=False)
        self.alarm_panel = AlarmPanel()
        self.gesture_summary = GestureSummary()
        self.gesture_panel = GesturePanel()
        self.serial_panel = SerialMonitor(self.controller)
        self.accel_source = SimulatedAccelSource(
            sample_rate_hz=float(self.preferences.simulation_rate_hz)
        )
        self.accel_graph = AccelerometerGraph(source=self.accel_source)
        self.accel_graph.rate_spin.valueChanged.connect(
            self._on_simulation_rate_changed
        )
        self.dashboard_graph = AccelerometerGraph(
            buffer_size=150, source=self.accel_source, compact=True
        )
        self.dashboard_signal_card = Card("Señales X/Y/Z")
        self.dashboard_signal_card.content_layout().addWidget(self.dashboard_graph)
        self.gesture_toast = GestureToast(
            self.accel_graph, anchor=self.accel_graph.plot
        )
        self.accel_source.sample_xyz.connect(self._on_simulated_sample)

        self.gesture_recognizer = GestureRecognizer(
            thresholds=TiltThresholds(
                x_g=self.preferences.threshold_x_g,
                y_g=self.preferences.threshold_y_g,
                z_g=self.preferences.threshold_z_g,
            ),
            window_samples=self.preferences.window_samples,
            hold_samples=self.preferences.hold_samples,
        )
        self.gesture_panel.set_recognition_parameters(
            (
                self.preferences.threshold_x_g,
                self.preferences.threshold_y_g,
                self.preferences.threshold_z_g,
            ),
            self.preferences.window_samples,
        )
        self._gesture_calibrated = False
        self._gesture_has_data = False
        self._last_gesture: str | None = None

        self._dashboard_grid = grid
        self._dashboard_widgets = (
            self.temp_panel,
            self.accel_panel,
            self.accel_y_panel,
            self.accel_z_panel,
            self.alarm_panel,
            self.dashboard_signal_card,
            self.gesture_summary,
            self.serial_panel,
        )
        self._dashboard_compact: bool | None = None
        self._arrange_dashboard()
        self.sidebar.width_changed.connect(self._arrange_dashboard)

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

        self.configuration_page = ConfigurationView(self.preferences)
        self.stack.addWidget(self.configuration_page)

        body_layout.setStretch(1, 1)
        root.addWidget(body, 1)

        self.status_bar = StatusBar()
        root.addWidget(self.status_bar)

        self._section_fade: QPropertyAnimation | None = None
        self.sidebar.section_changed.connect(self._navigate_to_section)
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
        self.configuration_page.preferences_changed.connect(
            self._apply_preferences
        )
        self.configuration_page.reset_baseline_requested.connect(
            self._clear_gesture_baseline
        )
        self.configuration_page.open_recognition_requested.connect(
            lambda: self.sidebar.select_section(2)
        )
        self._button_feedback = [
            ButtonFeedback(button)
            for button in self.findChildren(QAbstractButton)
        ]
        self._refresh_gesture_summary()
        self._refresh_configuration_context()

    def _navigate_to_section(self, index: int) -> None:
        """Cambia de página con un fade breve, solo al navegar."""
        if index == self.stack.currentIndex():
            return
        if self._section_fade is not None:
            self._section_fade.stop()
            self.stack.setGraphicsEffect(None)
            self._section_fade.deleteLater()
            self._section_fade = None

        self.stack.setCurrentIndex(index)
        effect = QGraphicsOpacityEffect(self.stack)
        effect.setOpacity(0.82)
        self.stack.setGraphicsEffect(effect)
        animation = QPropertyAnimation(effect, b"opacity", self)
        animation.setDuration(120)
        animation.setStartValue(0.82)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.OutCubic)

        def finish() -> None:
            if self.stack.graphicsEffect() is effect:
                self.stack.setGraphicsEffect(None)
            if self._section_fade is animation:
                self._section_fade = None
            animation.deleteLater()

        animation.finished.connect(finish)
        self._section_fade = animation
        animation.start()

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
        self.dashboard_graph.set_device_mode(device_mode)
        # No mezclar muestras ni reposo de simulación y dispositivo.
        was_calibrated = self._gesture_calibrated
        self._gesture_has_data = False
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
        self._refresh_configuration_context()
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
        self.dashboard_graph.add_live_sample(
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
        self._refresh_configuration_context()

    def _on_device_status(self, packet) -> None:
        self.temp_panel.set_threshold(packet.threshold_c)
        self._refresh_configuration_context()
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
        self._gesture_has_data = True
        self.gesture_panel.set_live_values(x_g, y_g, z_g)
        # Sin reposo capturado igual se acumulan muestras para poder capturarlo.
        gesture = self.gesture_recognizer.add_sample(x_g, y_g, z_g)
        if not self._gesture_calibrated or gesture is None:
            self._refresh_gesture_summary()
            return
        if gesture != self._last_gesture:
            self._last_gesture = gesture
            self.state.set_gesture(gesture)
        self._refresh_gesture_summary()

    def _on_gesture_changed(self, gesture: str) -> None:
        value = gesture or None
        self.gesture_panel.set_gesture(value)
        self._refresh_gesture_summary()
        self.gesture_toast.show_gesture(value)

    def _refresh_gesture_summary(self) -> None:
        gesture = self.state.data.gesture
        if gesture is not None:
            self.gesture_summary.set_gesture(gesture)
        elif not self._gesture_has_data:
            self.gesture_summary.set_pending(
                "SIN DATOS",
                "Iniciá la simulación o conectá el PIC.",
                WARNING_AMBER,
            )
        elif not self._gesture_calibrated:
            self.gesture_summary.set_pending(
                "SIN CALIBRAR",
                "Capturá el reposo en Reconocimiento.",
                WARNING_AMBER,
            )
        else:
            self.gesture_summary.set_pending(
                "RECONOCIENDO",
                "Esperando una inclinación sostenida.",
                ACCENT_CYAN,
            )

    def _on_gesture_thresholds_changed(self) -> None:
        x_g, y_g, z_g = self.gesture_panel.thresholds()
        self._apply_preferences(
            replace(
                self.preferences,
                threshold_x_g=x_g,
                threshold_y_g=y_g,
                threshold_z_g=z_g,
                window_samples=self.gesture_panel.window_samples(),
            )
        )

    def _on_gesture_baseline_changed(self) -> None:
        x_g, y_g, z_g = self.gesture_panel.baseline()
        self._apply_gesture_baseline(
            TiltBaseline(x_g=x_g, y_g=y_g, z_g=z_g),
            source="Reposo manual",
        )
        self._refresh_configuration_context()

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
        self._refresh_configuration_context()
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

    def _clear_gesture_baseline(self) -> None:
        """Descarta el reposo activo al restaurar las preferencias iniciales."""
        self.gesture_recognizer.clear_baseline()
        self._gesture_calibrated = False
        self._last_gesture = None
        self.state.set_gesture(None)
        self.gesture_panel.reset_baseline()
        self.gesture_panel.set_calibrated(False)
        self.gesture_panel.set_data_unavailable()
        self.gesture_panel.append_log(
            "Reposo activo reiniciado; capturalo nuevamente en Reconocimiento."
        )
        self._refresh_configuration_context()

    def _apply_preferences(self, preferences: GuiPreferences) -> None:
        """Aplica y persiste una única configuración compartida por las vistas."""
        if not isinstance(preferences, GuiPreferences):
            raise TypeError("preferences debe ser GuiPreferences")

        self.preferences_store.save(preferences)
        self.preferences = preferences
        if self.accel_source.sample_rate_hz != preferences.simulation_rate_hz:
            self.accel_source.set_sample_rate(
                float(preferences.simulation_rate_hz)
            )
        for graph in (self.accel_graph, self.dashboard_graph):
            spin = graph.rate_spin
            spin.blockSignals(True)
            spin.setValue(preferences.simulation_rate_hz)
            spin.blockSignals(False)

        self.gesture_recognizer.set_thresholds(
            TiltThresholds(
                x_g=preferences.threshold_x_g,
                y_g=preferences.threshold_y_g,
                z_g=preferences.threshold_z_g,
            )
        )
        self.gesture_recognizer.set_window_samples(
            preferences.window_samples
        )
        self.gesture_recognizer.set_hold_samples(
            preferences.hold_samples
        )
        self.gesture_panel.set_recognition_parameters(
            (
                preferences.threshold_x_g,
                preferences.threshold_y_g,
                preferences.threshold_z_g,
            ),
            preferences.window_samples,
        )
        self.configuration_page.set_preferences(preferences)

    def _on_simulation_rate_changed(self, rate_hz: int) -> None:
        self._apply_preferences(
            replace(self.preferences, simulation_rate_hz=rate_hz)
        )

    def _refresh_configuration_context(self) -> None:
        if not hasattr(self, "configuration_page"):
            return
        baseline = self.gesture_recognizer.baseline
        if baseline is None:
            baseline_values = None
        else:
            data_format = self.state.data.data_format_version
            firmware_version = self.state.data.firmware_version
            z_unavailable = self._device_mode and (
                data_format == 2
                or (data_format is None and firmware_version == 2)
            )
            baseline_values = (
                baseline.x_g,
                baseline.y_g,
                None if z_unavailable else baseline.z_g,
            )
        period_ms = (
            self.state.data.period_ms
            if self.state.data.protocol_version is not None
            else None
        )
        self.configuration_page.set_runtime_context(
            source_name="DISPOSITIVO" if self._device_mode else "SIMULACIÓN",
            device_period_ms=period_ms,
            baseline=baseline_values,
        )

    def _arrange_dashboard(self) -> None:
        """Refluye las tarjetas al ancho compacto sin rediseñar el dashboard."""
        available_width = self.width() - self.sidebar.width()
        compact = available_width < 1080
        if compact == self._dashboard_compact:
            return

        grid = self._dashboard_grid
        for widget in self._dashboard_widgets:
            grid.removeWidget(widget)
        for column in range(5):
            grid.setColumnStretch(column, 0)
        for row in range(4):
            grid.setRowStretch(row, 0)

        if compact:
            grid.addWidget(self.temp_panel, 0, 0)
            grid.addWidget(self.accel_panel, 0, 1)
            grid.addWidget(self.accel_y_panel, 0, 2)
            grid.addWidget(self.accel_z_panel, 1, 0)
            grid.addWidget(self.alarm_panel, 1, 1)
            grid.addWidget(self.gesture_summary, 1, 2)
            grid.addWidget(self.dashboard_signal_card, 2, 0, 1, 3)
            grid.addWidget(self.serial_panel, 3, 0, 1, 3)
            for column in range(3):
                grid.setColumnStretch(column, 1)
            grid.setRowStretch(2, 1)
        else:
            grid.addWidget(self.temp_panel, 0, 0)
            grid.addWidget(self.accel_panel, 0, 1)
            grid.addWidget(self.accel_y_panel, 0, 2)
            grid.addWidget(self.accel_z_panel, 0, 3)
            grid.addWidget(self.alarm_panel, 0, 4)
            grid.addWidget(self.dashboard_signal_card, 1, 0, 1, 3)
            grid.addWidget(self.gesture_summary, 1, 3, 1, 2)
            grid.addWidget(self.serial_panel, 2, 0, 1, 5)
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
        accent.setStyleSheet(
            f"background:{ACCENT_MAGENTA}; border:none;"
        )
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
