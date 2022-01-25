# Bang-Bang Temperature Control
Python implementation of a bang-bang control system using a Raspberry Pi, a DHT22 temperature sensor and a Tapo P100 SmartPlug.
The project is inspired by the following [Medium article](https://medium.com/initial-state/how-to-build-a-raspberry-pi-temperature-monitor-8c2f70acaea9).

## Functions
 - Control (on/off) of an electric room heater based on whether the room temperature is within a specified temperature band or not
 - Night mode - adapted temperature band during night hours
 - Dashboard to remotely read system state and control to switch on/off system remotely
 
 ## Hardware
 - Raspberry Pi Zero W or better with Raspbian
 - DHT22 temperature sensor (connect data pint to GPIO4 (pin 7), V+ to pin 2 and V-/GND to pin 6)

## Before running
- Create an [InitialState](https://www.initialstate.com/) account (free membership for students)
- Install dependencies using the following shell commands:
    - ``sudo apt install python-pip`` (if not already installed)
    - ``\curl -sSL https://get.initialstate.com/python -o - | sudo bash`` - when asked if you want an exampe file, type ``n`` and ``Enter``, then type ``2`` and ``Enter`` to select the [NEW!] option and enter your InitialState credentials
    - ``pip3 install ISStreamer``
    - ``pip3 install ISReader``
    - ``pip3 install adafruit-circuitpython-dht``
    - ``sudo apt-get install libgpiod2``

## Running the script:
- let it run in the background (detached from shell) using e.g. nohup (``nohup python3 start.py &``)
- install it as a service (better :+1:)
