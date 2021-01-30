#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: fenc=utf-8 ts=4 sw=4 et


import numpy as np
import cv2

class ColorDetection:

    def get_color_name(self, hsv):
        """ Get the name of the color based on the hue.

        :returns: string
        """
        (h,s,v) = hsv
        if h < 15 and v < 100:
            return 'red'
        if h <= 10 and v > 100:
            return 'orange'
        elif h <= 30 and s <= 100:
            return 'white'
        elif h <= 40:
            return 'yellow'
        elif h <= 85:
            return 'green'
        elif h <= 130:
            return 'blue'

        return 'white'

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

    def get_dominant_rgb_color(self, roi):
        """ Get dominant RGB from a certain region of interest.

        :param roi: the image array
        :returns: tuple
        """
        average = roi.mean(axis=0).mean(axis=0)
        pixels = np.float32(roi.reshape(-1, 3))

        n_colors = 5
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
        flags = cv2.KMEANS_RANDOM_CENTERS
        _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
        _, counts = np.unique(labels, return_counts=True)
        dominant = palette[np.argmax(counts)]
        color = tuple([int(c) for c in dominant])
        return color

ColorDetector = ColorDetection()
