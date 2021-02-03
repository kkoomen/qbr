#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: fenc=utf-8 ts=4 sw=4 et


import cv2
from colordetection import ColorDetector
import numpy as np
import math

STICKER_AREA_TILE_SIZE = 30
STICKER_AREA_TILE_GAP = 4
STICKER_AREA_OFFSET = 20
STICKER_CONTOUR_COLOR = (36, 255, 12)
CALIBRATE_MODE_KEY = 'c'
TEXT_FONT = cv2.FONT_HERSHEY_TRIPLEX
TEXT_SIZE = 0.5

class Webcam:

    def __init__(self):
        self.cube_sides = ['green', 'red', 'blue', 'orange', 'white', 'yellow']
        self.cam = cv2.VideoCapture(0)
        self.average_sticker_colors = {}
        self.sides = {}

        self.snapshot_state = [(255,255,255), (255,255,255), (255,255,255),
                               (255,255,255), (255,255,255), (255,255,255),
                               (255,255,255), (255,255,255), (255,255,255)]
        self.preview_state  = [(255,255,255), (255,255,255), (255,255,255),
                               (255,255,255), (255,255,255), (255,255,255),
                               (255,255,255), (255,255,255), (255,255,255)]

        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.width = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.calibrate_mode = False
        self.calibrated_colors = {}
        self.current_color_to_calibrate_index = 0
        self.done_calibrating = False

    def draw_stickers(self, frame, stickers, offset_x, offset_y):
        """Draws the given stickers onto the given frame."""
        index = -1
        for row in range(3):
            for col in range(3):
                index += 1
                x1 = (offset_x + STICKER_AREA_TILE_SIZE * col) + STICKER_AREA_TILE_GAP * col
                y1 = (offset_y + STICKER_AREA_TILE_SIZE * row) + STICKER_AREA_TILE_GAP * row
                x2 = x1 + STICKER_AREA_TILE_SIZE
                y2 = y1 + STICKER_AREA_TILE_SIZE

                # shadow
                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 0, 0),
                    -1
                )

                # foreground color
                cv2.rectangle(
                    frame,
                    (x1 + 1, y1 + 1),
                    (x2 - 1, y2 - 1),
                    ColorDetector.get_prominent_color(stickers[index]),
                    -1
                )

    def draw_preview_stickers(self, frame):
        """Draw the current preview state onto the given frame."""
        self.draw_stickers(frame, self.preview_state, STICKER_AREA_OFFSET, STICKER_AREA_OFFSET)

    def draw_snapshot_stickers(self, frame):
        """Draw the current snapshot state onto the given frame."""
        y = STICKER_AREA_TILE_SIZE * 3 + STICKER_AREA_TILE_GAP * 2 + STICKER_AREA_OFFSET * 2
        self.draw_stickers(frame, self.snapshot_state, STICKER_AREA_OFFSET, y)

    def find_contours(self, frame):
        """Finds the contours of a 3x3x3 cube."""
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
                if ratio >= 0.8 and ratio <= 1.2 and w >= 30 and w <= 60 and area / (w * h) > 0.4:
                    final_contours.append((x, y, w, h))

        # Remove those than have not that much neighbours.
        for contour in final_contours:
            neighbors = 0
            (x, y, w, h) = contour
            for (x2, y2, w2, h2) in final_contours:
                if abs(x - x2) < (w * 3.5) and abs(y - y2) < (h * 3.5):
                    neighbors += 1
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
        """Validate if the user scanned 9 colors for each side."""
        color_count = {}
        for side, preview in self.sides.items():
            for bgr in preview:
                key = str(bgr)
                if not key in color_count:
                    color_count[key] = 1
                else:
                    color_count[key] = color_count[key] + 1
        invalid_colors = [k for k, v in color_count.items() if v != 9]
        return len(invalid_colors) == 0

    def draw_contours(self, frame, contours):
        """Draw contours onto the given frame."""
        if self.calibrate_mode:
            # Only show the center piece's contour.
            (x, y, w, h) = contours[4]
            cv2.rectangle(frame, (x, y), (x + w, y + h), STICKER_CONTOUR_COLOR, 2)
        else:
            for index, (x, y, w, h) in enumerate(contours):
                cv2.rectangle(frame, (x, y), (x + w, y + h), STICKER_CONTOUR_COLOR, 2)

    def update_preview_state(self, frame, contours):
        """
        Get the average color value for the contour for every X amount of frames
        to prevent flickering and more precise results.
        """
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
                self.preview_state[index] = eval(most_common_color)
                break

            roi = frame[y+7:y+h-7, x+14:x+w-14]
            avg_bgr = ColorDetector.get_dominant_color(roi)
            closest_color = ColorDetector.get_closest_color(avg_bgr)['color_bgr']
            self.preview_state[index] = closest_color
            if index in self.average_sticker_colors:
                self.average_sticker_colors[index].append(closest_color)
            else:
                self.average_sticker_colors[index] = [closest_color]

    def update_snapshot_state(self, frame):
        """Update the snapshot state based on the current preview state."""
        self.snapshot_state = list(self.preview_state)
        center_color_name = ColorDetector.get_closest_color(self.snapshot_state[4])['color_name']
        self.sides[center_color_name] = self.snapshot_state
        self.draw_snapshot_stickers(frame)

    def render_text(self, frame, text, pos, color=(255, 255, 255), size=TEXT_SIZE):
        """Render text with a shadow."""
        cv2.putText(frame, text, pos, TEXT_FONT, size, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(frame, text, pos, TEXT_FONT, size, color, 1, cv2.LINE_AA)

    def display_scanned_sides(self, frame):
        """Display how many sides are scanned by the user."""
        text = 'scanned sides: {}/6'.format(len(self.sides.keys()))
        self.render_text(frame, text, (20, self.height - 20))

    def display_current_color_to_calibrate(self, frame):
        """Display the current side's color that needs to be calibrated."""
        if self.done_calibrating:
            messages = [
                'Calibrated successfully',
                'Press {} to quit calibrate mode'.format(CALIBRATE_MODE_KEY)
            ]
            for index, text in enumerate(messages):
                textsize = cv2.getTextSize(text, TEXT_FONT, TEXT_SIZE, 1)[0]
                y = 40 + 20 * index
                self.render_text(frame, text, (int(self.width / 2 - textsize[0] / 2), y))
        else:
            current_color = self.cube_sides[self.current_color_to_calibrate_index]
            text = 'Calibrating {} side'.format(current_color)
            textsize = cv2.getTextSize(text, TEXT_FONT, TEXT_SIZE, 1)[0]
            self.render_text(frame, text, (int(self.width / 2 - textsize[0] / 2), 40))

    def display_calibrated_colors(self, frame):
        """Display all the colors that are calibrated while in calibrate mode."""
        for index, (color_name, color_bgr) in enumerate(self.calibrated_colors.items()):
            y = int(STICKER_AREA_TILE_SIZE * (index + 1))
            cv2.rectangle(
                frame,
                (90, y),
                (90 + STICKER_AREA_TILE_SIZE, y + STICKER_AREA_TILE_SIZE),
                tuple([int(c) for c in color_bgr]),
                -1
            )
            self.render_text(frame, color_name, (20, y + 18))

    def reset_calibrate_mode(self):
        """Reset calibrate mode variables."""
        self.calibrated_colors = {}
        self.current_color_to_calibrate_index = 0
        self.done_calibrating = False

    def run(self):
        """
        Open up the webcam and present the user with the Qbr user interface.

        Returns a string of the scanned state in rubik's cube notation.
        """
        while True:
            _, frame = self.cam.read()
            key = cv2.waitKey(10) & 0xff

            # Quit on escape.
            if key == 27:
                break

            # Update the snapshot when space bar is pressed.
            if key == 32 and not self.calibrate_mode:
                self.update_snapshot_state(frame)

            # Toggle calibrate mode.
            if key == ord(CALIBRATE_MODE_KEY):
                self.reset_calibrate_mode()
                self.calibrate_mode = not self.calibrate_mode

            grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurredFrame = cv2.blur(grayFrame, (5, 5))
            cannyFrame = cv2.Canny(blurredFrame, 30, 60, 3)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
            dilatedFrame = cv2.dilate(cannyFrame, kernel)

            contours = self.find_contours(dilatedFrame)
            if len(contours) == 9:
                self.draw_contours(frame, contours)
                if not self.calibrate_mode:
                    self.update_preview_state(frame, contours)
                elif key == 32 and self.done_calibrating == False:
                    current_color = self.cube_sides[self.current_color_to_calibrate_index]
                    (x, y, w, h) = contours[4]
                    roi = frame[y+7:y+h-7, x+14:x+w-14]
                    avg_bgr = ColorDetector.get_dominant_color(roi)
                    self.calibrated_colors[current_color] = avg_bgr
                    self.current_color_to_calibrate_index += 1
                    self.done_calibrating = self.current_color_to_calibrate_index == len(self.cube_sides)
                    if self.done_calibrating:
                        ColorDetector.set_cube_color_pallete(self.calibrated_colors)

            if self.calibrate_mode:
                self.display_current_color_to_calibrate(frame)
                self.display_calibrated_colors(frame)
            else:
                self.draw_preview_stickers(frame)
                self.draw_snapshot_stickers(frame)
                self.display_scanned_sides(frame)

            cv2.imshow('default', frame)

        self.cam.release()
        cv2.destroyAllWindows()

        if len(self.sides.keys()) != 6:
            return False

        if not self.scanned_successfully():
            return False


        # Convert all the sides and their BGR colors to cube notation.
        notation = dict(self.sides)
        for side, preview in notation.items():
            for sticker_index, bgr in enumerate(preview):
                notation[side][sticker_index] = ColorDetector.convert_bgr_to_notation(bgr)

        # Join all the sides together into one single string.
        # Order must be URFDLB (white, red, green, yellow, orange, blue)
        combined = ''
        for side in ['white', 'red', 'green', 'yellow', 'orange', 'blue']:
            combined += ''.join(notation[side])
        return combined

webcam = Webcam()
