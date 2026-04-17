import numpy as np
import matplotlib.pyplot as plt
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

def solarIV(cell_p:int, cell_s:int, I_s:float, m:float, U_T:float, c_0:float, E:float,steps:int):
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