import logging, os
from datetime import datetime
from time import sleep
from gpiozero import Device, MotionSensor
from gpiozero.pins.mock import MockFactory, MockPin

change_time = .1 # time, in seconds, to change between levels, .1 is default and best effect IMO
brightness_level = 0 # starting level, 0 is brightest, 255 is off
dim_time = 300 # time, in seconds, to dim without presence, default 300 (5 minutes)
off_time = 1200 # time, in seconds, to turn off display, default 1200 (20 minutes)
pir_pin = 11 # gpio pin used by PIR sensor

## You should be able to leave everything below untouched

sample_wait_time_sec = (2/10)
last_time = datetime.now()
diff_seconds = 0
pir_debug = os.environ.get('PIR_DEBUG', 'false')

if pir_debug == 'true':
    logging.basicConfig(level=logging.DEBUG)
    logging.debug('Debugging with mock pins')
    Device.pin_factory = MockFactory()
    pin: MockPin = Device.pin_factory.pin(pir_pin)
    file_driver = "./test_brightness"
else:
    file_driver = "/sys/waveshare/rpi_backlight/brightness"
    logging.basicConfig(level=logging.WARN)

if os.geteuid() != 0:
    if pir_debug == 'true':
        logging.debug('NOT ROOT - in debug mode')
        logging.debug('This will fail in prod mode')
        logging.debug('only test/mock will run')
    else:
        print('NOT ROOT - cannot proceed')
        exit()

pir = MotionSensor(pir_pin)

def lcd_bright():
    if pir_debug == 'true':
        logging.debug('calling lcd_bright')
    global brightness_level
    while brightness_level >= 0:
        with open(file_driver, "w") as bright_file:
            bright_file.write(str(brightness_level))
            bright_file.close()
        sleep(change_time)
        brightness_level -= 10

def lcd_dim():
    if pir_debug == 'true':
        logging.debug('calling lcd_dim')
    global brightness_level
    while brightness_level <= 100:
        with open(file_driver, "w") as bright_file:
            bright_file.write(str(brightness_level))
            bright_file.close()
        sleep(change_time)
        brightness_level += 10

def lcd_off():
    global brightness_level
    if pir_debug == 'true':
        logging.debug('calling lcd_off')
    while brightness_level <= 255:
        with open(file_driver, "w") as bright_file:
            bright_file.write(str(brightness_level))
            bright_file.close()
        sleep(change_time)
        brightness_level += 10

def time_diff(last_time, current_time):
    global diff_seconds
    diff_time = current_time - last_time
    diff_seconds = diff_time.total_seconds()
    return diff_seconds

def pir_activated(channel):
    if pir_debug == 'true':
        logging.debug('Test Activated: motion detected: %s', pir.motion_detected)
        logging.debug('Test Activated: channel: %s', channel)
    lcd_bright()

def pir_deactivated(channel):
    global last_time
    if pir_debug == 'true':
        logging.debug('Test Deactived: motion detected: %s', pir.motion_detected)
        logging.debug('Test Deactivated: channel: %s', channel)
    last_time = datetime.now()
    return last_time

while True:
    pir.when_activated = pir_activated
    pir.when_deactivated = pir_deactivated
    # this is necessary because of the sample_wait configuration (1/10[sec]) in MotionSensor constructor
    # need at least 2/10[sec] to collect sample
    sleep(sample_wait_time_sec)
    if pir_debug == 'true':
        logging.debug('Testing driving pin high')
        pir.pin.drive_high()
        logging.debug('Sleeping for 5s')
        sleep(5)
        logging.debug('Testing driving pin low')
        pir.pin.drive_low()
        logging.debug('Sleeping for 6s')
        sleep(6)
        current_time = datetime.now()
        time_diff(last_time,current_time)
        logging.debug("diff_seconds is : %s" % diff_seconds)
        if (diff_seconds >= 5) and (diff_seconds <= 9):
            lcd_dim()
            logging.debug("Sleeping for 5s")
        sleep(5)
        current_time = datetime.now()
        time_diff(last_time,current_time)
        logging.debug("diff_seconds is : %s" % diff_seconds)
        if (diff_seconds >= 10):
            lcd_off()
            logging.debug("Sleeping for 5s")
        sleep(5)
    else:
        current_time = datetime.now()
        time_diff(last_time,current_time)
        if (diff_seconds >= dim_time) and (diff_seconds <= off_time):
            lcd_dim()
        elif (diff_seconds >= off_time):
            lcd_off()
        else:
            lcd_bright()