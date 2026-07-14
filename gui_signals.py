"""
This file wraps the signals for the gui.py user interface into it's own file,
contains the wrappers for the functions to be scheduled and how they connect to the UI.
"""

from PySide6.QtCore import QObject, Signal, Slot
from PySide6 import QtWidgets
import gui, curveutils, qt_scheduler
import power_supply_drivers.wrapper as coms

#placed this here temporarily, should be able to be removed later when the connect feature has been added to the GUI
supply = coms.SupplyCommunication("10.30.0.111", lookup = "tti", port = 9221, type="VISA")

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
    
    def __init__(self,scheduling,parent = None ):
        super().__init__(parent)
        #safe the scheduling wrapper class as attribute
        self.scheduling = scheduling

        #mode variable saves the state the UI and supply is in
        self.mode = "init"

        self.ui = gui.Ui_Dialog()
        self.ui.setupUi(self)

        # make sure to start on the connection index
        self.ui.option_tabs.setCurrentIndex(0)

        for i in range(self.ui.option_tabs.count()):
            self.ui.option_tabs.setTabEnabled(i, i == 0)

        
        # connect display signals
        self.scheduling.measure_signal.measurement_changed.connect(self.on_measurement)
        # connect pushbutton signals
        #connect connection failed or sucessfull signals
        # start with only connect tab enabled
        self._set_tabs_connected(False)
        self._connect_bridge = self.scheduling.connect_bridge
        self._connect_bridge.connected.connect(self.on_connection_result)
        self.ui.connect_button.clicked.connect(self.connect_to_supply)
        #on off buttons
        self.ui.curve_on_off.toggled.connect(self.toggle_power_curve_control)
        self.ui.on_botton.toggled.connect(self.toggle_power_curve_control)
        #apply buttons
        self.ui.apply_button.clicked.connect(self.apply_manual)
        #text input fields for IP and Port
        self.ip_address = None
        self.port = None
        self.ui.ip_address_field.textChanged.connect(self.handle_ip_port_input)
        self.ui.port_field.textChanged.connect(self.handle_ip_port_input)
        #text input fields for voltage, current and power
        self.voltage = None
        self.current = None
        self.power = None
        self.ui.input_field_voltage.textChanged.connect(self.handle_voltage_current_power_input)
        self.ui.input_field_current.textChanged.connect(self.handle_voltage_current_power_input)
        self.ui.input_field_power.textChanged.connect(self.handle_voltage_current_power_input)
        # dials
        #set max values to dials
        self.ui.voltage_dial.setMaximum(self.scheduling.measure_signal.supply.valuelimits.MAX_VOLT)
        self.ui.current_dial.setMaximum(self.scheduling.measure_signal.supply.valuelimits.MAX_CUR)
        self.ui.power_dial.setMaximum(self.scheduling.measure_signal.supply.valuelimits.MAX_POWER)
        #connect changed dial value to something meaningful
        self.ui.voltage_dial.valueChanged.connect(self.handle_voltage_current_power_dial)
        self.ui.current_dial.valueChanged.connect(self.handle_voltage_current_power_dial)
        self.ui.power_dial.valueChanged.connect(self.handle_voltage_current_power_dial)
    def on_measurement(self, voltage, current, power):
        """
        Handles the update of the LCD Displays at the top of the screen.
        """
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
        self.scheduling.measure_signal.turn_on_off(checked)
    def _set_tabs_connected(self, ok: bool):
        for i in range(self.ui.option_tabs.count()):
            self.ui.option_tabs.setTabEnabled(i, (i == 0) or ok)

    @Slot(bool, str)
    def on_connection_result(self, ok: bool, msg: str):
        """
        Deals with the result of attempting to set up the connection. If the connection is succesfull start measuring the outputs of the supply and enable
        the other tabs within the UI. 
        """
        if not ok:
            self._set_tabs_connected(False)
            return

        self._set_tabs_connected(True)
        """
        sched.add_periodic(
            "measure_set",
            period_s=0.01,
            func=measure_signal.measure_emit_set,
            args=(),
            kwargs={},
            start_immediately=True,
            semaphores=[psu_com],
        )
        """
        self.scheduling.measure()
        


    def connect_to_supply(self):
        # schedule connect (report result)
        #print(self.ip_address)
        """
        sched.add_periodic(
            "connect",
            period_s=0,
            func=self._connect_bridge.connect_and_report,
            args=(self.ip_address, self.port,),
            kwargs={},
            start_immediately=True,
            semaphores=[psu_com],
        )
        """
        scheduling.connect(self.ip_address, self.port)
        #print(self._connect_bridge.supply.socketvalues)
    def handle_ip_port_input(self):
        """
        Handles the signals sent by editing the values for Port and IP Address.
        """
        self.ip_address = self.ui.ip_address_field.text()
        self.port = self.ui.port_field.text()
        #print(self.ip_address)
    def handle_voltage_current_power_input(self):
        """
        Takes the text created by entering values into the fields for voltage current and power in the Manual tab.
        """
        self.voltage = float(self.ui.input_field_voltage.text())
        self.current = float(self.ui.input_field_current.text())
        self.power = float(self.ui.input_field_power.text())
    def handle_voltage_current_power_dial(self):
        self.voltage = float(self.ui.voltage_dial.value())
        self.current = float(self.ui.current_dial.value())
        self.power = float(self.ui.power_dial.value())
        return
    @Slot()
    def apply_manual(self):
        """
        Deal with what to do when the apply button in the manual tab is pressed. Basically: throw out the measure_set task so the supply stops 
        simulating a solar array and start to measure only.
        """

        
        #send out manual values
        scheduling.measure_signal.set_values_manual(self.voltage, self.current, self.power)
        #set the dials to the values put into the text fields
        self.ui.voltage_dial.setValue(int(self.voltage))
        self.ui.current_dial.setValue(int(self.current))
        self.ui.power_dial.setValue(int(self.power))
        #set the text tields to the values put in by the dials
        self.ui.input_field_voltage.setText(str(self.voltage))
        self.ui.input_field_current.setText(str(self.current))
        self.ui.input_field_power.setText(str(self.power))

