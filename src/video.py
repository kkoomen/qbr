#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: fenc=utf-8 ts=4 sw=4 et

import cv2
from colordetection import color_detector
from config import config
from helpers import get_next_locale
import i18n
from PIL import ImageFont, ImageDraw, Image
import numpy as np
from constants import (
    COLOR_PLACEHOLDER,
    LOCALES,
    ROOT_DIR,
    CUBE_PALETTE,
    MINI_STICKER_AREA_TILE_SIZE,
    MINI_STICKER_AREA_TILE_GAP,
    MINI_STICKER_AREA_OFFSET,
    STICKER_AREA_TILE_SIZE,
    STICKER_AREA_TILE_GAP,
    STICKER_AREA_OFFSET,
    STICKER_CONTOUR_COLOR,
    CALIBRATE_MODE_KEY,
    SWITCH_LANGUAGE_KEY,
    TEXT_SIZE,
    E_INCORRECTLY_SCANNED,
    E_ALREADY_SOLVED
)

class Webcam:

    def __init__(self):
        print('Starting webcam... (this might take a while, please be patient)')
        self.cam = cv2.VideoCapture(0)
        print('Webcam successfully started')

        self.colors_to_calibrate = ['green', 'red', 'blue', 'orange', 'white', 'yellow']
        self.average_sticker_colors = {}
        self.result_state = {}

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

    def draw_stickers(self, stickers, offset_x, offset_y):
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
                    self.frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 0, 0),
                    -1
                )

                # foreground color
                cv2.rectangle(
                    self.frame,
                    (x1 + 1, y1 + 1),
                    (x2 - 1, y2 - 1),
                    color_detector.get_prominent_color(stickers[index]),
                    -1
                )

    def draw_preview_stickers(self):
        """Draw the current preview state onto the given frame."""
        self.draw_stickers(self.preview_state, STICKER_AREA_OFFSET, STICKER_AREA_OFFSET)

    def draw_snapshot_stickers(self):
        """Draw the current snapshot state onto the given frame."""
        y = STICKER_AREA_TILE_SIZE * 3 + STICKER_AREA_TILE_GAP * 2 + STICKER_AREA_OFFSET * 2
        self.draw_stickers(self.snapshot_state, STICKER_AREA_OFFSET, y)

    def find_contours(self, dilatedFrame):
        """Find the contours of a 3x3x3 cube."""
        contours, hierarchy = cv2.findContours(dilatedFrame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        final_contours = []

        # Step 1/4: filter all contours to only those that are square-ish shapes.
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

        # Return early if we didn't found 9 or more contours.
        if len(final_contours) < 9:
            return []

        # Step 2/4: Find the contour that has 9 neighbors (including itself)
        # and return all of those neighbors.
        found = False
        contour_neighbors = {}
        for index, contour in enumerate(final_contours):
            (x, y, w, h) = contour
            contour_neighbors[index] = []
            center_x = x + w / 2
            center_y = y + h / 2
            radius = 1.5

            # Create 9 positions for the current contour which are the
            # neighbors. We'll use this to check how many neighbors each contour
            # has. The only way all of these can match is if the current contour
            # is the center of the cube. If we found the center, we also know
            # all the neighbors, thus knowing all the contours and thus knowing
            # this shape can be considered a 3x3x3 cube. When we've found those
            # contours, we sort them and return them.
            neighbor_positions = [
                # top left
                [(center_x - w * radius), (center_y - h * radius)],

                # top middle
                [center_x, (center_y - h * radius)],

                # top right
                [(center_x + w * radius), (center_y - h * radius)],

                # middle left
                [(center_x - w * radius), center_y],

                # center
                [center_x, center_y],

                # middle right
                [(center_x + w * radius), center_y],

                # bottom left
                [(center_x - w * radius), (center_y + h * radius)],

                # bottom middle
                [center_x, (center_y + h * radius)],

                # bottom right
                [(center_x + w * radius), (center_y + h * radius)],
            ]

            for neighbor in final_contours:
                (x2, y2, w2, h2) = neighbor
                for (x3, y3) in neighbor_positions:
                    # The neighbor_positions are located in the center of each
                    # contour instead of top-left corner.
                    # logic: (top left < center pos) and (bottom right > center pos)
                    if (x2 < x3 and y2 < y3) and (x2 + w2 > x3 and y2 + h2 > y3):
                        contour_neighbors[index].append(neighbor)

        # Step 3/4: Now that we know how many neighbors all contours have, we'll
        # loop over them and find the contour that has 9 neighbors, which
        # includes itself. This is the center piece of the cube. If we come
        # across it, then the 'neighbors' are actually all the contours we're
        # looking for.
        for (contour, neighbors) in contour_neighbors.items():
            if len(neighbors) == 9:
                found = True
                final_contours = neighbors
                break

        if not found:
            return []

        # Step 4/4: When we reached this part of the code we found a cube-like
        # contour. The code below will sort all the contours on their X and Y
        # values from the top-left to the bottom-right.

        # Sort contours on the y-value first.
        y_sorted = sorted(final_contours, key=lambda item: item[1])

        # Split into 3 rows and sort each row on the x-value.
        top_row = sorted(y_sorted[0:3], key=lambda item: item[0])
        middle_row = sorted(y_sorted[3:6], key=lambda item: item[0])
        bottom_row = sorted(y_sorted[6:9], key=lambda item: item[0])

        sorted_contours = top_row + middle_row + bottom_row
        return sorted_contours

    def scanned_successfully(self):
        """Validate if the user scanned 9 colors for each side."""
        color_count = {}
        for side, preview in self.result_state.items():
            for bgr in preview:
                key = str(bgr)
                if key not in color_count:
                    color_count[key] = 1
                else:
                    color_count[key] = color_count[key] + 1
        invalid_colors = [k for k, v in color_count.items() if v != 9]
        return len(invalid_colors) == 0

    def draw_contours(self, contours):
        """Draw contours onto the given frame."""
        if self.calibrate_mode:
            # Only show the center piece contour.
            (x, y, w, h) = contours[4]
            cv2.rectangle(self.frame, (x, y), (x + w, y + h), STICKER_CONTOUR_COLOR, 2)
        else:
            for index, (x, y, w, h) in enumerate(contours):
                cv2.rectangle(self.frame, (x, y), (x + w, y + h), STICKER_CONTOUR_COLOR, 2)

    def update_preview_state(self, contours):
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

            roi = self.frame[y+7:y+h-7, x+14:x+w-14]
            avg_bgr = color_detector.get_dominant_color(roi)
            closest_color = color_detector.get_closest_color(avg_bgr)['color_bgr']
            self.preview_state[index] = closest_color
            if index in self.average_sticker_colors:
                self.average_sticker_colors[index].append(closest_color)
            else:
                self.average_sticker_colors[index] = [closest_color]

    def update_snapshot_state(self):
        """Update the snapshot state based on the current preview state."""
        self.snapshot_state = list(self.preview_state)
        center_color_name = color_detector.get_closest_color(self.snapshot_state[4])['color_name']
        self.result_state[center_color_name] = self.snapshot_state
        self.draw_snapshot_stickers()

    def get_font(self, size=TEXT_SIZE):
        """Load the truetype font with the specified text size."""
        font_path = '{}/assets/arial-unicode-ms.ttf'.format(ROOT_DIR)
        return ImageFont.truetype(font_path, size)

    def render_text(self, text, pos, color=(255, 255, 255), size=TEXT_SIZE, anchor='lt'):
        """
        Render text with a shadow using the pillow module.
        """
        font = self.get_font(size)

        # Convert opencv frame (np.array) to PIL Image array.
        frame = Image.fromarray(self.frame)

        # Draw the text onto the image.
        draw = ImageDraw.Draw(frame)
        draw.text(pos, text, font=font, fill=color, anchor=anchor,
                  stroke_width=1, stroke_fill=(0, 0, 0))

        # Convert the pillow frame back to a numpy array.
        self.frame = np.array(frame)

    def get_text_size(self, text, size=TEXT_SIZE):
        """Get text size based on the default freetype2 loaded font."""
        return self.get_font(size).getsize(text)

    def draw_scanned_sides(self):
        """Display how many sides are scanned by the user."""
        text = i18n.t('scannedSides', num=len(self.result_state.keys()))
        self.render_text(text, (20, self.height - 20), anchor='lb')

    def draw_current_color_to_calibrate(self):
        """Display the current side's color that needs to be calibrated."""
        offset_y = 20
        font_size = int(TEXT_SIZE * 1.25)
        if self.done_calibrating:
            messages = [
                i18n.t('calibratedSuccessfully'),
                i18n.t('quitCalibrateMode', keyValue=CALIBRATE_MODE_KEY),
            ]
            for index, text in enumerate(messages):
                _, textsize_height = self.get_text_size(text, font_size)
                y = offset_y + (textsize_height + 10) * index
                self.render_text(text, (int(self.width / 2), y), size=font_size, anchor='mt')
        else:
            current_color = self.colors_to_calibrate[self.current_color_to_calibrate_index]
            text = i18n.t('currentCalibratingSide.{}'.format(current_color))
            self.render_text(text, (int(self.width / 2), offset_y), size=font_size, anchor='mt')

    def draw_calibrated_colors(self):
        """Display all the colors that are calibrated while in calibrate mode."""
        offset_y = 20
        for index, (color_name, color_bgr) in enumerate(self.calibrated_colors.items()):
            x1 = 90
            y1 = int(offset_y + STICKER_AREA_TILE_SIZE * index)
            x2 = x1 + STICKER_AREA_TILE_SIZE
            y2 = y1 + STICKER_AREA_TILE_SIZE

            # shadow
            cv2.rectangle(
                self.frame,
                (x1, y1),
                (x2, y2),
                (0, 0, 0),
                -1
            )

            # foreground
            cv2.rectangle(
                self.frame,
                (x1 + 1, y1 + 1),
                (x2 - 1, y2 - 1),
                tuple([int(c) for c in color_bgr]),
                -1
            )
            self.render_text(i18n.t(color_name), (20, y1 + STICKER_AREA_TILE_SIZE / 2 - 3), anchor='lm')

    def reset_calibrate_mode(self):
        """Reset calibrate mode variables."""
        self.calibrated_colors = {}
        self.current_color_to_calibrate_index = 0
        self.done_calibrating = False

    def draw_current_language(self):
        text = '{}: {}'.format(
            i18n.t('language'),
            LOCALES[config.get_setting('locale')]
        )
        offset = 20
        self.render_text(text, (self.width - offset, offset), anchor='rt')

    def draw_2d_cube_state(self):
        """
        Create a 2D cube state visualization and draw the self.result_state.

        We're gonna display the visualization like so:
                    -----
                  | W W W |
                  | W W W |
                  | W W W |
            -----   -----   -----   -----
          | O O O | G G G | R R R | B B B |
          | O O O | G G G | R R R | B B B |
          | O O O | G G G | R R R | B B B |
            -----   -----   -----   -----
                  | Y Y Y |
                  | Y Y Y |
                  | Y Y Y |
                    -----
        So we're gonna make a 4x3 grid and hardcode where each side has to go.
        Based on the x and y in that 4x3 grid we can calculate its position.
        """
        grid = {
            'white' : [1, 0],
            'orange': [0, 1],
            'green' : [1, 1],
            'red'   : [2, 1],
            'blue'  : [3, 1],
            'yellow': [1, 2],
        }

        # The offset in-between each side (white, red, etc).
        side_offset = MINI_STICKER_AREA_TILE_GAP * 3

        # The size of 1 whole side (containing 9 stickers).
        side_size = MINI_STICKER_AREA_TILE_SIZE * 3 + MINI_STICKER_AREA_TILE_GAP * 2

        # The X and Y offset is placed in the bottom-right corner, minus the
        # whole size of the 4x3 grid, minus an additional offset.
        offset_x = self.width - (side_size * 4) - (side_offset * 3) - MINI_STICKER_AREA_OFFSET
        offset_y = self.height - (side_size * 3) - (side_offset * 2) - MINI_STICKER_AREA_OFFSET

        for side, (grid_x, grid_y) in grid.items():
            index = -1
            for row in range(3):
                for col in range(3):
                    index += 1
                    x1 = int(
                        (offset_x + MINI_STICKER_AREA_TILE_SIZE * col) +
                        (MINI_STICKER_AREA_TILE_GAP * col) +
                        ((side_size + side_offset) * grid_x)
                    )
                    y1 = int(
                        (offset_y + MINI_STICKER_AREA_TILE_SIZE * row) +
                        (MINI_STICKER_AREA_TILE_GAP * row) +
                        ((side_size + side_offset) * grid_y)
                    )
                    x2 = int(x1 + MINI_STICKER_AREA_TILE_SIZE)
                    y2 = int(y1 + MINI_STICKER_AREA_TILE_SIZE)

                    foreground_color = COLOR_PLACEHOLDER
                    if side in self.result_state:
                        foreground_color = color_detector.get_prominent_color(self.result_state[side][index])

                    # shadow
                    cv2.rectangle(
                        self.frame,
                        (x1, y1),
                        (x2, y2),
                        (0, 0, 0),
                        -1
                    )

                    # foreground color
                    cv2.rectangle(
                        self.frame,
                        (x1 + 1, y1 + 1),
                        (x2 - 1, y2 - 1),
                        foreground_color,
                        -1
                    )

    def get_result_notation(self):
        """Convert all the sides and their BGR colors to cube notation."""
        notation = dict(self.result_state)
        for side, preview in notation.items():
            for sticker_index, bgr in enumerate(preview):
                notation[side][sticker_index] = color_detector.convert_bgr_to_notation(bgr)

        # Join all the sides together into one single string.
        # Order must be URFDLB (white, red, green, yellow, orange, blue)
        combined = ''
        for side in ['white', 'red', 'green', 'yellow', 'orange', 'blue']:
            combined += ''.join(notation[side])
        return combined

    def state_already_solved(self):
        """Find out if the cube hasn't been solved already."""
        for side in ['white', 'red', 'green', 'yellow', 'orange', 'blue']:
            # Get the center color of the current side.
            center_bgr = self.result_state[side][4]

            # Compare the center color to all neighbors. If we come across a
            # different color, then we can assume the cube isn't solved yet.
            for bgr in self.result_state[side]:
                if center_bgr != bgr:
                    return False
        return True

    def run(self):
        """
        Open up the webcam and present the user with the Qbr user interface.

        Returns a string of the scanned state in rubik's cube notation.
        """
        while True:
            _, frame = self.cam.read()
            self.frame = frame
            key = cv2.waitKey(10) & 0xff

            # Quit on escape.
            if key == 27:
                break

            if not self.calibrate_mode:
                # Update the snapshot when space bar is pressed.
                if key == 32:
                    self.update_snapshot_state()

                # Switch to another language.
                if key == ord(SWITCH_LANGUAGE_KEY):
                    next_locale = get_next_locale(config.get_setting('locale'))
                    config.set_setting('locale', next_locale)
                    i18n.set('locale', next_locale)

            # Toggle calibrate mode.
            if key == ord(CALIBRATE_MODE_KEY):
                self.reset_calibrate_mode()
                self.calibrate_mode = not self.calibrate_mode

            grayFrame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            blurredFrame = cv2.blur(grayFrame, (3, 3))
            cannyFrame = cv2.Canny(blurredFrame, 30, 60, 3)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
            dilatedFrame = cv2.dilate(cannyFrame, kernel)

            contours = self.find_contours(dilatedFrame)
            if len(contours) == 9:
                self.draw_contours(contours)
                if not self.calibrate_mode:
                    self.update_preview_state(contours)
                elif key == 32 and self.done_calibrating is False:
                    current_color = self.colors_to_calibrate[self.current_color_to_calibrate_index]
                    (x, y, w, h) = contours[4]
                    roi = self.frame[y+7:y+h-7, x+14:x+w-14]
                    avg_bgr = color_detector.get_dominant_color(roi)
                    self.calibrated_colors[current_color] = avg_bgr
                    self.current_color_to_calibrate_index += 1
                    self.done_calibrating = self.current_color_to_calibrate_index == len(self.colors_to_calibrate)
                    if self.done_calibrating:
                        color_detector.set_cube_color_pallete(self.calibrated_colors)
                        config.set_setting(CUBE_PALETTE, color_detector.cube_color_palette)

            if self.calibrate_mode:
                self.draw_current_color_to_calibrate()
                self.draw_calibrated_colors()
            else:
                self.draw_current_language()
                self.draw_preview_stickers()
                self.draw_snapshot_stickers()
                self.draw_scanned_sides()
                self.draw_2d_cube_state()

            cv2.imshow("Qbr - Rubik's cube solver", self.frame)

        self.cam.release()
        cv2.destroyAllWindows()

        if len(self.result_state.keys()) != 6:
            return E_INCORRECTLY_SCANNED

        if not self.scanned_successfully():
            return E_INCORRECTLY_SCANNED

        if self.state_already_solved():
            return E_ALREADY_SOLVED

        return self.get_result_notation()


webcam = Webcam()
