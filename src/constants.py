#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: fenc=utf-8 ts=4 sw=4 et

import os

# Global
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Colors
COLOR_PLACEHOLDER = (150, 150, 150)

# i18n
LOCALES = {
    'de': 'Deutsch',
    'hu': 'Hungarian',
    'fr': 'French',
    'en': 'English',
    'nl': 'Nederlands',
    'zh': '简体中文',
}

# Camera interface
MINI_STICKER_AREA_TILE_SIZE = 14
MINI_STICKER_AREA_TILE_GAP = 2
MINI_STICKER_AREA_OFFSET = 20

STICKER_AREA_TILE_SIZE = 30
STICKER_AREA_TILE_GAP = 4
STICKER_AREA_OFFSET = 20

STICKER_CONTOUR_COLOR = (36, 255, 12)
CALIBRATE_MODE_KEY = 'c'
SWITCH_LANGUAGE_KEY = 'l'
TEXT_SIZE = 18

# Config
CUBE_PALETTE = 'cube_palette'

# Application errors
E_INCORRECTLY_SCANNED = 1
E_ALREADY_SOLVED = 2
