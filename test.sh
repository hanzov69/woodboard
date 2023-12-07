#!/bin/bash
Help()
{
   # Display Help
   echo "options:"
   echo "m     mode, bright or dim, default is dim"
   echo "t     delay, in seconds, default is .1"
   echo
}

mode="dim"
delay=.1

while getopts ":hm:t:" option; do
	case $option in
		h) # display Help
			Help
			exit;;
		m) # mode
			mode=$OPTARG;;
		t) # delay time
			delay=$OPTARG;;
		\?) # invalid
			echo "Error: Invalid Option, try -h for help"
			exit;;
	esac
done

if [[ "$mode" == "bright" ]]
	then
		x=255
		while [ $x -ge 0 ]
		do
			echo $x > /sys/waveshare/rpi_backlight/brightness
			sleep $delay
			x=$(( x - 10 ))
		done
elif [[ "$mode" == "dim" ]]
	then
		x=0
		while [ $x -le 255 ]
		do
			echo $x > /sys/waveshare/rpi_backlight/brightness
			sleep $delay
			x=$(( x + 10 ))
		done
else
	echo "Invalid Mode!"
fi