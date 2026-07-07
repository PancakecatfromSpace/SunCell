"""
This file wraps the signals for the gui.py user interface into it's own file.
In the main file of this programm the class is called into an object and then the methods of the functions are given to the scheduler.
"""

from PySide6.QtCore import QObject, Signal, Slot
from PySide6 import QtWidgets
import gui
import power_supply_drivers.wrapper as coms

#placed this here temporarily, should be able to be removed later when the connect feature has been added to the GUI

supply = coms.SupplyCommunication("10.30.0.110", lookup = "tti", port = 9221, type="VISA")

class MainDialog(QtWidgets.QDialog):
    """
    This class wraps the gui.py file into a new QDialog, this way the singals and connections can be handled without directly editing gui.py.
    """
    
    def __init__(self, parent = None):
        super().__init__(parent)

        self.ui = gui.Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.voltage_display.value
        measure_signal.measurement_changed.connect(self.on_measurement)
    def on_measurement(self, voltage, current, power):
        self.ui.voltage_display.display(voltage)
        self.ui.current_display.display(current)
        self.ui.power_display.display(power)

class psu_measure_signal(QObject):
    """
    Wraps the call of the 
    """
    measurement_changed = Signal(float, float, float)

    def __init__(self, supply, parent = None):
        super().__init__(parent)
        self.supply = supply

    @Slot()
    def emit_new_values(self):
        self.supply.measureValues()
        voltage = self.supply.measuredpoints.voltage
        current = self.supply.measuredpoints.current
        power = self.supply.measuredpoints.power
        self.measurement_changed.emit(voltage, current, power)

measure_signal = psu_measure_signal(supply)