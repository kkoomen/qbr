#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Filename      : normalizer.py
# Author        : Kim K
# Created       : Sat, 30 Jan 2016
# Last Modified : Sat, 30 Jan 2016


from sys import exit as Die
try:
    import sys
    import json
except ImportError as err:
    Die(err)


class Normalizer:

    def algorithm(self, alg, language):
        """TODO: Docstring for algorithm.

        :param alg: The algorithm itself
        :returns: list
        """
        with open('solve-manual.json') as f:
            manual = json.load(f)

        solution = []
        for notation in alg.split(' '):
            solution.append(manual[language][notation])
        return solution

normalize = Normalizer()
