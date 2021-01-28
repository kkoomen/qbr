#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: fenc=utf-8 ts=4 sw=4 et


class Combine:

    def sides(self, sides):
        """Join all the sides together into one single string.

        :param sides: dictionary with all the sides
        :returns: string
        """
        combined = ''
        for face in 'URFDLB':
            combined += ''.join(sides[face])
        return combined

combine = Combine()
