"""
This file wraps the signals for the gui.py user interface into it's own file,
contains the wrappers for the functions to be scheduled and how they connect to the UI.
"""

from PySide6.QtCore import QObject, Signal, Slot, QSignalBlocker, Qt, QEvent
from PySide6 import QtWidgets
from PySide6.QtGui import QVector3D
import gui, curveutils, qt_scheduler, qt_wrapper
import power_supply_drivers.wrapper as coms
import time
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np

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
        # disable all non connection related tabs
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
        self.ip_address = self.scheduling.supply.socketvalues.SUPPLY_IP
        self.ui.ip_address_field.setText(self.ip_address)
        self.port = self.scheduling.supply.socketvalues.SUPPLY_PORT
        self.ui.port_field.setText(str(self.port))
        self.ui.ip_address_field.textChanged.connect(self.handle_ip_port_input)
        self.ui.port_field.textChanged.connect(self.handle_ip_port_input)
        #text input fields for voltage, current and power
        self.voltage = 0.0
        self.current = 0.0
        self.power = 0.0
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
        self.irradiance_standard = 1000
        self.cell_p = self.cell_p_standard
        self.cell_s = self.cell_s_standard
        self.i_s = self.i_s_standard
        self.m =  self.m_standard
        self.u_t = self.u_t_standard
        self.c_0 = self.c_0_standard
        self.irradiance = self.irradiance_standard
        #text input fields for diode model related parameters
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
        self.ui.irradiance_input_field.textChanged.connect(self.handle_irradiance_field)
        self.ui.irradiance_input_field.setText(str(self.irradiance))
        # dials
        #set max values to dials
        self.ui.voltage_dial.setMaximum(self.scheduling.measure_signal.supply.valuelimits.MAX_VOLT)
        self.ui.current_dial.setMaximum(self.scheduling.measure_signal.supply.valuelimits.MAX_CUR)
        self.ui.power_dial.setMaximum(self.scheduling.measure_signal.supply.valuelimits.MAX_VOLT * self.scheduling.measure_signal.supply.valuelimits.MAX_CUR)
        #connect changed dial value to something meaningful
        self.ui.voltage_dial.valueChanged.connect(self.handle_voltage_current_power_dial)
        self.ui.current_dial.valueChanged.connect(self.handle_voltage_current_power_dial)
        self.ui.power_dial.valueChanged.connect(self.handle_voltage_current_power_dial)
        #since the tti supply has no concept of maximum power the power dial has no function, it is therefore disabled
        self.ui.power_dial.setEnabled(False)
        self.ui.input_field_power.setEnabled(False)
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

        
        self.ui.irradiance_dial.setValue(int(self.irradiance))
        self.ui.irradiance_dial.valueChanged.connect(self.handle_irradiance_dial)
        #initialize the whole_day function as an attribute
        self.whole_day = curveutils.whole_day_dict(self.cell_p, self.cell_s, self.i_s, self.m, self.u_t, self.c_0,10000,0,1000,10)
        #initialize setter for one voltage and currents array so that setter can be initalized once and receive new values later
        U_1, I_1 = self.whole_day.return_for_irradiance(int(self.irradiance))
        self.scheduling.measure_signal.setter = curveutils.setter(U_1, I_1)
        self.values_3d_plot = self.whole_day.data_as_array()
        #add the 3D plot on the Diode Model page
        self.setup_3d_plot(self.ui.placeholder_3d_view)
        #self.setup_3d_plot(self.ui.placeholder_3d_view)
        self.iv_plot = IVCurvePlot(dash_every=10, parent=self)

        self.embed_plot_fixed_to_placeholder(self.ui.placeholder_2d_view, self.iv_plot)

        self.iv_plot.update_curve(U_1, I_1)
        self.iv_plot.update_points(self.scheduling.measure_signal.setter._max_power_point.voltage, self.scheduling.measure_signal.setter._max_power_point.current, 0.0,0.0)
    
    def embed_plot_fixed_to_placeholder(self, placeholder: QtWidgets.QWidget, plot: QtWidgets.QWidget):
        # Ensure we start with a clean layout situation
        old_layout = placeholder.layout()
        if old_layout is not None:
            # zero margins/spacing no matter what it is
            if hasattr(old_layout, "setContentsMargins"):
                old_layout.setContentsMargins(0, 0, 0, 0)
            if hasattr(old_layout, "setSpacing"):
                old_layout.setSpacing(0)
            # clear existing items
            while old_layout.count():
                item = old_layout.takeAt(0)
                w = item.widget()
                if w is not None:
                    w.setParent(None)

        # If there was no layout in Designer, create one
        if placeholder.layout() is None:
            layout = QtWidgets.QGridLayout(placeholder)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            placeholder.setLayout(layout)
        else:
            layout = placeholder.layout()

        # Force the plot widget to be EXACTLY placeholder-sized
        plot.setParent(placeholder)

        plot.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        plot.setMinimumSize(placeholder.size())
        plot.setMaximumSize(placeholder.size())
        plot.resize(placeholder.size())

        # Put plot into layout cell (0,0) only
        layout.addWidget(plot, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)

        # Keep it in sync when the dialog resizes
        class ResizeFilter(QObject):
            def eventFilter(self, obj, event):
                if obj is placeholder and event.type() == QEvent.Type.Resize:
                    s = placeholder.size()
                    plot.setMinimumSize(s)
                    plot.setMaximumSize(s)
                    plot.resize(s)
                return super().eventFilter(obj, event)

        placeholder.installEventFilter(ResizeFilter(placeholder))

    def on_measurement(self, voltage, current, power):
        """
        Handles the update of the LCD Displays at the top of the screen.
        """
        self.ui.voltage_display.display(voltage)
        self.ui.current_display.display(current)
        self.ui.power_display.display(power)

        self.iv_plot.update_points(self.scheduling.measure_signal.setter._max_power_point.voltage, self.scheduling.measure_signal.setter._max_power_point.current, voltage,current)

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
            print("Error! Connection Failed.")
            self._set_tabs_connected(False)
            self.show_connection_failed_dialog()
            return
        self.ui.connect_button.setEnabled(False)
        self.ui.ip_address_field.setEnabled(False)
        self.ui.port_field.setEnabled(False)
        self.scheduling.init()
        self._set_tabs_connected(True)
        self.ui.option_tabs.setCurrentIndex(1)

        self.scheduling.measure()

    def connect_to_supply(self):

        scheduling.connect(self.ip_address, self.port)
        self.set_active_irradiance(100)
        
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
        self.power = self.voltage * self.current 

        self.ui.voltage_dial.setValue(int(self.voltage))
        self.ui.current_dial.setValue(int(self.current))
        self.ui.power_dial.setValue(int(self.power))
    def handle_voltage_current_power_dial(self):
        self.voltage = float(self.ui.voltage_dial.value())
        self.current = float(self.ui.current_dial.value())
        self.power = float(self.ui.power_dial.value())

        self.ui.input_field_voltage.setText(str(self.voltage))
        self.ui.input_field_current.setText(str(self.current))
        self.ui.input_field_power.setText(str(self.power))
    def handle_diode_model_fields(self, update:bool=True):
        """
        Handles the diode model input fields. Can be run as an update or not. If run as an update the values displayed will be updated while ignoring 
        currently set values within the input text field.
        """
        if update:
            try:
                self.cell_p = int(self.ui.cells_parralel_input_field.text())
                self.cell_s = int(self.ui.cells_series_input_field.text())
                self.i_s = float(self.ui.saturation_current_input_field.text()) / 1e3
                self.m =  float(self.ui.diodefactor_input_field.text())
                self.u_t = float(self.ui.thermalvoltage_input_field.text()) / 1e3
                self.c_0 = float(self.ui.photo_current_coefficient_input_field.text()) / 1e3
                self.irradiance = int(float(self.ui.irradiance_input_field.text()))

                #self.irradiance = int(self.ui.irradiance_input_field.text())
            except:
                self.cell_p = self.cell_p_standard
                self.cell_s = self.cell_s_standard
                self.i_s = self.i_s_standard
                self.m =  self.m_standard
                self.u_t = self.u_t_standard
                self.c_0 = self.c_0_standard

                #self.irradiance = self.irradiance_standard

        self.ui.cells_parralel_input_slider.setValue(self.cell_p)
        self.ui.cells_series_input_slider.setValue(self.cell_s)
        self.ui.saturation_current_input_slider.setValue(int(self.i_s*100e3))
        self.ui.diodefactor_input_slider.setValue(int(self.m*10))
        self.ui.thermalvoltage_input_slider.setValue(int(self.u_t*10e3))
        self.ui.photo_current_coefficient_input_slider.setValue(int(self.c_0*100e3))

        self.ui.irradiance_dial.setValue(int(self.irradiance) / 10) 
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
            self.c_0 = float(self.ui.photo_current_coefficient_input_slider.value()) / 1e5

            self.irradiance = int(self.ui.irradiance_dial.value()) * 10
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
        self.ui.photo_current_coefficient_input_field.setText(str(self.c_0*100e3))

        #irradiance
        self.ui.irradiance_input_field.setText(str(self.irradiance))
        #print("The raw unformatted input of the field is:", self.ui.cells_parralel_input_slider.value())
        #reenable the apply button when a value has changed
        self.ui.apply_3d_preview_button.setEnabled(True)
    @Slot()
    def apply_manual(self):
        """
        Deal with what to do when the apply button in the manual tab is pressed. Basically: throw out the measure_set task so the supply stops 
        simulating a solar array and start to measure only.
        """
        #send out manual values
        scheduling.measure_signal.set_values_manual(self.voltage, self.current, self.power)
        #set the dials to the values put into the text fields
        """
        self.ui.voltage_dial.setValue(int(self.voltage))
        self.ui.current_dial.setValue(int(self.current))
        self.ui.power_dial.setValue(int(self.power))
        #set the text tields to the values put in by the dials
        self.ui.input_field_voltage.setText(str(self.voltage))
        self.ui.input_field_current.setText(str(self.current))
        self.ui.input_field_power.setText(str(self.power))
        """
    def apply_diode_model(self):
        """
        U_1, I_1 = curveutils.solarIV(self.cell_p, self.cell_s, self.i_s, self.m, self.u_t, self.c_0, 1000, 10000)
        #prepare data before running the controll algorithm, removes too low 
        U_1, I_1 = curveutils.min_remover(U_1, I_1, 5)
        U_1, I_1 = curveutils.stepsize_reducer(list(U_1), list(I_1), 0.025, 'right')
        """
        self.ui.apply_3d_preview_button.setEnabled(False)
        self.whole_day = curveutils.whole_day_dict(self.cell_p, self.cell_s, self.i_s, self.m, self.u_t, self.c_0,10000,0,1000,10)
        #print("The irradiance is:", int(self.irradiance))
        #self.ui.apply_3d_preview_button.setEnabled(True)
        U_1, I_1 = self.whole_day.return_for_irradiance(int(self.irradiance))
        try:
            self.scheduling.measure_signal.setter.set_voltages_currents(U_1, I_1)
            self.scheduling.measure_set_diode_model()
        except:
            print("Applying the new Diode model Failed. Current array:", I_1)
            print("Retaining previous values.")
        #print("Are all U Values Identical? ",self.whole_day.all_U_values_identical())
        #print("Let's see what we got here:",self.whole_day.data_as_array())
        self.values_3d_plot = self.whole_day.data_as_array()
        self.refresh_3d_surface()
    def reset_diode_model(self):
        """
        Handles the reset button on the Diode Model tab.
        Sets back to standard values, triggers handle for updating related fields and sliders
        """
        self.cell_p = self.cell_p_standard
        self.cell_s = self.cell_s_standard
        self.i_s = self.i_s_standard
        self.m = self.m_standard
        self.u_t = self.u_t_standard
        self.c_0 = self.c_0_standard
        self.irradiance = self.irradiance_standard

        # Block signals from all diode-model inputs/sliders while resetting
        
        blockers = [
            QSignalBlocker(self.ui.cells_parralel_input_field),
            QSignalBlocker(self.ui.cells_series_input_field),
            QSignalBlocker(self.ui.saturation_current_input_field),
            QSignalBlocker(self.ui.diodefactor_input_field),
            QSignalBlocker(self.ui.thermalvoltage_input_field),
            QSignalBlocker(self.ui.photo_current_coefficient_input_field),
            QSignalBlocker(self.ui.irradiance_input_field),

            QSignalBlocker(self.ui.cells_parralel_input_slider),
            QSignalBlocker(self.ui.cells_series_input_slider),
            QSignalBlocker(self.ui.saturation_current_input_slider),
            QSignalBlocker(self.ui.diodefactor_input_slider),
            QSignalBlocker(self.ui.thermalvoltage_input_slider),
            QSignalBlocker(self.ui.photo_current_coefficient_input_slider),
            QSignalBlocker(self.ui.irradiance_dial),
        ]
        # (Keep references alive until end of function)

        try:
            # Now it’s safe to write all values; handlers won’t re-trigger mid-reset
            self.handle_diode_model_fields(update=False)
            self.handle_diode_model_sliders(update=False)
        finally:
            # Unblock happens automatically when blockers go out of scope,
            # but the `finally` ensures cleanup even if something errors.
            pass
    def handle_irradiance_dial(self):
        self.handle_diode_model_sliders()
        #self.whole_day = curveutils.whole_day_dict(self.cell_p, self.cell_s, self.i_s, self.m, self.u_t, self.c_0,10000,0,1000,10)
        #U_1, I_1 = self.whole_day.return_for_irradiance(self.irradiance)
        #self.scheduling.measure_signal.setter = curveutils.setter(U_1, I_1)
        #self.scheduling.measure_set_diode_model()

        print("The irradiance is:", int(self.irradiance))
        U_1, I_1 = self.whole_day.return_for_irradiance(int(self.irradiance))
        self.iv_plot.update_curve(U_1, I_1)
        #self.iv_plot.update_points(self.scheduling.measure_signal.setter._max_power_point.voltage, self.scheduling.measure_signal.setter._max_power_point.current, 0.0,0.0)
        self.scheduling.measure_signal.setter.set_voltages_currents(U_1, I_1)
        self.set_active_irradiance(self.irradiance/10)
    def handle_irradiance_field(self):
        self.handle_diode_model_fields()
        #self.whole_day = curveutils.whole_day_dict(self.cell_p, self.cell_s, self.i_s, self.m, self.u_t, self.c_0,10000,0,1000,10)
        #U_1, I_1 = self.whole_day.return_for_irradiance(self.irradiance)
        
        #self.scheduling.measure_signal.setter = curveutils.setter(U_1, I_1)
        #self.scheduling.measure_set_diode_model()
    def closeEvent(self, event):
        print("Closing Window...")
        #stop the scheduler, this ensures no other job still running in the background can influence the shutdown process
        self.scheduling.scheduler.stop()
        #this is a bit of a dirty hack due to the scheduler lacking the capability to process interrupts. Basically wait after stopping to make sure there's nothing in the pipeline
        time.sleep(0.5)
        turn_on = ("OP1 1")
        turn_off = ("OP1 0")
        try:
            self.scheduling.supply.sendOnly(turn_off)
            self.scheduling.supply.setValues(0,0,0)
        except:
            print("Turning the supply off properly after closing the Window failed.")
    def show_connection_failed_dialog(self, error_text=None):
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setWindowTitle("Connection failed")
        msg.setText(error_text or "Could not connect to the supply.")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.open()

    def setup_3d_plot(self, placeholder):
        """
        initalizes the 3D plot with a set of initial values
        """
        #overwrite 3D plot placeholder
        container = placeholder # this is the Designer placeholder
        #set layout of the new widget
        layout = QtWidgets.QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        #create the opengl plot and add a reasonable camera position
        self.gl_view = ClampedGLViewWidget()
        #set black background
        self.gl_view.setBackgroundColor((80, 140, 210, 255))
        self.gl_view.opts['distance'] = 10
        #add plot widget to layout
        #layout.addWidget(self.gl_view)
        #setup grid
        self.grid = gl.GLGridItem()
        self.grid.setSize(x=1, y=1, z=1)
        self.grid.setSpacing(x=1, y=1, z=1)
        self.grid.setColor((0.6, 0.6, 0.6, 0.2))
        self.grid.setGLOptions('translucent')
        self.gl_view.addItem(self.grid)
        #self.gl_view = gl.GLViewWidget(rotationMethod='quaternion')
        out = self.values_3d_plot        # shape (nG, nU, 3)
        E_grid = out[:, :, 0]*0.1
        U_grid = out[:, :, 1]
        I_grid = out[:, :, 2]
        #convert grid varaibles to fit shape expected by GLSurfacePlotItem
        E_vals = E_grid[:, 0]             # length nG
        U_vals = U_grid[0, :]  
        #scale down E_vals so the graph will look right
        #E_vals = E_vals * 0.25
        #set the grid as part of the GLSurfacePlot
        #np.savetxt("out.txt", out.reshape(-1, out.shape[-1]))
        
        self.surface = gl.GLSurfacePlotItem(
            x=E_vals,
            y=U_vals,
            z=I_grid,
            shader='heightColor',
            computeNormals=True,
            smooth=False
        )
        self.surface.setGLOptions('opaque')  # or 'translucent'
        self.gl_view.addItem(self.surface)
        #set max values
        E_min, E_max = float(E_grid.min()), float(E_grid.max())
        U_min, U_max = float(U_grid.min()), float(U_grid.max())
        I_min, I_max = float(I_grid.min()), float(I_grid.max())
        #determine center of plot
        center = QVector3D((E_min + E_max)/2, (U_min + U_max)/2, (I_min + I_max)/2)
        # distance large enough to see the whole surface
        extent = np.array([E_max - E_min, U_max - U_min, I_max - I_min], dtype=float)
        radius = np.linalg.norm(extent) / 2.0
        distance = max(radius * 3.0, 1.0)

        self.gl_view.opts['center'] = center

        # Start with a camera that puts +E and +U toward the lower-right,
        # while making +I project upward.
        self.gl_view.setCameraPosition(
            distance=distance,
            elevation=35,   # tilt: raise/lower how much of the "up" comes from I
            azimuth=35     # rotate around the center: left/right mapping
        )
        # constant colour gradiant without sharp transition
        I = I_grid  # shape (nG, nU)
        zmin = float(I.min())
        zmax = float(I.max())
        r = zmax - zmin

        if r > 0:
            k_green = 0.75     # <1 keeps high values from turning fully yellow (tunes "red at max")
            gamma_blue = 2.5  # >1 makes blue drop faster so mid values look more yellow/green

            # heightColor shader uses:
            # red   = colorMap[0] * (z + colorMap[1]) ^ colorMap[2]
            # green = colorMap[3] * (z + colorMap[4]) ^ colorMap[5]
            # blue  = colorMap[6] * (z + colorMap[7]) ^ colorMap[8]
            self.surface.shader()['colorMap'] = np.array([
                1.0/r,   -zmin,     1.0,      # red   = (z - zmin)/range
                k_green/r, -zmin,   1.0,      # green = k * (z - zmin)/range
                -1.0/r,  -zmax,     gamma_blue  # blue  = ((zmax - z)/range) ^ gamma_blue
            ], dtype=np.float32)
        else:
            # all I values equal -> no meaningful gradient
            pass
        self._add_axis_labels(E_min, E_max, U_min, U_max, I_min, I_max)
        self._init_active_curve_items()
        layout.addWidget(self.gl_view)

    def _add_axis_labels(self, E_min, E_max, U_min, U_max, I_min, I_max, update=False):
        # Create storage on first use
        if not hasattr(self, "_axis_items"):
            self._axis_items = []
        else:
            if update:
                # Remove old axis items (lines + ticks + all text)
                for item in self._axis_items:
                    try:
                        self.gl_view.removeItem(item)
                    except Exception:
                        pass
                self._axis_items.clear()

        def add_text(pos, text, color=(255, 255, 255, 1), size=12):
            t = gl.GLTextItem(
                pos=pos,
                text=text,
                color=color,
                font=pg.QtGui.QFont("Arial", size),
            )
            self.gl_view.addItem(t)
            self._axis_items.append(t)
            return t

        def add_line(p0, p1, color=(255, 255, 255, 255), width=2):
            ln = gl.GLLinePlotItem(
                pos=np.array([p0, p1], dtype=float),
                color=color,
                width=width,
                antialias=True,
            )
            self.gl_view.addItem(ln)
            self._axis_items.append(ln)
            return ln

        # Ranges (used for offsets/tick lengths)
        dE = float(E_max - E_min)
        dU = float(U_max - U_min)
        dI = float(I_max - I_min)
        maxd = max(dE, dU, dI, 1e-12)

        # Origin and axis endpoints
        O = (E_min, U_min, I_min)
        E_end = (E_max, U_min, I_min)
        U_end = (E_min, U_max, I_min)
        I_end = (E_min, U_min, I_max)

        # Axes lines
        add_line(O, E_end, color=(0, 255, 0, 255), width=2)       # E axis
        add_line(O, U_end, color=(0, 0, 255, 255), width=2)       # U axis
        add_line(O, I_end, color=(255, 0, 0, 255), width=2)       # I axis

        # Axis letters at corners (like your original)
        add_text((E_max, U_min, I_min), "E", color=(0, 255, 0, 1), size=200)
        add_text((E_min, U_max, I_min), "U", color=(0, 0, 255, 1), size=16)
        add_text((E_min, U_min, I_max), "I", color=(255, 0, 0, 1), size=16)

        # Tick settings: "every 10th value" -> 10 segments along the axis
        nSegments = 10
        tick_len = 0.015 * maxd  # how long the tick marks are

        # Tick label formatting
        def fmt(v):
            # adjust as needed
            return f"{v:.3g}"

        # Tick labels for E (x direction)
        for k in range(nSegments + 1):
            t = k / nSegments
            x = E_min + t * dE
            # tick mark: along z a little at the bottom plane
            add_line((x, U_min, I_min), (x, U_min, I_min + tick_len),
                    color=(220, 220, 220, 200), width=1)
            # label offset (slightly in +z so it doesn't sit exactly on the line)
            add_text((x, U_min, I_min + tick_len * 1.2),
                    fmt(x), color=(240, 240, 240, 1), size=10)

        # Tick labels for U (y direction)
        for k in range(nSegments + 1):
            t = k / nSegments
            y = U_min + t * dU
            add_line((E_min, y, I_min), (E_min + tick_len, y, I_min),
                    color=(220, 220, 220, 200), width=1)
            add_text((E_min + tick_len * 1.2, y, I_min),
                    fmt(y), color=(240, 240, 240, 1), size=10)

        # Tick labels for I (z direction)
        for k in range(nSegments + 1):
            t = k / nSegments
            z = I_min + t * dI
            add_line((E_min, U_min, z), (E_min + tick_len, U_min, z),
                    color=(220, 220, 220, 200), width=1)
            add_text((E_min + tick_len * 1.2, U_min, z),
                    fmt(z), color=(240, 240, 240, 1), size=10)


    def _update_surface_colormap(self, I_grid):
        zmin = float(I_grid.min())
        zmax = float(I_grid.max())
        r = zmax - zmin

        if r <= 0:
            return

        # Same tuning knobs that made your gradient work
        k_green = 0.75
        gamma_blue = 2.5

        # heightColor shader mapping:
        # red   = pow(z * cm[0] + cm[1], cm[2])
        # green = pow(z * cm[3] + cm[4], cm[5])
        # blue  = pow(z * cm[6] + cm[7], cm[8])
        self.surface.shader()['colorMap'] = np.array([
            1.0/r,     -zmin,    1.0,      # red
            k_green/r, -zmin,    1.0,      # green
            -1.0/r,    -zmax,    gamma_blue  # blue
        ], dtype=np.float32)


    def refresh_3d_surface(self, update_camera=True):
        out = self.values_3d_plot  # (nG, nU, 3)

        E_grid = out[:, :, 0] * 0.1
        U_grid = out[:, :, 1]
        I_grid = out[:, :, 2]       # shape (nG, nU)

        # GLSurfacePlotItem mapping (use the corrected orientation):
        E_vals = E_grid[:, 0]       # (nG,)
        U_vals = U_grid[0, :]       # (nU,)

        # Update geometry (if x/y unchanged you can skip them; keeping them is fine)
        self.surface.setData(
            x=E_vals,
            y=U_vals,
            z=I_grid
        )

        # Update colormap to match new min/max of I
        self._update_surface_colormap(I_grid)

        if update_camera:
            E_min, E_max = float(E_grid.min()), float(E_grid.max())
            U_min, U_max = float(U_grid.min()), float(U_grid.max())
            I_min, I_max = float(I_grid.min()), float(I_grid.max())

            center = QVector3D((E_min + E_max) / 2, (U_min + U_max) / 2, (I_min + I_max) / 2)
            self.gl_view.opts['center'] = center

            extent = np.array([E_max - E_min, U_max - U_min, I_max - I_min], dtype=float)
            radius = np.linalg.norm(extent) / 2.0
            distance = max(radius * 3.0, 1.0)

            # Keep the same orientation you liked earlier; adjust if you want
            self.gl_view.setCameraPosition(distance=distance, elevation=35, azimuth=35)
        self._add_axis_labels(E_min, E_max, U_min, U_max, I_min, I_max, update=True)
        self._update_active_curve()


    def _init_active_curve_items(self):
        # Store selection (default)
        if not hasattr(self, "_active_E_index"):
            self._active_E_index = 0

        # --- 3D red highlight curve ---
        self._active_curve_3d = gl.GLLinePlotItem(
            pos=np.zeros((2, 3), dtype=float),
            color=(255, 0, 0, 255),
            width=3,
            antialias=True,
        )
        self.gl_view.addItem(self._active_curve_3d)

        # --- 2D curve plot (pick your UI widget name) ---
        # Change this to whatever your UI element is called.
        self._active_curve_2d_plot = self.ui.placeholder_2d_view  # <-- rename if needed

        #self._active_curve_2d_plot.showGrid(x=True, y=True)
        #self._active_curve_2d_plot.setLabel("bottom", "U")
        #self._active_curve_2d_plot.setLabel("left", "I")

        #self._active_curve_2d_line = self._active_curve_2d_plot.plot(
        #    pen=pg.mkPen(color=(255, 0, 0), width=2)
        #)

        # Initial draw (with whatever current data you have)
        self._update_active_curve()
    def set_active_irradiance(self, E_index=None, E_value=None):
        """
        Call this from your UI selection logic.
        - E_index: row index in your irradiance grid
        - E_value: pick closest E in the grid
        """
        out = self.values_3d_plot
        E_grid = out[:, :, 0] * 0.1
        U_grid = out[:, :, 1]
        I_grid = out[:, :, 2]

        nG, nU = I_grid.shape
        E_vals = E_grid[:, 0]  # (nG,)

        if E_index is None and E_value is None:
            E_index = getattr(self, "_active_E_index", 0)

        if E_index is not None:
            self._active_E_index = int(np.clip(E_index, 0, nG - 1))
        else:
            self._active_E_index = int(np.argmin(np.abs(E_vals - E_value)))

        self._update_active_curve()

    def _update_active_curve(self):
        out = self.values_3d_plot
        E_grid = out[:, :, 0] * 0.1
        U_grid = out[:, :, 1]
        I_grid = out[:, :, 2]  # (nG, nU)

        nG, nU = I_grid.shape
        E_index = int(np.clip(getattr(self, "_active_E_index", 0), 0, nG - 1))

        E_vals = E_grid[:, 0]   # (nG,)
        U_vals = U_grid[0, :]   # (nU,)
        I_curve = I_grid[E_index, :]  # (nU,)

        E_fixed = float(E_vals[E_index])

        # ---- update 3D red curve ----
        # points: (E_fixed, U_vals[j], I_curve[j])
        pts = np.column_stack([
            np.full(nU, E_fixed, dtype=float),
            U_vals.astype(float),
            I_curve.astype(float),
        ])
        self._active_curve_3d.setData(pos=pts)

        # ---- update 2D curve ----
        #self._active_curve_2d_line.setData(U_vals, I_curve)



