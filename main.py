import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
import time
import coms
import curveutils

set = coms.SetPoints()
limits = coms.Limits()
socketvals = coms.SocketVals("10.30.0.105")
socket = coms.OpenSocket(socketvals)

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

#set voltage to half the step width of the first value
set.voltage = U_1[1]/4
set.current = I_1[0]*1.1
set.power = 10.0

try:
    while True:
        #read the slider and update the value
        #current_slider = curr_slider.val

        UM = float(coms.measureVoltage(socket))
        IM = float(coms.measureCurrent(socket))

        set.voltage = curveutils.select_voltage_for_current(U_1, I_1, IM)
        coms.set_checked(set, limits, socket)

        soll.set_data([set.voltage], [set.current])      # <- scalar -> sequence
        ist.set_data([UM], [IM])

        measure_label.set_position((UM, IM+I_1.max()*0.05))
        setpoint_label.set_position((set.voltage, set.current+I_1.max()*0.05))

        fig.canvas.draw_idle()
        fig.canvas.flush_events()
        
        time.sleep(0.1)
except KeyboardInterrupt:
    pass

coms.closeSocket(socket)