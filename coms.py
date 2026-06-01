import socket
import pyvisa
from dataclasses import dataclass

# heavily modified version of the example provided by delta electronica
# communicates via a TCP socket with SCPI commands as found in the programming manual
# also adds VISA devices as a possible alternative

validSrcList = ["front", "web", "seq", "eth", "slot1", "slot2", "slot3", "slot4", "loc", "rem"]

@dataclass
class SocketVals:
    """
    Values the socket requires to communicate with the supply. Contains default values except for the IP Address.

    Args:
    SUPPLY_IP (str): IP Address of the power supply
    SUPPLY_PORT (int): Port of the power supply (Default: 8462)
    TIMOUT_SECONDS (int): Timeout after which the socket is closed (Default: 10 Seconds)
    BUFFER_SIZE (int): Maximum number of bytes to read from the socket for the response. (Default: 128)
    """
    SUPPLY_IP:str
    SUPPLY_PORT:int = 8462
    TIMEOUT_SECONDS:int = 10
    BUFFER_SIZE:int = 128

@dataclass
class Limits:
    """
    Limits within which the supply can accept values, populated with default values.
    """
    MAX_VOLT: float = 210 # default
    MIN_VOLT: float = -10
    MAX_CUR: float = 32    #default
    MIN_CUR: float = -10
    MAX_POWER: float = 3000
    MIN_POWER: float = -10

@dataclass
class VCP:
    """
    Stores Values for voltage current and power
    """
    voltage:float = 0
    current:float = 0
    power:float = 0


class SupplyCommunication:
    """
    Handles communication with power supply.
    
    Args:
        IP(str): IP Address as String, in the Format: 192.168.178.1, expects no subnet mask!
    """
    def __init__(self, IP:str, port = SocketVals.SUPPLY_PORT, timeout = SocketVals.TIMEOUT_SECONDS):
        """
        Initialzie the communication. All attributes but IP are optional. Not specified attributes will be read from dataclass SocketVals.
        """
        self.socketvalues = SocketVals(IP, port, timeout)
        self.valuelimits = Limits()
        self.setpoints = VCP()
        if CheckVISA(IP):
            self.socket = OpenVISASocket(self.socketvalues)
            self.type = "VISA_TCP"
        else:
            self.socket = OpenSocket(self.socketvalues)
            self.type = "RAW_TCP"
        self.measuredpoints = VCP()
    def setValues(self, U = None, I = None, P = None):
        """
        Sets all values, checks if value is within self.valuelimits. 
        All Values are optional. If none given the method will take the last value given. If none are given standard values from dataclass will be used.
        Attributes:
            U (float): Voltage to set the output to
            I (float): Current to set the output to
            P (float): Power to set the output to
        """
        if U is not None:
            self.setpoints.voltage = U
        if I is not None:
            self.setpoints.current = I
        if P is not None:
            self.setpoints.power = P
        set_checked(self.setpoints, self.valuelimits, self.socket, self.type)
    def setLimits(self, limits:Limits):
        """
        Set limits to limits. Expects Limits data object. Checks if each MIN limit is smaller and not equal to the MAX limit.
        Attributes:
            limits (Limits): Object of the class Limits
        Raises:
            Exception: if any MIN value is larger or euqal to a MAX value the programm will crash
        """
        if limits.MIN_VOLT >= limits.MAX_VOLT:
            raise Exception(f"Error! MIN_VOLT ({limits.MIN_VOLT}) larger or equal to MAX_VOLT ({limits.MAX_VOLT})")
        if limits.MIN_CUR >= limits.MAX_CUR:
            raise Exception(f"Error! MIN_CUR ({limits.MIN_CUR}) larger or equal to MAX_CUR ({limits.MAX_CUR})")
        if limits.MIN_POWER >= limits.MAX_POWER:
            raise Exception(f"Error! MIN_CUR ({limits.MIN_POWER}) larger or equal to MAX_CUR ({limits.MAX_POWER})")
        self.valuelimits = limits
    def measureValues(self):
        """
        Measures all voltages and saves the result in self.measuredpoints
        """
        self.measuredpoints.voltage = float(measureVoltage(self.socket))
        self.measuredpoints.current = float(measureCurrent(self.socket))
        self.measuredpoints.power = float(measurePower(self.socket))
    def sendOnly(self, command:str):
        """
        Send raw scpi command to supply without expecting a response. 
        WARNING! No checks are performed when calling this method.
        """
        sendCommand(command, self.socket)

    def sendReceive(self, command:str) -> str:
        """
        Send raw scpi command to supply and output response as string.
        WARNING! No checks are performed when calling this method. Result will not be saved in object.
        """
        return sendAndReceiveCommand(command, self.socket)


