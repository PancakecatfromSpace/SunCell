# shared dataclasses used by both VISA and raw TCP/IP drivers
from dataclasses import dataclass
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