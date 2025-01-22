# Woodboard

A little project to add PIR to a DAKboard build, which enables automatic brightness adjustment for the Waveshare 10.1" DSI Toucscreen LCD. Should/may work with other ACPI displays that allow manipulation of backlight levels via `/sys/class/backlight/`

## Notes

There are some assumptions made here:
- Your user is `pi` and that you are cloning this in to /home/pi/woodboard/
- You are using a compatible PIR sensor and it is correctly connected to GPIO 11
- That this is a raspberry pi, which comes with `gpiozero` by default
- You are actually using a Waveshare 10.1" DSI Touchscreen LCD (see hardware)
- You understand that in order for this script to work correctly, it MUST run as root

## Installation

If all the assumption above are correct, you should be able to clone this repo and run `bash install.sh`

This will install the service (which runs as *root*) and will begin watching the PIR and adjusting brightness.

## Installation (advanced)

If for some reason you aren't using the user `pi`, or the path is different, edit `woodboard.service` before you install

## Customizing

If you want to change the pin assignment, or the timer values for the dimmer, edit `woodboard.py` variables.

## Testing
### Without a PIR

You can run this script interactively in "debug" mode by setting the environment variable `PIR_DEBUG=true`. 

When running the script, it will not require you to run it as root, or have any type of hardware connected. Program
output is logged on screen. You can also `tail -f ./test_brightness` to see the values as they are written in real time. 

### Testing Transitions

The "official" Waveshare method of changing brightness from the CLI is via a simple `echo`.

If you want to test transition speeds, there is a bash script included, `test.sh`

example: `sudo bash test.sh -m bright -t .5` would test the brighten effect with a .5 second delay (slow!)
Running without any flags demos the dim with .1 second delay

## Hardware

My DAKboard build uses the following components - the only hard requirement for this is the LCD

- [Waveshare 10.1 Capacitive Touch Display for Raspberry Pi 1280x800 IPS, DSI Interface](https://www.waveshare.com/10.1inch-DSI-LCD-C.htm)
- [HiLetgo Mini SR602 Motion Sensor Detector (Amazon)](https://www.amazon.com/HiLetgo-Detector-Pyroelectric-Infrared-Sensitivity/dp/B07VLFL5VP)
- Raspberry Pi 4 (3 would work just as well)
- 90º / right angle USB-C cable for power (display is portrait, keeps cable tidy)

All of this is mounted in a custom picture frame, with hole for PIR, and hanging in our kitchen.

## Additional Notes

### Operating System / DAKboard
If you decide to go this route, be aware that the DAKboardOS is a slightly dated distro and the waveshare driver install doesn't play smoothly. I highly recommend doing your own DAKboard install. 

Good directions can be found [Here](https://pimylifeup.com/raspberry-pi-dakboard/)

A few deviations from this article:
I chose to use the 64-bit Raspberry Pi OS (the Pi4 supports this), and newer versions of Raspberry Pi OS default to Wayland. This article was written around X11. You have two options, adapt the article to Wayland, or switch back to X11. If you choose to switch back to X11, this is easily done by running `sudo raspi-config`, under "Advanced", switch it. 

### Drivers
~~You can find directions for setting up the Waveshare LCD [Here](https://www.waveshare.com/wiki/10.1inch_DSI_LCD_(C)#Method_1:_Install_Manually)~~ (Skip all this, drivers are built in now)

add the following to `/boot/config.txt`

`dtoverlay=vc4-kms-dsi-waveshare-panel,10_1_inchC,i2c10,sizex=800,sizey=1280`

`dtoverlay=vc4-kms-v3d`

I don't recommend going with the prebuilt image. 

### Hardware Troubleshooting
Kind of outside the scope of this project, but figured I would share some extra bits

- Display doesn't turn on
Double check that you have the DSI ribbon inserted correctly - it's possible to put in backwards 💀

- No touch screen
Double check the pogo pin contact with the PCB on the Waveshare. It's possible to mount the Pi uneven/slightly off and not obtain good contact. 
Double check the i2c bus you are using, `i2cdetect` can help with this (google further instructions)