def OpenSocket(socketvals:SocketVals):
    """
    Create and return a connected TCP socket.

    Args:
    SocketVals: Dataclass which contains all values needed to establish a connection

    Returns:
    socket.socket: A connected TCP socket with timeout set.

    """

    # Add attribute BUFFER_SIZE to socket.socket before creating an object from it
    socket.socket.buffer_size = socketvals.BUFFER_SIZE
    supplySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # set up socket
    supplySocket.connect((socketvals.SUPPLY_IP, socketvals.SUPPLY_PORT)) # connect socket
    supplySocket.settimeout(socketvals.TIMEOUT_SECONDS)
    return supplySocket

def OpenVISASocket(socketvals:SocketVals):
    """
    Create and return a connected TCP VISA socket.

    Args:
    SocketVals: Dataclass which contains all values needed to establish a connection, all values except SUPPLY_IP are ignored since they are not necessary.

    Returns:
    socket.socket: A connected TCP socket with timeout set.

    """
    # check all available instruments that are visa, specifies to use the PyVISA-py backend
    rm = pyvisa.ResourceManager('@py')
    # search all available VISA devices for a TCPIP device matching the IP set in SocketVals
    matching_available_devices = rm.list_resources(f"TCPIP::{socketvals.SUPPLY_IP}")
    # put amount of matching devices in own 
    matching_devices_amount = len(matching_available_devices)
    match matching_devices_amount:
        case 0:
            raise Exception(f"Error! No VISA TCP/IP Device matching the IP: {socketvals.SUPPLY_IP}!")
        case 1:
            #print(matching_available_devices[0])
            VISASocket = rm.open_resource(matching_available_devices[0])
        case _:
            raise Exception(f"Error! {matching_devices_amount} Devices matching the IP Address! Matching devices: {matching_available_devices}")

    return VISASocket

def CheckVISA(IP: str):
    """
    Checks if there is a VISA device with a matching IP Address.

    Args:
    IP(str): IP Address that is to be checked.
    Returns:
    TRUE: IP Address belongs to one or more VISA devices.
    FALSE: IP Address doesn't belong to a VISA device.
    """
    if len(pyvisa.ResourceManager('@py').list_resources(f"TCPIP::{IP}")) > 0:
        return True
    return False


def sendAndReceiveCommand(msg: str, supplySocket) -> str:
    """
    Send a command string over a socket, then receive and return the response.

    Args:
    msg (str): Command text to send (without trailing newline). A newline will be appended automatically.
    supplySocket: object of class socket.socket

    Returns:
    str: Decoded response from the socket with trailing newline and whitespace stripped.

    """
    msg =  msg + "\n"
    supplySocket.sendall(msg.encode("UTF-8"))
    return supplySocket.recv(supplySocket.buffer_size).decode("UTF-8").rstrip()


# set value without receiving a response
def sendCommand(msg: str, supplySocket, type:str) -> None:
    """
    Send a command string over a socket.

    Args:
    msg (str): Command text to send (without trailing newline). A newline will be appended automatically.
    supplySocket: Connected socket-like object with .sendall(bytes) method (e.g., socket.socket).
    type (string): Type of the communication, e.g.: VISA_TCP, RAW_TCP

    Returns:
    None
    """
    match type:
        case "RAW_TCP":
            msg =  msg + "\n"
            supplySocket.sendall(msg.encode("UTF-8"))
        case "VISA_TCP":
            supplySocket.write(msg)


def setRemoteShutdownState(state:bool, supplySocket):
    """
    Args:
    state (bool): Desired remote shutdown state. True to enable remote shutdown (sends "SYST:RSD 1"); False to disable remote shutdown (sends "SYST:RSD 0").
    supplySocket: Connected socket-like object with .sendall(bytes) method (e.g., socket.socket).

    Returns:
    None
    """

    if state:
        sendCommand("SYST:RSD 1", supplySocket)
    else:
        sendCommand("SYST:RSD 0", supplySocket)


