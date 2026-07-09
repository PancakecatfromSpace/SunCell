"""
This file wraps the signals for the gui.py user interface into it's own file,
contains the wrappers for the functions to be scheduled and how they connect to the UI.
"""

from PySide6.QtCore import QObject, Signal, Slot
from PySide6 import QtWidgets
import gui, curveutils, qt_scheduler
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
        #mode variable saves the state the UI and supply is in
        self.mode = "init"

        self.ui = gui.Ui_Dialog()
        self.ui.setupUi(self)

        # make sure to start on the connection index
        self.ui.option_tabs.setCurrentIndex(0)

        for i in range(self.ui.option_tabs.count()):
            self.ui.option_tabs.setTabEnabled(i, i == 0)

        
        # connect display signals
        measure_signal.measurement_changed.connect(self.on_measurement)
        # connect pushbutton signals
        #connect connection failed or sucessfull signals
        # start with only connect tab enabled
        self._set_tabs_connected(False)
        self._connect_bridge = ConnectBridge(supply)
        self._connect_bridge.connected.connect(self.on_connection_result)

        self.connect_to_supply()
        #on off buttons
        self.ui.curve_on_off.toggled.connect(self.toggle_power_curve_control)
        self.ui.on_botton.toggled.connect(self.toggle_power_curve_control)
    def on_measurement(self, voltage, current, power):
        self.ui.voltage_display.display(voltage)
        self.ui.current_display.display(current)
        self.ui.power_display.display(power)
    def toggle_power_curve_control(self, checked: bool):
        # make sure that both curve_on_off and on_botton have the same status
        sender = self.sender()

        # set the other button without re-triggering
        b1 = self.ui.curve_on_off
        b2 = self.ui.on_botton

        self._sync_block = getattr(self, "_sync_block", False)
        if self._sync_block:
            return

        self._sync_block = True
        try:
            if sender is b1:
                b2.setChecked(checked)
            elif sender is b2:
                b1.setChecked(checked)
        finally:
            self._sync_block = False
        # actually do something when the button is pressed
        measure_signal.turn_on_off(checked)
    def _set_tabs_connected(self, ok: bool):
        for i in range(self.ui.option_tabs.count()):
            self.ui.option_tabs.setTabEnabled(i, (i == 0) or ok)

    @Slot(bool, str)
    def on_connection_result(self, ok: bool, msg: str):
        if not ok:
            self._set_tabs_connected(False)
            return

        self._set_tabs_connected(True)

        sched.add_periodic(
            "measure_set",
            period_s=0.01,
            func=measure_signal.measure_emit_set,
            args=(),
            kwargs={},
            start_immediately=True,
            semaphores=[psu_com],
        )


    def connect_to_supply(self):
        # schedule connect (report result)
        sched.add_periodic(
            "connect",
            period_s=0,
            func=self._connect_bridge.connect_and_report,
            args=(),
            kwargs={},
            start_immediately=True,
            semaphores=[psu_com],
        )

class psu_measure_signal(QObject):
    """
    Wraps the call of the function to measure the supply Values into a class which contains a signal that can be processed by the UI.
    After receiving the Data a signal is send to update the UI.
    Also contains the logic to determine and set the output value.
    """
    measurement_changed = Signal(float, float, float)

    def __init__(self, scheduler, supply, setter, parent = None):
        super().__init__(parent)
        self.supply = supply
        self.setter = setter
        self.scheduler = scheduler

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
    def turn_on_off(self, on:bool):
        # set commands as variable, commands are taken from tti documentation, must be modified if other supply is used
        turn_on = ("OP1 1")
        turn_off = ("OP1 0")
        psu_com = qt_scheduler.semaphore(semaphore_name="psu_com")
        if on:
            self.scheduler.add_periodic(
                "turn_on",
                period_s=0,
                func=self.supply.sendOnly,
                args=(turn_on,),          # only supply is static
                kwargs={},
                start_immediately=True,
                semaphores=[psu_com]
            )
        else:
            self.scheduler.add_periodic(
                "turn_off",
                period_s=0,
                func=self.supply.sendOnly,
                args=(turn_off,),          # only supply is static
                kwargs={},
                start_immediately=True,
                semaphores=[psu_com]
            )

        return

class ConnectBridge(QObject):
    """
    See if the attempt to connect times out and connect it to a signal that can be processed by the UI
    """
    connected = Signal(bool, str)  # (ok, message)

    def __init__(self, supply):
        super().__init__()
        self.supply = supply

    @Slot()
    def connect_and_report(self):
        try:
            # If your supply.connect supports a timeout parameter, use it here.
            # e.g.: self.supply.connect(timeout_s=5)
            self.supply.connect()
            self.connected.emit(True, "")
        except TimeoutError as e:
            self.connected.emit(False, str(e) or "Connection timed out")
        except Exception as e:
            self.connected.emit(False, str(e))

# defines scheduler so it can be accessed at the relevant locations
sched = qt_scheduler.Scheduler(tick_ms=1)
# define semaphores
psu_com = qt_scheduler.semaphore(semaphore_name="psu_com")        
# functions from the before created clases to be added to the scheduler
measure_signal = psu_measure_signal(sched, supply, set_supply)
#wrap the supply into another class that can handle the raised exceptions and signal them to the UI
supply_qt_signals = ConnectBridge(supply)