class ClampedGLViewWidget(gl.GLViewWidget):
    def mouseMoveEvent(self, ev):
        super().mouseMoveEvent(ev)
        # Clamp elevation to avoid pole flips/distortions (Euler mode only)
        if self.opts.get('rotationMethod', 'euler') == 'euler':
            self.opts['elevation'] = float(np.clip(self.opts.get('elevation', 0), -80.0, 80.0))

class IVCurvePlot(pg.PlotWidget):
    def __init__(self, dash_every=10, parent=None):
        super().__init__(parent=parent)

        self.dash_every = int(dash_every)

        self.setMinimumSize(0, 0)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                           QtWidgets.QSizePolicy.Policy.Expanding)

        # Correct: margins on the widget, not on self.layout (method)
        self.setContentsMargins(0, 0, 0, 0)

        self.curve = self.plot(pen=pg.mkPen(color=(40, 120, 255), width=2))

        self.mppSpot = pg.ScatterPlotItem(
            size=14,
            pen=pg.mkPen((220, 40, 40), width=2),
            brush=pg.mkBrush((220, 40, 40, 160))
        )
        self.measSpot = pg.ScatterPlotItem(
            size=14,
            pen=pg.mkPen((40, 180, 80), width=2),
            brush=pg.mkBrush((40, 180, 80, 160))
        )
        self.addItem(self.mppSpot)
        self.addItem(self.measSpot)

        self.mppLabel = pg.TextItem("MPP", color=(220, 40, 40), anchor=(0, 1))
        self.measLabel = pg.TextItem("Measured Value", color=(40, 180, 80), anchor=(0, 1))
        self.addItem(self.mppLabel)
        self.addItem(self.measLabel)

        self.showGrid(x=True, y=True, alpha=0.25)
        self.setLabel("bottom", "Voltage", units="V")
        self.setLabel("left", "Current", units="A")

        self._vmin = 0.0; self._vmax = 1.0
        self._imin = 0.0; self._imax = 1.0
    def update_curve(self, voltages, currents):
        v = np.asarray(voltages, dtype=float).ravel()
        i = np.asarray(currents, dtype=float).ravel()
        if v.size == 0 or i.size == 0 or v.size != i.size:
            return

        order = np.argsort(v)
        v = v[order]
        i = i[order]

        self.curve.setData(v, i)

        self._vmin, self._vmax = float(v.min()), float(v.max())
        self._imin, self._imax = float(i.min()), float(i.max())

        self.setXRange(self._vmin, self._vmax, padding=0)
        self.setYRange(self._imin, self._imax, padding=0)

        #self._set_ticks_every_n(self.getAxis("bottom"), v)
        #self._set_ticks_every_n(self.getAxis("left"), i)

    def update_points(self, mpp_v, mpp_i, measured_v, measured_i):
        mpp_v = float(mpp_v); mpp_i = float(mpp_i)
        measured_v = float(measured_v); measured_i = float(measured_i)

        self.mppSpot.setData([mpp_v], [mpp_i])
        self.measSpot.setData([measured_v], [measured_i])

        dx = 0.01 * (self._vmax - self._vmin) if self._vmax > self._vmin else 0.001
        dy = 0.01 * (self._imax - self._imin) if self._imax > self._imin else 0.001

        self.mppLabel.setPos(mpp_v + dx, mpp_i + dy)
        self.measLabel.setPos(measured_v + dx, measured_i + dy)

scheduling = qt_wrapper.scheduling(supply, set_supply, 5)
