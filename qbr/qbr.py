#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Filename      : qbr.py
# Author        : Kim K
# Created       : Tue, 26 Jan 2016
# Last Modified : Fri, 29 Jan 2016


from sys import exit as Die
try:
    import sys
    import os
    import kociemba

    from colordetection import ColorDetector
    from combiner import combine
    from video import webcam
except Exception as err:
    Die(err)


class Qbr:

    def run(self):
        state         = webcam.scan()
        unsolvedState = combine.sides(state)
        algorithm     = kociemba.solve(unsolvedState)
        length        = len(algorithm.split(' '))
        print('-- SOLUTION --')
        print('Starting position:\n    front: green\n    top: white\n')
        print(algorithm, '({0} moves)'.format(length))

if __name__ == '__main__':
    Qbr().run()
