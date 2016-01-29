#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Filename      : video.py
# Author        : Kim K
# Created       : Fri, 29 Jan 2016
# Last Modified : Fri, 29 Jan 2016


from sys import exit as Die
try:
    import sys
    import cv2
    from colordetection import ColorDetector
except ImportError as err:
    Die(err)


class Webcam:

    def __init__(self):
        self.cam              = cv2.VideoCapture(0)
        self.stickers         = self.get_sticker_coordinates()
        self.preview_stickers = self.get_preview_sticker_coordinates()

    def get_sticker_coordinates(self):
        """
        Every array has 2 values: x and y.
        Grouped per 3 , since on the cam will be
        3 rows of 3 stickers.

        :returns: list
        """
        stickers = [
            [200, 120], [300, 120], [400, 120],
            [200, 220], [300, 220], [400, 220],
            [200, 320], [300, 320], [400, 320]
        ]
        return stickers

    def get_preview_sticker_coordinates(self):
        """
        Every array has 2 values: x and y starting point.
        Grouped per 3 , since on the cam will be
        3 rows of 3 stickers.

        :returns: array
        """
        stickers = [
            [20, 20], [54, 20], [88, 20],
            [20, 54], [54, 54], [88, 54],
            [20, 88], [54, 88], [88, 88]
        ]
        return stickers

    def draw_stickers(self, frame):
        """Draws the 9 stickers in the frame."""
        for x,y in self.stickers:
            cv2.rectangle(frame, (x,y), (x+80, y+80), (255,255,255), 2)

    def draw_preview(self, frame, state):
        """Draws the 9 preview stickers in the frame."""
        for index,(x,y) in enumerate(self.preview_stickers):
            cv2.rectangle(frame, (x,y), (x+32, y+32), self.name_to_rgb(state[index]), -1)

    def name_to_rgb(self, name):
        """
        Get the main RGB color for a name.

        :param name: the main color name that has to be converted to RGB
        :returns: tuple
        """
        hexs = {
            'red'    : (0,0,255),
            'orange' : (0,165,255),
            'blue'   : (255,0,0),
            'green'  : (0,255,0),
            'white'  : (255,255,255),
            'yellow' : (0,255,255)
        }
        return hexs[name]

    def color_to_notation(self, color):
        """
        Return the notation from a specific color.
        We want a user to have green in front, white on top,
        which is the usual.

        :param color: the requested color
        """
        colors = {
            'green'  : 'F',
            'white'  : 'U',
            'blue'   : 'B',
            'red'    : 'R',
            'orange' : 'L',
            'yellow' : 'D'
        }
        return colors[color]

    def scan(self):
        """
        Open up the webcam and scan the regions 9 in the center
        and show a preview in the left upper corner.

        :returns: dictionary
        """

        sides = {}
        while True:
            _, frame = self.cam.read()
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            key = cv2.waitKey(10) & 0xff
            self.draw_stickers(frame)

            state = [0,0,0,
                     0,0,0,
                     0,0,0]
            for index,(x,y) in enumerate(self.stickers):
                roi          = hsv[y:y+80, x:x+80]
                rgb          = ColorDetector.average_rgb(roi)
                color_name   = ColorDetector.get_color_name(rgb)
                state[index] = color_name
            self.draw_preview(frame, state)
            cv2.imshow("default", frame)

            if key == 32:
                face = self.color_to_notation(state[4])
                notation = [self.color_to_notation(color) for color in state]
                sides[face] = notation
            elif key == 27:
                break
        self.cam.release()
        cv2.destroyAllWindows()
        return sides

webcam = Webcam()
