#!/usr/bin/env python

import unicornhat as unicorn
import time, math, colorsys
import numpy as np
import random
import RPi.GPIO as GPIO
import time
import web, thread
import Enum

# Raspberry pin setup
ir_detector_pin = 16
GPIO.setmode(GPIO.BOARD)
GPIO.setup(ir_detector_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(ir_detector_pin, GPIO.FALLING, bouncetime=1000)

# Constants related to visual effects
modes = Enum('flame-red', 'flame-green', 'flame-teal', 'flame-blue', 'flame-pink', 'rainbow')
hue_spread = 0.05          # +/- 5% hue deviation
hue_centroid_red   = 0.05
hue_centroid_green = 1.25
hue_centroid_gof  = 2.35
hue_centroid_blue  = 2.6
hue_centroid_pink  = 2.9
pixel_chg_thresh = 0.5
brightness_centroid = 0.5
brightness_spread = 0.3

mode_flame_red
mode_rainbow = 5
rainbow_i = 0.0
rainbox_offset = 30


modes = [hue_centroid_red, hue_centroid_green, hue_centroid_gof, hue_centroid_blue, hue_centroid_pink, mode_rainbow]
unicorn.brightness(0.7)


mode_index = 0


while True:
	if GPIO.event_detected(ir_detector_pin):
		centroid_index = (centroid_index + 1) % len(centroids)
		print("Switching to centroid: %s" % (centroids[centroid_index]))

	if centroid_index == mode_rainbow:
	        i = i + 0.3
        	for y in range(8):
                	for x in range(8):
                        	r = 0#x * 32
	                        g = 0#y * 32
        	                xy = x + y / 4
                	        r = (math.cos((x+i)/2.0) + math.cos((y+i)/2.0)) * 64.0 + 128.0
                        	g = (math.sin((x+i)/1.5) + math.sin((y+i)/2.0)) * 64.0 + 128.0
	                        b = (math.sin((x+i)/2.0) + math.cos((y+i)/1.5)) * 64.0 + 128.0
        	                r = max(0, min(255, r + offset))
                	        g = max(0, min(255, g + offset))
                        	b = max(0, min(255, b + offset))
	                        unicorn.set_pixel(x,y,int(r),int(g),int(b))
        	unicorn.show()
	        time.sleep(0.01)
	else:
		unicorn.brightness(brightness_centroid + random.random() * brightness_spread)
		rand_mat = np.random.rand(8,8)	
		for y in range(8):
			for x in range(8):
				if random.random() > pixel_chg_thresh:
					#h = 0.1 * rand_mat[x, y]
					#h = hue_centroid_blue + hue_spread * rand_mat[x, y]
					h = centroids[centroid_index] + hue_spread * rand_mat[x, y]
					s = 0.8
					v = rand_mat[x, y]
					rgb = colorsys.hsv_to_rgb(h, s, v)
					r = int(rgb[0]*255.0)
					g = int(rgb[1]*255.0)
					b = int(rgb[2]*255.0)
					unicorn.set_pixel(x, y, r, g, b)
		unicorn.show()	
		time.sleep(0.1)
