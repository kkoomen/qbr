#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Filename      : qbr.py
# Author        : Kim K
# Created       : Tue, 26 Jan 2016
# Last Modified : Tue, 26 Jan 2016


from sys import exit as Die
try:
    import sys
    import os
    import kociemba

    from colordetection import ColorDetector
    from combiner import combine
except Exception as err:
    Die(err)


class Qbr:

    def __init__(self):
        self.images = ['img/{}'.format(img) for img in os.listdir('img/')]

    def run(self):
        full_cube_state = {}
        for image in self.images:
            # Here we receive the following two-dimensional array from the
            # ColorDetector (just an example. Could be any scramble).
            #
            # [[ 'green' , 'red'    , 'white' ],
            #  [ 'green' , 'orange' , 'white' ],
            #  [ 'blue'  , 'orange' , 'yellow' ]]
            humanizedState = ColorDetector.detect(image)
            face = humanizedState[1][1]

            # Convert the color words into actual cubing letters.
            # Let's say we convert the above to letters. That'd be:
            #
            # [[ 'F' , 'R' , 'U' ],
            #  [ 'F' , 'L' , 'U' ],
            #  [ 'B' , 'L' , 'D' ]]
            state = ColorDetector.to_letter(humanizedState)

            # join the two-dimensional arrays into a string.
            combinedStates = combine.state(face, state)

            # append to full_cube_state where the index 0 is the face
            # and index 1 is the state.
            full_cube_state[combinedStates[0]] = combinedStates[1]

        # finally we start combining all the sides into the solved state.
        unsolvedState = combine.sides(full_cube_state)

        # use the kociemba algorithm to solve this.
        solvingAlgorithm = kociemba.solve(unsolvedState)
        print(solvingAlgorithm)


if __name__ == '__main__':
    Qbr().run()
