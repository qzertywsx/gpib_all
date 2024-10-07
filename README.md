# gpib_all
Python module for the AR488 USB-GPIB and WiFi-GPIB converter

# Usage USB-GPIB adapter:
```python
from gpib_all import AR488

gpib = AR488(port="/dev/ttyACM0", baudrate=115200, timeout=2)
gpib.set_address(3)
print(gpib)
print(gpib.get_IDN())
gpib.write("READ?")
print(gpib.query("++read"))
```
Result of executing the above code (Not done yet):
```
GPIB address: 3, Port: /dev/ttyACM0, Baud rate: 115200
```

# Usage Wifi-GPIB adapter:
```python
from gpib_all import AR488Wifi

gpib = AR488Wifi('192.168.178.36', timeout=5)
gpib.set_address(3)
print(gpib)
print(gpib.get_IDN())
gpib.write("READ?")
print(gpib.query("++read"))
```
Result of executing the above code (Not done yet):
```
GPIB address: 3, IP: 192.168.178.36
```

