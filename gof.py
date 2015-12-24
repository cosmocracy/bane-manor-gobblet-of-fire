#!/usr/bin/env python

import unicornhat as unicorn
import time, math, colorsys
import numpy as np
import random
import RPi.GPIO as GPIO
import time
import web, thread

# Raspberry pin setup (read IR off GPIO physical pin #16 using a pull-down resistor; 1.0sec bounce attenuation)
ir_detector_pin = 16
GPIO.setmode(GPIO.BOARD)
GPIO.setup(ir_detector_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(ir_detector_pin, GPIO.FALLING, bouncetime=1000)

# Unicorn setup
unicorn.brightness(0.7)

# Classes to handle Goblet modes and time-slicing

class GobletMode(object):
	def __init__(self, name):
		self.name = name
	# Abstract method--subclasses implement to provide mode-specific servicing of time slices (and delay, if desired)
	def timeslice(self):
		raise NotImplementedError("Abstract base class--Implement this method!")
		
class FlameMode(GobletMode):
	# Constants related to the flame effect
	flame_hue_spread = 0.05          # +/- 5% hue deviation
	flame_pixel_chg_thresh = 0.5     # 50% pixel attenuation change during fade
	flame_brightness_centroid = 0.5  # 50% brightness for cells as a starting point
	flame_brightness_spread = 0.3	 # +/- 30% brightness deviation
	
	# Constructor for flame-based modes
	def __init__(self, name, hue_centroid):
		self.name = name
		self.hue_centroid = hue_centroid
		
	# Provide flame-specific timeslice handling
	def timeslice(self):
		unicorn.brightness(FlameMode.flame_brightness_centroid + random.random() * FlameMode.flame_brightness_spread)
		# Initialize an 8x8 matrix of random numbers (between 0.0 and 1.0)
		led_matrix = np.random.rand(8,8)
		# For each Y position
		for y in range(8):
			# For each X position
			for x in range(8):
				# Determine (randomly) if this pixel should switch to the new color yet (for a visual fade transition)
				if random.random() > FlameMode.flame_pixel_chg_thresh:
					# Let the hue vary about the flame color's centroid by the spread scaled by the cell's random value
					h = self.hue_centroid + FlameMode.flame_hue_spread * led_matrix[x, y]
					# Lock in color saturation at 80%
					s = 0.8
					# Make the brightness equal to the random value
					v = led_matrix[x, y]
					# Convert HSV/HSB to RGB for the Unicorn hat and break out the R/G/B channels (scaled 0..255)
					rgb = colorsys.hsv_to_rgb(h, s, v)
					r = int(rgb[0]*255.0)
					g = int(rgb[1]*255.0)
					b = int(rgb[2]*255.0)
					# Set the color channels that will be maintained by the Unicorn's PWM
					unicorn.set_pixel(x, y, r, g, b)
		# Now that new values have been specified for the cells, tell the Unicorn to refresh the display from the accumulated frame buffer
		unicorn.show()	
		# Pause the effect so the effect can be seen
		time.sleep(0.1)

class RainbowMode(GobletMode):
	# Constants related to the rainbow effect
	i = 0.0
	offset = 30
		
	# Provide rainbow-specific timeslice handling
	def timeslice(self):
	        RainbowMode.i = RainbowMode.i + 0.3
        	for y in range(8):
                	for x in range(8):
                        	r = 0
	                        g = 0
        	                xy = x + y / 4
                	        r = (math.cos((x+i)/2.0) + math.cos((y+i)/2.0)) * 64.0 + 128.0
                        	g = (math.sin((x+i)/1.5) + math.sin((y+i)/2.0)) * 64.0 + 128.0
	                        b = (math.sin((x+i)/2.0) + math.cos((y+i)/1.5)) * 64.0 + 128.0
        	                r = max(0, min(255, r + RainbowMode.offset))
                	        g = max(0, min(255, g + RainbowMode.offset))
                        	b = max(0, min(255, b + RainbowMode.offset))
	                        unicorn.set_pixel(x,y,int(r),int(g),int(b))
        	unicorn.show()
	        time.sleep(0.01)

# Mode setup (an array of the sequential modes and an index pointing to the current/active mode)
goblet_modes = [ FlameMode('red', 0.05), FlameMode('green', 1.25), FlameMode('teal', 2.35), FlameMode('blue', 2.6), FlameMode('pink', 2.9), RainbowMode('rainbow') ]
goblet_mode_index = 0

while True:
	if GPIO.event_detected(ir_detector_pin):
		goblet_mode_index = (goblet_mode_index + 1) % len(goblet_modes)
		print("Switching to mode: %s" % (goblet_modes[goblet_mode_index].name))

	goblet_mode = goblet_modes[goblet_mode_index]
	goblet_mode.timeslice()
