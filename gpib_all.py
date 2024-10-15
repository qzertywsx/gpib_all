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

    def wait_for_data(self):
        """Wait for the data to arrive"""
        return False

    def get_buffer(self,
                   show_byte=True # pylint: disable=unused-argument
                  ):
        """Receive all the data from the instrument"""
        return False

    def get_plot_buffer(self, show_byte=True):
        """Get plot data from the instrument (Device-initialed plot)"""
        _buffer = self.get_buffer(show_byte)
        if not isinstance(_buffer, bool):
            return _buffer.decode("UTF-8")
        return False

    def get_plot_file(self, filename, show_byte=True):
        """Get plot data from the instrument (Device-initialed plot) (file .plt)"""
        _buffer = self.get_plot_buffer(show_byte)
        if isinstance(_buffer, bool):
            return False
        with open(filename, "w", encoding="utf-8") as binary_file:
            binary_file.write(_buffer)
        return True

    def get_plc_print_buffer(self, show_byte=True):
        """Get PLC print data from the instrument (Device-initialed print) (file .pcl)"""
        return self.get_buffer(show_byte)

    def get_plc_print_file(self, filename, show_byte=True):
        """Get PLC print data from the instrument (Device-initialed print) (file .pcl)"""
        _buffer = self.get_plc_print_buffer(show_byte)
        if not isinstance(_buffer, bool):
            return False
        with open(filename, "wb") as binary_file:
            binary_file.write(_buffer)
        return True

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

    def query(self, message, sleep=0.2):
        """Write message to GPIB bus and read results."""
        self.write(message, sleep)
        self.wait_for_data()
        return self.read()

    def wait_for_data(self):
        """Wait for the data to arrive"""
        num_retry = 10
        while not self.ser.in_waiting:
            time.sleep(2)
            num_retry -= 1
            if num_retry == 0:
                return False
        return True

    def get_buffer(self, show_byte=True):
        """Receive all the data from the instrument"""
        _buffer = bytearray()
        l = 0
        data = self.wait_for_data()
        if isinstance(data, bool) and not data:
            return False
        while True:
            try:
                data = self.ser.read(256)
            except TimeoutError:
                break
            l += len(data)
            if show_byte:
                print(f"\r{l}", end="")
            if not data:
                break
            _buffer.extend(data)
        if show_byte:
            print()
        return _buffer

class AR488Wifi(AR488Base):
    """Class to represent AR488 WiFi-GPIB adapter.
    The AR488 is an Arduino-based USB-GPIB adapter modified with a esp-link for wireless operation
    For details see: https://github.com/Twilight-Logic/AR488
    and: https://github.com/jeelabs/esp-link
    """

    def __init__(self, ip, timeout=1, debug=False):
        super().__init__(debug)
        self.ip = ip
        self.timeout = timeout
        try:
            socket.setdefaulttimeout(self.timeout)
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

    def wait_for_data(self):
        """Wait until data arrive"""
        num_retry = 10
        while True:
            try:
                data = self.session.recv(1024)
                if data:
                    return data
            except TimeoutError:
                num_retry -= 1
                if num_retry == 0:
                    return False

    def get_buffer(self, show_byte=True):
        """Receive all the data from the instrument"""
        _buffer = bytearray()
        l = 0
        data = self.wait_for_data()
        if isinstance(data, bool):
            return False
        _buffer.extend(data)
        while True:
            try:
                data = self.session.recv(1024)
            except TimeoutError:
                break
            l += len(data)
            if show_byte:
                print(f"\r{l}", end="")
            if not data:
                break
            _buffer.extend(data)
        if show_byte:
            print()
        return _buffer

    def query(self, message, sleep=0.2):
        """Write message to GPIB bus and read results."""
        self.write(message, sleep)
        return self.read()
