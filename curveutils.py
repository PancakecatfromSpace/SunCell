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
    https://stackoverflow.com/questions/30734258/efficiently-check-if-numpy-ndarray-values-are-strictly-increasing
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

def reduce_steps(array, stepsize, direction='left', inplace=False):
    """
    Reduce step changes in a 1D numeric array by copying neighbor values when
    the absolute difference between adjacent elements is below `stepsize`.

    Args:
    array (array-like): 1D sequence of numeric values.
    stepsize (float): threshold; if abs(a[i] - a[i-1]) < stepsize, replace one of them.
    direction (str): 'left' to copy left neighbor into right element, 'right' to copy right neighbor into left element.
    inplace (bool): if True modify the provided array (converted to numpy); otherwise work on a copy.

    Returns:
      numpy.ndarray: array with reduced steps.
    """

        

    arr = np.asarray(array)
    if arr.ndim != 1:
        raise ValueError("array must be 1D")

    if not inplace:
        arr = arr.copy()
        
    match direction:
        case 'left':
            for i in range(1, arr.size):
                if abs(arr[i] - arr[i-1]) < stepsize:
                    arr[i] = arr[i-1]
        case 'right':
            for i in range(arr.size - 2, -1, -1):
                if abs(arr[i] - arr[i+1]) < stepsize:
                    arr[i] = arr[i+1]
        case _:
            raise ValueError("direction must be 'left' or 'right'")
        
    if not inplace:
        return arr

def stepsize_reducer(voltages, currents, stepsize, direction='left'):
    """
    Discards all voltage current value pairs where the difference between two neighbouring current values is bellow stepsize.

    Args:
    voltages(1D-array-like): one dimensional array like structure.
    currents(1D-array-like): one dimensional array like structure, must have same length as voltages.
    stepsize(float): minimum step size between current values before they get deleted.
    direction(string): can be left or right, sets wheather the left value bellow the threshhold should be retained or the right value.
    
    Returns:
    voltages(1D-list): One dimensional list.
    currents(1D-list): One dimensional list.

    Raises:
    ValueError: If the input list not one dimensional, the lists have different shapes or if the direction given is invalid.
    """
    
    volt = np.asarray(voltages)
    curr = np.asarray(currents)
    #check if voltage and current array are both one dimensional
    if volt.ndim != 1 and curr.ndim != 1:
        raise ValueError("Error! Arrays for voltages and currents must be 1D.")
    #check if voltage and current array have the same amount of elements
    if volt.size != curr.size:
        raise ValueError("Error! Arrays for voltages and currents must have the same length.")

    volt = volt.copy()
    curr = curr.copy()
    #decide weather to approach the current array from left to right or from right to left, if left the left value is retained if right the right value is retained
    match direction:
        case 'left':
            for i in range(1, curr.size):
                #copies values that are bellow the stepsize so they can be discarded later
                if abs(curr[i] - curr[i-1]) < stepsize:
                    curr[i] = curr[i-1]
                    volt[i] = volt[i-1]
        case 'right':
            for i in range(curr.size - 2, -1, -1):
                if abs(curr[i] - curr[i+1]) < stepsize:
                    curr[i] = curr[i+1]
                    volt[i] = volt[i+1]
        case _:
            raise ValueError("Error! Direction must be 'left' or 'right'.")
    #this somehow removed duplicates from both arrays but I'm not sure how, I just copied it from here: https://www.geeksforgeeks.org/python/python-ways-to-remove-duplicates-from-list/
    volt = list(dict.fromkeys(volt))
    curr = list(dict.fromkeys(curr))

    return volt,curr

def min_remover(voltages, currents, minimal_voltage, inplace=False):
    """
    Removes value pairs if the voltage is bellow a certain threshhold. This is due to an instability problem when the voltage is too low the wire resistance stops a sufficient current from flowing, causing the setpoint to jump around irradically.
    Args:
    voltages: a 1D array of equidistant voltages
    currents: a 1D array of currents corresponding to voltages
    min_voltage: integer of the minimal value, every value pair bellow this value will be removed

    Returns:
    voltages: Voltage to the left of the selected point

    Raises:
    Exception: detects if currents vector is monotonous and will result in a crash if it is not.
    """
    volt = np.asarray(voltages)
    curr = np.asarray(currents)
    if not inplace:
        volt = volt.copy()
        curr = curr.copy()
    if np.all(np.diff(volt) > 0):
        # finds index where the voltage should be placed when decreasing monotonely
        idx = np.searchsorted(volt, minimal_voltage, side='left')
        # clamps to valid index, index can never be lower than zero nor the arrays maximum leghth
        idx = min(max(idx, 0), len(voltages)-1)
        if not inplace:
            return volt[idx:],curr[idx:]
    else:
        # crash when current is constant or non monotonous
        raise Exception("Error! Given voltage curve must increase monotonely!")