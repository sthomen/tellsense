# tellsense

Tellsense is a [Net-SNMP](http://www.net-snmp.org) passthrough script that
interfaces with the Telldus TellCore python library to communicate with
telldusd and through connected TellStick devices to 433MHz remote
devices and sensors.

It exposes data from sensors and devices and also enabled SET commands
to write value data to devices enabling remote control of simple outlets
as well as dimmer switches.

Sample snmpd.conf fragment

```
pass_persist .1.3.6.1.4.1.8072.9999.9999.1 /path/to/tellsense.py
```
