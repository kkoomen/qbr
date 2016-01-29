#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Filename      : colordetection.py
# Author        : Kim K
# Created       : Tue, 26 Jan 2016
# Last Modified : Fri, 29 Jan 2016


from sys import exit as Die
try:
    import sys
except ImportError as err:
    Die(err)

class ColorDetection:

    def get_color_name(self, hsv):
        """ Get the name of the color based on the hue.

        :returns: string
        """
        (h,s,v) = hsv
        if h > 150 or h <= 10:
            return 'red'
        elif h <= 20 and s <= 150:
            return 'white'
        elif h <= 20:
            return 'orange'
        elif h <= 36:
            return 'yellow'
        elif h <= 70:
            return 'green'
        elif h <= 130:
            return 'blue'

        return 'white'

    def average_rgb(self, roi):
        """ Average the RGB colors in a region of interest.

        :param roi: the image array
        :returns: tuple
        """
        red   = 0
        green = 0
        blue  = 0
        num   = 0
        for y in range(len(roi)):
            if y % 10 == 0:
                for x in range(len(roi[y])):
                    if x % 10 == 0:
                        b = roi[y][x]
                        num += 1
                        red += b[0]
                        green += b[1]
                        blue += b[2]
        red /= num
        green /= num
        blue /= num
        return (int(red), int(green), int(blue))

ColorDetector = ColorDetection()
