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
            #print(matching_available_devices[0])
            VISASocket = rm.open_resource(matching_available_devices[0])
        case _:
            raise Exception(f"Error! {matching_devices_amount} Devices matching the IP Address! Matching devices: {matching_available_devices}")

    return VISASocket
