import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
import time
import coms
import curveutils
from functools import partial

supply = coms.SupplyCommunication("10.30.0.105") # connect to power supply with this IP Address

#create two vectors and populate them with the values from a one diode model
U_1, I_1 = curveutils.solarIV(5, 300, 8.75e-3, 4.0, 25.7e-3, 3e-3, 1000, 500)

fig, ax = plt.subplots()
#points on the plot
ax.plot(U_1, I_1, color='C0')
#makes points interactable and updateable
soll, = ax.plot([], [], marker='o', color='red', markersize=8)
ist, = ax.plot([], [], marker='o', color='green', markersize=8)
#set the limits for the plot to be the max and min values in the vector U_1 and I_1
ax.set_xlim(U_1.min(), U_1.max())
ax.set_ylim(0, I_1.max()*1.1)
#label stuff
ax.set_xlabel("Voltage")
ax.set_ylabel("Current")
#make a text to move with the point
measure_label = ax.text(10, 10,"Measured Value")
setpoint_label = ax.text(10, 10, "Set Value")
"""
# adjust placement of plot to make room for slider
fig.subplots_adjust(bottom=0.25)
# Make a horizontal slider to control current
axcurr = fig.add_axes([0.25, 0.1, 0.65, 0.03])
curr_slider = Slider(
    ax=axcurr,
    label='Current (amp)',
    valmin=0,
    valmax=I_1.max()*1.1,
    valinit=I_1.max()/2,
)
"""
plt.ion()
plt.show()

#eddited the value of the initial voltage to 5, by suggestion by Rüdiger Mann 27.04.26
supply.setValues(5, I_1.max()*1.1, 3000.0)

def update_supply():
    #read the slider and update the value
    #current_slider = curr_slider.val

    supply.measureValues()
    #selects the voltage for the previously measured current
    supply.setValues(curveutils.select_voltage_for_current(U_1, I_1, supply.measuredpoints.current))

def update_gui():
    soll.set_data([supply.setpoints.voltage], [supply.setpoints.current])      # <- scalar -> sequence
    ist.set_data([supply.measuredpoints.voltage], [supply.measuredpoints.current])

    measure_label.set_position((supply.measuredpoints.voltage, supply.measuredpoints.current+I_1.max()*0.05))
    setpoint_label.set_position((supply.setpoints.voltage, supply.setpoints.current+I_1.max()*0.05))

    fig.canvas.draw_idle()
    #fig.canvas.flush_events()
#time.sleep(5)

timer = fig.canvas.new_timer(interval=500) #interval is time in miliseconds
timer2 = fig.canvas.new_timer(interval=1)
timer.add_callback(lambda: update_supply())
timer2.add_callback(lambda: update_gui())
timer.start()
timer2.start()

plt.show(block=True)

#coms.closeSocket(socket)