#wraps the drivers into a class that can be called to edit the values within the power supply, currently designed to work with a DE SM210-CP-150 and TTI QPX1200SP
import shared

class SupplyCommunication:
    """
    Handles communication with power supply.
    
    Args:
        IP(str): IP Address as String, in the Format: 192.168.178.1, expects no subnet mask!
        type(str): Type of communication, determines the driver to be used. Supports Auto, EA, VISA_TTI (Default: Auto, automatically check and choose the appropiate driver
    """
    def __init__(self, IP:str, type = shared.SocketVals.TYPE, port = shared.SocketVals.SUPPLY_PORT, timeout = shared.SocketVals.TIMEOUT_SECONDS):
        """
        Initialzie the communication. All attributes but IP are optional. Not specified attributes will be read from dataclass SocketVals.
        """
        self.socketvalues = shared.SocketVals(IP, type, port, timeout)
        self.valuelimits = shared.Limits()
        self.setpoints = shared.VCP()
        self.measuredpoints = shared.VCP()
        # check if the TYPE variable is set and act accordingly
        match self.socketvalues.TYPE:
            case "Auto":
                # if the Auto option is choosen, check if a VISA or TCP/IP Device can be found matching the IP Adress or the IP Adress and port
                # if neither is found, crash accordingly
                if shared.CheckVISA(self.socketvalues.SUPPLY_IP):
                    self.socketvalues.TYPE = "VISA_TTI"
                    import driver_visa
                    self.driver = driver_visa
                    print("VISA Device detected.")
                elif shared.CheckTCP(self.socketvalues.SUPPLY_IP, self.socketvalues.SUPPLY_PORT):
                    self.socketvalues.TYPE = "DE"
                    import driver_scpi_tcp
                    self.driver = driver_scpi_tcp
                    print("DE TCP Device detected.")
                else:
                    raise Exception(f"Error! Neither VISA device nor TCP/IP Device found with Address: {self.socketvalues.SUPPLY_IP}:{self.socketvalues.SUPPLY_PORT} Auto connection failed.")
            # Skips the auto detection and instantly loads a driver
            case "VISA_TTI":
                import driver_visa
                self.driver = driver_visa
            case "DE":
                import driver_scpi_tcp
                self.driver = driver_scpi_tcp
            case _:
                raise Exception(f"Error! Socket Type {self.socketvalues.TYPE} is an invalid choice!")
        self.socket = self.driver.OpenSocket(self.socketvalues)
        
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
        self.driver.set_checked(self.setpoints, self.valuelimits, self.socket)
    def setLimits(self, limits:shared.Limits):
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
        self.measuredpoints.voltage = float(self.driver.measureVoltage(self.socket))
        self.measuredpoints.current = float(self.driver.measureCurrent(self.socket))
        self.measuredpoints.power = float(self.driver.measurePower(self.socket))
    def sendOnly(self, command:str):
        """
        Send raw scpi command to supply without expecting a response. 
        WARNING! No checks are performed when calling this method.
        """
        self.driver.sendCommand(command, self.socket)

    def sendReceive(self, command:str) -> str:
        """
        Send raw scpi command to supply and output response as string.
        WARNING! No checks are performed when calling this method. Result will not be saved in object.
        """
        return self.driver.sendAndReceiveCommand(command, self.socket)