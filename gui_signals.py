"""
This file wraps the signals for the gui.py user interface into it's own file,
contains the wrappers for the functions to be scheduled and how they connect to the UI.
"""

from PySide6.QtCore import QObject, Signal, Slot
from PySide6 import QtWidgets
import gui, curveutils, qt_scheduler, qt_wrapper
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
        self.ui.apply_3d_preview_button.clicked.connect(self.apply_diode_model)
        #reset diode model button
        self.ui.reset_diode_modell.clicked.connect(self.reset_diode_model)
        # Text input fields
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
        # safe the values as reasonable standard values
        self.cell_p_standard = 4
        self.cell_s_standard = 50
        self.i_s_standard = 8.75e-3
        self.m_standard =  4.0
        self.u_t_standard = 25.7e-3
        self.c_0_standard = 3e-3
        #text input fields for diode model related parameters
        self.cell_p = self.cell_p_standard
        self.cell_s = self.cell_s_standard
        self.i_s = self.i_s_standard
        self.m =  self.m_standard
        self.u_t = self.u_t_standard
        self.c_0 = self.c_0_standard
        self.ui.cells_parralel_input_field.textChanged.connect(self.handle_diode_model_fields)
        self.ui.cells_parralel_input_field.setText(str(self.cell_p))
        self.ui.cells_series_input_field.textChanged.connect(self.handle_diode_model_fields)
        self.ui.cells_series_input_field.setText(str(self.cell_s))
        self.ui.saturation_current_input_field.textChanged.connect(self.handle_diode_model_fields)
        self.ui.saturation_current_input_field.setText(str(self.i_s*1000))
        self.ui.diodefactor_input_field.textChanged.connect(self.handle_diode_model_fields)
        self.ui.diodefactor_input_field.setText(str(self.m*10))
        self.ui.thermalvoltage_input_field.textChanged.connect(self.handle_diode_model_fields)
        self.ui.thermalvoltage_input_field.setText(str(self.u_t*1000))
        self.ui.photo_current_coefficient_input_field.textChanged.connect(self.handle_diode_model_fields)
        self.ui.photo_current_coefficient_input_field.setText(str(self.c_0*1000))
        # dials
        #set max values to dials
        self.ui.voltage_dial.setMaximum(self.scheduling.measure_signal.supply.valuelimits.MAX_VOLT)
        self.ui.current_dial.setMaximum(self.scheduling.measure_signal.supply.valuelimits.MAX_CUR)
        self.ui.power_dial.setMaximum(self.scheduling.measure_signal.supply.valuelimits.MAX_POWER)
        #connect changed dial value to something meaningful
        self.ui.voltage_dial.valueChanged.connect(self.handle_voltage_current_power_dial)
        self.ui.current_dial.valueChanged.connect(self.handle_voltage_current_power_dial)
        self.ui.power_dial.valueChanged.connect(self.handle_voltage_current_power_dial)
        # sliders
        #sliders for diode model
        self.ui.cells_parralel_input_slider.setValue(self.cell_p)
        self.ui.cells_parralel_input_slider.valueChanged.connect(self.handle_diode_model_sliders)

        self.ui.cells_series_input_slider.setValue(self.cell_s)
        self.ui.cells_series_input_slider.valueChanged.connect(self.handle_diode_model_sliders)

        self.ui.saturation_current_input_slider.setValue(int(self.i_s*100e3))
        self.ui.saturation_current_input_slider.valueChanged.connect(self.handle_diode_model_sliders)

        self.ui.diodefactor_input_slider.setValue(int(self.m*10))
        self.ui.diodefactor_input_slider.valueChanged.connect(self.handle_diode_model_sliders)

        self.ui.thermalvoltage_input_slider.setValue(int(self.u_t*10000))
        self.ui.thermalvoltage_input_slider.valueChanged.connect(self.handle_diode_model_sliders)

        self.ui.photo_current_coefficient_input_slider.setValue(int(self.c_0*100e3))
        self.ui.photo_current_coefficient_input_slider.valueChanged.connect(self.handle_diode_model_sliders)
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

        self.scheduling.measure()

    def connect_to_supply(self):

        scheduling.connect(self.ip_address, self.port)
        
    def handle_ip_port_input(self):
        """
        Handles the signals sent by editing the values for Port and IP Address.
        """
        self.ip_address = self.ui.ip_address_field.text()
        self.port = self.ui.port_field.text()
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
    def handle_diode_model_fields(self, update:bool=True):
        """
        Handles the diode model input fields. Can be run as an update or not. If run as an update the values displayed will be updated while ignoring 
        currently set values.
        """
        if update:
            try:
                self.cell_p = int(self.ui.cells_parralel_input_field.text())
                self.cell_s = int(self.ui.cells_series_input_field.text())
                self.i_s = float(self.ui.saturation_current_input_field.text()) / 1e3
                self.m =  float(self.ui.diodefactor_input_field.text())
                self.u_t = float(self.ui.thermalvoltage_input_field.text()) / 1e3
                self.c_0 = float(self.ui.photo_current_coefficient_input_field.text()) / 1e3
            except:
                self.cell_p = self.cell_p_standard
                self.cell_s = self.cell_s_standard
                self.i_s = self.i_s_standard
                self.m =  self.m_standard
                self.u_t = self.u_t_standard
                self.c_0 = self.c_0_standard

        self.ui.cells_parralel_input_slider.setValue(self.cell_p)
        self.ui.cells_series_input_slider.setValue(self.cell_s)
        self.ui.saturation_current_input_slider.setValue(int(self.i_s*100e3))
        self.ui.diodefactor_input_slider.setValue(int(self.m*10))
        self.ui.thermalvoltage_input_slider.setValue(int(self.u_t*10e3))
        self.ui.photo_current_coefficient_input_slider.setValue(int(self.c_0*100e3))
    def handle_diode_model_sliders(self, update:bool=True):
        """
        Handles the diode model sliders. Can be run to read the input and update the values or it can be run so that the values won't be changed and instead 
        the displays get set to the called for value.
        """
        if update:
            self.cell_p = int(self.ui.cells_parralel_input_slider.value())
            self.cell_s = int(self.ui.cells_series_input_slider.value())
            self.i_s = float(self.ui.saturation_current_input_slider.value()) / 1e5
            self.m = float(self.ui.diodefactor_input_slider.value()) / 10
            self.u_t = float(self.ui.thermalvoltage_input_slider.value()) / 1e4
        #cells parallel
        self.ui.cells_parralel_input_field.setText(str(self.cell_p))
        #cells series
        self.ui.cells_series_input_field.setText(str(self.cell_s))
        #saturation current
        self.ui.saturation_current_input_field.setText(str(self.i_s*100e3))
        #diodefactor
        self.ui.diodefactor_input_field.setText(str(self.m*100))
        #thermalvoltage
        self.ui.thermalvoltage_input_field.setText(str(self.u_t*1e4))
        #photo current coefficient
        self.c_0 = float(self.ui.photo_current_coefficient_input_slider.value()) / 1e5
        self.ui.photo_current_coefficient_input_field.setText(str(self.c_0*100e3))
        #print("The raw unformatted input of the field is:", self.ui.cells_parralel_input_slider.value())
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
    def apply_diode_model(self):
        U_1, I_1 = curveutils.solarIV(self.cell_p, self.cell_s, self.i_s, self.m, self.u_t, self.c_0, 1000, 10000)
        #prepare data before running the controll algorithm, removes too low 
        U_1, I_1 = curveutils.min_remover(U_1, I_1, 5)
        U_1, I_1 = curveutils.stepsize_reducer(list(U_1), list(I_1), 0.025, 'right')
        self.scheduling.measure_signal.setter = curveutils.setter(U_1, I_1)
        self.scheduling.measure_set_diode_model()
    def reset_diode_model(self):
        """
        Handles the reset button on the Diode Model tab.
        Sets back to standard values, triggers handle for updating related fields and sliders
        """
        self.cell_p = self.cell_p_standard
        self.cell_s = self.cell_s_standard
        self.i_s = self.i_s_standard
        self.m =  self.m_standard
        self.u_t = self.u_t_standard
        self.c_0 = self.c_0_standard
        self.handle_diode_model_fields(update=False)
        self.handle_diode_model_sliders(update=False)

# defines scheduler so it can be accessed at the relevant locations
scheduling = qt_wrapper.scheduling(supply, set_supply)
