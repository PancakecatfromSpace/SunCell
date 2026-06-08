from shared import SocketVals, VCP, Limits
import pyvisa

def OpenSocket(socketvals:SocketVals):
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
            match socketvals.CMD_LOOKUP:
                case "tti":
                    #This is stupid but necessary if the supply has a half assed implementation of the full VXI-11 Standard. 
                    #In this case the manufacturer TTI didn't bother to implement the VXI-11 Dicovery Protocoll. 
                    #See QPX1200S_SP Manual under the sections VXI-11 Discovery Protocoll and VISA Resource-Name for more details.
                    VISASocket = rm.open_resource(f"TCPIP::{socketvals.SUPPLY_IP}::{socketvals.SUPPLY_PORT}::SOCKET")

                case _:
                    #print(matching_available_devices[0])
                    VISASocket = rm.open_resource(matching_available_devices[0])                    
        case _:
            raise Exception(f"Error! {matching_devices_amount} Devices matching the IP Address! Matching devices: {matching_available_devices}")                    
    #set the termination socket to the value specified in SocketVals
    VISASocket.read_termination = socketvals.TERMINATION_STRING
    return VISASocket

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
    #supplySocket.sendall(msg.encode("UTF-8"))
    return supplySocket.query(msg)