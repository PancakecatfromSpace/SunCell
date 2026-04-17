import socket

# heavily modified version of the example provided by delta electronica
# communicates via a TCP socket with SCPI commands as found in the programming manual

validSrcList = ["front", "web", "seq", "eth", "slot1", "slot2", "slot3", "slot4", "loc", "rem"]




def OpenSocket(SUPPLY_IP: str, SUPPLY_PORT, TIMEOUT_SECONDS: int, BUFFER_SIZE: int):
    """
    Create and return a connected TCP socket.

    Args:
    SUPPLY_IP (str): IPv4 address or hostname of the server to connect to.
    SUPPLY_PORT (int): TCP port number on the server.
    TIMEOUT_SECONDS (float): Socket timeout in seconds for blocking operations.
    BUFFER_SIZE (int): Maximum number of bytes to read from the socket for the response.

    Returns:
    socket.socket: A connected TCP socket with timeout set.

    """
    # Add attribute BUFFER_SIZE to socket.socket before creating an object from it
    socket.socket.buffer_size = BUFFER_SIZE
    supplySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # set up socket
    supplySocket.connect((SUPPLY_IP, SUPPLY_PORT)) # connect socket
    supplySocket.settimeout(TIMEOUT_SECONDS)
    return supplySocket


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
def sendCommand(msg: str, supplySocket) -> None:
    """
    Send a command string over a socket.

    Args:
    msg (str): Command text to send (without trailing newline). A newline will be appended automatically.
    supplySocket: Connected socket-like object with .sendall(bytes) method (e.g., socket.socket).

    Returns:
    None
    """

    msg =  msg + "\n"
    supplySocket.sendall(msg.encode("UTF-8"))


def setRemoteShutdownState(state, supplySocket):
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


def setVoltage(volt:float, MAX_VOLT:float, MIN_VOLT:float, supplySocket) -> int:
    """
    Sets the voltage to the specified value if it is within the allowed range.

    Args:
    volt (float): The voltage value to set.
    MAX_VOLT (float): The maximum allowed voltage.
    MIN_VOLT (float): The minimum allowed voltage.
    supplySocket: Connected socket-like object with .sendall(bytes) method (e.g., socket.socket).

    Returns:
    int: 0 if the voltage was set successfully, -1 if the voltage is out of range.
    """
    retval = 0
    if volt >= MIN_VOLT and volt <= MAX_VOLT:
        sendCommand("SOUR:VOLT {0}".format(volt), supplySocket)
    else:

        retval = -1

    return retval


def setCurrent(cur:float, MAX_CUR:float, MIN_CUR:float, supplySocket) -> int:
    """
    Sets the current to the specified value if it is within the allowed range.

    Args:
    cur (float): The current value to set.
    MAX_CUR (float): The maximum allowed current.
    MIN_CUR (float): The minimum allowed current.
    supplySocket: Connected socket-like object with .sendall(bytes) method (e.g., socket.socket).

    Returns:
    int: 0 if the current was set successfully, -1 if the current is out of range.
    """
    retval = 0
    if cur >= MIN_CUR and cur <= MAX_CUR:
        sendCommand("SOUR:CUR {0}".format(cur), supplySocket)
    else:
        retval = -1

    return retval
# set positive power, check if command is given valid number
def setPowerPos(power:float, MAX_POWER:float, MIN_POWER:float, supplySocket):
    """
    Sets the power to the specified value if it is within the allowed range.

    Args:
    power (float): The power value to set.
    MAX_POWER (float): The maximum allowed power.
    MIN_POWER (float): The minimum allowed power.
    supplySocket: The socket to which the command should be sent.

    Returns:
    int: 0 if the power was set successfully, -1 if the power is out of range.
    """
    retval = 0
    if power >= MIN_POWER and power <= MAX_POWER_POS:
        sendCommand("SOUR:POW {0}".format(power), supplySocket)
    else:
        retval = -1
    return retval


def readVoltage(supplySocket) -> float:
    """
    Query the power supply for its output voltage.

    Args:
    supplySocket: The socket to which the command should be sent.

    Returns:
    float: The measured or configured output voltage parsed from the device response.
    """
    return sendAndReceiveCommand("SOUR:VOLT?", supplySocket)

def readCurrent(supplySocket) -> float:
    """
    Query the power supply for its output current.

    Args:
    supplySocket: The socket to which the command should be sent.

    Returns:
    float: The measured or configured output current parsed from the device response.
    """
    return sendAndReceiveCommand("SOUR:CUR?", supplySocket)


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
def setProgSourceP(src, supplySocket) -> int:
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
