#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: fenc=utf-8 ts=4 sw=4 et


import cv2
from colordetection import ColorDetector
import numpy as np
import math


SCAN_STICKERS_AREA_TILE_SIZE = 30
PREVIEW_STICKER_STATE_TILE_SIZE = 32


class Webcam:

    def __init__(self):
        self.cam              = cv2.VideoCapture(0)
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
                # [200, 120], [300, 120], [400, 120],
                # [200, 220], [300, 220], [400, 220],
                # [200, 320], [300, 320], [400, 320]
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


    def draw_stickers(self, stickers, frame, state):
        """Draws the 9 current stickers in the frame."""
        for index, (x, y) in enumerate(stickers):
            cv2.rectangle(
                frame,
                (x, y),
                (x+PREVIEW_STICKER_STATE_TILE_SIZE, y+PREVIEW_STICKER_STATE_TILE_SIZE),
                state[index],
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
                # Find aspect ratio of boundary rectangle around the countours.
                ratio = w / float(h)
                # Check if contour is close to a square.
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

        # Sort contours on the y-value first.
        ySorted = sorted(finalContours[:9], key=lambda item: item[1])

        # Split into 3 rows and sort each row on the x-value.
        top_row = sorted(ySorted[0:3], key=lambda item: item[0])
        middle_row = sorted(ySorted[3:6], key=lambda item: item[0])
        bottom_row = sorted(ySorted[6:9], key=lambda item: item[0])

        sortedContours = top_row + middle_row + bottom_row
        return sortedContours

    def draw_contours(self, frame, contours):
        if len(contours) == 9:
            for index, (x, y, w, h) in enumerate(contours):
                cv2.rectangle(frame, (x, y), (x + w, y + h), (36, 255, 12), 2)
                cv2.putText(
                    frame,
                    '#{}'.format(index + 1),
                    (int(x + (w / 4)), int(y + h / 2)),
                    cv2.FONT_HERSHEY_TRIPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA
                )

    def scan(self):
        """
        Open up the webcam and scans the 9 regions in the center
        and show a preview in the left upper corner.

        After hitting the space bar to confirm, the block below the
        current stickers shows the current state that you have.
        This is show every user can see what the computer toke as input.

        :returns: dictionary
        """

        sides   = []
        preview = [(0,0,0), (0,0,0), (0,0,0),
                   (0,0,0), (0,0,0), (0,0,0),
                   (0,0,0), (0,0,0), (0,0,0)]
        state   = [(0,0,0), (0,0,0), (0,0,0),
                   (0,0,0), (0,0,0), (0,0,0),
                   (0,0,0), (0,0,0), (0,0,0)]
        while True:
            key = cv2.waitKey(10) & 0xff

            # Quit on escape.
            if key == 27:
                break

            _, frame = self.cam.read()
            # labFrame = cv2.cvtColor(frame, cv2.COLOR_RGB2LAB)
            grayFrame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            denoisedFrame = cv2.fastNlMeansDenoising(grayFrame, None, 10, 7, 7)
            blurredFrame = cv2.blur(denoisedFrame, (5, 5))
            cannyFrame = cv2.Canny(blurredFrame, 30, 60, 3)

            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
            dilatedFrame = cv2.dilate(cannyFrame, kernel)

            contours = self.find_contours(dilatedFrame)
            self.draw_contours(frame, contours)

            for index, (x, y, w, h) in enumerate(contours):
                roi = frame[y+10:y+h-10, x+10:x+w-10]
                avg_rgb = ColorDetector.get_dominant_rgb_color(roi)
                state[index] = avg_rgb

            # Update the snapshot preview when space bar is pressed.
            if key == 32:
                preview = list(state)
                sides.append(state)
                self.draw_stickers(self.preview_stickers, frame, preview)
                if len(sides) == 6:
                    break

            self.draw_stickers(self.current_stickers, frame, state)
            self.draw_stickers(self.preview_stickers, frame, preview)

            # Dislay amount of scanned sides.
            text = 'scanned sides: {}/6'.format(len(sides))
            cv2.putText(frame,
                        text,
                        (20, self.height - 20),
                        cv2.FONT_HERSHEY_TRIPLEX,
                        0.5,
                        (255, 255, 255),
                        1,
                        cv2.LINE_AA)

            # Show the result.
            cv2.imshow('default', frame)

        self.cam.release()
        cv2.destroyAllWindows()

        # TODO: convert rgb to color names.
        return sides if len(sides) == 6 else False

webcam = Webcam()
