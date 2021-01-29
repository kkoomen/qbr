#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: fenc=utf-8 ts=4 sw=4 et


import cv2
from colordetection import ColorDetector
import numpy as np
import math


SCAN_STICKERS_AREA_TILE_SIZE = 30
CURRENT_STICKER_STATE_TILE_SIZE = 32
PREVIEW_STICKER_STATE_TILE_SIZE = 32


class Webcam:

    def __init__(self):
        self.cam              = cv2.VideoCapture(0)
        self.stickers         = self.get_sticker_coordinates('main')
        self.current_stickers = self.get_sticker_coordinates('current')
        self.preview_stickers = self.get_sticker_coordinates('preview')

        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.width  = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))


    def get_sticker_coordinates(self, name):
        """
        Every array has 2 values: x and y.
        Grouped per 3 since on the cam will be
        3 rows of 3 stickers.

        :param name: the requested color type
        :returns: list
        """
        stickers = {
            'main': [
                [200, 120], [300, 120], [400, 120],
                [200, 220], [300, 220], [400, 220],
                [200, 320], [300, 320], [400, 320]
            ],
            'current': [
                [20, 20], [54, 20], [88, 20],
                [20, 54], [54, 54], [88, 54],
                [20, 88], [54, 88], [88, 88]
            ],
            'preview': [
                [20, 130], [54, 130], [88, 130],
                [20, 164], [54, 164], [88, 164],
                [20, 198], [54, 198], [88, 198]
            ]
        }

        return stickers[name]


    def draw_main_stickers(self, frame):
        """Draws the 9 stickers in the frame."""
        for x, y in self.stickers:
            cv2.rectangle(
                frame,
                (x, y),
                (x+SCAN_STICKERS_AREA_TILE_SIZE, y+SCAN_STICKERS_AREA_TILE_SIZE),
                (255, 255, 255),
                2
            )

    def draw_current_stickers(self, frame, state):
        """Draws the 9 current stickers in the frame."""
        for index, (x, y) in enumerate(self.current_stickers):
            cv2.rectangle(
                frame,
                (x, y),
                (x+CURRENT_STICKER_STATE_TILE_SIZE, y+CURRENT_STICKER_STATE_TILE_SIZE),
                ColorDetector.name_to_rgb(state[index]),
                -1
            )

    def draw_preview_stickers(self, frame, state):
        """Draws the 9 preview stickers in the frame."""
        for index, (x, y) in enumerate(self.preview_stickers):
            cv2.rectangle(
                frame,
                (x, y),
                (x+PREVIEW_STICKER_STATE_TILE_SIZE, y+PREVIEW_STICKER_STATE_TILE_SIZE),
                ColorDetector.name_to_rgb(state[index]),
                -1
            )

    def color_to_notation(self, color):
        """
        Return the notation from a specific color.
        We want a user to have green in front, white on top,
        which is the usual.

        :param color: the requested color
        """
        notation = {
            'green'  : 'F',
            'white'  : 'U',
            'blue'   : 'B',
            'red'    : 'R',
            'orange' : 'L',
            'yellow' : 'D'
        }
        return notation[color]

    def find_contours(self, frame):
        contours, hierarchy = cv2.findContours(frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        finalContours = []
        for contour in contours:
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.1 * perimeter, True)
            if len (approx) == 4:
                area = cv2.contourArea(contour)
                (x, y, w, h) = cv2.boundingRect(approx)
                # Find aspect ratio of boundary rectangle around the countours
                ratio = w / float(h)
                # Check if contour is close to a square
                if ratio > 0.8 and ratio < 1.2 and w > 30 and w < 60 and area / (w * h) > 0.4:
                    finalContours.append((x, y, w, h))

        # Remove those than have not that much neighbours.
        for contour in finalContours:
            neighbors = 0
            (x, y, w, h) = contour
            for (x2, y2, w2, h2) in finalContours:
                if abs(x - x2) < (w * 3.5) and abs(y - y2) < (h * 3.5):
                    neighbors +=1
            if neighbors < 5:
                finalContours.remove(contour)

        # Only return the first 9 contours.
        return finalContours[:9]

    def draw_contours(self, frame, contours):
        for x, y, w, h in contours:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (36, 255, 12), 2)

    def scan(self):
        """
        Open up the webcam and scans the 9 regions in the center
        and show a preview in the left upper corner.

        After hitting the space bar to confirm, the block below the
        current stickers shows the current state that you have.
        This is show every user can see what the computer toke as input.

        :returns: dictionary
        """

        sides   = {}
        preview = ['white', 'white', 'white',
                   'white', 'white', 'white',
                   'white', 'white', 'white']
        state   = [0, 0, 0,
                   0, 0, 0,
                   0, 0, 0]
        while True:
            _, frame = self.cam.read()
            grayFrame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            denoisedFrame = cv2.fastNlMeansDenoising(grayFrame, None, 10, 7, 7)
            blurredFrame = cv2.blur(denoisedFrame, (5, 5))
            cannyFrame = cv2.Canny(blurredFrame, 30, 60, 3)

            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
            dilatedFrame = cv2.dilate(cannyFrame, kernel)
            contours = self.find_contours(dilatedFrame)
            self.draw_contours(frame, contours)

            # hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            key = cv2.waitKey(10) & 0xff

            # init certain stickers.
            # self.draw_main_stickers(frame)
            # self.draw_preview_stickers(frame, preview)

            # for index, (x, y) in enumerate(self.stickers):
            #     roi          = hsv[y:y+32, x:x+32]
            #     avg_hsv      = ColorDetector.average_hsv(roi)
            #     color_name   = ColorDetector.get_color_name(avg_hsv)
            #     state[index] = color_name
            #
            #     # update when space bar is pressed.
            #     if key == 32:
            #         preview = list(state)
            #         self.draw_preview_stickers(frame, state)
            #         face = self.color_to_notation(state[4])
            #         notation = [self.color_to_notation(color) for color in state]
            #         sides[face] = notation

            # show the new stickers
            # self.draw_current_stickers(frame, state)

            # append amount of scanned sides
            text = 'scanned sides: {}/6'.format(len(sides))
            cv2.putText(frame, text, (20, self.height - 20), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

            # quit on escape.
            if key == 27:
                break

            # show result
            cv2.imshow('default', frame)
            # cv2.imshow('denoised', denoisedFrame)
            # cv2.imshow('gray', grayFrame)
            # cv2.imshow('blur', blurredFrame)
            cv2.imshow('dilated', dilatedFrame)

        self.cam.release()
        cv2.destroyAllWindows()
        return sides if len(sides) == 6 else False

webcam = Webcam()