class psu_measure_signal(QObject):
    """
    Wraps the call of the function to measure the supply Values into a class which contains a signal that can be processed by the UI.
    After receiving the Data a signal is send to update the UI.
    Also contains the logic to determine and set the output value.
    """
    measurement_changed = Signal(float, float, float)

    def __init__(self, scheduling, supply, setter, parent = None):
        super().__init__(parent)
        self.supply = supply
        self.setter = setter
        self.scheduling = scheduling

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
        """
        Defines the necessary commands for turning the supply on and off and schedules them accordingly.
        """
        """
        # set commands as variable, commands are taken from tti documentation, must be modified if other supply is used
        turn_on = ("OP1 1")
        turn_off = ("OP1 0")
        psu_com = qt_scheduler.semaphore(semaphore_name="psu_com")
        if on:
            self.scheduling.scheduler.add_periodic(
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
        """
        scheduling.on_off(on)

        return
    def set_values_manual(self, voltage, current, power):
        #logic to delete job for running it all continousely and set voltage manually
        #print("Setting values Manually.")
        #this is an unholy hack, but it'll work fine, probably, basically "throw the measure set job out" and "add job that only measures"
        """
        sched.remove_job("measure_set")
        
        sched.add_periodic(
            'measure',
            period_s=0.01,
            func=measure_signal.emit_new_values,
            args=(),
            kwargs={},
            start_immediately=True,
            semaphores=[psu_com],
        )
        self.scheduler.remove_job("set_values")
        self.scheduler.add_periodic(
                "set_values",
                period_s=0.5,
                func=self.supply.setValues,
                args=(voltage,current,power,),          # only supply is static
                kwargs={},
                start_immediately=True,
                semaphores=[psu_com]
            )
        """
        scheduling.measure_manual(voltage, current, power)
        #print(self.supply.setpoints)


