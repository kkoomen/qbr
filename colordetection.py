#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Filename      : colordetection.py
# Author        : Kim K
# Created       : Tue, 26 Jan 2016
# Last Modified : Tue, 26 Jan 2016


from sys import exit as Die
try:
    from PIL import Image
    import numpy
    from math import ceil
    import json
except Exception as err:
    Die(err)

class ColorDetection:

    def to_hex(self, r, g, b):
        """
        :param r: string containing a red RGB value.
        :param g: string containing a green RGB value.
        :param b: string containing a blue RGB value.
        :returns: string
        """
        HEX = '#%02x%02x%02x' % (r, g, b)
        return HEX.upper()

    def to_letter(self, side):
        """
        Since the ColorDetector returns a dimensional array with all the colors
        we also need for every color to determine a face with it.

        :param side: this will be one side of the cube which includes 9 colors.
        :returns: array
        """
        letters = {
            'green'  : 'F',
            'white'  : 'U',
            'blue'   : 'B',
            'red'    : 'R',
            'orange' : 'L',
            'yellow' : 'D'
        }
        state = [[0, 0, 0],
                 [0, 0, 0],
                 [0, 0, 0]]
        for yi,y in enumerate(side):
            for xi,x in enumerate(side[yi]):
                color = side[yi][xi]
                state[yi][xi] = letters[color]
        return state

    def detect(self, imagePath):
        """
        Get the 9 colors of the image and return for each color its name.
        Names can be: yellow, white, red, orange, blue, green.

        :param imagePath: an image path received in the format => img/filename.ext
        :returns: string
        """
        # Gather all the websafecolors (dictionary)
        with open('websafecolors.json') as f:
            websafecolors = eval(f.read())

        # Open image and convert every row/column of pixels into an array.
        img      = Image.open(imagePath)
        imageArr = numpy.asarray(img)

        # Get 1/6th, 3/6th and 5/6th of the image foreach row and column.
        # With this we have for every sticker its center.
        row    = [ceil(len(imageArr) / 6 * n) for n in (1,3,5)]
        column = [ceil(len(imageArr[0]) / 6 * n) for n in (1,3,5)]

        state = [[0, 0, 0],
                 [0, 0, 0],
                 [0, 0, 0]]
        for yi, y in enumerate(row):
            for xi,x in enumerate(column):
                # convert the RGB to web safe color palette.
                r,g,b      = [ceil((imageArr[y][x][i] / 255) * 5) * 51 for i,num in enumerate(imageArr[y][x])]
                hexVersion = self.to_hex(r,g,b)
                for color in websafecolors:
                    if hexVersion in websafecolors[color]:
                        state[yi][xi] = color
                        break
                else:
                    newColor = input('[UNDEFINED HEX] {}. \nWhat color does this HEX belongs to? '.format(hexVersion))
                    if (newColor):
                        print('Thank you for your feedback. \
                                {} has been saved under the color {}'.format(hexVersion, newColor))
                        websafecolors[newColor].append(hexVersion)
                        json.dump(websafecolors, open('websafecolors.json', 'w'), sort_keys=True, indent=4)

        return state
        #Die(0)

ColorDetector = ColorDetection()