def setVoltage(volt:float, MAX_VOLT:float, MIN_VOLT:float, supplySocket, type:str) -> int:
    """
    Sets the voltage to the specified value if it is within the allowed range.

    Args:
    volt (float): The voltage value to set.
    MAX_VOLT (float): The maximum allowed voltage.
    MIN_VOLT (float): The minimum allowed voltage.
    supplySocket: Connected socket-like object with .sendall(bytes) method (e.g., socket.socket).
    type (string): Type of the communication, e.g.: VISA_TCP, RAW_TCP

    Returns:
    int: 0 if the voltage was set successfully, -1 if the voltage is out of range.
    """
    retval = 0
    if volt >= MIN_VOLT and volt <= MAX_VOLT:
        sendCommand("SOUR:VOLT {0}".format(volt), supplySocket,type)
    else:

        retval = -1

    return retval


def setCurrent(cur:float, MAX_CUR:float, MIN_CUR:float, supplySocket, type:str) -> int:
    """
    Sets the current to the specified value if it is within the allowed range.

    Args:
    cur (float): The current value to set.
    MAX_CUR (float): The maximum allowed current.
    MIN_CUR (float): The minimum allowed current.
    supplySocket: Connected socket-like object with .sendall(bytes) method (e.g., socket.socket).
    type (string): Type of the communication, e.g.: VISA_TCP, RAW_TCP

    Returns:
    int: 0 if the current was set successfully, -1 if the current is out of range.
    """
    retval = 0
    if cur >= MIN_CUR and cur <= MAX_CUR:
        sendCommand("SOUR:CUR {0}".format(cur), supplySocket, type)
    else:
        retval = -1

    return retval
# set positive power, check if command is given valid number
def setPowerPos(power:float, MAX_POWER:float, MIN_POWER:float, supplySocket, type:str):
    """
    Sets the power to the specified value if it is within the allowed range.

    Args:
    power (float): The power value to set.
    MAX_POWER (float): The maximum allowed power.
    MIN_POWER (float): The minimum allowed power.
    supplySocket: The socket to which the command should be sent.
    type (string): Type of the communication, e.g.: VISA_TCP, RAW_TCP

    Returns:
    int: 0 if the power was set successfully, -1 if the power is out of range.
    """
    retval = 0
    if power >= MIN_POWER and power <= MAX_POWER:
        sendCommand("SOUR:POW {0}".format(power), supplySocket, type)
    else:
        retval = -1
    return retval


def readVoltage(supplySocket) -> float:
    """
    Query the power supply for its maximum output voltage.

    Args:
    supplySocket: The socket to which the command should be sent.

    Returns:
    float: The configured maximum output voltage parsed from the device response.
    """
    return sendAndReceiveCommand("SOUR:VOLT?", supplySocket)

def readCurrent(supplySocket) -> float:
    """
    Query the power supply for its maximum output current.

    Args:
    supplySocket: The socket to which the command should be sent.

    Returns:
    float: The configured maximum output current parsed from the device response.
    """
    return sendAndReceiveCommand("SOUR:CUR?", supplySocket)

def measureVoltage(supplySocket) -> float:
    """
    Query the measured output Voltage

    Args:
    supplySocket: The socket to which the command should be sent.

    Returns:
    float: The measured output voltage parsed from the device response.
    """
    return sendAndReceiveCommand("MEAS:VOL?", supplySocket)

def measureCurrent(supplySocket) -> float:
    """
    Query the measured output Current

    Args:
    supplySocket: The socket to which the command should be sent.

    Returns:
    float: The measured output current parsed from the device response.
    """
    return sendAndReceiveCommand("MEAS:CUR?", supplySocket)

def measurePower(supplySocket) -> float:
    """
    Query the measured output Power

    Args:
    supplySocket: The socket to which the command should be sent.

    Returns:
    float: The measured output power parsed from the device response.
    """
    return sendAndReceiveCommand("MEAS:POW?", supplySocket)



