#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: fenc=utf-8 ts=4 sw=4 et


import sys
import kociemba
import argparse
from combiner import combine
from video import webcam
from normalizer import normalize


class Qbr:

    def __init__(self, normalize, language):
        self.humanize = normalize
        self.language = (language[0]) if isinstance(language, list) else language

    def run(self):
        state = webcam.scan()
        if not state:
            print('\033[0;33m[QBR SCAN ERROR] Ops, you did not scan in all 6 sides.')
            print('Please try again.\033[0m')
            Die(1)

        unsolvedState = combine.sides(state)
        try:
            algorithm = kociemba.solve(unsolvedState)
            length = len(algorithm.split(' '))
        except Exception as err:
            print('\033[0;33m[QBR SOLVE ERROR] Ops, you did not scan in all 6 sides correctly.')
            print('Please try again.\033[0m')
            Die(1)

        print('-- SOLUTION --')
        print('Starting position:\n    front: green\n    top: white\n')
        print(algorithm, '({0} moves)'.format(length), '\n')

        if self.humanize:
            manual = normalize.algorithm(algorithm, self.language)
            for index, text in enumerate(manual):
                print('{}. {}'.format(index+1, text))
        Die(0)

if __name__ == '__main__':
    # define argument parser.
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--normalize', default=False, action='store_true',
            help='Shows the solution normalized. For example "R2" would be: \
                    "Turn the right side 180 degrees".')
    parser.add_argument('-l', '--language', nargs=1, default='en',
            help='You can pass in a single \
                    argument which will be the language for the normalization output. \
                    Default is "en".')
    args = parser.parse_args()

    # run Qbr with its arguments.
    Qbr(
        args.normalize,
        args.language
    ).run()
