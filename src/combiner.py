#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Filename      : combiner.py
# Author        : Kim K
# Created       : Tue, 26 Jan 2016
# Last Modified : Sat, 30 Jan 2016

from typing import List, Dict


class Combine:

    @staticmethod
    def sides(sides: Dict[str, List[str]]) -> str:
        """
        Join all the sides together into one single string.

        :param sides: dictionary with all the sides
        :returns: string
        """
        combined = ''
        for face in 'URFDLB':
            combined += ''.join(sides[face])
        return combined


combine = Combine()
