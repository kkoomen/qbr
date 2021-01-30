#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: fenc=utf-8 ts=4 sw=4 et


import json


class Normalizer:

    def algorithm(self, alg, language):
        """
        Normalize an algorithm with the solve manual.

        :param alg: The algorithm itself.
        :returns: list
        """
        with open('solve-manual.json') as f:
            manual = json.load(f)

        solution = []
        for notation in alg.split(' '):
            solution.append(manual[language][notation])
        return solution

normalize = Normalizer()
