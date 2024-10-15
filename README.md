# gpib_all
Python module for the AR488 USB-GPIB and WiFi-GPIB converter

## Supported command:
### set_address(address):
Specify address of GPIB device with which to communicate.

When the AR488 is in device mode rather than controller mode, this instead sets the address of the AR488.

### get_current_address():
Return the currently specified address.

### get_idn(idn="*IDN?"):
Return the currently specified address.

`idn` is the command for read the idn string of the instrument (default: *IDN?)

### local():
Return to local mode

### write(message, sleep=0.2):
Write `message` to GPIB bus.

`sleep` is a delay after sending the message (some instrument require same delay)

### read():
Read from GPIB bus.

### query(message, sleep=0.2):
Write `message` to GPIB bus and read results.

`sleep` is a delay after sending the message (some instrument require same delay)

### wait_for_data():
Wait for the data to arrive

### get_buffer(show_byte=True):
Receive all the data from the instrument

with `show_byte` you can see on the terminal how many bytes are received

### get_plot_buffer(show_byte=True):
Get plot data from the instrument (Device-initialed plot)

with `show_byte` you can see on the terminal how many bytes are received

### get_plot_file(filename, show_byte=True):
Get plot data from the instrument (Device-initialed plot) (file .plt)

with `show_byte` you can see on the terminal how many bytes are received

### get_plc_print_buffer(show_byte=True):
Get PLC print data from the instrument (Device-initialed print) (file .pcl)

with `show_byte` you can see on the terminal how many bytes are received

### get_plc_print_file(filename, show_byte=True):
Get PLC print data from the instrument (Device-initialed print) (file .pcl)

with `show_byte` you can see on the terminal how many bytes are received

# Usage USB-GPIB adapter:
```python
from gpib_all import AR488

gpib = AR488(port="/dev/ttyACM2", timeout=5)
print(gpib)
gpib.set_address(8)
print(gpib.query("++ver"))
gpib.write("++eor 2")
gpib.write("*IDN?")
print(gpib.query("++read"))
```
Result of executing the above code:
```
GPIB address: 1, Port: /dev/ttyACM2, Baud rate: 115200
AR488 GPIB controller, ver. 0.51.29, 18/03/2024
HEWLETT-PACKARD,54620A,0,A.01.30
```

# Usage Wifi-GPIB adapter:
```python
from gpib_all import AR488Wifi

gpib = AR488Wifi('192.168.178.36', timeout=5)#, debug=True)
print(gpib)
gpib.set_address(8)
print(gpib.query("++ver"))
gpib.write("++eor 2")
gpib.write("*IDN?")
print(gpib.query("++read"))
```
Result of executing the above code:
```
GPIB address: 8, IP: 192.168.178.36
AR488 GPIB controller, ver. 0.51.29, 18/03/2024
HEWLETT-PACKARD,54620A,0,A.01.30
```

