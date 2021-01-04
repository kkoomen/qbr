#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Filename      : colordetection.py
# Author        : Kim K
# Created       : Tue, 26 Jan 2016
# Last Modified : Sun, 31 Jan 2016

# Built-ins
from sys import exit as die
from typing import Tuple

# 3rd Party
try:
    from numpy import ndarray as np_ndarray     # type: ignore
except ImportError as err:
    np_ndarray = None
    die(err)


class ColorDetection:

    @staticmethod
    def get_color_name(hsv: Tuple[int, int, int]) -> str:
        """
        Get the name of the color based on the hue.

        :param hsv: An HSV tuple
        :returns: The name of the color
        """
        (h, s, v) = hsv
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

    @staticmethod
    def name_to_rgb(name: str) -> Tuple[int, int, int]:
        """
        Get the main RGB color for a name.

        :param name: the color name that is requested
        :returns: tuple
        """
        color = {
            'red':      (0, 0, 255),
            'orange':   (0, 165, 255),
            'blue':     (255, 0, 0),
            'green':    (0, 255, 0),
            'white':    (255, 255, 255),
            'yellow':   (0, 255, 255)
        }
        return color[name]

    @staticmethod
    def average_hsv(roi: np_ndarray) -> Tuple[int, int, int]:
        """ Average the HSV colors in a region of interest.

        :param roi: the image array
        :returns: tuple
        """
        h, s, v, num = (0.0, 0.0, 0.0, 0)
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
        return int(h), int(s), int(v)


color_detector = ColorDetection()
