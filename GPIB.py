"""Module providing an interface to the GPIB-USB adapter"""
import time
import socket
import serial

class SerialError(Exception):
    """Serial error exception"""

class RemoteSerialError(Exception):
    """Serial error exception"""

class AR488Base():
    """Base class to represent AR488 adapter.
    The AR488 is an Arduino-based USB-GPIB adapter.
    For details see: https://github.com/Twilight-Logic/AR488
    """

    def __init__(self, debug):
        self.address = 0
        self.debug = debug

    def __enter__(self):
        return self

    def send(self, message):
        """Send something to the gpib adapter"""

    def receive(self):
        """Receive something from the gpib adapter"""
        return False

    def write(self, message, sleep=0.2):
        """Write message to GPIB bus."""
        if self.debug:
            print("->", message)
        self.send(message)
        if sleep != 0:
            time.sleep(sleep)

    def read(self):
        """Read from GPIB bus."""
        try:
            tmp = self.receive()
            if self.debug:
                print("<-", "'"+tmp+"'")
            return tmp
        except TimeoutError:
            return False

    def query(self, message, sleep=0.2):
        """Write message to GPIB bus and read results."""

    def set_address(self, address):
        """Specify address of GPIB device with which to communicate.
        When the AR488 is in device mode rather than controller mode, this
        instead sets the address of the AR488.
        """
        self.write(f"++addr {address}")
        self.address = address

    def get_current_address(self):
        """Return the currently specified address."""
        return self.query("++addr")

    def get_idn(self, idn="*IDN?"):
        """Return the currently specified address."""
        self.write(idn)
        return self.query("++read")

    def local(self):
        """Return to local mode"""
        self.write("++loc")

class AR488(AR488Base):
    """Class to represent AR488 USB-GPIB adapter.
    The AR488 is an Arduino-based USB-GPIB adapter.
    For details see: https://github.com/Twilight-Logic/AR488
    """

    def __init__(self, port="/dev/ttyACM3", baudrate=115200, timeout=1, debug=False):
        super().__init__(debug)
        try:
            self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
            self.address = self.query("++addr")
        except (serial.serialutil.SerialException, FileNotFoundError) as e:
            raise SerialError(f"Error opening serial port {port}") from e

    def __del__(self):
        try:
            self.ser.close()
        except AttributeError:
            pass

    def __exit__(self, exc_type, exc_value, exc_tb):
        try:
            self.ser.close()
        except AttributeError:
            pass

    def __str__(self):
        return "GPIB address: " + str(self.address) + ", Port: " +\
            self.ser.name + ", Baud rate: " + str(self.ser.baudrate)

    def send(self, message):
        """Send something to the gpib adapter"""
        self.ser.write(f"{message}\n".encode("ASCII"))

    def receive(self):
        """Receive something from the gpib adapter"""
        return self.ser.readline().decode("UTF-8").strip()

    def read_all(self):
        """Send something to the gpib adapter"""
        return self.ser.read_all().decode("UTF-8").strip()

    def read_lines(self):
        """Send something to the gpib adapter"""
        tmp = []
        while self.ser.in_waiting:
            tmp += self.ser.readline().decode("UTF-8").strip()
        return tmp

    def query(self, message, sleep=0.2):
        """Write message to GPIB bus and read results."""
        self.write(message, sleep)
        self.wait_data()
        return self.read()

    def wait_data(self):
        """Wait for the data to arrive"""
        while not self.ser.in_waiting:
            pass

class AR488Wifi(AR488Base):
    """Class to represent AR488 WiFi-GPIB adapter.
    The AR488 is an Arduino-based USB-GPIB adapter modified with a esp-link for wireless operation
    For details see: https://github.com/Twilight-Logic/AR488
    and: https://github.com/jeelabs/esp-link
    """

    def __init__(self, ip, timeout=1, debug=False):
        super().__init__(debug)
        self.ip = ip
        try:
            socket.setdefaulttimeout(timeout)
            self.session = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.session.connect((self.ip, 23))
            self.address = self.query("++addr")
        except OSError as e:
            if e.errno == 113:
                raise RemoteSerialError(f"Error opening serial port at {self.ip}") from e

    def __del__(self):
        self.session.close()

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.session.close()

    def __str__(self):
        return "GPIB address: " + str(self.address) + ", IP: " + self.ip

    def send(self, message):
        """Send something to the gpib adapter"""
        self.session.sendall(f"{message}\n".encode("ASCII"))

    def receive(self):
        """Receive something from the gpib adapter"""
        return self.session.recv(1024).decode("UTF-8").strip()

    def query(self, message, sleep=0.2):
        """Write message to GPIB bus and read results."""
        self.write(message, sleep)
        return self.read()
