"""
PV/IV curve utilities

Provides functions and models for generating and working with photovoltaic
I–V and V–I curves (single-diode model, helpers for selecting voltages for a
given current, and related utilities). Intended for reuse and extension with
additional curve models, parameterized generators, interpolation helpers, and
plotting utilities.
"""

import numpy as np

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


def select_voltage_for_current(voltages, currents, measured_current):
    if currents[0] > currents[-1]:
        # finds index where the voltage should be placed when decreasing monotonely
        idx = np.searchsorted(-currents, -measured_current, side='right')
        # clamps to valid index, index can never be lower than zero nor the arrays maximum leghth
        idx = min(max(idx, 0), len(currents)-1)
        return voltages[idx]
    elif currents[-1] > currents[0]:
        # same as  above but for monotonely increasing functions
        idx = np.searchsorted(currents, measured_current, side='right')
        idx = min(max(idx, 0), len(currents)-1)
        return voltages[idx]
    else:
        # crash when current is constant over array
        raise Exception("Error! Current given to select_voltage_for_current is neither decreasing nor increasing!")