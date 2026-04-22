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

def resistorIV(R:float, U_min:float, U_max:float, steps:int):
    """
    calculates the current voltage curve of a single resistor, allows negative values to check behaiviour of select_voltage_for_current
    
    Args:
    R: resistance in Ohm
    U_min: minimum voltage 
    U_max: maximum voltage
    steps: amount of values to be calculated from minimum to maximum value
    
    Returns:
    U: voltages, equidistant between U_min and U_max with steps amount of steps in between
    I: currents
    """
    if R == 0:
        raise Exception(f"Fault! Resistor Value cannot be 0! Given Value: {R}")
    
    U = np.linspace(U_min, U_max, steps)

    # vectorized implementation
    I = U / R


    return U, I

def unmonotonousIV(U_min:float, U_max:float, steps:int):
    """
    Creates a curve that is I = U², only to check behaiviour of select_voltage_for_current (checks if non monotonous curves are caught)
    
    Args:
    U_min: minimum voltage 
    U_max: maximum voltage
    steps: amount of values to be calculated from minimum to maximum value
    
    Returns:
    U: voltages
    I: currents
    """
    U = np.linspace(U_min, U_max, steps)

    # vectorized implementation
    I = np.square(U)


    return U, I
def unmonotonousIV2(U_min:float, U_max:float, I_val:float, steps:int):
    """
    Creates a curve that is I = , only to check behaiviour of select_voltage_for_current (checks if horizontal lines are detected and how they're handled)
    
    Args:
    U_min: minimum voltage 
    U_max: maximum voltage
    I_val: value to which to set 
    steps: amount of values to be calculated from minimum to maximum value
    
    Returns:
    U: voltages
    I: currents
    """
    U = np.linspace(U_min, U_max, steps)

    # vectorized implementation
    # set I to be the same vector as U
    I = U
    # set all values of vector I to I_val
    I = np.full_like(U,I_val)


    return U, I


def select_voltage_for_current(voltages, currents, measured_current):
    """
    Selects voltage value for given current value. Expects two vectors, one vector with equidistant voltage steps and one with corresponding currents.

    The currents vector may be discontinuous but it must be monotonous, non monotonous current arrays result in a crash, see Raises.
    Args:
    voltages: a 1D array of equidistant voltages
    currents: a 1D array of currents corresponding to voltages

    Returns:
    voltages: Voltage to the left of the selected point

    Raises:
    Exception: detects if currents vector is monotonous and will result in a crash if it is not.

    """
    """
    np.all(np.diff(currents) < 0) and np.all(np.diff(currents) > 0) are a clever way to check for monotony, np.diff creates the difference of all neighbouring
    values and fills the answer to the question if it is greater than zero into an array, np.all checks if any of the values in said array is false and if it is
    returns false
    """
    if np.all(np.diff(currents) < 0):
        # finds index where the voltage should be placed when decreasing monotonely
        idx = np.searchsorted(-currents, -measured_current, side='right')
        # clamps to valid index, index can never be lower than zero nor the arrays maximum leghth
        idx = min(max(idx, 0), len(currents)-1)
        return voltages[idx]
    elif np.all(np.diff(currents) > 0):
        # same as  above but for monotonely increasing functions
        idx = np.searchsorted(currents, measured_current, side='right')
        idx = min(max(idx, 0), len(currents)-1)
        return voltages[idx]
    else:
        # crash when current is constant or non monotonous
        raise Exception("Error! Given current curve is non monotonous or constant!")