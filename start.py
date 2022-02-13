import Adafruit_DHT
from ISStreamer.Streamer import Streamer
from ISReader.Reader import Reader
import time
import logging
import datetime
from PyP100 import PyP100

# Initialize Logging
logging.basicConfig(
    filename="tempctrl.log",
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO
)
logging.info("--- Started program ---")

# Script setup here
# ----------------------------------
LOWER_BOUND_DAY = 22.8
UPPER_BOUND_DAY = 25.3
LOWER_BOUND_NIGHT = 21.3
UPPER_BOUND_NIGHT = 23.0
NIGHT_START = datetime.time(23,0,0)
NIGHT_END = datetime.time(7,0,0)
SENSOR_LOCATION_NAME = "<SENSOR NAME>"

# Initial State Credentials
BUCKET_NAME = "<BUCKET NAME>"
BUCKET_KEY = "<BUCKET KEY>"
ACCESS_KEY = "<ACCESS KEY>"
MINUTES_BETWEEN_READS = 5

# Tapo P100 details and credentials
TAPO_IP = "<Local IP of Tapo P100>"
TAPO_USER = "<TAPO LOGIN-EMAIL>"
TAPO_PASS = "<TAPO LOGIN-PASS>"
# -----------------------------------

# Initialize Plug Control
p100 = PyP100.P100(TAPO_IP, TAPO_USER, TAPO_PASS)

def timeInRange(start, end, x):
    """ check if date x is inbetween start and end
    Args:
        start (datetime.time): start time
        end (datetime.time): end time
        x (datetime.time): time to check
    Returns:
        bool: true if x lies inbetween start and end, otherwise false
    """
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end

streamer = Streamer(bucket_name=BUCKET_NAME, bucket_key=BUCKET_KEY, access_key=ACCESS_KEY)
reader = Reader(bucket_key=BUCKET_KEY, access_key=ACCESS_KEY)
p100.handshake()
p100.login()
plugState = p100.getDeviceInfo()

if plugState['result']['device_on'] in (True, False):
    heaterState = int(plugState['result']['device_on'])
else:
    # Initialize to turned off as a fallback
    heaterState = 1

while True:
        events = reader.get_latest()
        if events and events['systemSwitch']['value'] and events['systemSwitch']['value'].lower() != 'off':
        # only do something when system switch is on
            # Initialize Heater State
            try:
                humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 4)
            except Exception:
                logging.warning("Error reading sensor, trying again..")
                continue
            if temperature is None or humidity is None:
                continue
            humidity = float(format(humidity,".2f"))
            temperature = float(format(temperature,".2f"))
            logging.info(f"Temperature (C): {temperature}")
            logging.info(f"Humidity (%): {humidity}")
            streamer.log(SENSOR_LOCATION_NAME + " Humidity(%)", humidity)
            streamer.log(SENSOR_LOCATION_NAME + " Temperature(C)", temperature)
            if timeInRange(NIGHT_START, NIGHT_END, datetime.datetime.now().time()):
                LOWER_BOUND = LOWER_BOUND_NIGHT
                UPPER_BOUND = UPPER_BOUND_NIGHT
                logging.info("Nightmode enabled.")
                streamer.log('nightmodeSwitch', 'on')
                streamer.log('upperBound', UPPER_BOUND)
                streamer.log('lowerBound', LOWER_BOUND)
            else:
                LOWER_BOUND = LOWER_BOUND_DAY
                UPPER_BOUND = UPPER_BOUND_DAY
                logging.info("Nightmode disabled.")
                streamer.log('nightmodeSwitch', 'off')
                streamer.log('upperBound', UPPER_BOUND)
                streamer.log('lowerBound', LOWER_BOUND)
            if temperature < LOWER_BOUND:
                try:
                    p100.handshake()
                    p100.login()
                    currentState = p100.getDeviceInfo()
                    streamer.log("Plug connection", ":white_check_mark:")
                except Exception:
                    logging.info("Error connecting to plug, retrying...")
                    streamer.log("Plug connection", ":no_entry_sign:")
                    continue
                if currentState['result']['device_on'] is not True:
                    p100.turnOn()
                    logging.info(f"Temperature dropped below {LOWER_BOUND}C ({temperature}C), turning on heater.")
                streamer.log("Heater", 1)
                heaterState = 1
            elif temperature > UPPER_BOUND:
                try:
                    p100.handshake()
                    p100.login()
                    currentState = p100.getDeviceInfo()
                    streamer.log("Plug connection", ":white_check_mark:")
                except Exception:
                    logging.info("Error connecting to plug, retrying")
                    streamer.log("Plug connection", ":no_entry_sign:")
                    continue
                if currentState['result']['device_on'] is not False:
                    p100.turnOff()
                    logging.info(f"Temperature went above {UPPER_BOUND}C ({temperature}C), turning off heater.")
                streamer.log("Heater", 0)
                heaterState = 0
            else:
                logging.info(f"Temperature is within bounds, heater state is {heaterState} (0=off/1=on), no heater control necessary.")
                streamer.log("Heater", heaterState)

            streamer.flush()
        else:
            logging.info(f"System switch is off, nothing to do (last heater state: {heaterState} (0=off/1=on)")
        time.sleep(60*MINUTES_BETWEEN_READS)
