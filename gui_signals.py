"""
This file wraps the signals for the gui.py user interface into it's own file,
contains the wrappers for the functions to be scheduled and how they connect to the UI.
"""

from PySide6.QtCore import QObject, Signal, Slot
from PySide6 import QtWidgets
import gui, curveutils
import power_supply_drivers.wrapper as coms

#placed this here temporarily, should be able to be removed later when the connect feature has been added to the GUI
supply = coms.SupplyCommunication("10.30.0.110", lookup = "tti", port = 9221, type="VISA")
#placed this here temporarily, should be able to be removed later when the features for editing the values has been added to the GUI
#create two vectors and populate them with the values from a one diode model
U_1, I_1 = curveutils.solarIV(4, 50, 8.75e-3, 4.0, 25.7e-3, 3e-3, 1000, 10000)
#prepare data before running the controll algorithm, removes too low 
U_1, I_1 = curveutils.min_remover(U_1, I_1, 5)
U_1, I_1 = curveutils.stepsize_reducer(list(U_1), list(I_1), 0.025, 'right')
set_supply = curveutils.setter(U_1, I_1)


class MainDialog(QtWidgets.QDialog):
    """
    This class wraps the gui.py file into a new QDialog, this way the singals and connections can be handled without directly editing gui.py.
    """
    
    def __init__(self, parent = None):
        super().__init__(parent)

        self.ui = gui.Ui_Dialog()
        self.ui.setupUi(self)
        #eddited the value of the initial voltage to 5, by suggestion by Rüdiger Mann 27.04.26, stub left here as initial thing to run
        #kinda out of place here, best to be removed later since it relies on I_1 being available in the namespace of the class definition
        supply.setValues(5, I_1.max()*1.1, 3000.0)

        self.ui.voltage_display.value
        measure_signal.measurement_changed.connect(self.on_measurement)
    def on_measurement(self, voltage, current, power):
        self.ui.voltage_display.display(voltage)
        self.ui.current_display.display(current)
        self.ui.power_display.display(power)

class psu_measure_signal(QObject):
    """
    Wraps the call of the function to measure the supply Values into a class which contains a signal that can be processed by the UI.
    After receiving the Data a signal is send to update the UI.
    Also contains the logic to determine and set the output value.
    """
    measurement_changed = Signal(float, float, float)

    def __init__(self, supply, setter, parent = None):
        super().__init__(parent)
        self.supply = supply
        self.setter = setter

    @Slot()
    def emit_new_values(self):
        """
        Sets the measurement_changed signal and emits the signal to update the UI
        """
        self.supply.measureValues()
        voltage = self.supply.measuredpoints.voltage
        current = self.supply.measuredpoints.current
        power = self.supply.measuredpoints.power
        self.measurement_changed.emit(voltage, current, power)
    def determine_set_output(self):
        """
        Takes the measured values stored within the supply object and uses them to determine the next value to set for the power supply 
        before sending the results to the supply.
        """
        self.supply.setValues(self.setter.u_for_i_incremental(self.supply.measuredpoints.current))
        return
    def measure_emit_set(self):
        """
        Measures the values from the supply, emits the signal to the UI to update the Display 
        """
        self.emit_new_values()
        self.determine_set_output()
        
# functions from the before created clases to be added to the scheduler
measure_signal = psu_measure_signal(supply, set_supply)