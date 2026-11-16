"""Pruebas básicas de importación e instanciación de componentes UI."""

from PySide6.QtWidgets import QApplication

from hand_motion.communication.protocol import DataPacket
from hand_motion.core.controller import AppController
from hand_motion.core.state import AppState
from hand_motion.preferences import GuiPreferencesStore
from hand_motion.ui.widgets.sensor_card import SensorCard
from hand_motion.ui.widgets.connection_indicator import ConnectionIndicator
from hand_motion.ui.widgets.temperature_indicator import TemperatureIndicator
from hand_motion.ui.widgets.accelerometer_panel import AccelerometerPanel
from hand_motion.ui.widgets.accelerometer_graph import AccelerometerGraph
from hand_motion.ui.widgets.alarm_panel import AlarmPanel
from hand_motion.ui.widgets.serial_monitor import SerialMonitor
from hand_motion.ui.widgets.status_bar import StatusBar
from hand_motion.ui.main_window import MainWindow
from preferences_helpers import MemorySettings


def test_components_instantiate() -> None:
    app = QApplication([])
    controller = AppController(AppState())
    main_window = MainWindow(
        preferences_store=GuiPreferencesStore(MemorySettings())
    )
    widgets = [
        SensorCard("T", "1", "u", "ok"),
        ConnectionIndicator(),
        TemperatureIndicator(),
        AccelerometerPanel(),
        AccelerometerGraph(),
        AlarmPanel(),
        SerialMonitor(controller),
        StatusBar(),
        main_window,
    ]
    assert all(w is not None for w in widgets)
    assert main_window.stack.count() == 4
    assert [button.toolTip() for button in main_window.sidebar._buttons] == [
        "Dashboard",
        "Adquisición",
        "Reconocimiento",
        "Configuración",
    ]
    main_window._set_mode(True)
    assert main_window.accel_y_panel._card.value_label.text() == "--"
    main_window.state.set_data_packet(DataPacket(1, 25, -250, 125, False, 0))
    assert main_window.accel_panel._card.value_label.text() == "-0.250 g"
    assert main_window.accel_y_panel._card.value_label.text() == "+0.125 g"
    assert "Y: +0.125 g" in main_window.accel_graph.last_value_label.text()
    main_window.close()
    main_window.controller.close()
    controller.close()
    app.quit()