class ConnectBridge(QObject):
    """
    See if the attempt to connect times out and connect it to a signal that can be processed by the UI. Used to determine weather the other tabs should be
    enabled or remain grayed out.
    """
    connected = Signal(bool, str)  # (ok, message)

    def __init__(self, supply):
        super().__init__()
        self.supply = supply

    @Slot()
    def connect_and_report(self, ip, port):
        print("Attempting to connect...")
        try:
            # If your supply.connect supports a timeout parameter, use it here.
            # e.g.: self.supply.connect(timeout_s=5)
            if ip is not None:
                self.supply.socketvalues.SUPPLY_IP = ip
            if port is not None:
                self.supply.socketvalues.SUPPLY_PORT = port
            self.supply.connect()
            self.connected.emit(True, "")
        except TimeoutError as e:
            self.connected.emit(False, str(e) or "Connection timed out")
        except Exception as e:
            self.connected.emit(False, str(e))
        print(self.supply.socketvalues)

class scheduling():
    """
    This class wraps all scheduling tasks. Some jobs cannot run while other jobs are running, for example the measure_set function can never run at the
    same time as the measure job.
    """
    def __init__(self, supply:coms.SupplyCommunication, setter:curveutils.setter, tick_ms:int = 1):
        self.scheduler = qt_scheduler.Scheduler(tick_ms=tick_ms)
        self.psu_com = qt_scheduler.semaphore(semaphore_name="psu_com")
        self.supply = supply
        self.measure_signal = psu_measure_signal(self, self.supply, setter)
        self.connect_bridge = ConnectBridge(self.supply)
    def connect(self, ip_address:str, port:int):
        """
        Scheduler the connect job to connect the power supply.
        Args:
        ip_address(str): IP Adress to connect the supply to.
        port(int): port to connect the supply to.
        """
        self.scheduler.add_periodic(
            "connect",
            period_s=0,
            func=self.connect_bridge.connect_and_report,
            args=(ip_address, port,),
            kwargs={},
            start_immediately=True,
            semaphores=[self.psu_com],
        )
    def on_off(self, on:bool):
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
                semaphores=[self.psu_com]
            )
        else:
            self.scheduler.add_periodic(
                "turn_off",
                period_s=0,
                func=self.supply.sendOnly,
                args=(turn_off,),          # only supply is static
                kwargs={},
                start_immediately=True,
                semaphores=[self.psu_com]
            )
    def measure(self):
        """
        Sets only the job that measures and updates the UI
        """
        self.scheduler.remove_job("measure_set")
        self.scheduler.remove_job("set_values")

        self.scheduler.add_periodic(
            name="measure",
            period_s=0.01,
            func=self.measure_signal.emit_new_values,
            semaphores=[self.psu_com],
            start_immediately=True,
        )

    def measure_manual(self, voltage:float, current:float, power:float):
        """
        Delete the measure_set job and start the measuring job before creating the set_values job setting the currently given values for manual control.
        """
        self.scheduler.remove_job("measure_set")
        
        self.scheduler.add_periodic(
            'measure',
            period_s=0.01,
            func=self.measure_signal.emit_new_values,
            args=(),
            kwargs={},
            start_immediately=True,
            semaphores=[self.psu_com],
        )
        self.scheduler.remove_job("set_values")
        self.scheduler.add_periodic(
            "set_values",
            period_s=0.5,
            func=self.supply.setValues,
            args=(voltage,current,power,),          # only supply is static
            kwargs={},
            start_immediately=True,
            semaphores=[self.psu_com]
        )


# defines scheduler so it can be accessed at the relevant locations
#sched = qt_scheduler.Scheduler(tick_ms=1)
#measure_signal = psu_measure_signal(scheduling.scheduler, supply, set_supply)
scheduling = scheduling(supply, set_supply)
# define semaphores
       
# functions from the before created clases to be added to the scheduler
