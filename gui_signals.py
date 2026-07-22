"""
This file wraps the signals for the gui.py user interface into it's own file,
contains the wrappers for the functions to be scheduled and how they connect to the UI.
"""

from PySide6.QtCore import QObject, Signal, Slot, QSignalBlocker, Qt
from PySide6 import QtWidgets
from PySide6.QtGui import QVector3D
import gui, curveutils, qt_scheduler, qt_wrapper
import power_supply_drivers.wrapper as coms
import time
import pyqtgraph.opengl as gl
import pyqtgraph as pg

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
        self.setup_3d_plot()


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
        self.scheduling.measure_signal.setter.set_voltages_currents(U_1, I_1)
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

    def setup_3d_plot(self):
        """
        initalizes the 3D plot with a set of initial values
        """
        #overwrite 3D plot placeholder
        container = self.ui.plot_3d_preview  # this is the Designer placeholder
        #set layout of the new widget
        layout = QtWidgets.QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        #create the opengl plot and add a reasonable camera position
        self.gl_view = gl.GLViewWidget()
        #set black background
        self.gl_view.setBackgroundColor((80, 140, 210, 255))
        self.gl_view.opts['distance'] = 10
        #add plot widget to layout
        layout.addWidget(self.gl_view)
        #setup grid
        self.grid = gl.GLGridItem()
        self.grid.setSize(x=1, y=1, z=1)
        self.grid.setSpacing(x=1, y=1, z=1)
        self.grid.setColor((0.6, 0.6, 0.6, 0.2))
        self.grid.setGLOptions('translucent')
        self.gl_view.addItem(self.grid)
        out = self.values_3d_plot        # shape (nG, nU, 3)
        E_grid = out[:, :, 0] * 0.1
        U_grid = out[:, :, 1]
        I_grid = out[:, :, 2]
        #convert grid varaibles to fit shape expected by GLSurfacePlotItem
        E_vals = E_grid[:, 0]             # length nG
        U_vals = U_grid[0, :]  
        #scale down E_vals so the graph will look right
        #E_vals = E_vals * 0.25
        #set the grid as part of the GLSurfacePlot
        self.surface = gl.GLSurfacePlotItem(
            x=E_vals,
            y=U_vals,
            z=I_grid,
            shader='shaded',
            computeNormals=True,
            smooth=True
        )
        self.surface.setGLOptions('opaque')  # or 'translucent'
        self.gl_view.addItem(self.surface)
        #set max values
        E_min, E_max = float(E_grid.min()), float(E_grid.max())
        U_min, U_max = float(U_grid.min()), float(U_grid.max())
        I_min, I_max = float(I_grid.min()), float(I_grid.max())
        #determine center of plot
        center = QVector3D((E_min + E_max)/2, (U_min + U_max)/2, (I_min + I_max)/2)

        # Place camera diagonally above the surface
        self.gl_view.setCameraPosition(
            pos=QVector3D(E_max, U_max, I_max * 2.0),
            elevation=30,
            azimuth=-45
        )
        self._add_axis_labels(E_min, E_max, U_min, U_max, I_min, I_max)
        layout.addWidget(self.gl_view)

    def _add_axis_labels(self, E_min, E_max, U_min, U_max, I_min, I_max):
        # pyqtgraph GLTextItem uses 3D coordinates.
        # Note: you may need to tweak positions depending on your data ranges.
        def add_text(pos, text, color=(255, 255, 255, 1), size=12):
            t = gl.GLTextItem(pos=pos, text=text, color=color, font=pg.QtGui.QFont("Arial", size))
            #t.scale(0.1,0.1,0.1)  # adjust if text is too big/small
            self.gl_view.addItem(t)

        # Roughly place labels near the “max” corners
        add_text((E_max, U_min, I_min), "E",color=(0,255,0), size=16)
        add_text((E_min, U_max, I_min), "U", color=(0,0,255),size=16)
        add_text((E_min, U_min, I_max), "I",color=(255,0,0), size=16)

scheduling = qt_wrapper.scheduling(supply, set_supply, 5)
