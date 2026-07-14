"""
This file contains wrapper functions, functions that are mentioned in different parts of the programm get wrapped so they're easily scheduled,
can react to qt signal appropiatly and create their own signals when required.
"""
from PySide6.QtCore import QObject, Signal, Slot
from PySide6 import QtWidgets
import gui, curveutils, qt_scheduler
import power_supply_drivers.wrapper as coms

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

        self.scheduling.on_off(on)

        return
    def set_values_manual(self, voltage, current, power):
        #logic to delete job for running it all continousely and set voltage manually
        #print("Setting values Manually.")
        #this is an unholy hack, but it'll work fine, probably, basically "throw the measure set job out" and "add job that only measures"

        self.scheduling.measure_manual(voltage=voltage, current=current, power=power)
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
            self.scheduler.remove_job("turn_off")
            self.scheduler.add_periodic(
                "turn_on",
                period_s=0.5,
                func=self.supply.sendOnly,
                args=(turn_on,),          # only supply is static
                kwargs={},
                start_immediately=True,
                semaphores=[self.psu_com]
            )
        else:
            self.scheduler.remove_job("turn_on")
            self.scheduler.add_periodic(
                "turn_off",
                period_s=0.5,
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

    def measure_manual(self, voltage, current, power):
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