def setProgSourceV(src:str, supplySocket) -> int:
    """
    Set the voltage source on the power supply.

    Args:
    src (str): The source identifier to set (must be one of the entries in `validSrcList`, e.g., a string like "front" or "web").
    supplySocket: The socket to which the command should be sent.

    Returns:
    int: 0 on success (command sent), -1 if `src` is not in `validSrcList`.
    """

    retval = 0
    if src in validSrcList:
        sendCommand("SYST:REM:CV {0}".format(src), supplySocket)

    else:
        retval = -1
    return retval


def setProgSourceI(src:str, supplySocket) -> int:
    """
    Set the current source on the power supply.
    Args:
    src (str): The source identifier to set (must be one of the entries in `validSrcList`, e.g., a string like "front" or "web").
    supplySocket: The socket to which the command should be sent.   

    Returns:
    int: 0 on success (command sent), -1 if `src` is not in `validSrcList`.

    """
    retval = 0
    if src.lower() in validSrcList:
        sendCommand("SYST:REM:CC {0}".format(src), supplySocket)
    else:
        retval = -1
    return retval

#set source of max pos power
def setProgSourceP(src:str, supplySocket) -> int:
    """
    Set the power source on the power supply.

    Args:
    src (str): The source identifier to set (must be one of the entries in `validSrcList`, e.g., a string like "front" or "web").
    supplySocket: The socket to which the command should be sent.   

    Returns:
    int: 0 on success (command sent), -1 if `src` is not in `validSrcList`.

    """
    retval = 0
    if src.lower() in validSrcList:
        sendCommand("SYST:REM:CP {0}".format(src), supplySocket)
    else:
        retval = -1
    return retval

def setOutputState(state:bool, supplySocket):
    """
    Enable or disable the power supply output.

    Args:
    state (bool): Desired output state. True to enable the output (sends command "OUTPUT 1"), False to disable the output (sends "OUTPUT 0").
    supplySocket: The socket to which the command should be sent.   

    Returns:
    None
    """
    if state:
        sendCommand("OUTPUT 1", supplySocket)

    else:
        sendCommand("OUTPUT 0", supplySocket)

def closeSocket(supplySocket):
    """
    Closes the socket and ends the connection the power supply.

    Args:
    supplySocket: The socket to which the command should be sent.   

    Returns:
    None
    """
    supplySocket.close()

def set_checked(setpoints:VCP, limits:Limits, socket:socket,type:str):
    """
    Checks if the set points for voltage current and power are within the given limits. Sets the power supply connected to socket to that value.

    Args:
    setpoints (SetPoints): dataclass containing current voltage and power
    limits (Lmits): dataclass containing the correstponding limits.
    socket (socket):  dataclass containting the connected socket.
    Raises:
    Exception: if a value of setpoints is out of range set by limits
    """
    # if the current or voltage is out of range, put everything to zero and end
    if setCurrent(setpoints.current, limits.MAX_CUR, limits.MIN_CUR, socket, type) == -1:
        emergency_off(limits, socket)
        raise Exception(f"Fault! Attempted to set current {setpoints.current} outside range [{limits.MIN_CUR}, {limits.MAX_CUR}]!")
    if setVoltage(setpoints.voltage, limits.MAX_VOLT, limits.MIN_VOLT, socket, type) == -1:
        emergency_off(limits, socket)
        raise Exception(f"Fault! Attempted to set voltage {setpoints.voltage} outside range [{limits.MIN_VOLT}, {limits.MAX_VOLT}]!")
    if setPowerPos(setpoints.power, limits.MAX_POWER, limits.MIN_POWER, socket, type) == -1:
        emergency_off(limits, socket)
        raise Exception(f"Fault! Attempted to set power {setpoints.power} outside range [{limits.MIN_POWER}, {limits.MAX_POWER}]!")

def emergency_off(limits: Limits, socket:socket):
    """
    shuts off everything and closes the socket
    """
    setCurrent(0, limits.MAX_CUR, limits.MIN_CUR, socket)
    setVoltage(0, limits.MAX_VOLT, limits.MIN_VOLT, socket)
    setPowerPos(0, limits.MAX_POWER, limits.MIN_POWER, socket)
    closeSocket(socket)
