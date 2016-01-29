#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Filename      : combiner.py
# Author        : Kim K
# Created       : Tue, 26 Jan 2016
# Last Modified : Fri, 29 Jan 2016


class Combine:

    def sides(self, sides):
        """Join all the sides together into one single string.

        :param sides: dictionary with all the sides
        :returns: string
        """
        combined = ''
        for face in ('U','R','F','D','L','B'):
            combined += ''.join(sides[face])
        return combined

combine = Combine()
