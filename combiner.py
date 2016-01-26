#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Filename      : combiner.py
# Author        : Kim K
# Created       : Tue, 26 Jan 2016
# Last Modified : Tue, 26 Jan 2016


class Combine:

    def sides(self, sides):
        """
        TODO: combine all the sides into one string

        :param sides: dictionary with the whole cube and all its sides
        :returns: string
        """
        combined = ''
        for face in ('U','R','F','D','L','B'):
            combined += sides[face]
        return combined

    def state(self, face, state):
        """
        Comebine the jagged array into a string.

        :param face: the face color (in human-readable format).
        :param state: the scrambled state of a side.
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
        combined = ''
        for index,y in enumerate(state):
            combined += ''.join(state[index])
        return [letters[face], combined]

combine = Combine()
