#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: fenc=utf-8 ts=4 sw=4 et


import color_params

class ColorDetection:

    def get_color_name(self, hsv):
        """ Get the name of the color based on the hue.

        :returns: string
        """
        (h,s,v) = hsv

        if s <= color_params.sat_W and v >= color_params.val_W:
            return 'white'
        elif color_params.orange_L <= h < color_params.orange_H:
            return 'orange'
        elif color_params.orange_H <= h < color_params.yellow_H:
            return 'yellow'
        elif color_params.yellow_H <= h < color_params.green_H:
            if s < 150:
                return 'white' # green s is always higher
            else:
                return 'green'
        elif color_params.green_H <= h < color_params.blue_H:
            if s < 150:
                return 'white' # blue s is always higher
            else:
                return 'blue'
        else:
            return 'red'

    def name_to_rgb(self, name):
        """
        Get the main RGB color for a name.

        :param name: the color name that is requested
        :returns: tuple
        """
        color = {
            'red'    : (0,0,255),
            'orange' : (0,165,255),
            'blue'   : (255,0,0),
            'green'  : (0,255,0),
            'white'  : (255,255,255),
            'yellow' : (0,255,255)
        }
        return color[name]

    def average_hsv(self, roi):
        """ Average the HSV colors in a region of interest.

        :param roi: the image array
        :returns: tuple
        """
        h   = 0
        s   = 0
        v   = 0
        num = 0
        for y in range(len(roi)):
            if y % 10 == 0:
                for x in range(len(roi[y])):
                    if x % 10 == 0:
                        chunk = roi[y][x]
                        num += 1
                        h += chunk[0]
                        s += chunk[1]
                        v += chunk[2]
        h /= num
        s /= num
        v /= num
        return (int(h), int(s), int(v))

ColorDetector = ColorDetection()
