"""Pruebas básicas de importación e instanciación de componentes UI."""

from PySide6.QtWidgets import QApplication

from hand_motion.ui.widgets.sensor_card import SensorCard
from hand_motion.ui.widgets.connection_indicator import ConnectionIndicator
from hand_motion.ui.widgets.temperature_indicator import TemperatureIndicator
from hand_motion.ui.widgets.accelerometer_panel import AccelerometerPanel
from hand_motion.ui.widgets.accelerometer_graph import AccelerometerGraph
from hand_motion.ui.widgets.alarm_panel import AlarmPanel
from hand_motion.ui.widgets.serial_monitor import SerialMonitor
from hand_motion.ui.widgets.status_bar import StatusBar
from hand_motion.ui.main_window import MainWindow


def test_components_instantiate() -> None:
    app = QApplication([])
    widgets = [
        SensorCard("T", "1", "u", "ok"),
        ConnectionIndicator(),
        TemperatureIndicator(),
        AccelerometerPanel(),
        AccelerometerGraph(),
        AlarmPanel(),
        SerialMonitor(),
        StatusBar(),
        MainWindow(),
    ]
    assert all(w is not None for w in widgets)
    app.quit()