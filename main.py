import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
import time
import coms

#values relating to the connection to the power supply
SUPPLY_IP = "10.30.0.105"
SUPPLY_PORT = 8462
BUFFER_SIZE = 128 # max msg size
TIMEOUT_SECONDS = 10 # return error if we dont hear from supply within 10 sec

#ranges within which the voltages, currents and power can be set
MAX_VOLT = 210 # default
MIN_VOLT = -10
MAX_CUR = 32    #default
MIN_CUR = -10
MAX_POWER = 100
MIN_POWER = -10

def solarIV(cell_p:int, cell_s:int, I_s:float, m:float, U_T:float, c_0:float, E:float, steps:int):
    """
    calculates the current voltage curve of an array of solar cells
    
    Args:
    cell_p: solar cells in parralel
    cell_s: solar cells in series
    I_s: saturation current
    m: diodefactor
    U_T: Thermalvoltage
    c_0: photo current coefficient
    E: irradiance
    steps: amount of values to be calculated from minimum to maximum value
    
    Returns:
    U: voltages from min to max
    I: currents from min to max
    """

    # implements the simple one diode model since it requires no numeric solution
    
    U = np.linspace(0.0, 0.6, steps)

    # vectorized implementation
    I_ph = c_0 * E
    diode = I_s * (np.exp(U / (m * U_T)) - 1.0)
    I = + I_ph - diode

    # amount of solar cells in series and in parralel
    U = U*cell_s
    I = I*cell_p

    return U, I

#create two vectors and populate them with the values from a one diode model
U_1, I_1 = solarIV(10, 300, 8.75e-3, 4.0, 25.7e-3, 3e-3, 1000, 5)

#populate a vector that is always in the middle between two points within the vector U_1
U_1_mid = (U_1[:-1] + U_1[1:]) / 2.0
I_1_mid = (I_1[:-1] + I_1[1:]) / 2.0

U_2 = [50, 50]
I_2 = [I_1.min(), I_1.max()]

socket = coms.OpenSocket(SUPPLY_IP, SUPPLY_PORT, TIMEOUT_SECONDS, BUFFER_SIZE)

fig, ax = plt.subplots()
#points on the plot
ax.plot(U_1, I_1, color='C0')
#makes points interactable and updateable
point1, = ax.plot([], [], marker='o', color='red', markersize=8)
point2, = ax.plot([], [], marker='o', color='green', markersize=8)
#set the limits for the plot to be the max and min values in the vector U_1 and I_1
ax.set_xlim(U_1.min(), U_1.max())
ax.set_ylim(0, I_1.max()*1.1)
#label stuff
ax.set_xlabel("Voltage")
ax.set_ylabel("Current")
# adjust placement of plot to make room for slider
fig.subplots_adjust(bottom=0.25)

#draw vertical lines to mark the switching range
for i_u in U_1_mid:
    plt.axvline(x=i_u, color='blue')
for i_i in I_1_mid:
    plt.axhline(y=i_i, color='red')

# Make a horizontal slider to control current
axcurr = fig.add_axes([0.25, 0.1, 0.65, 0.03])

curr_slider = Slider(
    ax=axcurr,
    label='Current (amp)',
    valmin=0,
    valmax=I_1.max(),
    valinit=I_1.max()/2,
)

plt.ion()
plt.show()

curr = I_1[np.argmax(U_1)]
volt = U_1.max()

print(curr, volt)

volt2 = 0
power = 10

i = 0
end = 5

def emergency_off():
    """
    shuts off everything
    """
    coms.setCurrent(0, MAX_CUR, MIN_CUR, socket)
    coms.setVoltage(0, MAX_VOLT, MIN_VOLT, socket)
    coms.setPowerPos(0, MAX_POWER, MIN_POWER, socket)
    coms.closeSocket(socket)

#time.sleep(5)

try:
    while True:
        #read the slider and update the value
        current_slider = curr_slider.val
        #plt.annotate(f'({U0:.2f}, {I0:.2f})', xy=(U0, I0), xytext=(5, 5), textcoords='offset points', color='red')
        
            
        # if the current or voltage is out of range, put everything to zero and end
        if coms.setCurrent(curr, MAX_CUR, MIN_CUR, socket) == -1:
            emergency_off()
            raise Exception(f"Fault! Attempted to set current {curr} outside range [{MIN_CUR}, {MAX_CUR}]!")
        if coms.setVoltage(volt, MAX_VOLT, MIN_VOLT, socket) == -1:
            emergency_off()
            raise Exception(f"Fault! Attempted to set voltage {volt} outside range [{MIN_VOLT}, {MAX_VOLT}]!")
        if coms.setPowerPos(power, MAX_POWER, MIN_POWER, socket) == -1:
            emergency_off()
            raise Exception(f"Fault! Attempted to set power {power} outside range [{MIN_POWER}, {MAX_POWER}]!")

        U0 = float(coms.readVoltage(socket))
        I0 = float(coms.readCurrent(socket))

        #print(readVoltage())
        point1.set_data([U0], [I0])      # <- scalar -> sequence
        point2.set_data([float(coms.measureVoltage(socket))], [current_slider])

        print(current_slider)

        fig.canvas.draw_idle()
        fig.canvas.flush_events()
        #volt = volt + 0.1
        #volt2 = volt2 + 0.5
        time.sleep(0.1)
        U0 = U0 + 5
        i = i + 1
except KeyboardInterrupt:
    pass

coms.closeSocket(socket)