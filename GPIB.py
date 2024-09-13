import serial
import time

class AR488(object):
	"""Class to represent AR488 USB-GPIB adapter.
	The AR488 is an Arduino-based USB-GPIB adapter.
	For details see: https://github.com/Twilight-Logic/AR488
	"""

	def __init__(self, port="/dev/ttyACM3", baudrate=115200, timeout=1):
		self.address = 0
		try:
			self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
		except:
			sys.exit("error opening serial port {}".format(port))

	def __del__(self):
		self.ser.close()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, exc_tb):
		self.ser.close()

	def __str__(self):
		return "GPIB address: " + str(self.address) + ", Port: " + self.ser.name + ", Baud rate: " + str(self.ser.baudrate)

	def write(self, message, sleep=0.2):
		"""Write message to GPIB bus."""
		#print(message)
		self.ser.write("{}\r".format(message).encode("ASCII"))
		time.sleep(sleep)

	def read(self):
		"""Read from GPIB bus."""
		return self.ser.readline().decode("UTF-8").strip()

	def query(self, message, sleep=0.2):
		"""Write message to GPIB bus and read results."""
		self.write(message, sleep)
		self.waitData()
		return self.read()

	def set_address(self, address):
		"""Specify address of GPIB device with which to communicate.
		When the AR488 is in device mode rather than controller mode, this
		instead sets the address of the AR488.
		"""
		self.write("++addr {}".format(address))
		self.address = address

	def get_current_address(self):
		"""Return the currently specified address."""
		return self.query("++addr")

	def get_IDN(self, idn="*IDN?"):
		"""Return the currently specified address."""
		self.write(idn)
		return self.query("++read")
	
	def local(self):
		"""Return to local mode"""
		self.write("++loc")
	
	def waitData(self):
		while not self.ser.in_waiting:
			pass
