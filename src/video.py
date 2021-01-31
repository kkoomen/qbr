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
        self.average_sticker_colors = {}
        self.sides = {}

        self.preview = [(0,0,0), (0,0,0), (0,0,0),
                        (0,0,0), (0,0,0), (0,0,0),
                        (0,0,0), (0,0,0), (0,0,0)]
        self.state   = [(0,0,0), (0,0,0), (0,0,0),
                        (0,0,0), (0,0,0), (0,0,0),
                        (0,0,0), (0,0,0), (0,0,0)]

        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.width  = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def get_sticker_coordinates(self, group):
        """
        Get sticker coordinates from a specific group.
        These coordinates are the state previews in the top left corner.

        Every array has 2 values: x and y.

        :param group: The requested color type coordinates.
        :returns: list
        """
        stickers = {
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
        return stickers[group]


    def draw_stickers(self, stickers, frame, state):
        """Draws the 9 current stickers in the frame."""
        for index, (x, y) in enumerate(stickers):
            cv2.rectangle(
                frame,
                (x, y),
                (x+PREVIEW_STICKER_STATE_TILE_SIZE, y+PREVIEW_STICKER_STATE_TILE_SIZE),
                tuple([int(c) for c in state[index]]),
                -1
            )

    def find_contours(self, frame):
        """Finds the contours of the 3x3."""
        contours, hierarchy = cv2.findContours(frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        final_contours = []
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
                    final_contours.append((x, y, w, h))

        # Remove those than have not that much neighbours.
        for contour in final_contours:
            neighbors = 0
            (x, y, w, h) = contour
            for (x2, y2, w2, h2) in final_contours:
                if abs(x - x2) < (w * 3.5) and abs(y - y2) < (h * 3.5):
                    neighbors +=1
            if neighbors < 5:
                final_contours.remove(contour)

        # Sort contours on the y-value first.
        y_sorted = sorted(final_contours[:9], key=lambda item: item[1])

        # Split into 3 rows and sort each row on the x-value.
        top_row = sorted(y_sorted[0:3], key=lambda item: item[0])
        middle_row = sorted(y_sorted[3:6], key=lambda item: item[0])
        bottom_row = sorted(y_sorted[6:9], key=lambda item: item[0])

        sorted_contours = top_row + middle_row + bottom_row
        return sorted_contours

    def scanned_successfully(self):
        """
        Validate if the user scanned 9 colors for each side.

        :param state list: The completely scanned cube state.
        :returns: boolean
        """
        color_count = {}
        for side, state in self.sides.items():
            for bgr in state:
                key = str(bgr)
                if not key in color_count:
                    color_count[key] = 1
                else:
                    color_count[key] = color_count[key] + 1
        invalid_colors = [k for k, v in color_count.items() if v != 9]
        return len(invalid_colors) == 0

    def draw_contours(self, frame, contours):
        for index, (x, y, w, h) in enumerate(contours):
            cv2.rectangle(frame, (x, y), (x + w, y + h), (36, 255, 12), 2)

    def update_state(self, frame, contours):
        # Get the average color value for the contour for every X
        # amount of frames to prevent flickering.
        max_average_rounds = 8
        for index, (x, y, w, h) in enumerate(contours):
            if index in self.average_sticker_colors and len(self.average_sticker_colors[index]) == max_average_rounds:
                sorted_items = {}
                for bgr in self.average_sticker_colors[index]:
                    key = str(bgr)
                    if key in sorted_items:
                        sorted_items[key] += 1
                    else:
                        sorted_items[key] = 1
                most_common_color = max(sorted_items, key=lambda i: sorted_items[i])
                self.average_sticker_colors[index] = []
                self.state[index] = eval(most_common_color)
                break

            roi = frame[y+7:y+h-7, x+14:x+w-14]
            avg_bgr = ColorDetector.get_dominant_color(roi)
            closest_color = ColorDetector.get_closest_color(avg_bgr)['color_bgr']
            self.state[index] = closest_color
            if index in self.average_sticker_colors:
                self.average_sticker_colors[index].append(closest_color)
            else:
                self.average_sticker_colors[index] = [closest_color]

    def update_preview(self, frame):
        self.preview = list(self.state)
        center_color_name = ColorDetector.get_closest_color(self.preview[4])['color_name']
        self.sides[center_color_name] = self.preview
        self.draw_stickers(self.preview_stickers, frame, self.preview)

    def scan(self):
        """
        Open up the webcam and scans the 9 regions in the center
        and show a preview in the left upper corner.

        After hitting the space bar to confirm, the block below the
        current stickers shows the current state that you have.
        This is show every user can see what the computer toke as input.

        :returns: dictionary
        """
        while True:
            key = cv2.waitKey(10) & 0xff

            # Quit on escape.
            if key == 27:
                break

            _, frame = self.cam.read()
            grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # denoisedFrame = cv2.fastNlMeansDenoising(grayFrame, None, 10, 7, 7)
            blurredFrame = cv2.blur(grayFrame, (5, 5))
            cannyFrame = cv2.Canny(blurredFrame, 30, 60, 3)

            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
            dilatedFrame = cv2.dilate(cannyFrame, kernel)

            contours = self.find_contours(dilatedFrame)
            if len(contours) == 9:
                self.draw_contours(frame, contours)
                self.update_state(frame, contours)

            # Update the snapshot preview when space bar is pressed.
            if key == 32:
                self.update_preview(frame)

            self.draw_stickers(self.current_stickers, frame, self.state)
            self.draw_stickers(self.preview_stickers, frame, self.preview)

            # Dislay amount of scanned sides.
            text = 'scanned sides: {}/6'.format(len(self.sides.keys()))
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

        if len(self.sides.keys()) != 6:
            return False

        if not self.scanned_successfully():
            return False


        # Convert all the sides and their BGR colors to cube notation.
        notation = dict(self.sides)
        for side, state in notation.items():
            for sticker_index, bgr in enumerate(state):
                notation[side][sticker_index] = ColorDetector.convert_bgr_to_notation(bgr)

        # Join all the sides together into one single string.
        # Order must be URFDLB (white, red, green, yellow, orange, blue)
        combined = ''
        for side in ['white', 'red', 'green', 'yellow', 'orange', 'blue']:
            combined += ''.join(notation[side])
        return combined

webcam = Webcam()
