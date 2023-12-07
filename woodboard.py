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

sample_wait_time_sec = (2/10) # may not need to be a var, do not recommend changing
last_time = datetime.now() # instantiate variable with current time
diff_seconds = 0 # instantiate variable
pir_debug = os.environ.get('PIR_DEBUG', 'false') # if we haven't set the env var, default to false

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

def sleeper(sleep_time):
        """
        sleeps for time and logs if debugging.
        We do these things so often this consolidates a bit
        """
        logging.debug('Sleeping for %ss' % sleep_time)
        sleep(sleep_time)

def lcd_bright():
    """
    brings the LCD up to full brightness
    """
    global brightness_level
    logging.debug('calling lcd_bright')
    while brightness_level >= 0:
        with open(file_driver, "w") as bright_file:
            bright_file.write(str(brightness_level))
        sleeper(change_time)
        brightness_level -= 10

def lcd_dim():
    """
    dims the lcd to approx half brightness
    """
    global brightness_level
    logging.debug('calling lcd_dim')
    while brightness_level <= 100:
        with open(file_driver, "w") as bright_file:
            bright_file.write(str(brightness_level))
        sleeper(change_time)
        brightness_level += 10

def lcd_off():
    """
    turns the backlight off completely
    """
    global brightness_level
    logging.debug('calling lcd_off')
    while brightness_level <= 255:
        with open(file_driver, "w") as bright_file:
            bright_file.write(str(brightness_level))
        sleeper(change_time)
        brightness_level += 10

def time_diff(last_time, current_time):
    """
    figures out how many seconds have elapsed between two times
    returns a much higher precision that we really need, but whatevs
    """
    global diff_seconds
    diff_time = current_time - last_time
    diff_seconds = diff_time.total_seconds()

def pir_activated(channel):
    """
    called when the PIR is activated
    currently just calls func to bring lcd to full bright
    could be useful for other detection features
    """
    logging.debug('Test Activated: motion detected: %s', pir.motion_detected)
    logging.debug('Test Activated: channel: %s', channel)
    lcd_bright()

def pir_deactivated(channel):
    """
    called when PIR is brought low / no activity
    currently just stamps some time used for determining dimming 
    but could be useful for other detection features
    """
    global last_time
    logging.debug('Test Deactived: motion detected: %s', pir.motion_detected)
    logging.debug('Test Deactivated: channel: %s', channel)
    last_time = datetime.now()

while True:
    pir.when_activated = pir_activated
    pir.when_deactivated = pir_deactivated
    # this is necessary because of the sample_wait configuration (1/10[sec]) in MotionSensor constructor
    # need at least 2/10[sec] to collect sample
    sleeper(sample_wait_time_sec)
    if pir_debug == 'true':
        # everything here is for testing/debugging only, values are much shorter by design
        # pin high is the result of the PIR detecting presence/motion
        logging.debug('Testing driving pin high')
        pir.pin.drive_high()
        sleeper(5)
        # pin low is lack of presence/motion
        logging.debug('Testing driving pin low')
        pir.pin.drive_low()
        # using 6 here because we don't have perfect precision and 5 + 5 is sometimes <10
        sleeper(6)
        current_time = datetime.now()
        time_diff(last_time,current_time)
        logging.debug("diff_seconds is : %s" % diff_seconds)
        # this checks our time elapsed with pin low and should fall within the dim threshold
        if (diff_seconds >= 5) and (diff_seconds <= 9):
            lcd_dim()
        sleeper(5)
        current_time = datetime.now()
        time_diff(last_time,current_time)
        logging.debug("diff_seconds is : %s" % diff_seconds)
        # checking time elapsed again, should now be over our backlight off threshold
        if (diff_seconds >= 10):
            lcd_off()
        sleeper(5)
    else:
        current_time = datetime.now()
        time_diff(last_time,current_time)
        if (diff_seconds >= dim_time) and (diff_seconds <= off_time):
            lcd_dim()
        elif (diff_seconds >= off_time):
            lcd_off()
        else:
            lcd_bright()