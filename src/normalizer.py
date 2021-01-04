#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Filename      : normalizer.py
# Author        : Kim K
# Created       : Sat, 30 Jan 2016
# Last Modified : Mon, 01 Feb 2016

import json
from typing import List


class Normalizer:

    @staticmethod
    def algorithm(alg: str, language: str) -> List[str]:
        """
        Normalize an algorithm from the json-written manual.

        :param alg: The algorithm itself
        :param language: Language symbol
        :returns: list
        """
        with open('solve-manual.json') as f:
            manual = json.load(f)

        solution = []
        for notation in alg.split(' '):
            solution.append(manual[language][notation])
        return solution


normalize = Normalizer()
